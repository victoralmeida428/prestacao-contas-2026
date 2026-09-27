"""Componentes de UI reutilizaveis (sem logica de dados)."""

from __future__ import annotations

from dash import dcc, html


def card(titulo: str, valor: str, sub: str, cor: str) -> html.Div:
    return html.Div(
        [
            html.Div(titulo, className="kpi-label"),
            html.Div(valor, className="kpi-value"),
            html.Div(sub, className="kpi-sub"),
        ],
        className="kpi",
        style={"borderLeftColor": cor},
    )


def campo(label: str, componente) -> html.Div:
    return html.Div([html.Label(label), componente], className="field")


def dropdown(id_: str, opcoes: list[dict]) -> dcc.Dropdown:
    return dcc.Dropdown(id=id_, options=opcoes, value="TODOS", clearable=False, className="dropdown")


def painel(id_: str) -> html.Div:
    return html.Div(
        dcc.Graph(id=id_, config={"displayModeBar": False}),
        className="panel",
    )
