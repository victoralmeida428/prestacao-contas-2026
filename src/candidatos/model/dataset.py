"""Gera o parquet enxuto consumido pelo dashboard a partir dos CSV brutos.

Apenas as colunas realmente usadas pelas visualizacoes sao mantidas, o que
reduz ~1,6 GB de CSV para ~20 MB de parquet (zstd) - leve o suficiente para
versionar no Git e para a imagem Docker.
"""

from __future__ import annotations

from pathlib import Path

import polars as pl

from .. import config
from . import loader
from .schema import COLUNAS_DASHBOARD


def build(
    destino_dir: Path | str = config.DASH_DIR,
    raw_dir: Path | str = config.RAW_DIR,
) -> dict[str, Path]:
    """Le os CSV, seleciona as colunas do dashboard e grava o parquet."""
    destino_dir = Path(destino_dir)
    destino_dir.mkdir(parents=True, exist_ok=True)

    caminhos: dict[str, Path] = {}
    for tabela, colunas in COLUNAS_DASHBOARD.items():
        df = loader.load_tse(tabela, colunas=colunas, base_dir=raw_dir)
        destino = destino_dir / f"{tabela}.parquet"
        df.write_parquet(destino, compression="zstd", statistics=False)
        caminhos[tabela] = destino
    return caminhos


def _main() -> None:
    print(f"Lendo CSV de {config.RAW_DIR}")
    caminhos = build()
    total = 0
    for tabela, caminho in caminhos.items():
        mb = caminho.stat().st_size / 1e6
        total += mb
        print(f"  {tabela:24s} -> {caminho.name} ({mb:5.1f} MB)")
    print(f"Total: {total:.1f} MB em {config.DASH_DIR}")


if __name__ == "__main__":
    _main()
