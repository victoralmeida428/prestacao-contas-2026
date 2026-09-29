"""Construcao das figuras Plotly a partir de agregacoes (model/metrics).

Nao ha graficos de pizza neste dashboard: composicoes sao mostradas em barras.
"""

from __future__ import annotations

import json
import math
from functools import lru_cache

import plotly.graph_objects as go
import polars as pl

from .. import config
from ..model.espectro import CORES_ESPECTRO, ORDEM_ESPECTRO
from ..model.schema import UFS


def _layout(fig: go.Figure, titulo: str, altura: int = 360, legenda: bool = False) -> go.Figure:
    fig.update_layout(
        title=dict(text=titulo, font=dict(size=15, color="#1f2733"), x=0.02),
        template="plotly_white",
        margin=dict(l=58, r=18, t=54, b=48),
        height=altura,
        showlegend=legenda,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        font=dict(color="#364152"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        clickmode="event",
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#eef1f5")
    return fig


def _vazio(titulo: str, altura: int = 360) -> go.Figure:
    return _layout(go.Figure(), titulo, altura)


def _cd(valores) -> list:
    """customdata por ponto (valor cru da dimensao) para o filtro cruzado."""
    return [[v] for v in valores]


def _rgb(cor: str) -> tuple[int, int, int]:
    h = cor.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _clarear(cor: str, alpha: float = 0.28) -> str:
    r, g, b = _rgb(cor)
    return f"rgba({r},{g},{b},{alpha})"


def _cores(labels, cor: str, destaque: str | None):
    """Destaque: a barra selecionada fica na cor cheia; as demais, claras."""
    if destaque is None:
        return cor
    return [cor if str(lbl) == str(destaque) else _clarear(cor) for lbl in labels]


def _cores_de(cores: list, labels, destaque: str | None):
    if destaque is None:
        return cores
    return [c if str(lbl) == str(destaque) else _clarear(c) for c, lbl in zip(cores, labels)]


def _rotulo_br(v: float) -> str:
    """Rotulo de eixo em pt-BR: k (mil), M (milhao) e B (bilhao)."""
    for div, suf in ((1e9, "B"), (1e6, "M"), (1e3, "k")):
        if abs(v) >= div:
            n = v / div
            texto = f"{n:.0f}" if n == int(n) else f"{n:.1f}".replace(".", ",")
            return texto + suf
    return f"{v:.0f}"


def _ticks(vmin: float, vmax: float, n: int = 6) -> tuple[list, list]:
    """Ticks "redondos" (passo 1/2/2,5/5 x 10^k) com rotulos pt-BR."""
    if vmax <= vmin:
        return [vmin, vmax], [_rotulo_br(vmin), _rotulo_br(vmax)]
    bruto = (vmax - vmin) / n
    mag = 10 ** math.floor(math.log10(bruto))
    passo = next(m * mag for m in (1, 2, 2.5, 5, 10) if bruto <= m * mag)
    inicio = math.floor(vmin / passo) * passo
    fim = math.ceil(vmax / passo) * passo
    vals: list[float] = []
    v = inicio
    while v <= fim + passo / 2:
        vals.append(round(v, 6))
        v += passo
    return vals, [_rotulo_br(v) for v in vals]


def _eixo_valor(fig: go.Figure, valores, eixo: str = "y") -> go.Figure:
    """Substitui o SI do Plotly (k/M/G) por k/M/B no eixo de valores."""
    limpos = [float(v) for v in valores if v is not None]
    if not limpos:
        return fig
    vals, txt = _ticks(0.0, max(limpos))
    (fig.update_xaxes if eixo == "x" else fig.update_yaxes)(tickvals=vals, ticktext=txt)
    return fig


def barra_h(labels, valores, titulo, cor=config.AZUL, altura=360, customdata=None) -> go.Figure:
    fig = go.Figure(go.Bar(x=valores, y=labels, orientation="h", marker_color=cor, customdata=customdata))
    return _layout(_eixo_valor(fig, valores, "x"), titulo, altura)


def _xy(df: pl.DataFrame, x: str) -> tuple[list, list]:
    return df[x].to_list(), df["valor"].to_list()


# Escala sequencial de verde: quanto mais escuro, maior a receita.
VERDES_RECEITA = [
    [0.0, "#eaf6ec"],
    [0.25, "#a8dab5"],
    [0.5, "#5cb85c"],
    [0.75, "#2ea043"],
    [1.0, "#0b4f1c"],
]

CORES_GENERO = {"Masculino": config.AZUL, "Feminino": config.ROXO}
CORES_COR = {
    "Branca": config.AZUL,
    "Parda": config.LARANJA,
    "Preta": config.ROXO,
    "Amarela": "#b08900",
    "Indígena": config.VERDE,
}


@lru_cache(maxsize=1)
def _geojson_br() -> dict:
    return json.loads(config.BRAZIL_GEOJSON.read_text(encoding="utf-8"))


def fig_receita_uf_mapa(rec: dict, destaque: str | None = None) -> go.Figure:
    d = rec["por_uf"].filter(pl.col("SG_UF").is_in(UFS))
    ufs = d["SG_UF"].to_list()
    valores = d["valor"].to_list()
    fig = go.Figure(
        go.Choropleth(
            geojson=_geojson_br(),
            locations=ufs,
            z=valores,
            locationmode="geojson-id",
            featureidkey="properties.sigla",
            colorscale=VERDES_RECEITA,
            marker=dict(line=dict(color="#ffffff", width=0.7)),
            colorbar=dict(title="Receita", thickness=12, len=0.72),
            customdata=_cd(ufs),
            hovertemplate="<b>%{location}</b><br>Receita: R$ %{z:,.0f}<extra></extra>",
        )
    )
    if destaque in ufs:
        fig.add_trace(
            go.Choropleth(
                geojson=_geojson_br(),
                locations=[destaque],
                z=[0],
                zmin=0,
                zmax=1,
                locationmode="geojson-id",
                featureidkey="properties.sigla",
                colorscale=[[0.0, "rgba(0,0,0,0)"], [1.0, "rgba(0,0,0,0)"]],
                marker=dict(line=dict(color="#0b1f3a", width=2.5)),
                showscale=False,
                hoverinfo="skip",
            )
        )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(
        title=dict(text="Receita declarada por UF", font=dict(size=15, color="#1f2733"), x=0.02),
        template="plotly_white",
        margin=dict(l=8, r=8, t=54, b=8),
        height=360,
        font=dict(color="#364152"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        clickmode="event",
    )
    return fig


def fig_receita_genero_box(rec: dict) -> go.Figure:
    """Boxplot da receita por candidato: espectro politico x genero."""
    return _boxplot_espectro(rec, "DS_GENERO", CORES_GENERO, "Receita por candidato - espectro x genero")


def fig_receita_cor_box(rec: dict) -> go.Figure:
    """Boxplot da receita por candidato: espectro politico x cor/raca."""
    return _boxplot_espectro(rec, "DS_COR_RACA", CORES_COR, "Receita por candidato - espectro x cor/raca")


def _boxplot_espectro(rec: dict, dim: str, cores: dict, titulo: str) -> go.Figure:
    d = rec["demografia_candidato"].drop_nulls(dim).filter(pl.col("ESPECTRO") != "Não classificado")
    fig = go.Figure()
    if d.height > 0:
        presentes = set(d.select(pl.col(dim).unique()).to_series().to_list())
        ordem = [c for c in cores if c in presentes]
        ordem += [c for c in presentes if c not in cores]
        for categoria in ordem:
            sub = d.filter(pl.col(dim) == categoria)
            cor = cores.get(str(categoria), config.CINZA)
            fig.add_trace(
                go.Box(
                    x=sub["ESPECTRO"].to_list(),
                    y=sub["valor"].to_list(),
                    name=str(categoria),
                    marker_color=cor,
                    fillcolor=_clarear(cor, 0.45),
                    line=dict(width=1.4),
                    boxpoints=False,
                    hovertemplate=f"<b>%{{x}}</b><br>{categoria}<br>Receita: R$ %{{y:,.0f}}<extra></extra>",
                )
            )
    espectros = [e for e, _ in sorted(ORDEM_ESPECTRO.items(), key=lambda kv: kv[1]) if e != "Não classificado"]
    fig.update_layout(
        title=dict(text=titulo, font=dict(size=15, color="#1f2733"), x=0.02),
        template="plotly_white",
        margin=dict(l=58, r=18, t=88, b=48),
        height=420,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        font=dict(color="#364152"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        boxmode="group",
    )
    fig.update_xaxes(showgrid=False, categoryorder="array", categoryarray=espectros)
    fig.update_yaxes(gridcolor="#eef1f5", type="log", title="Receita por candidato (R$, escala log)")
    return fig


def fig_receita_partido(rec: dict, destaque: str | None = None) -> go.Figure:
    d = rec["por_partido"].head(15).sort("valor")
    x, y = _xy(d, "SG_PARTIDO")
    return barra_h(x, y, "Top 15 partidos por receita", _cores(x, config.VERDE, destaque), customdata=_cd(x))


def fig_receita_espectro(rec: dict, destaque: str | None = None) -> go.Figure:
    d = rec["por_espectro"]
    eixos = d["ESPECTRO"].to_list()
    cores = [CORES_ESPECTRO.get(e, config.CINZA) for e in eixos]
    fig = go.Figure(go.Bar(x=eixos, y=d["valor"].to_list(), marker_color=_cores_de(cores, eixos, destaque), customdata=_cd(eixos)))
    return _layout(_eixo_valor(fig, d["valor"].to_list(), "y"), "Receita por espectro politico", 360)


def fig_despesa_espectro(desp: dict, destaque: str | None = None) -> go.Figure:
    d = desp["por_espectro"]
    eixos = d["ESPECTRO"].to_list()
    cores = [CORES_ESPECTRO.get(e, config.CINZA) for e in eixos]
    fig = go.Figure(go.Bar(x=eixos, y=d["valor"].to_list(), marker_color=_cores_de(cores, eixos, destaque), customdata=_cd(eixos)))
    return _layout(_eixo_valor(fig, d["valor"].to_list(), "y"), "Despesa contratada por espectro politico", 360)


def fig_fonte(rec: dict, destaque: str | None = None) -> go.Figure:
    d = rec["por_fonte"].sort("valor")
    x, y = _xy(d, "DS_FONTE_RECEITA")
    return barra_h(x, y, "Origem dos recursos (fonte)", _cores(x, config.LARANJA, destaque), customdata=_cd(x))


def fig_natureza(rec: dict, destaque: str | None = None) -> go.Figure:
    d = rec["por_natureza"].sort("valor")
    x, y = _xy(d, "DS_NATUREZA_RECEITA")
    return barra_h(x, y, "Natureza da receita (financeiro x estimavel)", _cores(x, config.AZUL, destaque), 300, customdata=_cd(x))


def fig_genero(rec: dict, destaque: str | None = None) -> go.Figure:
    d = rec["por_genero"].sort("valor")
    x, y = _xy(d, "DS_GENERO")
    return barra_h(x, y, "Candidatos por genero (autodeclarado)", _cores(x, config.ROXO, destaque), 300, customdata=_cd(x))


def fig_cor_raca(rec: dict, destaque: str | None = None) -> go.Figure:
    d = rec["por_cor"].sort("valor")
    x, y = _xy(d, "DS_COR_RACA")
    return barra_h(x, y, "Candidatos por cor/raca (autodeclarado)", _cores(x, config.ROXO, destaque), 320, customdata=_cd(x))


def fig_despesa_categoria(desp: dict, destaque: str | None = None) -> go.Figure:
    d = desp["por_origem"].sort("valor")
    x, y = _xy(d, "DS_ORIGEM_DESPESA")
    return barra_h(x, y, "Top 12 categorias de despesa contratada", _cores(x, config.LARANJA, destaque), 400, customdata=_cd(x))


def fig_contratado_pago(desp: dict, pag: dict, destaque: str | None = None) -> go.Figure:
    c = desp["por_uf"].rename({"valor": "contratado"})
    p = pag["por_uf"].rename({"valor": "pago"})
    d = c.join(p, on="SG_UF", how="full", coalesce=True).fill_null(0).sort("contratado", descending=True)
    ufs = d["SG_UF"].to_list()
    fig = go.Figure()
    fig.add_bar(x=ufs, y=d["contratado"].to_list(), name="Contratado", marker_color=_cores(ufs, config.AZUL, destaque), customdata=_cd(ufs))
    fig.add_bar(x=ufs, y=d["pago"].to_list(), name="Pago", marker_color=_cores(ufs, config.VERDE, destaque), customdata=_cd(ufs))
    fig.update_layout(barmode="group")
    return _layout(_eixo_valor(fig, d["contratado"].to_list() + d["pago"].to_list(), "y"), "Despesas por UF - contratado x pago", 360, legenda=True)


def fig_fornecedores(desp: dict, destaque: str | None = None) -> go.Figure:
    d = desp["por_fornecedor"].sort("valor")
    nomes = d["NM_FORNECEDOR"].to_list()
    labels = [n[:38] for n in nomes]
    return barra_h(labels, d["valor"].to_list(), "Top 15 fornecedores (despesa contratada)", _cores(nomes, config.VERMELHO, destaque), 400, customdata=_cd(nomes))


def fig_concentracao(rec: dict) -> go.Figure:
    d = rec["por_candidato"]
    n = d.height
    if n == 0:
        return _vazio("Concentracao da receita entre candidatos")
    cum = (d["valor"].cum_sum() / d["valor"].sum() * 100).to_list()
    eixo_x = [i / n * 100 for i in range(1, n + 1)]
    fig = go.Figure(
        go.Scatter(
            x=eixo_x, y=cum, mode="lines",
            line=dict(color=config.AZUL, width=3),
            fill="tozeroy", fillcolor="rgba(31,111,235,0.10)",
        )
    )
    fig.update_xaxes(title="% de candidatos (do maior para o menor)", showgrid=False)
    fig.update_yaxes(title="% acumulada da receita", gridcolor="#eef1f5")
    return _layout(fig, "Concentracao da receita entre candidatos")
