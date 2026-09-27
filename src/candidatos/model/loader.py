"""Leitura e limpeza dos CSV brutos do TSE com Polars (usado no build).

Nota: o ``scan_csv`` (lazy) do Polars nao aceita ``encoding="latin1"``; por
isso a leitura e eager. Como o Polars e colunar, ``despesas_contratadas``
(479 MB em disco) ocupa poucas centenas de MB em memoria.
"""

from __future__ import annotations

from pathlib import Path

import polars as pl

from .. import config
from .schema import (
    COLUNAS_CATEGORICAS,
    COLUNAS_DATA,
    COLUNAS_VALOR,
    PREFIXOS,
    SENTINELAS,
)


def _valor_expr(coluna: str) -> pl.Expr:
    """'1.234,56' -> 1234.56; NA permanece NA."""
    return (
        pl.col(coluna)
        .str.replace_all(r"\.", "")
        .str.replace(",", ".")
        .cast(pl.Float64, strict=False)
        .alias(coluna)
    )


def load_tse(
    tabela: str,
    uf: str = config.UF_CONSOLIDADO,
    ano: int = config.ANO_ELEICAO,
    colunas: list[str] | None = None,
    categoria: bool = True,
    base_dir: Path | str = config.RAW_DIR,
) -> pl.DataFrame:
    """Carrega e limpa uma tabela de prestacao de contas a partir do CSV."""
    if tabela not in PREFIXOS:
        raise KeyError(f"tabela invalida: {tabela!r}. Use uma de {list(PREFIXOS)}")

    caminho = Path(base_dir) / f"{PREFIXOS[tabela]}_{ano}_{uf}.csv"
    if not caminho.exists():
        raise FileNotFoundError(caminho)

    df = pl.read_csv(
        caminho,
        separator=";",
        encoding="latin1",
        infer_schema_length=0,
        null_values=SENTINELAS,
        quote_char='"',
        columns=colunas,
    )

    exprs: list[pl.Expr] = []
    for col in df.columns:
        if col in COLUNAS_VALOR:
            exprs.append(_valor_expr(col))
        elif col in COLUNAS_DATA:
            exprs.append(
                pl.col(col).str.strptime(pl.Date, "%d/%m/%Y", strict=False).alias(col)
            )
    if exprs:
        df = df.with_columns(exprs)

    if categoria:
        cats = [c for c in df.columns if c in COLUNAS_CATEGORICAS]
        if cats:
            df = df.with_columns([pl.col(c).cast(pl.Categorical) for c in cats])

    return df


def load_all(
    uf: str = config.UF_CONSOLIDADO,
    ano: int = config.ANO_ELEICAO,
    colunas_por_tabela: dict[str, list[str]] | None = None,
    base_dir: Path | str = config.RAW_DIR,
) -> dict[str, pl.DataFrame]:
    """Carrega as quatro tabelas e devolve um dict nomeado."""
    colunas_por_tabela = colunas_por_tabela or {}
    return {
        nome: load_tse(
            nome,
            uf=uf,
            ano=ano,
            colunas=colunas_por_tabela.get(nome),
            base_dir=base_dir,
        )
        for nome in PREFIXOS
    }


def relatorio_nulos(df: pl.DataFrame) -> pl.DataFrame:
    """Resumo de nulos por coluna, ordenado do maior para o menor."""
    n = df.height
    return (
        pl.DataFrame(
            {
                "coluna": df.columns,
                "nulos": [df[c].null_count() for c in df.columns],
                "tipo": [str(df.schema[c]) for c in df.columns],
                "unicos": [df[c].n_unique() for c in df.columns],
            }
        )
        .with_columns((pl.col("nulos") / n * 100).round(2).alias("pct"))
        .sort("nulos", descending=True)
    )
