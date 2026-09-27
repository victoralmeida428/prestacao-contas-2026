"""Executa o dashboard em modo de desenvolvimento: ``python -m candidatos``."""

from __future__ import annotations

import os

from . import config
from .app import app

if __name__ == "__main__":
    app.run(host=config.HOST, port=int(os.environ.get("PORT", config.PORT)), debug=False)
