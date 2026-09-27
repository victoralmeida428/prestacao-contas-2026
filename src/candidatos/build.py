"""Gera o parquet do dashboard a partir dos CSV: ``python -m candidatos.build``."""

from __future__ import annotations

from .model.dataset import _main

if __name__ == "__main__":
    _main()
