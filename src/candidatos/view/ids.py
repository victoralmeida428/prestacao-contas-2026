"""Identificadores de componentes compartilhados entre layout e callbacks."""

from __future__ import annotations

FILTRO_UF = "f-uf"
FILTRO_CARGO = "f-cargo"
FILTRO_PARTIDO = "f-partido"
FILTRO_ESPECTRO = "f-espectro"

KPIS = "kpis"

SELECAO = "sel-cruzada"
SELECOES_INFO = "sel-info"
BOTAO_LIMPAR = "sel-limpar"

# A ordem define a ordem dos Outputs no callback.
GRAFICOS = [
    "g-receita-uf",
    "g-receita-partido",
    "g-espectro",
    "g-desp-espectro",
    "g-fonte",
    "g-natureza",
    "g-desp-cat",
    "g-contratado-pago",
    "g-fornecedores",
    "g-genero",
    "g-cor",
    "g-concentracao",
    "g-receita-box-genero",
    "g-receita-box-cor",
]

# Filtro cruzado: dimensao (coluna, rotulo) controlada por cada grafico ao clicar
# numa barra. Graficos ausentes daqui (ex.: concentracao) nao participam.
DIMENSOES = {
    "g-receita-uf": ("SG_UF", "UF"),
    "g-receita-partido": ("SG_PARTIDO", "Partido"),
    "g-espectro": ("ESPECTRO", "Espectro"),
    "g-desp-espectro": ("ESPECTRO", "Espectro"),
    "g-fonte": ("DS_FONTE_RECEITA", "Fonte"),
    "g-natureza": ("DS_NATUREZA_RECEITA", "Natureza"),
    "g-desp-cat": ("DS_ORIGEM_DESPESA", "Categoria"),
    "g-contratado-pago": ("SG_UF", "UF"),
    "g-fornecedores": ("NM_FORNECEDOR", "Fornecedor"),
    "g-genero": ("DS_GENERO", "Genero"),
    "g-cor": ("DS_COR_RACA", "Cor/raca"),
}

# coluna -> rotulo legivel (para os chips das selecoes ativas).
ROTULO_DIMENSAO = {col: rot for col, rot in DIMENSOES.values()}
