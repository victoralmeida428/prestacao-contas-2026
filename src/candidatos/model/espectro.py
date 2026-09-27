"""Classificacao dos partidos no espectro politico.

Classificacao CONVENCIONAL e aproximada, feita por PARTIDO (vale para todos os
cargos, inclusive os presidenciais). Partidos de alianca ampla (MDB, PSD, UNIAO)
sao sensiveis ao criterio - ajuste o dicionario abaixo conforme a metodologia.
"""

from __future__ import annotations

import polars as pl

ESPECTRO = {
    # Esquerda
    "PSTU": "Esquerda",
    "UP": "Esquerda",
    "PCB": "Esquerda",
    "PCO": "Esquerda",
    "PSOL": "Esquerda",
    "PCDOB": "Esquerda",
    "PV": "Esquerda",
    "REDE": "Esquerda",
    # Centro-esquerda
    "PT": "Centro-esquerda",
    "PDT": "Centro-esquerda",
    "PSB": "Centro-esquerda",
    # Centro
    "MDB": "Centro",
    "PODE": "Centro",
    "PSDB": "Centro",
    "PRD": "Centro",
    "SOLIDARIEDADE": "Centro",
    "CIDADANIA": "Centro",
    "AGIR": "Centro",
    # Centro-direita
    "UNIÃO": "Centro-direita",
    "PSD": "Centro-direita",
    "AVANTE": "Centro-direita",
    "MOBILIZA": "Centro-direita",
    # Direita
    "PL": "Direita",
    "REPUBLICANOS": "Direita",
    "PP": "Direita",
    "NOVO": "Direita",
    "MISSÃO": "Direita",
    "DC": "Direita",
    "DEMOCRATA": "Direita",
    "PRTB": "Direita",
}

ORDEM_ESPECTRO = {
    "Esquerda radical": 0,
    "Esquerda": 1,
    "Centro-esquerda": 2,
    "Centro": 3,
    "Centro-direita": 4,
    "Direita": 5,
    "Não classificado": 6,
}

CORES_ESPECTRO = {
    "Esquerda radical": "#9b1c1c",
    "Esquerda": "#d64545",
    "Centro-esquerda": "#e8a3a3",
    "Centro": "#9aa4b2",
    "Centro-direita": "#8fb4e0",
    "Direita": "#1f6feb",
    "Não classificado": "#6e7781",
}

NAO_CLASSIFICADO = "Não classificado"


def com_espectro(df: pl.DataFrame) -> pl.DataFrame:
    """Adiciona a coluna ``ESPECTRO`` a partir de ``SG_PARTIDO``."""
    return df.with_columns(
        pl.col("SG_PARTIDO")
        .cast(pl.String)
        .replace_strict(ESPECTRO, default=NAO_CLASSIFICADO)
        .alias("ESPECTRO")
    )


def opcoes_espectro() -> list[dict]:
    return [{"label": "Todo o espectro", "value": "TODOS"}] + [
        {"label": e, "value": e} for e in ORDEM_ESPECTRO
    ]
