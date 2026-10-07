# -*- coding: utf-8 -*-
"""Verificacion automatica de la pieza ya renderizada.

El solver dice si un encuadre CUMPLE segun su propia aritmetica. Esto es otra
cosa: mide el PNG final. Existe porque las dos pueden divergir -- basta que el
solver y la capa fotografica redondeen distinto -- y porque hay fallas que el
solver no puede ver: texto desbordado, o texto blanco sobre una zona clara de
la foto.

Cada hallazgo trae nivel, que se reviso y con que numeros, para que el informe
sirva para arreglar y no solo para alarmar.
"""
from PIL import Image

from . import plantilla as _plantilla
from . import rostro, solver, svgdoc, texto, zonas

Image.MAX_IMAGE_PIXELS = None

# Luminancia media maxima admisible bajo texto blanco.
#
# Calibrado contra las 166 piezas aprobadas de la campana IPG 2027: los Post
# van de 62 a 140 (mediana 111) y los Story de 50 a 111 (mediana 89). El umbral
# se fija por encima del maximo aprobado, porque un QA que marca como falla lo
# que el cliente ya firmo deja de leerse a los tres dias.
LUMINANCIA_MAX = 145

# Margen al comparar el rostro medido sobre el PNG final contra las zonas.
#
# El tope del pelo es una ESTIMACION -- el pelo no tiene geometria estable y
# ninguna libreria lo marca -- asi que medirlo sobre el render no devuelve
# exactamente el valor que uso el solver. Diferencias de unos pocos pixeles
# son ruido de la propia medicion, no defectos de la pieza: reportarlas como
# error hace que el informe sea todo rojo y nadie lo mire.
TOLERANCIA_PX = 10


class Hallazgo:
    def __init__(self, nivel, regla, mensaje):
        self.nivel = nivel          # "error" | "aviso" | "ok"
        self.regla = regla
        self.mensaje = mensaje

    def __str__(self):
        marca = {"error": "ERROR", "aviso": "aviso", "ok": "ok   "}[self.nivel]
        return "%s  %-18s %s" % (marca, self.regla, self.mensaje)


def _luminancia_media(im, caja):
    x0, y0, x1, y1 = [int(v) for v in caja]
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(im.width, x1), min(im.height, y1)
    if x1 <= x0 or y1 <= y0:
        return None
    recorte = im.crop((x0, y0, x1, y1)).convert("L")
    recorte = recorte.resize((min(120, recorte.width), min(120, recorte.height)))
    px = list(recorte.getdata())
    return sum(px) / float(len(px))


def revisar_texto(svg, formato, campos):
    """Comprueba que ningun texto se salga del lienzo ni de su ancho maximo."""
    out = []
    reglas = _plantilla.estilos(svg)
    for el in formato.elementos:
        if el["tipo"] == "repetido" or not el.get("id"):
            continue
        ids = [el["id"]] + ["%s-l%d" % (el["id"], i) for i in range(2, 5)]
        for id_ in ids:
            if not svgdoc.existe(svg, id_):
                continue
            contenido = _contenido_de(svg, id_)
            if not contenido:
                continue
            x, _ = _plantilla.pose_de(svg, id_)
            size = _plantilla.cuerpo_de(svg, id_, reglas)
            w = texto.ancho(contenido, el["fuente"], size)
            limite = float(el["max_ancho"]) if el.get("max_ancho") else formato.ancho - x
            if w > limite + 0.5:
                out.append(Hallazgo(
                    "error", "texto-desborda",
                    "id=%s: %.0f px de ancho contra un limite de %.0f (\"%s\")"
                    % (id_, w, limite, contenido[:40])))
            elif x + w > formato.ancho:
                out.append(Hallazgo(
                    "error", "texto-fuera",
                    "id=%s termina en x=%.0f, fuera del lienzo de %d"
                    % (id_, x + w, formato.ancho)))
    return out


def _contenido_de(svg, id_):
    import re
    e = svgdoc.localizar(svg, id_)
    if e["inicio_interior"] is None:
        return ""
    interior = svg[e["inicio_interior"]:e["fin_interior"]]
    return re.sub(r"<[^>]+>", "", interior).strip()


def revisar_encuadre(svg, formato, pieza):
    """Verifica el encuadre por aritmetica, no por deteccion.

    Es la comprobacion FUERTE, y por eso la unica que puede declarar un error:
    recalcula donde caen pelo, menton y cara con los parametros realmente
    aplicados, usando las mismas formulas que la capa fotografica. Detecta lo
    que importa de verdad -- que alguien edite un encuadre a mano y lo rompa,
    o que cambie el largo del nombre y el titulo suba hasta el menton -- sin
    depender de volver a encontrar la cara en una imagen ya recortada.
    """
    out = []
    z = formato.zonas
    medidas = pieza.get("medidas")
    encuadre = (pieza.get("encuadre") or {}).get(formato.nombre)
    if not medidas or not encuadre or not encuadre.get("focal"):
        return out

    p = solver.prever(medidas, (formato.ancho, formato.alto),
                      encuadre.get("expansiones"), tuple(encuadre["focal"]),
                      float(encuadre.get("zoom", 1.0)))
    techo = _techo_titulo(svg, formato, z)
    limite = z.get("pelo_min", 0)

    if p["pelo"] < limite - TOLERANCIA_PX:
        out.append(Hallazgo(
            "error", "pelo-en-logo",
            "el pelo cae en y=%.0f y el limite es %d: la cabeza invade el logo"
            % (p["pelo"], limite)))
    if techo is not None and p["menton"] > techo + TOLERANCIA_PX:
        out.append(Hallazgo(
            "error", "menton-en-texto",
            "el menton cae en y=%.0f y el titulo empieza en y=%.0f: falta aire"
            % (p["menton"], techo)))
    if z.get("silueta"):
        sx, sx1 = z["silueta"]
        if not (sx - TOLERANCIA_PX <= p["cara_x"] <= sx1 + TOLERANCIA_PX):
            out.append(Hallazgo(
                "aviso", "fuera-de-silueta",
                "la cara queda en x=%.0f, fuera de la silueta [%d, %d]"
                % (p["cara_x"], sx, sx1)))
    if not any(h.nivel == "error" for h in out):
        out.append(Hallazgo("ok", "encuadre", "pelo %.0f  menton %.0f  cara_x %.0f"
                            % (p["pelo"], p["menton"], p["cara_x"])))
    return out


def revisar_render(png, formato, pieza, con_rostro=False):
    """Mide el PNG terminado: tamano, contraste y -- si se pide -- el rostro.

    La re-deteccion del rostro sobre la pieza ya compuesta es DELIBERADAMENTE
    advertencia y nunca error, y viene apagada por defecto. Sobre el render la
    cara esta recortada, atenuada por el degradado y a veces acompanada de otra
    persona, asi que un detector liviano se equivoca seguido: en la campana IPG
    marco 21 piezas ya aprobadas, con desvios de hasta 250 px que no son ruido
    de medicion sino detecciones directamente erroneas. Un QA que marca en rojo
    lo que el cliente ya firmo deja de leerse a los tres dias.

    Sirve, eso si, para lo que la aritmetica no ve: que el sujeto detectado no
    sea el que se eligio. Asi se encontro que la foto de Podologia trae dos
    profesionales.
    """
    out = []
    im = Image.open(png).convert("RGB")
    z = formato.zonas

    if im.size != (formato.ancho, formato.alto):
        out.append(Hallazgo("error", "tamano",
                            "el PNG mide %dx%d y el formato declara %dx%d"
                            % (im.size[0], im.size[1], formato.ancho, formato.alto)))

    if "texto_y" in z:
        lum = _luminancia_media(im, (0, z["texto_y"], formato.ancho, formato.alto))
        if lum is not None:
            if lum > LUMINANCIA_MAX:
                out.append(Hallazgo(
                    "aviso", "contraste",
                    "la zona de texto tiene luminancia media %.0f (max %d): el texto "
                    "blanco puede perderse. Suele ser el degradado quedando corto."
                    % (lum, LUMINANCIA_MAX)))
            else:
                out.append(Hallazgo("ok", "contraste",
                                    "luminancia %.0f bajo el texto" % lum))

    if con_rostro:
        try:
            m = rostro.medir(png, sujeto=pieza.get("sujeto", "mayor"),
                             pelo_factor=pieza.get("pelo_factor"))
        except rostro.SinRostro:
            out.append(Hallazgo("aviso", "rostro",
                                "no se pudo re-detectar el rostro en la pieza "
                                "(normal: esta recortado y bajo el degradado)"))
        else:
            previsto = revisar_encuadre_valores(formato, pieza)
            detectado_x = m["cara_x"] * formato.ancho
            if previsto and abs(detectado_x - previsto["cara_x"]) > 120:
                out.append(Hallazgo(
                    "aviso", "sujeto-dudoso",
                    "la cara detectada esta en x=%.0f y se esperaba x=%.0f. "
                    "Si la foto trae mas de una persona, fija \"sujeto\"."
                    % (detectado_x, previsto["cara_x"])))
    return out


def revisar_encuadre_valores(formato, pieza):
    medidas = pieza.get("medidas")
    encuadre = (pieza.get("encuadre") or {}).get(formato.nombre)
    if not medidas or not encuadre or not encuadre.get("focal"):
        return None
    return solver.prever(medidas, (formato.ancho, formato.alto),
                         encuadre.get("expansiones"), tuple(encuadre["focal"]),
                         float(encuadre.get("zoom", 1.0)))


def _techo_titulo(svg, formato, z):
    ids = z.get("bloque_titulo")
    if not ids:
        return None
    try:
        return zonas.techo_texto(svg, ids, formato)
    except Exception:
        return None


def revisar(svg, png, formato, pieza, con_rostro=False):
    """Informe completo de una pieza.

    Tres capas, de mas a menos fiable: medidas exactas sobre el SVG (texto),
    aritmetica del encuadre (posicion del sujeto) y, opcional, re-deteccion
    sobre el PNG. Solo las dos primeras pueden declarar un error.
    """
    hallazgos = revisar_texto(svg, formato, pieza["campos"])
    hallazgos += revisar_encuadre(svg, formato, pieza)
    if png:
        hallazgos += revisar_render(png, formato, pieza, con_rostro)
    return hallazgos


def resumen(hallazgos):
    errores = sum(1 for h in hallazgos if h.nivel == "error")
    avisos = sum(1 for h in hallazgos if h.nivel == "aviso")
    return errores, avisos
