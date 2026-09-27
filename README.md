# Prestação de contas eleitorais 2026 (TSE)

Dashboard interativo e análise exploratória da **prestação de contas dos candidatos das Eleições Gerais 2026**, a partir dos dados abertos do TSE.

- **Candidatos:** Presidente, Governador, Senador, Deputado Federal, Estadual e Distrital.
- **Fonte:** repositório de dados eleitorais do TSE (`prestacao_de_contas_eleitorais_candidatos_2026`).
- **Snapshot:** 27/09/2026 (eleição em 04/10/2026) — contém apenas prestações **Parcial** e **Relatório Financeiro**. **Não há entrega Final**, logo todos os totais são *preliminares*.

## Stack

- [Polars](https://pola.rs) — leitura, limpeza e agregação (colunar, rápido e econômico em memória)
- [Dash](https://dash.plotly.com) + [Plotly](https://plotly.com/python/) — dashboard web
- [Gunicorn](https://gunicorn.org) — servidor WSGI em produção
- JupyterLab / matplotlib / pandas — notebook de EDA (grupo `dev`, fora da imagem de produção)

## Dados

| Tabela                  | Linhas      | Parquet enxuto |
|-------------------------|------------:|---------------:|
| `receitas`              | 136.240     | 2,2 MB         |
| `despesas_contratadas`  | 797.385     | 12,5 MB        |
| `despesas_pagas`        | 447.828     | 1,5 MB         |

Os CSV brutos (~1,6 GB) **não são versionados** (ver `.gitignore`). O dashboard consome apenas um parquet enxuto (~16 MB) em `data/dashboard/`, gerado por:

```bash
uv run python -m candidatos.build
```

O comando lê os CSV de `data/prestacao_de_contas_eleitorais_candidatos_2026/`, seleciona as colunas usadas nas visualizações e grava `data/dashboard/*.parquet` (compressão `zstd`).

Em runtime as tabelas são abertas de forma **lazy** (`pl.scan_parquet`) e as agregações só materializam o resultado final — o pico de memória fica em ~300 MB mesmo com os CSV de ~1,6 GB (por isso roda no plano free do Render, 512 MB). O Polars usa 1 thread por worker (`POLARS_MAX_THREADS=1`, definido em `config.py`).

## Estrutura (MVC em `src/`)

```
src/candidatos/
├── config.py                  # caminhos, paleta, porta
├── app.py                     # create_app() + server (WSGI)
├── __main__.py                # python -m candidatos
├── build.py                   # python -m candidatos.build
├── model/                     # MODEL
│   ├── schema.py              # sentinelas, colunas, contas DRD
│   ├── espectro.py            # partidos -> 6 faixas do espectro político
│   ├── loader.py              # leitura/limpeza dos CSV do TSE
│   ├── dataset.py             # gera o parquet enxuto
│   ├── repository.py          # carrega parquet, filtra, opções de filtro
│   └── metrics.py             # agregações e KPIs (cacheados)
├── view/                      # VIEW
│   ├── layout.py              # layout da página
│   ├── components.py          # cards, painéis, dropdowns
│   ├── charts.py              # figuras Plotly
│   ├── formatting.py          # formatação pt-BR
│   ├── ids.py                 # ids compartilhados
│   └── assets/style.css       # CSS (Dash carrega automaticamente)
└── controller/callbacks.py    # CONTROLLER (filtros -> dados -> figuras)
```

## Como rodar

Pré-requisito: [uv](https://docs.astral.sh/uv/) e Python ≥ 3.13.

```bash
uv sync                          # cria o ambiente e instala o pacote (editable)

# 1) gerar o parquet do dashboard a partir dos CSV brutos
uv run python -m candidatos.build

# 2) ambiente de desenvolvimento
uv run python -m candidatos      # http://127.0.0.1:8050

# 3) produção local (mesmo comando do container)
uv run gunicorn -w 1 --threads 4 -b 0.0.0.0:8000 candidatos.app:server
```

Variáveis de ambiente opcionais: `PORT`, `CANDIDATOS_RAW_DIR`, `CANDIDATOS_DASH_DIR`.

### Docker

```bash
docker build -t candidatos-dashboard .
docker run -p 8000:8000 candidatos-dashboard
```

A imagem (`python:3.13-slim`) instala apenas as dependências de runtime e copia `src/` e `data/dashboard/`; o servidor sobe via gunicorn na porta `$PORT` (padrão `8000`).

### Deploy no Render

O repositório inclui `render.yaml`. Basta criar um **Blueprint** no Render apontando para o repositório — ele usa Docker, faz o health check em `/` e injeta o `$PORT` automaticamente.

## Notebook de EDA

`eda_prestacao_contas_2026.ipynb` traz a análise exploratória completa (qualidade dos dados, receitas, despesas, dívida de campanha, doadores originários, recortes de gênero/cor e concentração). Ele usa o grupo `dev` (JupyterLab/matplotlib) e importa de `candidatos.model.loader`.

## Funcionalidades do dashboard

- **Filtros:** UF, Cargo, Partido e Espectro político.
- **Filtro cruzado:** clicar numa barra filtra os demais gráficos pela dimensão daquele gráfico (ex.: clicar em `SP` filtra os outros por UF; clicar em `PL` filtra por partido). Seleções de gráficos diferentes se acumulam, o gráfico clicado não se filtra pela própria dimensão, clicar de novo na mesma barra desliga e o botão **Limpar seleções** zera tudo. Os cliques combinam com os dropdowns.
- **KPIs:** receita declarada, despesas contratadas, despesas pagas, dívida estimada (C − P) e nº de candidatos.
- **Gráficos:** receita por UF, top partidos, receita/despesa por espectro, origem dos recursos, natureza, categorias de despesa, contratado × pago por UF, top fornecedores, gênero, cor/raça e curva de concentração. Sem gráficos de pizza.

## Espectro político

Classificação **por partido** em 6 faixas ordenadas — *Esquerda radical, Esquerda, Centro-esquerda, Centro, Centro-direita, Direita* — em `src/candidatos/model/espectro.py`. É convencional e aproximada: partidos de aliança ampla (MDB, PSD, União) são sensíveis ao critério. Ajuste o dicionário `ESPECTRO` conforme a metodologia desejada.

## Ressalvas

- Totais **preliminares** (sem prestação Final).
- Usar **apenas os arquivos consolidados** `*_BRASIL.csv`; somar com os arquivos por UF duplicaria os registros.
- `SQ_RECEITA` e `SQ_DESPESA` **não são chaves únicas** (não deduplicar sem analisar o contexto).
- `despesas_pagas` não traz `SG_PARTIDO`/`DS_CARGO`: os filtros de partido/cargo/espectro não se aplicam aos KPIs de pago e dívida (somente UF).
