# -*- coding: utf-8 -*-
"""Zonas seguras: se derivan de la plantilla en vez de medirse a mano.

Dos cosas distintas viven aqui.

`techo_texto` responde "donde empieza realmente el titulo de ESTA pieza".
Depende del largo del nombre, porque un titulo que se parte en dos lineas sube
el bloque completo una interlinea que a su vez depende del cuerpo ya
autoajustado. La version original lo resolvia renderizando cada pieza a PNG y
buscando el primer pixel blanco. Aca se calcula: la linea base sale del SVG ya
construido y el alto de mayusculas sale de la fuente. Es exacto, no necesita
rasterizador y es instantaneo.

`derivar` propone el resto de las zonas analizando el arte de la plantilla sin
foto: donde hay tinta arriba es el bloque de logo, donde vuelve a haber tinta
abajo empieza el texto. Lo que devuelve es una PROPUESTA para revisar, no un
dato cerrado: la caja de silueta es una decision de composicion -- donde se
quiere a la persona -- y eso ningun analisis de pixeles lo sabe.
"""
from PIL import Image

from . import plantilla as _plantilla
from . import render, svgdoc, texto

Image.MAX_IMAGE_PIXELS = None


def techo_texto(svg, ids, formato):
    """Y del pixel mas alto del bloque de texto, sobre un SVG ya construido.

    Se toma el minimo entre todos los elementos del bloque porque el que manda
    es el de mas arriba -- normalmente el prefijo, no el nombre.
    """
    reglas = _plantilla.estilos(svg)
    topes = []
    for id_ in ids:
        real = id_ if svgdoc.existe(svg, id_) else None
        if real is None:
            continue
        _, y = _plantilla.pose_de(svg, real)
        size = _plantilla.cuerpo_de(svg, real, reglas)
        fuente = _fuente_de(formato, id_)
        topes.append(y - texto.alto_mayusculas(fuente, size))
    if not topes:
        raise ValueError("Ningun id del bloque de titulo existe en el SVG: %s" % (ids,))
    return min(topes)


def _fuente_de(formato, id_):
    for el in formato.elementos:
        if el.get("id") == id_:
            return el["fuente"]
        for slot in el.get("slots", []):
            if slot.get("texto_id") == id_:
                return el["fuente"]
    raise KeyError("El id \"%s\" no esta declarado en los elementos del formato" % id_)


def titulo_de_pieza(formato, campos):
    """Techo del bloque de titulo para una fila concreta de datos."""
    ids = formato.zonas.get("bloque_titulo")
    if not ids:
        return None
    return techo_texto(formato.construir(campos), ids, formato)


# --------------------------------------------------- derivacion desde el arte

def _arte_sin_foto(formato):
    """SVG de la plantilla con la capa de foto vaciada y la plancha quitada.

    Lo que queda es solo el arte: logo, textos y pastillas sobre transparente.
    """
    svg = formato.leer_svg()
    cfg = formato.foto or {}
    for id_ in cfg.get("quitar", []):
        svg = svgdoc.eliminar_elemento(svg, id_, si_existe=True)
    if cfg.get("capa_id") and svgdoc.existe(svg, cfg["capa_id"]):
        svg = svgdoc.reemplazar_interior(svg, cfg["capa_id"], "")
    return svg


# Alpha a partir del cual un pixel cuenta como tinta. Es alto a proposito: las
# plantillas suelen traer degradados de ancho completo para asentar el logo o el
# texto, y esos lavados NO son obstaculos -- un rostro puede quedar debajo de un
# degradado, no debajo del logo. Contarlos como tinta hacia que el bloque de
# logo se detectara del ancho del lienzo.
UMBRAL_TINTA = 160


def _filas_con_tinta(png, umbral_alpha=UMBRAL_TINTA, minimo_pixeles=3):
    """Para cada fila devuelve (x_min, x_max) de tinta, o None si esta vacia."""
    im = Image.open(png).convert("RGBA")
    w, h = im.size
    px = im.load()
    filas = []
    for y in range(h):
        x0, x1, n = None, None, 0
        for x in range(0, w, 2):  # de a 2: la tinta de un logo nunca es de 1 px
            if px[x, y][3] > umbral_alpha:
                n += 1
                if x0 is None:
                    x0 = x
                x1 = x
        filas.append((x0, x1) if n >= minimo_pixeles else None)
    return filas, w, h


def derivar(formato, tolerancia_hueco=12):
    """Propone las zonas seguras analizando el arte de la plantilla.

    Devuelve un dict listo para pegar en plantilla.json, mas notas sobre que
    esta derivado y que es una convencion que conviene revisar.
    """
    svg = _arte_sin_foto(formato)
    png = render.cadena_a_png(
        svg, __import__("tempfile").mktemp(suffix=".png"),
        formato.ancho, formato.alto)
    try:
        filas, w, h = _filas_con_tinta(png)
    finally:
        import os
        if os.path.exists(png):
            os.remove(png)

    # --- bloque de logo: primera banda continua de tinta desde arriba
    y0 = next((i for i, f in enumerate(filas) if f), None)
    if y0 is None:
        raise ValueError("La plantilla no tiene tinta: revisa que los ids de "
                         "\"foto.quitar\" sean los correctos")
    y1, hueco = y0, 0
    for i in range(y0, h):
        if filas[i]:
            y1, hueco = i, 0
        else:
            hueco += 1
            if hueco > tolerancia_hueco:
                break
    banda = [f for f in filas[y0:y1 + 1] if f]
    lx0 = min(f[0] for f in banda)
    lx1 = max(f[1] for f in banda)

    # El bbox de tinta es exacto pero pegado: una cabeza que lo roce ya se lee
    # como invasion. Se agrega el margen de seguridad que un disenador dejaria.
    margen_logo = int(w * 0.028)
    lx0, lx1 = max(0, lx0 - margen_logo), min(w, lx1 + margen_logo)
    y0, y1 = max(0, y0 - margen_logo), min(h, y1 + margen_logo)

    # --- zona de texto: la PRIMERA tinta despues del hueco que sigue al logo.
    # No se busca desde la mitad del lienzo: en un formato cuadrado el titulo
    # empieza por encima de esa mitad y quedaria sin detectar.
    ty = next((i for i in range(y1 + tolerancia_hueco, h) if filas[i]), int(h * 0.68))

    # --- silueta: a la derecha del logo, dejando libre el margen izquierdo.
    # Es una CONVENCION, no una medicion: el margen izquierdo se reserva para
    # el logo arriba y el titulo abajo, asi que el sujeto se corre a la derecha.
    margen = int(w * 0.11)
    sx1 = w - margen
    sx0 = max(0, min(int(lx1 - w * 0.10), sx1 - int(w * 0.25)))

    return {
        "logo": [int(lx0), int(y0), int(lx1), int(y1)],
        "texto_y": int(ty),
        "pelo_min": int(y1) + 20,
        "titulo": int(ty),
        "rostros": [int(y1) + 15, int(ty) - 10],
        "silueta": [sx0, sx1],
        "aire": {"1": 70, "2": 50},
        "ancla": 1,
        "_derivado": {
            "medido": ["logo", "texto_y", "titulo", "pelo_min", "rostros"],
            "convencion_revisar": ["silueta", "aire", "ancla"],
            "nota": ("silueta y aire son decisiones de composicion, no medidas. "
                     "Revisalas contra una pieza real con --zonas antes de lanzar el lote."),
        },
    }
