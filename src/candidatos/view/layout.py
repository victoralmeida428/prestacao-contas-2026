"""Layout da pagina (composicao de componentes e graficos)."""

from __future__ import annotations

from dash import dcc, html

from ..model import repository
from ..model.espectro import opcoes_espectro
from . import ids
from .components import campo, dropdown, painel


def build_layout() -> html.Div:
    opcoes = repository.opcoes_filtro()
    return html.Div(
        [
            html.Div(
                [
                    html.H1("Prestacao de contas eleitorais - Eleicoes 2026"),
                    html.P(
                        "Fonte: TSE - snapshot de 27/09/2026, com apenas prestacoes Parcial e "
                        "Relatorio Financeiro (sem entrega Final). Todos os totais sao preliminares."
                    ),
                ],
                className="header",
            ),
            html.Div(
                [
                    campo("UF", dropdown(ids.FILTRO_UF, opcoes["uf"])),
                    campo("Cargo", dropdown(ids.FILTRO_CARGO, opcoes["cargo"])),
                    campo("Partido", dropdown(ids.FILTRO_PARTIDO, opcoes["partido"])),
                    campo("Espectro", dropdown(ids.FILTRO_ESPECTRO, opcoes_espectro())),
                ],
                className="toolbar",
            ),
            dcc.Store(id=ids.SELECAO, data={}),
            html.Div(
                [
                    html.Div(id=ids.SELECOES_INFO, className="chips"),
                    html.Button(
                        "Limpar selecoes",
                        id=ids.BOTAO_LIMPAR,
                        n_clicks=0,
                        className="limpar",
                    ),
                ],
                className="selecoes",
            ),
            html.Div(id=ids.KPIS, className="kpis"),
            html.Div([painel(g) for g in ids.GRAFICOS], className="grid"),
            html.Div(
                [
                    html.Div(
                        [
                            html.B("Espectro politico: "),
                            "classificacao por PARTIDO em 6 faixas ordenadas (Esquerda radical, "
                            "Esquerda, Centro-esquerda, Centro, Centro-direita, Direita). E "
                            "convencional e aproximada; partidos de alianca ampla (MDB, PSD, "
                            "UNIAO) sao sensiveis ao criterio e a mesma chave vale para os 13 "
                            "presidenciais.",
                        ]
                    ),
                    html.Div(
                        [
                            html.B("Filtros: "),
                            "O filtro de "
                            "espectro nao se aplica aos KPIs de pago e divida "
                            "(somente UF).",
                        ]
                    ),
                ],
                className="nota",
            ),
        ],
        className="app",
    )
