"""Agregacoes do dashboard (camada de modelo).

Cada funcao recebe os filtros, monta um plano *lazy* sobre o parquet e so
materializa os resultados agregados (pequenos), que sao cacheados. Assim a
memoria fica baixa: nunca mantemos uma copia inteira das linhas filtradas.
"""

from __future__ import annotations

from functools import lru_cache

import polars as pl

from . import repository
from .espectro import ORDEM_ESPECTRO
from .schema import EXCL_CONTRATADAS, EXCL_PAGAS

TODOS = repository.TODOS


def _grupo(lf: pl.LazyFrame, coluna: str, valor: str) -> pl.DataFrame:
    return (
        lf.group_by(coluna)
        .agg(pl.col(valor).sum().alias("valor"))
        .sort("valor", descending=True)
        .collect()
    )


def _por_espectro(lf: pl.LazyFrame, valor: str) -> pl.DataFrame:
    return (
        lf.group_by("ESPECTRO")
        .agg(pl.col(valor).sum().alias("valor"))
        .with_columns(pl.col("ESPECTRO").replace_strict(ORDEM_ESPECTRO, default=9).alias("ord"))
        .sort("ord")
        .drop("ord")
        .collect()
    )


def _totais(lf: pl.LazyFrame, valor: str, n_candidatos: bool = False, n_doadores: bool = False) -> dict:
    exprs = [pl.col(valor).sum().alias("total"), pl.len().alias("n_lancamentos")]
    if n_candidatos:
        exprs.append(pl.col("SQ_CANDIDATO").n_unique().alias("n_candidatos"))
    if n_doadores:
        exprs.append(pl.col("NR_CPF_CNPJ_DOADOR").n_unique().alias("n_doadores"))
    return lf.select(exprs).collect().row(0, named=True)


@lru_cache(maxsize=512)
def resumo_receitas(uf: str, cargo: str, partido: str, espectro: str, extras: tuple = ()) -> dict:
    rec = repository.filtrar(
        repository.carregar()["receitas"], uf, cargo, partido, espectro, dict(extras)
    )
    valor = "VR_RECEITA"
    base = _totais(rec, valor, n_candidatos=True, n_doadores=True)
    return {
        **base,
        "por_uf": _grupo(rec, "SG_UF", valor),
        "por_partido": _grupo(rec, "SG_PARTIDO", valor),
        "por_espectro": _por_espectro(rec, valor),
        "por_fonte": _grupo(rec, "DS_FONTE_RECEITA", valor),
        "por_natureza": _grupo(rec, "DS_NATUREZA_RECEITA", valor),
        "por_genero": _grupo(rec, "DS_GENERO", valor),
        "por_cor": _grupo(rec, "DS_COR_RACA", valor),
        "por_candidato": _grupo(rec, "SQ_CANDIDATO", valor),
    }


@lru_cache(maxsize=512)
def resumo_despesas(uf: str, cargo: str, partido: str, espectro: str, extras: tuple = ()) -> dict:
    con = repository.filtrar(
        repository.carregar()["despesas_contratadas"], uf, cargo, partido, espectro, dict(extras)
    )
    valor = "VR_DESPESA_CONTRATADA"
    elegivel = con.filter(~pl.col("CD_ORIGEM_DESPESA").is_in(EXCL_CONTRATADAS))
    fn = "NM_FORNECEDOR"
    return {
        **_totais(con, valor, n_candidatos=True),
        "total_elegivel": elegivel.select(pl.col(valor).sum()).collect().item(),
        "por_uf": _grupo(con, "SG_UF", valor),
        "por_espectro": _por_espectro(con, valor),
        "por_origem": (
            con.group_by("DS_ORIGEM_DESPESA")
            .agg(pl.col(valor).sum().alias("valor"))
            .sort("valor", descending=True)
            .head(12)
            .collect()
        ),
        "por_documento": _grupo(con, "DS_TIPO_DOCUMENTO", valor),
        "por_fornecedor": (
            con.drop_nulls("NR_CPF_CNPJ_FORNECEDOR")
            .group_by("NR_CPF_CNPJ_FORNECEDOR")
            .agg(
                pl.col(valor).sum().alias("valor"),
                pl.col(fn).first().alias(fn),
            )
            .sort("valor", descending=True)
            .head(15)
            .collect()
        ),
    }


@lru_cache(maxsize=512)
def resumo_pagas(uf: str, extras: tuple = ()) -> dict:
    pag = repository.filtrar(
        repository.carregar()["despesas_pagas"], uf=uf, extras=dict(extras)
    )
    valor = "VR_PAGTO_DESPESA"
    elegivel = pag.filter(~pl.col("CD_ORIGEM_DESPESA").is_in(EXCL_PAGAS))
    return {
        "total": pag.select(pl.col(valor).sum()).collect().item(),
        "total_elegivel": elegivel.select(pl.col(valor).sum()).collect().item(),
        **_totais(pag, valor),
        "por_uf": _grupo(pag, "SG_UF", valor),
        "por_origem": _grupo(pag, "DS_ORIGEM_DESPESA", valor),
    }


def indicadores(rec: dict, desp: dict, pag: dict) -> dict:
    """KPIs consolidados para os cards."""
    return {
        "receita": rec["total"],
        "n_lancamentos_receita": rec["n_lancamentos"],
        "contratado": desp["total"],
        "n_lancamentos_despesa": desp["n_lancamentos"],
        "pago": pag["total"],
        "n_lancamentos_pago": pag["n_lancamentos"],
        "divida": desp["total_elegivel"] - pag["total_elegivel"],
        "candidatos": rec["n_candidatos"],
    }
