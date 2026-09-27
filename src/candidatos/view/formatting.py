"""Formatacao de numeros no padrao brasileiro."""

from __future__ import annotations


def num(valor: float | None, casas: int = 2) -> str:
    if valor is None:
        return "-"
    return f"{valor:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def brl(valor: float | None) -> str:
    """Formata em reais, abreviando para mil/mi/bi."""
    if valor is None:
        return "-"
    for div, suf in ((1e9, " bi"), (1e6, " mi"), (1e3, " mil")):
        if abs(valor) >= div:
            return f"R$ {num(valor / div)}{suf}".strip()
    return f"R$ {num(valor)}"
