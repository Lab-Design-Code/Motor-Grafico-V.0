# -*- coding: utf-8 -*-
"""Plantillas declarativas: el binding vive en plantilla.json, no en el codigo.

La version original de este motor llevaba dentro del .py un diccionario por
formato con ~47 constantes cada uno -- clases CSS, coordenadas, cuerpos,
regex literales. Montar una marca nueva significaba editar Python.

Aca el binding es un JSON, y ademas es mucho mas corto, porque **casi todo se
lee del propio SVG**:

  - la posicion sale del `transform` del elemento;
  - el cuerpo sale de la regla CSS de su clase, resuelta desde el <style>;
  - el ancho y la x de las pastillas salen de sus atributos.

Lo unico que hay que declarar es lo que el SVG no puede saber: que campo de
datos va en cada elemento, que fuente usa para medirlo, y las pocas reglas de
comportamiento (ancho maximo del titulo, que elementos arrastra al partirse).
"""
import json
import os
import re

from . import svgdoc, texto

# ------------------------------------------------------------------ formateo

_CAMPO_RE = re.compile(r"\{([A-Za-z_][\w]*)(?::([a-z_]+))?\}")


def _miles(v):
    """1234567 -> '1.234.567'. Separador de miles con punto, como se usa en Chile."""
    return format(int(round(float(v))), ",d").replace(",", ".")


FILTROS = {
    "miles": _miles,
    "entero": lambda v: str(int(round(float(v)))),
    "mayus": lambda v: str(v).upper(),
    "minus": lambda v: str(v).lower(),
    "capital": lambda v: str(v).title(),
}


def formatear(patron, campos):
    """Resuelve '{cuota:miles}' contra el diccionario de datos.

    Se usa un formateador propio y no str.format porque las plantillas traen
    '$' y '%' literales alrededor de los campos, y porque un campo ausente
    tiene que dar un error que diga cual falta.
    """
    def _sub(m):
        nombre, filtro = m.group(1), m.group(2)
        if nombre not in campos:
            raise KeyError(
                "El dato '%s' no esta en esta fila (la plantilla lo pide en \"%s\")"
                % (nombre, patron))
        valor = campos[nombre]
        if filtro:
            if filtro not in FILTROS:
                raise KeyError("Filtro desconocido '%s'. Disponibles: %s"
                               % (filtro, ", ".join(sorted(FILTROS))))
            valor = FILTROS[filtro](valor)
        return str(valor)
    return _CAMPO_RE.sub(_sub, patron)


# ------------------------------------------------- lectura de estilo y pose

_ESTILO_RE = re.compile(r"([^{}]+)\{([^}]*)\}")


def estilos(svg):
    """Mapa clase -> propiedades, leido del bloque <style> de la plantilla.

    Illustrator agrupa selectores (`.cls-1, .cls-6 { font-family: ... }`): la
    regla vale para TODAS las clases del grupo, no solo para la ultima.
    """
    reglas = {}
    for bloque in re.findall(r"<style[^>]*>(.*?)</style>", svg, re.S):
        for selectores, cuerpo in _ESTILO_RE.findall(bloque):
            for sel in selectores.split(","):
                sel = sel.strip()
                if not re.match(r"^\.[\w-]+$", sel):
                    continue
                props = reglas.setdefault(sel[1:], {})
                for par in cuerpo.split(";"):
                    if ":" in par:
                        k, v = par.split(":", 1)
                        props[k.strip()] = v.strip()
    return reglas


def cuerpo_de(svg, id_, reglas=None):
    """Cuerpo tipografico efectivo de un elemento de texto.

    Prioridad: style inline > clase CSS. Es el orden real de la cascada, y es
    justo el que hizo perder horas en la version original: un atributo
    font-size="60px" es ignorado cuando la clase define font-size, de modo que
    el unico override que funciona es el style inline.
    """
    e = svgdoc.localizar(svg, id_)
    m = re.search(r'style="[^"]*font-size\s*:\s*([\d.]+)', e["apertura"])
    if m:
        return float(m.group(1))
    reglas = reglas if reglas is not None else estilos(svg)
    mc = re.search(r'class="([^"]*)"', e["apertura"])
    for clase in (mc.group(1).split() if mc else []):
        tam = reglas.get(clase, {}).get("font-size")
        if tam:
            return float(re.sub(r"[^\d.]", "", tam))
    # Exportacion de Illustrator con "atributos de presentacion" en vez de CSS.
    ma = re.search(r'\sfont-size="([\d.]+)', e["apertura"])
    if ma:
        return float(ma.group(1))
    raise ValueError(
        "No pude deducir el cuerpo de id=\"%s\": no tiene style inline ni una "
        "clase con font-size. Declaralo con \"size\" en plantilla.json." % id_)


def pose_de(svg, id_):
    """(x, y) del translate de un elemento."""
    t = svgdoc.leer_atributo(svg, id_, "transform") or ""
    m = re.search(r"translate\(\s*([-\d.]+)[\s,]+([-\d.]+)", t)
    if not m:
        raise ValueError("El elemento id=\"%s\" no tiene translate(x y)" % id_)
    return float(m.group(1)), float(m.group(2))


def _numero(svg, id_, attr, defecto=0.0):
    v = svgdoc.leer_atributo(svg, id_, attr)
    return float(v) if v is not None else defecto


def mover_y(svg, id_, delta):
    """Sube o baja un elemento, sea por transform o por atributo y."""
    t = svgdoc.leer_atributo(svg, id_, "transform")
    if t and "translate(" in t:
        x, y = pose_de(svg, id_)
        nuevo = re.sub(r"translate\(\s*[-\d.]+[\s,]+[-\d.]+",
                       "translate(%s %.2f" % (x, y + delta), t, count=1)
        return svgdoc.fijar_atributo(svg, id_, "transform", nuevo)
    return svgdoc.fijar_atributo(svg, id_, "y", "%.2f" % (_numero(svg, id_, "y") + delta))


# ------------------------------------------------------------- dibujo de texto

def _nodo_texto(id_, apertura, x, y, contenido, size=None):
    """Rearma un <text> conservando sus atributos salvo pose y cuerpo.

    Se reescribe el nodo completo con un solo <tspan> en vez de conservar los
    tspan originales: Illustrator parte cada palabra en varios tspan con x
    manual por kerning, y al cambiar el contenido esas x quedan sin sentido.
    Se pierde el kerning fino del export; a ojo el resultado es identico.
    """
    ap = re.sub(r'\stransform="[^"]*"', "", apertura)
    ap = re.sub(r'\sstyle="[^"]*"', "", ap)
    ap = ap.rstrip()
    ap = ap[:-2].rstrip() if ap.endswith("/>") else ap[:-1].rstrip()
    estilo = ' style="font-size:%.2fpx"' % size if size else ""
    return ('%s transform="translate(%.4f %.4f)"%s><tspan x="0" y="0">%s</tspan></text>'
            % (ap, x, y, estilo, svgdoc.escapar(contenido)))


def _ajustar_pastilla(svg, cfg_pastilla, x_texto, ancho_texto):
    """Estira el rect que hace de fondo (o de subrayado) hasta cubrir el texto."""
    id_p = cfg_pastilla["id"]
    pad = float(cfg_pastilla.get("pad", 0.0))
    x0 = cfg_pastilla.get("x")
    x0 = float(x0) if x0 is not None else _numero(svg, id_p, "x")
    return svgdoc.fijar_atributo(
        svg, id_p, "width", "%.2f" % ((x_texto + ancho_texto + pad) - x0))


# ------------------------------------------------------------------ elementos

def _render_texto(svg, el, campos, reglas):
    id_ = el["id"]
    contenido = formatear(el["plantilla"], campos) if "plantilla" in el \
        else str(campos[el["campo"]])
    e = svgdoc.localizar(svg, id_)
    x, y = pose_de(svg, id_)
    size = float(el["size"]) if "size" in el else cuerpo_de(svg, id_, reglas)
    fuente = el["fuente"]

    max_ancho = el.get("max_ancho")
    if max_ancho:
        size = texto.cuerpo_para_caber(contenido, fuente, size, float(max_ancho))
        svg = svgdoc.reemplazar_elemento(
            svg, id_, _nodo_texto(id_, e["apertura"], x, y, contenido, size))
    else:
        svg = svgdoc.reemplazar_elemento(
            svg, id_, _nodo_texto(id_, e["apertura"], x, y, contenido))

    if "pastilla" in el:
        svg = _ajustar_pastilla(svg, el["pastilla"], x,
                                texto.ancho(contenido, fuente, size))
    return svg


def _render_centrado(svg, el, campos, reglas):
    """Texto centrado dentro de una caja, que se achica si no cabe.

    La caja se declara como [x0, x1] o se toma del rect indicado en "caja_id",
    que es lo comodo cuando la pastilla ya existe en el arte.
    """
    id_ = el["id"]
    contenido = formatear(el["plantilla"], campos) if "plantilla" in el \
        else str(campos[el["campo"]])
    e = svgdoc.localizar(svg, id_)
    _, y = pose_de(svg, id_)
    size = float(el["size"]) if "size" in el else cuerpo_de(svg, id_, reglas)
    fuente = el["fuente"]

    if "caja_id" in el:
        x0 = _numero(svg, el["caja_id"], "x")
        x1 = x0 + _numero(svg, el["caja_id"], "width")
    else:
        x0, x1 = [float(v) for v in el["caja"]]

    margen = float(el.get("margen", 0.0))
    disponible = (x1 - x0) - margen
    original = size
    w = texto.ancho(contenido, fuente, size)
    if w > disponible:
        size = disponible / w * size
        w = texto.ancho(contenido, fuente, size)

    x = x0 + ((x1 - x0) - w) / 2.0
    return svgdoc.reemplazar_elemento(
        svg, id_, _nodo_texto(id_, e["apertura"], x, y, contenido,
                              size if abs(size - original) > 0.01 else None))


def _render_titulo(svg, el, campos, reglas):
    """Titular con autoajuste, corte en varias lineas y arrastre del bloque.

    Cuando el titulo se parte, el bloque entero sube una interlinea por cada
    linea extra: el titulo crece hacia abajo, asi que sin subirlo invadiria lo
    que tiene debajo. Los elementos listados en "arrastra" (el prefijo y su
    subrayado, tipicamente) suben lo mismo para no despegarse del titulo.
    """
    id_ = el["id"]
    contenido = formatear(el["plantilla"], campos) if "plantilla" in el \
        else str(campos[el["campo"]])
    e = svgdoc.localizar(svg, id_)
    x, y = pose_de(svg, id_)
    size_base = float(el["size"]) if "size" in el else cuerpo_de(svg, id_, reglas)
    fuente = el["fuente"]

    lineas, size = texto.ajustar_titulo(
        contenido, fuente, size_base, float(el["max_ancho"]),
        min_escala=float(el.get("min_escala", 0.82)),
        max_lineas=int(el.get("max_lineas", 2)))

    interlinea = size * float(el.get("interlinea", 1.08))
    # "crece": "abajo" es el parrafo comun: la primera linea queda fija y las
    # demas bajan. Por defecto el titulo crece hacia arriba (ver docstring).
    desplazamiento = 0.0 if el.get("crece") == "abajo" else interlinea * (len(lineas) - 1)

    nodos = []
    for i, linea in enumerate(lineas):
        apertura = e["apertura"]
        if i:  # los ids deben ser unicos dentro del documento
            apertura = apertura.replace('id="%s"' % id_, 'id="%s-l%d"' % (id_, i + 1))
        nodos.append(_nodo_texto(id_, apertura, x,
                                 y - desplazamiento + i * interlinea, linea, size))
    svg = svgdoc.reemplazar_elemento(svg, id_, "".join(nodos))

    if desplazamiento:
        for otro in el.get("arrastra", []):
            svg = mover_y(svg, otro, -desplazamiento)

    return svg


def _render_repetido(svg, el, campos, reglas):
    """Serie de pastillas (los "badges"): centra las que se usan, borra el resto.

    Las pastillas no se redimensionan, se conservan tal como las dibujo el
    disenador; lo que se ajusta es la posicion del texto dentro de cada una.
    Las sobrantes se eliminan junto con su texto.
    """
    valores = campos.get(el["campo"]) or []
    if isinstance(valores, str):
        valores = [valores]
    fuente = el["fuente"]

    for i, slot in enumerate(el["slots"]):
        id_txt, id_rect = slot["texto_id"], slot.get("rect_id")
        if i >= len(valores):
            svg = svgdoc.eliminar_elemento(svg, id_txt, si_existe=True)
            if id_rect:
                svg = svgdoc.eliminar_elemento(svg, id_rect, si_existe=True)
            continue

        etiqueta = str(valores[i])
        e = svgdoc.localizar(svg, id_txt)
        _, y = pose_de(svg, id_txt)
        size = float(el["size"]) if "size" in el else cuerpo_de(svg, id_txt, reglas)

        if id_rect:
            rx = _numero(svg, id_rect, "x")
            rw = _numero(svg, id_rect, "width")
        else:
            rx, rw = float(slot["x"]), float(slot["ancho"])

        w = texto.ancho(etiqueta, fuente, size)
        if w > rw - float(el.get("margen", 0.0)):
            size = (rw - float(el.get("margen", 0.0))) / w * size
            w = texto.ancho(etiqueta, fuente, size)
            nodo = _nodo_texto(id_txt, e["apertura"], rx + (rw - w) / 2.0, y, etiqueta, size)
        else:
            nodo = _nodo_texto(id_txt, e["apertura"], rx + (rw - w) / 2.0, y, etiqueta)
        svg = svgdoc.reemplazar_elemento(svg, id_txt, nodo)

    return svg


RENDERERS = {
    "texto": _render_texto,
    "titulo": _render_titulo,
    "centrado": _render_centrado,
    "repetido": _render_repetido,
}


# -------------------------------------------------------------------- modelo

class Formato:
    """Un formato de salida (post, story, feed 4:5...) con su SVG y su binding."""

    def __init__(self, nombre, cfg, carpeta):
        self.nombre = nombre
        self.cfg = cfg
        self.carpeta = carpeta
        self.archivo = os.path.join(carpeta, cfg["archivo"])
        self.ancho = int(cfg["ancho"])
        self.alto = int(cfg["alto"])
        self.elementos = cfg.get("elementos", [])
        self.foto = cfg.get("foto", {})
        self.zonas = cfg.get("zonas", {})

    def leer_svg(self):
        with open(self.archivo, encoding="utf-8") as f:
            return f.read()

    def construir(self, campos):
        """Aplica una fila de datos sobre la plantilla y devuelve el SVG."""
        svg = self.leer_svg()
        reglas = estilos(svg)
        for el in self.elementos:
            fn = RENDERERS.get(el["tipo"])
            if fn is None:
                raise KeyError("Tipo de elemento desconocido: %r (usa uno de %s)"
                               % (el["tipo"], ", ".join(sorted(RENDERERS))))
            if el.get("campo") and el["campo"] not in campos and "plantilla" not in el:
                if el.get("opcional"):
                    continue
                raise KeyError("Falta el dato '%s' que pide el elemento id=\"%s\""
                               % (el["campo"], el.get("id", "?")))
            svg = fn(svg, el, campos, reglas)
        return svg


class Plantilla:
    def __init__(self, ruta):
        self.ruta = os.path.abspath(ruta)
        self.carpeta = os.path.dirname(self.ruta)
        with open(self.ruta, encoding="utf-8") as f:
            self.cfg = json.load(f)
        self.nombre = self.cfg.get("nombre", os.path.basename(self.carpeta))
        self.campos = self.cfg.get("campos", {})
        self.formatos = {
            k: Formato(k, v, self.carpeta)
            for k, v in self.cfg["formatos"].items()
        }

    def __getitem__(self, nombre):
        return self.formatos[nombre]

    def validar_fila(self, campos):
        """Devuelve la lista de problemas de una fila de datos (vacia si esta bien)."""
        faltan = [k for k, spec in self.campos.items()
                  if spec.get("requerido") and k not in campos]
        return ["falta el campo requerido '%s'" % k for k in faltan]


def cargar(ruta):
    if os.path.isdir(ruta):
        ruta = os.path.join(ruta, "plantilla.json")
    return Plantilla(ruta)
