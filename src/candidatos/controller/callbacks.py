"""Registro dos callbacks (controller)."""

from __future__ import annotations

from dash import Input, Output, State, ctx, html, no_update

from .. import config
from ..model import metrics
from ..view import charts, ids
from ..view.components import card
from ..view.formatting import brl, num


def _kpis(ind: dict) -> list:
    return [
        card("Receita declarada", brl(ind["receita"]), f"{num(ind['n_lancamentos_receita'], 0)} lancamentos", config.AZUL),
        card("Despesas contratadas", brl(ind["contratado"]), f"{num(ind['n_lancamentos_despesa'], 0)} lancamentos", config.LARANJA),
        card("Despesas pagas", brl(ind["pago"]), f"{num(ind['n_lancamentos_pago'], 0)} lancamentos", config.VERDE),
        card("Divida estimada (C - P)", brl(ind["divida"]), "sem entrega Final (estimativa)", config.VERMELHO),
        card("Candidatos", num(ind["candidatos"], 0), "com receita declarada", config.ROXO),
    ]


def _selecoes_info(selecao: dict) -> list:
    if not selecao:
        return [html.Span(
            "Clique numa barra para filtrar os demais graficos (clique de novo para desligar).",
            className="sel-hint",
        )]
    itens = []
    for coluna, valor in selecao.items():
        rotulo = ids.ROTULO_DIMENSAO.get(coluna, coluna)
        itens.append(html.Span([html.B(f"{rotulo}: "), str(valor)], className="chip"))
    return itens


def _sem_dimensao(selecao: dict, dim: str | None) -> tuple:
    return tuple(sorted((k, v) for k, v in selecao.items() if k != dim))


def atualizar(uf: str, cargo: str, partido: str, espectro: str, selecao: dict | None = None) -> tuple:
    """Calcula KPIs e figuras para um conjunto de filtros (testavel isoladamente).

    O filtro cruzado (``selecao``) e aplicado a cada grafico, exceto na dimensao
    que aquele proprio grafico controla. Assim, ao clicar em SP no grafico de UF,
    os demais graficos filtram por SP, mas o grafico de UF continua mostrando todas
    as UFs (para permitir trocar a selecao).
    """
    selecao = selecao or {}
    base = (uf, cargo, partido, espectro)
    cache: dict[tuple, tuple] = {}

    def resumos(extras: tuple) -> tuple:
        if extras not in cache:
            u, c, p, e = base
            cache[extras] = (
                metrics.resumo_receitas(u, c, p, e, extras),
                metrics.resumo_despesas(u, c, p, e, extras),
                metrics.resumo_pagas(u, extras),
            )
        return cache[extras]

    def para(grafico: str) -> tuple:
        dim = ids.DIMENSOES.get(grafico, (None, None))[0]
        return resumos(_sem_dimensao(selecao, dim)), selecao.get(dim)

    rec_full, desp_full, pag_full = resumos(tuple(sorted(selecao.items())))
    ind = metrics.indicadores(rec_full, desp_full, pag_full)

    rec_uf, d_uf = para("g-receita-uf")
    ctp, d_ctp = para("g-contratado-pago")
    rec_p, d_p = para("g-receita-partido")
    rec_e, d_e = para("g-espectro")
    desp_e, d_desp_e = para("g-desp-espectro")
    rec_f, d_f = para("g-fonte")
    rec_n, d_n = para("g-natureza")
    desp_c, d_c = para("g-desp-cat")
    desp_fr, d_fr = para("g-fornecedores")
    rec_g, d_g = para("g-genero")
    rec_c, d_cor = para("g-cor")
    rec_bg, _ = para("g-receita-box-genero")
    rec_bc, _ = para("g-receita-box-cor")
    rec_conc, _ = para("g-concentracao")

    return (
        _kpis(ind),
        _selecoes_info(selecao),
        charts.fig_receita_uf_mapa(rec_uf[0], d_uf),
        charts.fig_receita_partido(rec_p[0], d_p),
        charts.fig_receita_espectro(rec_e[0], d_e),
        charts.fig_despesa_espectro(desp_e[1], d_desp_e),
        charts.fig_fonte(rec_f[0], d_f),
        charts.fig_natureza(rec_n[0], d_n),
        charts.fig_despesa_categoria(desp_c[1], d_c),
        charts.fig_contratado_pago(ctp[1], ctp[2], d_ctp),
        charts.fig_fornecedores(desp_fr[1], d_fr),
        charts.fig_genero(rec_g[0], d_g),
        charts.fig_cor_raca(rec_c[0], d_cor),
        charts.fig_concentracao(rec_conc[0]),
        charts.fig_receita_genero_box(rec_bg[0]),
        charts.fig_receita_cor_box(rec_bc[0]),
    )


def _valor_clicado(click_data: dict | None):
    if not click_data or not click_data.get("points"):
        return None
    ponto = click_data["points"][0]
    custom = ponto.get("customdata")
    if isinstance(custom, (list, tuple)):
        return custom[0] if custom else None
    if custom is not None:
        return custom
    return ponto.get("x") if ponto.get("x") is not None else ponto.get("y")


def register_callbacks(app) -> None:
    @app.callback(
        Output(ids.SELECAO, "data"),
        *[Output(g, "clickData") for g in ids.GRAFICOS],
        *[Input(g, "clickData") for g in ids.GRAFICOS],
        Input(ids.BOTAO_LIMPAR, "n_clicks"),
        State(ids.SELECAO, "data"),
        prevent_initial_call=True,
    )
    def _selecionar(*args):
        cliques = args[: len(ids.GRAFICOS)]
        selecao = dict(args[-1] or {})
        acionado = ctx.triggered_id

        if acionado == ids.BOTAO_LIMPAR:
            return ({}, *[None] * len(ids.GRAFICOS))

        if acionado not in ids.DIMENSOES:
            return (no_update, *[no_update] * len(ids.GRAFICOS))

        valor = _valor_clicado(cliques[ids.GRAFICOS.index(acionado)])
        if valor is None:
            # Eco do reset de clickData que fizemos no clique anterior.
            return (no_update, *[no_update] * len(ids.GRAFICOS))

        dim = ids.DIMENSOES[acionado][0]
        if selecao.get(dim) == valor:
            selecao.pop(dim, None)
        else:
            selecao[dim] = valor
        # Reseta clickData para que cliques repetidos voltem a disparar o callback.
        return (selecao, *[None] * len(ids.GRAFICOS))

    @app.callback(
        Output(ids.KPIS, "children"),
        Output(ids.SELECOES_INFO, "children"),
        *[Output(g, "figure") for g in ids.GRAFICOS],
        Input(ids.FILTRO_UF, "value"),
        Input(ids.FILTRO_CARGO, "value"),
        Input(ids.FILTRO_PARTIDO, "value"),
        Input(ids.FILTRO_ESPECTRO, "value"),
        Input(ids.SELECAO, "data"),
    )
    def _atualizar(uf, cargo, partido, espectro, selecao):
        return atualizar(uf, cargo, partido, espectro, selecao)
