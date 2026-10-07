# -*- coding: utf-8 -*-
"""Metricas de fuente y ajuste automatico de titulos.

El ancho se mide sobre la fuente real (fontTools), no se estima. Es lo que
permite decidir antes de renderizar si un nombre cabe, cuanto hay que achicarlo
o donde partirlo, y es la diferencia entre "el texto se desborda a veces" y
"nunca se desborda".
"""
from fontTools.ttLib import TTFont

from . import entorno

_cache = {}


def _metricas(nombre_fuente):
    ruta = entorno.buscar_fuente(nombre_fuente)
    if ruta not in _cache:
        f = TTFont(ruta, fontNumber=0)
        _cache[ruta] = (f.getBestCmap(), f["hmtx"], f["head"].unitsPerEm,
                        _cap_height(f))
    return _cache[ruta][:3]


def _cap_height(f):
    """Alto de mayusculas en unidades de em.

    OS/2 v2+ lo declara; si no, se mide la caja de la 'H', que es la definicion
    original. El ultimo recurso es 0.70, la proporcion tipica de una grotesca.
    """
    try:
        cap = getattr(f["OS/2"], "sCapHeight", 0)
        if cap:
            return cap
    except KeyError:
        pass
    try:
        glifo = f.getBestCmap().get(ord("H"))
        if glifo:
            bounds = f.getGlyphSet()[glifo]
            from fontTools.pens.boundsPen import BoundsPen
            pen = BoundsPen(f.getGlyphSet())
            bounds.draw(pen)
            if pen.bounds:
                return pen.bounds[3]
    except Exception:
        pass
    return 0.70 * f["head"].unitsPerEm


def alto_mayusculas(nombre_fuente, size):
    """Cuanto sube la tinta de una mayuscula por encima de la linea base.

    Es lo que convierte una baseline en el techo visible del texto, y con eso
    el solver puede saber donde empieza realmente el titulo sin renderizar ni
    escanear pixeles.
    """
    _metricas(nombre_fuente)
    ruta = entorno.buscar_fuente(nombre_fuente)
    _, _, upem, cap = _cache[ruta]
    return cap * size / upem


def ancho(texto, nombre_fuente, size):
    """Ancho de avance en px del texto a ese cuerpo.

    Suma anchos de avance sin kerning ni ligaduras. Es una cota levemente
    superior al ancho real de tinta, que para decidir si algo cabe es
    exactamente el lado por el que conviene equivocarse.
    """
    cmap, hmtx, upem = _metricas(nombre_fuente)
    total = 0
    for ch in str(texto):
        glifo = cmap.get(ord(ch)) or cmap.get(ord("?"))
        if glifo is None:
            continue
        total += hmtx[glifo][0]
    return total * size / upem


def cuerpo_para_caber(texto, nombre_fuente, size, max_ancho):
    """Cuerpo necesario para que el texto entre en max_ancho (nunca agranda)."""
    w = ancho(texto, nombre_fuente, size)
    if w <= max_ancho:
        return size
    return max_ancho / w * size


def partir_balanceado(texto, nombre_fuente, size, lineas=2):
    """Parte el texto en N lineas buscando el corte mas parejo.

    Balancear en vez de llenar la primera linea no es estetica: un titular con
    la segunda linea de tres letras se lee como un error de maquetado. Corta
    solo en espacios; si no hay, devuelve el texto entero en una linea.
    """
    palabras = str(texto).split()
    if len(palabras) < lineas or lineas < 2:
        return [str(texto)]

    if lineas == 2:
        mejor, dif = 1, float("inf")
        for i in range(1, len(palabras)):
            a = ancho(" ".join(palabras[:i]), nombre_fuente, size)
            b = ancho(" ".join(palabras[i:]), nombre_fuente, size)
            if abs(a - b) < dif:
                dif, mejor = abs(a - b), i
        return [" ".join(palabras[:mejor]), " ".join(palabras[mejor:])]

    # Para 3+ lineas: reparto greedy por ancho objetivo, suficiente en titulares.
    total = ancho(" ".join(palabras), nombre_fuente, size)
    objetivo = total / lineas
    resultado, actual = [], []
    for p in palabras:
        prueba = " ".join(actual + [p])
        if actual and ancho(prueba, nombre_fuente, size) > objetivo and len(resultado) < lineas - 1:
            resultado.append(" ".join(actual))
            actual = [p]
        else:
            actual.append(p)
    resultado.append(" ".join(actual))
    return resultado


def ajustar_titulo(texto, nombre_fuente, size, max_ancho,
                   min_escala=0.82, max_lineas=2):
    """Resuelve cuerpo y numero de lineas de un titular.

    Estrategia, en orden:
      1. si cabe tal cual, no se toca;
      2. se achica hasta `min_escala` del cuerpo original;
      3. si asi no cabe, se parte en lineas balanceadas y, si aun se pasa,
         se achica lo justo para que entre la linea mas larga.

    Devuelve (lineas, cuerpo). El llamador es quien sabe cuanto hay que subir
    el bloque: son `len(lineas) - 1` interlineas.
    """
    texto = str(texto)
    if ancho(texto, nombre_fuente, size) <= max_ancho:
        return [texto], size

    requerido = cuerpo_para_caber(texto, nombre_fuente, size, max_ancho)
    if requerido >= size * min_escala:
        return [texto], requerido

    for n in range(2, max_lineas + 1):
        lineas = partir_balanceado(texto, nombre_fuente, size, n)
        if len(lineas) < n:
            break
        mas_ancha = max(ancho(l, nombre_fuente, size) for l in lineas)
        if mas_ancha <= max_ancho:
            return lineas, size
        if n == max_lineas:
            return lineas, max_ancho / mas_ancha * size

    # Sin espacios donde cortar: no queda mas que achicar.
    return [texto], requerido
