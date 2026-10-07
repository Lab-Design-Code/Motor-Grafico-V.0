# -*- coding: utf-8 -*-
"""Rasterizado SVG -> PNG.

Regla de oro heredada a golpes: **Inkscape devuelve codigo de salida 0 aunque
no escriba nada**. Pasa, por ejemplo, cuando la ruta lleva espacios y se cuela
por shell: interpreta cada fragmento como un archivo de entrada distinto,
aborta y sale con 0 igual. La unica verificacion valida es que el archivo
exista despues y sea posterior a la llamada, nunca el exit code.

Por eso ademas se invoca siempre por lista de argumentos y jamas por shell.
"""
import os
import subprocess
import tempfile

from . import entorno


class ErrorDeRender(RuntimeError):
    pass


def _comando(clase, binario, svg, png, ancho, alto):
    if clase == "resvg":
        cmd = [binario, svg, png]
        if ancho:
            cmd += ["--width", str(int(ancho))]
        if alto:
            cmd += ["--height", str(int(alto))]
        return cmd
    cmd = [binario, svg, "--export-type=png", "--export-filename=" + png]
    if ancho:
        cmd.append("--export-width=%d" % int(ancho))
    if alto:
        cmd.append("--export-height=%d" % int(alto))
    return cmd


def a_png(svg_path, png_path, ancho=None, alto=None):
    clase, binario = entorno.buscar_rasterizador()
    if os.path.exists(png_path):
        os.remove(png_path)
    os.makedirs(os.path.dirname(os.path.abspath(png_path)), exist_ok=True)

    proc = subprocess.run(_comando(clase, binario, svg_path, png_path, ancho, alto),
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if not os.path.exists(png_path):
        raise ErrorDeRender(
            "%s no escribio %s (exit %d)\n%s"
            % (clase, png_path, proc.returncode,
               (proc.stderr or b"").decode("utf-8", "replace")[:800]))
    return png_path


def cadena_a_png(svg, png_path, ancho=None, alto=None):
    """Rasteriza un SVG que esta en memoria, sin dejar el .svg en la entrega."""
    fd, tmp = tempfile.mkstemp(suffix=".svg")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(svg)
        return a_png(tmp, png_path, ancho, alto)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)
