# -*- coding: utf-8 -*-
"""Motor de graficas: plantilla + datos -> piezas verificadas.

Generico por diseno: el binding a una marca concreta vive en un plantilla.json,
no en el codigo. Ver README.md.
"""
__version__ = "1.0.0"

from . import (entorno, foto, lote, plantilla, qa, render, rostro, solver,  # noqa: F401
               svgdoc, texto, zonas)
