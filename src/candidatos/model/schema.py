"""Constantes do repositorio de dados eleitorais do TSE.

Os CSV do TSE sao Latin-1, separados por ``;``, com tudo entre aspas,
decimal com virgula e documentos sentinela (``#NULO``/``-1``, ``#NE``/``-3``
e ``-4`` para dados nao divulgaiveis).
"""

from __future__ import annotations

PREFIXOS = {
    "receitas": "receitas_candidatos",
    "receitas_doador_originario": "receitas_candidatos_doador_originario",
    "despesas_contratadas": "despesas_contratadas_candidatos",
    "despesas_pagas": "despesas_pagas_candidatos",
}

SENTINELAS = ["#NULO", "#NULO#", "#NE", "-1", "-3", "-4", ""]

COLUNAS_VALOR = ("VR_RECEITA", "VR_DESPESA_CONTRATADA", "VR_PAGTO_DESPESA")

COLUNAS_DATA = (
    "DT_GERACAO",
    "DT_ELEICAO",
    "DT_PRESTACAO_CONTAS",
    "DT_RECEITA",
    "DT_DESPESA",
    "DT_PAGTO_DESPESA",
)

COLUNAS_CATEGORICAS = (
    "NM_TIPO_ELEICAO",
    "DS_ELEICAO",
    "TP_PRESTACAO_CONTAS",
    "SG_UF",
    "SG_UE",
    "NM_UE",
    "DS_CARGO",
    "DS_CARGO_FORNECEDOR",
    "DS_CARGO_CANDIDATO_DOADOR",
    "NM_PARTIDO",
    "NM_PARTIDO_DOADOR",
    "NM_PARTIDO_FORNECEDOR",
    "DS_FONTE_RECEITA",
    "DS_ORIGEM_RECEITA",
    "DS_NATUREZA_RECEITA",
    "DS_ESPECIE_RECEITA",
    "DS_NATUREZA_RECURSO_ESTIMAVEL",
    "DS_FONTE_DESPESA",
    "DS_ORIGEM_DESPESA",
    "DS_NATUREZA_DESPESA",
    "DS_ESPECIE_RECURSO",
    "DS_TIPO_FORNECEDOR",
    "DS_CNAE_FORNECEDOR",
    "DS_TIPO_DOCUMENTO",
    "DS_ESFERA_PARTIDARIA_DOADOR",
    "DS_ESFERA_PART_FORNECEDOR",
    "DS_GENERO",
    "DS_COR_RACA",
    "NM_MUNICIPIO_DOADOR",
    "NM_MUNICIPIO_FORNECEDOR",
)

UFS = [
    "AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS",
    "MT", "PA", "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC",
    "SE", "SP", "TO",
]

# Contas DRD excluidas do calculo de divida de campanha (ver leiame).
EXCL_CONTRATADAS = [
    "20320000", "30020000", "20330000", "20340000", "20370000", "20380000", "20390000",
]
EXCL_PAGAS = ["20330000", "20340000", "20370000", "20380000", "20390000"]

# Colunas necessarias ao dashboard (usadas para gerar o parquet enxuto).
COLUNAS_DASHBOARD = {
    "receitas": [
        "SG_UF", "DS_CARGO", "SG_PARTIDO",
        "DS_FONTE_RECEITA", "DS_NATUREZA_RECEITA", "DS_GENERO", "DS_COR_RACA",
        "DS_ORIGEM_RECEITA", "VR_RECEITA", "SQ_CANDIDATO",
        "NR_CPF_CNPJ_DOADOR", "NM_DOADOR",
    ],
    "despesas_contratadas": [
        "SG_UF", "DS_CARGO", "SG_PARTIDO",
        "DS_ORIGEM_DESPESA", "DS_TIPO_DOCUMENTO",
        "NR_CPF_CNPJ_FORNECEDOR", "NM_FORNECEDOR",
        "VR_DESPESA_CONTRATADA", "SQ_CANDIDATO",
        "CD_ORIGEM_DESPESA",
    ],
    "despesas_pagas": [
        "SG_UF", "DS_ORIGEM_DESPESA", "VR_PAGTO_DESPESA", "CD_ORIGEM_DESPESA",
    ],
}
