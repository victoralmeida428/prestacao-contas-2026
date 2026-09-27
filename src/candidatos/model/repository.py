"""Acesso aos dados do dashboard: le o parquet e filtra por dimensao.

As tabelas sao abertas de forma *lazy* (``scan_parquet``): o dashboard agrega
antes de materializar, entao a memoria fica baixa mesmo com os CSV do TSE
grandes. O filtro devolve um ``LazyFrame`` e as agregacoes fazem ``collect``.
"""

from __future__ import annotations

from functools import lru_cache

import polars as pl

from .. import config
from .espectro import com_espectro
from .schema import COLUNAS_DASHBOARD

TABELAS = tuple(COLUNAS_DASHBOARD)

TODOS = "TODOS"


@lru_cache(maxsize=1)
def carregar() -> dict[str, pl.LazyFrame]:
    """Abre (uma unica vez) as tabelas do parquet enxuto em modo lazy."""
    frames: dict[str, pl.LazyFrame] = {}
    for nome in TABELAS:
        caminho = config.DASH_DIR / f"{nome}.parquet"
        if not caminho.exists():
            raise FileNotFoundError(
                f"{caminho} nao encontrado. Rode: python -m candidatos.build"
            )
        frames[nome] = pl.scan_parquet(caminho)

    for nome in ("receitas", "despesas_contratadas"):
        frames[nome] = com_espectro(frames[nome])
    return frames


def filtrar(
    df: pl.LazyFrame,
    uf: str = TODOS,
    cargo: str = TODOS,
    partido: str = TODOS,
    espectro: str = TODOS,
    extras: dict[str, str] | None = None,
) -> pl.LazyFrame:
    """Aplica os filtros disponiveis; ignora dimensoes ausentes na tabela.

    ``extras`` sao as dimensoes do filtro cruzado (clique nas barras), no formato
    ``{coluna: valor}``.
    """
    cond = pl.lit(True)
    cols = df.collect_schema().names()
    if uf != TODOS and "SG_UF" in cols:
        cond = cond & (pl.col("SG_UF") == uf)
    if cargo != TODOS and "DS_CARGO" in cols:
        cond = cond & (pl.col("DS_CARGO") == cargo)
    if partido != TODOS and "SG_PARTIDO" in cols:
        cond = cond & (pl.col("SG_PARTIDO") == partido)
    if espectro != TODOS and "ESPECTRO" in cols:
        cond = cond & (pl.col("ESPECTRO") == espectro)
    for coluna, valor in (extras or {}).items():
        if coluna in cols:
            cond = cond & (pl.col(coluna) == valor)
    return df.filter(cond)


@lru_cache(maxsize=1)
def opcoes_filtro() -> dict[str, list[dict]]:
    """Opcoes dos dropdowns derivadas dos proprios dados."""
    rec = carregar()["receitas"]

    def opcoes(coluna: str, rotulo: str) -> list[dict]:
        valores = sorted(
            rec.select(coluna).drop_nulls().unique().collect().to_series().to_list()
        )
        return [{"label": rotulo, "value": TODOS}] + [
            {"label": v, "value": v} for v in valores
        ]

    return {
        "uf": opcoes("SG_UF", "Todas as UFs"),
        "cargo": opcoes("DS_CARGO", "Todos os cargos"),
        "partido": opcoes("SG_PARTIDO", "Todos os partidos"),
    }
