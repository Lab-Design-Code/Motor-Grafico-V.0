# -*- coding: utf-8 -*-
"""Descubrimiento del entorno: fuentes y rasterizador.

No hay archivo de configuracion a proposito. En vez de declarar rutas, el motor
las busca en los lugares donde realmente viven, en orden de prioridad. Asi la
carpeta se copia a otra maquina y funciona sin editar nada.

La primera ruta de busqueda es `fuentes/` dentro del propio motor: si ahi se
dejan los .otf, el proyecto es portable de verdad y deja de depender de que la
fuente este instalada en el sistema.
"""
import os
import shutil
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Orden de busqueda de fuentes. `fuentes/` primero: una copia local dentro del
# motor gana siempre a la instalada en el sistema, que puede ser otra version.
DIRS_FUENTES = [
    os.path.join(RAIZ, "fuentes"),
    os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Windows\Fonts"),
    r"C:\Windows\Fonts",
    os.path.expanduser("~/.fonts"),
    os.path.expanduser("~/Library/Fonts"),
    "/usr/share/fonts",
    "/usr/local/share/fonts",
]

EXTENSIONES_FUENTE = (".otf", ".ttf", ".ttc")

# Candidatos de rasterizador, en orden de preferencia. resvg va primero cuando
# esta disponible: es un solo binario, varias veces mas rapido que Inkscape y
# no arrastra una instalacion de escritorio.
CANDIDATOS_RENDER = [
    ("resvg", ["resvg"]),
    ("inkscape", [
        "inkscape",
        r"C:\Program Files\Inkscape\bin\inkscape.exe",
        r"C:\Program Files (x86)\Inkscape\bin\inkscape.exe",
        "/usr/bin/inkscape",
        "/Applications/Inkscape.app/Contents/MacOS/inkscape",
    ]),
]

_cache_fuentes = {}
_cache_render = None


class EntornoIncompleto(RuntimeError):
    """Falta algo del entorno y el mensaje explica como resolverlo."""


def buscar_fuente(nombre):
    """Devuelve la ruta de una fuente a partir de su nombre de archivo.

    `nombre` puede venir con extension ("Montserrat-Black.otf") o sin ella
    ("Montserrat-Black"), porque la misma familia se distribuye como .otf o
    .ttf segun de donde se haya instalado y la plantilla no tiene por que
    saber cual de las dos hay en esta maquina.
    """
    if nombre in _cache_fuentes:
        return _cache_fuentes[nombre]

    if os.path.isabs(nombre) and os.path.exists(nombre):
        _cache_fuentes[nombre] = nombre
        return nombre

    base, ext = os.path.splitext(nombre)
    extensiones = [ext] if ext else list(EXTENSIONES_FUENTE)

    for d in DIRS_FUENTES:
        if not d or not os.path.isdir(d):
            continue
        for e in extensiones:
            ruta = os.path.join(d, base + e)
            if os.path.exists(ruta):
                _cache_fuentes[nombre] = ruta
                return ruta

    raise EntornoIncompleto(
        "No encuentro la fuente '%s'.\n"
        "Buscada en:\n  %s\n"
        "Solucion: instalala en el sistema, o copia el archivo a\n  %s\n"
        "(esa carpeta es la primera en el orden de busqueda y hace portable el motor)."
        % (nombre, "\n  ".join(d for d in DIRS_FUENTES if d),
           os.path.join(RAIZ, "fuentes")))


def buscar_rasterizador():
    """Devuelve (clase, ruta) del primer rasterizador disponible.

    `clase` es "resvg" o "inkscape" porque la linea de comandos difiere; el
    resto del motor no necesita saber cual es.
    """
    global _cache_render
    if _cache_render is not None:
        return _cache_render

    entorno = os.environ.get("MOTOR_RASTERIZADOR")
    if entorno and os.path.exists(entorno):
        clase = "resvg" if "resvg" in os.path.basename(entorno).lower() else "inkscape"
        _cache_render = (clase, entorno)
        return _cache_render

    for clase, candidatos in CANDIDATOS_RENDER:
        for c in candidatos:
            ruta = c if os.path.isabs(c) and os.path.exists(c) else shutil.which(c)
            if ruta:
                _cache_render = (clase, ruta)
                return _cache_render

    raise EntornoIncompleto(
        "No encuentro un rasterizador SVG -> PNG.\n"
        "Instala una de estas dos opciones:\n"
        "  - resvg   (recomendado, un solo binario): https://github.com/linebender/resvg/releases\n"
        "  - Inkscape: https://inkscape.org/release/\n"
        "Si ya lo tienes en una ruta no estandar, exporta MOTOR_RASTERIZADOR con la ruta al ejecutable.")


def diagnostico():
    """Reporte legible de que encontro el motor. Es lo primero que hay que
    correr al estrenar el motor en una maquina nueva."""
    lineas = ["Python      %s" % sys.version.split()[0]]

    for mod, nota in (("PIL", "obligatorio"), ("fontTools", "obligatorio"),
                      ("numpy", "para rostro automatico"),
                      ("cv2", "para rostro automatico"),
                      ("mediapipe", "opcional, mejora la precision del rostro")):
        try:
            m = __import__(mod)
            lineas.append("%-11s %s" % (mod, getattr(m, "__version__", "ok")))
        except ImportError:
            lineas.append("%-11s FALTA  (%s)" % (mod, nota))

    try:
        clase, ruta = buscar_rasterizador()
        lineas.append("%-11s %s (%s)" % ("render", ruta, clase))
    except EntornoIncompleto as e:
        lineas.append("%-11s FALTA\n%s" % ("render", e))

    lineas.append("")
    lineas.append("Carpetas de fuentes visibles:")
    for d in DIRS_FUENTES:
        if d and os.path.isdir(d):
            lineas.append("  %s" % d)
    return "\n".join(lineas)
