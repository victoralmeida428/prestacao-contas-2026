"""Fabrica da aplicacao Dash e exposicao do WSGI para producao."""

from __future__ import annotations

from dash import Dash

from . import config
from .controller.callbacks import register_callbacks
from .model import repository
from .view.layout import build_layout


def create_app() -> Dash:
    """Cria o app Dash (carrega os dados e registra layout/callbacks)."""
    repository.carregar()  # aquece o cache e valida o parquet

    dash_app = Dash(
        __name__,
        title="Prestacao de contas 2026",
        assets_folder=str(config.ASSETS_DIR),
        meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    )
    dash_app.layout = build_layout()
    register_callbacks(dash_app)
    return dash_app


app = create_app()

# Alvo do gunicorn em producao: ``candidatos.app:server``
server = app.server
