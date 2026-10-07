# -*- coding: utf-8 -*-
"""Capa fotografica: expansion de lienzo, encuadre cover y degradados.

El encuadre no recorta la foto: la escala para cubrir el lienzo y la desplaza
hasta alinear un punto focal. Antes de eso puede agrandar el lienzo de la foto
estirando y difuminando sus bordes, que es lo que da recorrido cuando la toma
original no trae suficiente aire.

Las tres expansiones se aplican SIEMPRE en el orden lados -> arriba -> abajo, y
cada fraccion se lee sobre el tamano que la imagen trae en ese punto de la
cadena, no sobre el original. Alterar el orden cambia el encuadre, asi que es
parte del contrato y el solver replica la misma aritmetica -- incluidos los
int() que redondean hacia abajo.
"""
import base64
import os

from PIL import Image, ImageFilter

from . import svgdoc

# Las fotos expandidas superan con holgura los 100 MP y Pillow las rechaza por
# defecto como decompression bomb. Son archivos que genera este mismo modulo.
Image.MAX_IMAGE_PIXELS = None

MIMES = {".jpg": "image/jpeg", ".jpeg": "image/jpeg",
         ".png": "image/png", ".webp": "image/webp"}


# ------------------------------------------------------------- expansiones

def _difuminar_tira(tira, radio=60):
    return tira.filter(ImageFilter.GaussianBlur(radius=radio))


def expandir_arriba(entrada, salida, frac=0.15):
    """Agrega cielo/fondo sobre la cabeza estirando el borde superior."""
    im = Image.open(entrada).convert("RGB")
    nw, nh = im.size
    extra = int(nh * frac)
    alto_tira = max(60, int(nh * 0.01))
    tira = _difuminar_tira(im.crop((0, 0, nw, alto_tira)).resize((nw, extra), Image.LANCZOS))
    nuevo = Image.new("RGB", (nw, nh + extra))
    nuevo.paste(tira, (0, 0))
    nuevo.paste(im, (0, extra))
    costura = im.crop((0, 0, nw, alto_tira * 3)).filter(ImageFilter.GaussianBlur(radius=25))
    nuevo.paste(costura, (0, extra - alto_tira))
    nuevo.save(salida, quality=93)


def expandir_abajo(entrada, salida, frac=0.05):
    """Agrega piso bajo el sujeto.

    Es el unico recurso que sube al sujeto SIN agrandarlo cuando la foto va
    anclada al borde inferior: ahi mover el punto focal no hace nada, porque no
    queda holgura vertical que recorrer. Cada pixel de piso lo empuja hacia
    arriba. La tira cae bajo el degradado del pie, asi que no necesita ser
    exacta.
    """
    im = Image.open(entrada).convert("RGB")
    nw, nh = im.size
    extra = int(nh * frac)
    alto_tira = max(60, int(nh * 0.01))
    tira = _difuminar_tira(
        im.crop((0, nh - alto_tira, nw, nh)).resize((nw, extra), Image.LANCZOS))
    nuevo = Image.new("RGB", (nw, nh + extra))
    nuevo.paste(im, (0, 0))
    nuevo.paste(tira, (0, nh))
    costura = im.crop((0, nh - alto_tira * 3, nw, nh)).filter(ImageFilter.GaussianBlur(radius=25))
    nuevo.paste(costura, (0, nh - alto_tira * 2))
    nuevo.save(salida, quality=93)


def expandir_lados(entrada, salida, frac=0.4):
    """Agrega fondo a izquierda y derecha (mitad a cada lado).

    No es cosmetico: es lo unico que da recorrido horizontal. Sin ancho
    sobrante el cover no puede correr la foto lo suficiente para llevar la
    cabeza hasta la caja de silueta, y el recorte la deja a medio camino
    contra el borde.
    """
    im = Image.open(entrada).convert("RGB")
    nw, nh = im.size
    extra = int(nw * frac / 2)
    ancho_tira = max(60, int(nw * 0.01))
    izq = _difuminar_tira(im.crop((0, 0, ancho_tira, nh)).resize((extra, nh), Image.LANCZOS))
    der = _difuminar_tira(
        im.crop((nw - ancho_tira, 0, nw, nh)).resize((extra, nh), Image.LANCZOS))
    nuevo = Image.new("RGB", (nw + extra * 2, nh))
    nuevo.paste(izq, (0, 0))
    nuevo.paste(der, (extra + nw, 0))
    nuevo.paste(im, (extra, 0))
    c_izq = im.crop((0, 0, ancho_tira * 3, nh)).filter(ImageFilter.GaussianBlur(radius=25))
    nuevo.paste(c_izq, (extra - ancho_tira, 0))
    c_der = im.crop((nw - ancho_tira * 3, 0, nw, nh)).filter(ImageFilter.GaussianBlur(radius=25))
    nuevo.paste(c_der, (extra + nw - ancho_tira * 2, 0))
    nuevo.save(salida, quality=93)


# (clave, funcion, sigla para el cache). Las siglas son explicitas y no la
# inicial de la clave: "arriba" y "abajo" empiezan igual, y dos expansiones
# distintas con el mismo valor terminarian compartiendo archivo de cache.
CADENA = (("lados", expandir_lados, "lat"),
          ("arriba", expandir_arriba, "sup"),
          ("abajo", expandir_abajo, "inf"))


def preparar(ruta, expansiones, cache):
    """Devuelve la ruta de la foto expandida, generandola si hace falta.

    El nombre del cache codifica los parametros, de modo que cambiar un
    encuadre no invalida los demas y volver a un valor anterior no recalcula.
    """
    activas = {k: v for k, v in (expansiones or {}).items() if v}
    if not activas:
        return ruta

    base, ext = os.path.splitext(os.path.basename(ruta))
    etiqueta = base + "".join("-%s%s" % (sigla, activas[k])
                              for k, _, sigla in CADENA if activas.get(k)) + ext
    destino = os.path.join(cache, etiqueta)
    if os.path.exists(destino):
        return destino
    os.makedirs(cache, exist_ok=True)

    paso, temporales = ruta, []
    for clave, fn, _ in CADENA:
        frac = activas.get(clave)
        if not frac:
            continue
        intermedio = "%s.%s.jpg" % (destino, clave)
        fn(paso, intermedio, frac=float(frac))
        paso = intermedio
        temporales.append(intermedio)
    os.replace(paso, destino)
    for t in temporales:
        if os.path.exists(t):
            os.remove(t)
    return destino


# ------------------------------------------------------------------ encuadre

def cover(nw, nh, cw, ch, fx, fy, fxt, fyt, zoom=1.0):
    """Escala para cubrir el lienzo y alinea el punto focal (fx,fy) con (fxt,fyt).

    El clamp final es el que impide que queden huecos, y tambien el que explica
    por que a veces mover el focal "no hace nada": si la dimension no tiene
    holgura, el desplazamiento pedido queda fuera de rango y se recorta.
    """
    s = max(cw / nw, ch / nh) * zoom
    sw, sh = nw * s, nh * s
    tx = min(0.0, max(cw - sw, cw * fxt - sw * fx))
    ty = min(0.0, max(ch - sh, ch * fyt - sh * fy))
    return s, tx, ty


def _linear_gradient(g):
    stops = "".join(
        '<stop offset="%s" stop-color="%s" stop-opacity="%s"/>' % (o, c, a)
        for o, c, a in g["stops"])
    return ('<linearGradient id="%s" x1="%s" y1="%s" x2="%s" y2="%s" '
            'gradientUnits="userSpaceOnUse">%s</linearGradient>'
            % (g["id"], g.get("x0", 0), g["y0"], g.get("x1", 0), g["y1"], stops))


def poner(svg, cfg_foto, ruta, focal, zoom=1.0):
    """Inserta la foto a sangre en la capa declarada y reaplica los degradados.

    `cfg_foto` viene del bloque "foto" del formato en plantilla.json:
      capa_id      -- id del placeholder que recibe la imagen
      quitar       -- ids a eliminar cuando hay foto (la plancha gris de relleno)
      degradados   -- rect + (ref a un gradiente del arte | definicion nueva)
    """
    nw, nh = Image.open(ruta).size
    cw, ch = cfg_foto["_canvas"]
    s, tx, ty = cover(nw, nh, cw, ch, *focal, zoom=zoom)

    with open(ruta, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    mime = MIMES.get(os.path.splitext(ruta)[1].lower(), "image/jpeg")

    partes = ['<image width="%d" height="%d" transform="translate(%.2f %.2f) scale(%.5f)" '
              'xlink:href="data:%s;base64,%s"/>' % (nw, nh, tx, ty, s, mime, b64)]

    defs = []
    for d in cfg_foto.get("degradados", []):
        if "gradiente" in d:
            defs.append(_linear_gradient(d["gradiente"]))
            ref = d["gradiente"]["id"]
        else:
            ref = d["ref"]
        x, y, w, h = d["rect"]
        partes.append('<rect fill="url(#%s)" x="%s" y="%s" width="%s" height="%s"/>'
                      % (ref, x, y, w, h))

    for id_ in cfg_foto.get("quitar", []):
        svg = svgdoc.eliminar_elemento(svg, id_, si_existe=True)

    svg = svgdoc.reemplazar_interior(svg, cfg_foto["capa_id"], "".join(partes))
    if defs:
        svg = svgdoc.insertar_en_defs(svg, "".join(defs))
    return svg


# --------------------------------------------------------- mapa de depuracion

def mapa_zonas(svg, zonas, canvas):
    """Superpone las zonas seguras. Es la herramienta de diagnostico: cuando una
    pieza "se ve mal" pero el solver dice que cumple, aca se ve por que."""
    cw, ch = canvas
    ov = ['<g id="zonas-debug" opacity="0.9">']

    if "logo" in zonas:
        x0, y0, x1, y1 = zonas["logo"]
        ov.append('<rect x="%s" y="%s" width="%s" height="%s" fill="#ff0033" '
                  'fill-opacity="0.28" stroke="#ff0033" stroke-width="4"/>'
                  % (x0, y0, x1 - x0, y1 - y0))
    if "rostros" in zonas:
        r0, r1 = zonas["rostros"]
        ov.append('<rect x="0" y="%s" width="%s" height="%s" fill="#00e0ff" '
                  'fill-opacity="0.10"/>' % (r0, cw, r1 - r0))
    if "texto_y" in zonas:
        ty = zonas["texto_y"]
        ov.append('<rect x="0" y="%s" width="%s" height="%s" fill="#ffcc00" '
                  'fill-opacity="0.16"/>' % (ty, cw, ch - ty))
    if "silueta" in zonas:
        sx, sx2 = zonas["silueta"]
        sy = zonas.get("silueta_y", 0)
        ov.append('<rect x="%s" y="%s" width="%s" height="%s" fill="none" '
                  'stroke="#fff" stroke-width="5"/>' % (sx, sy, sx2 - sx, ch - sy))
        ov.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="#fff" '
                  'stroke-width="3" stroke-dasharray="14 10"/>'
                  % ((sx + sx2) / 2, sy, (sx + sx2) / 2, ch))
    ov.append("</g>")
    return svgdoc.antes_de_cierre(svg, "".join(ov))
