"""Configuracao central: caminhos, parametros e paleta."""

from __future__ import annotations

import os
from pathlib import Path

# Repo root: <repo>/src/candidatos/config.py -> parents[2] == <repo>
REPO_ROOT = Path(__file__).resolve().parents[2]

# Diretorios com override por variavel de ambiente (util em container).
RAW_DIR = Path(
    os.environ.get(
        "CANDIDATOS_RAW_DIR",
        REPO_ROOT / "data" / "prestacao_de_contas_eleitorais_candidatos_2026",
    )
)
DASH_DIR = Path(
    os.environ.get("CANDIDATOS_DASH_DIR", REPO_ROOT / "data" / "dashboard")
)
ASSETS_DIR = Path(__file__).resolve().parent / "assets"

ANO_ELEICAO = 2026
UF_CONSOLIDADO = "BRASIL"

# Paleta
AZUL = "#1f6feb"
VERDE = "#2ea043"
VERMELHO = "#d1242f"
LARANJA = "#e08c2a"
ROXO = "#8250df"
CINZA = "#6e7781"

# Servidor
HOST = "0.0.0.0"
PORT = 8050
