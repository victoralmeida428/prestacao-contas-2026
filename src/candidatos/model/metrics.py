"""Agregacoes do dashboard (camada de modelo).

Cada funcao recebe os filtros, aplica sobre os dados uma unica vez e devolve
resultados pequenos (totais e tabelas agregadas), que sao cacheados. Dessa
forma evitamos manter copias gigantes de linhas filtradas em memoria.
"""

from __future__ import annotations

from functools import lru_cache

import polars as pl

from . import repository
from .espectro import ORDEM_ESPECTRO
from .schema import EXCL_CONTRATADAS, EXCL_PAGAS

TODOS = repository.TODOS


def _por_espectro(df: pl.DataFrame, valor: str) -> pl.DataFrame:
    return (
        df.group_by("ESPECTRO")
        .agg(pl.col(valor).sum().alias("valor"))
        .with_columns(pl.col("ESPECTRO").replace_strict(ORDEM_ESPECTRO, default=9).alias("ord"))
        .sort("ord")
        .drop("ord")
    )


@lru_cache(maxsize=512)
def resumo_receitas(uf: str, cargo: str, partido: str, espectro: str, extras: tuple = ()) -> dict:
    rec = repository.filtrar(
        repository.carregar()["receitas"], uf, cargo, partido, espectro, dict(extras)
    )
    valor = "VR_RECEITA"
    return {
        "total": rec[valor].sum(),
        "n_lancamentos": rec.height,
        "n_candidatos": rec["SQ_CANDIDATO"].n_unique() if rec.height else 0,
        "n_doadores": rec["NR_CPF_CNPJ_DOADOR"].n_unique() if rec.height else 0,
        "por_uf": rec.group_by("SG_UF").agg(pl.col(valor).sum().alias("valor")).sort("valor", descending=True),
        "por_partido": rec.group_by("SG_PARTIDO").agg(pl.col(valor).sum().alias("valor")).sort("valor", descending=True),
        "por_espectro": _por_espectro(rec, valor),
        "por_fonte": rec.group_by("DS_FONTE_RECEITA").agg(pl.col(valor).sum().alias("valor")).sort("valor", descending=True),
        "por_natureza": rec.group_by("DS_NATUREZA_RECEITA").agg(pl.col(valor).sum().alias("valor")).sort("valor", descending=True),
        "por_genero": rec.group_by("DS_GENERO").agg(pl.col(valor).sum().alias("valor")).sort("valor", descending=True),
        "por_cor": rec.group_by("DS_COR_RACA").agg(pl.col(valor).sum().alias("valor")).sort("valor", descending=True),
        "por_candidato": rec.group_by("SQ_CANDIDATO").agg(pl.col(valor).sum().alias("valor")).sort("valor", descending=True),
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
        "total": con[valor].sum(),
        "total_elegivel": elegivel[valor].sum(),
        "n_lancamentos": con.height,
        "n_candidatos": con["SQ_CANDIDATO"].n_unique() if con.height else 0,
        "por_uf": con.group_by("SG_UF").agg(pl.col(valor).sum().alias("valor")).sort("valor", descending=True),
        "por_espectro": _por_espectro(con, valor),
        "por_origem": (
            con.group_by("DS_ORIGEM_DESPESA")
            .agg(pl.col(valor).sum().alias("valor"))
            .sort("valor", descending=True)
            .head(12)
        ),
        "por_documento": con.group_by("DS_TIPO_DOCUMENTO").agg(pl.col(valor).sum().alias("valor")).sort("valor", descending=True),
        "por_fornecedor": (
            con.drop_nulls("NR_CPF_CNPJ_FORNECEDOR")
            .group_by(["NR_CPF_CNPJ_FORNECEDOR", fn])
            .agg(pl.col(valor).sum().alias("valor"))
            .sort("valor", descending=True)
            .head(15)
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
        "total": pag[valor].sum(),
        "total_elegivel": elegivel[valor].sum(),
        "n_lancamentos": pag.height,
        "por_uf": pag.group_by("SG_UF").agg(pl.col(valor).sum().alias("valor")).sort("valor", descending=True),
        "por_origem": pag.group_by("DS_ORIGEM_DESPESA").agg(pl.col(valor).sum().alias("valor")).sort("valor", descending=True),
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
