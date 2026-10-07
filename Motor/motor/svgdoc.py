# -*- coding: utf-8 -*-
"""Manipulacion de SVG por `id`, no por clase CSS.

Por que esto existe
-------------------
La version original de este motor localizaba cada elemento por su clase CSS
mas su transform exacto: `<text class="cls-14" transform="translate(34.22 585.03)">`.
Funciona, pero Illustrator **renumera las clases en cada exportacion**. Si el
disenador vuelve a exportar la plantilla, `cls-14` pasa a ser otra cosa y todas
las piezas dejan de generarse -- sin un error claro, porque el regex
simplemente no encuentra nada.

Un `id` en cambio es estable: Illustrator exporta el nombre de la capa como
`id`, asi que si la capa se llama "m-nombre" el atributo sobrevive a
re-exportaciones, a cambios de color y a que se muevan los elementos.

El scanner es deliberadamente simple (no arma un DOM) porque las plantillas son
exportaciones de Illustrator, no SVG arbitrario: no traen CDATA, ni namespaces
raros, ni comentarios con `<` adentro. A cambio, conserva el archivo byte a
byte salvo donde se toca, que es justo lo que se necesita para no alterar el
arte.
"""
import re


class ElementoNoEncontrado(KeyError):
    def __init__(self, id_):
        super().__init__(id_)
        self.id = id_

    def __str__(self):
        return (
            "No encuentro el elemento id=\"%s\" en la plantilla.\n"
            "Causas habituales:\n"
            "  - la plantilla SVG no fue preparada: corre\n"
            "      python herramientas/preparar_plantilla.py <receta.json>\n"
            "  - el disenador renombro la capa en Illustrator\n"
            "  - el id esta escrito distinto en plantilla.json" % self.id)


def _fin_etiqueta_apertura(svg, inicio):
    """Devuelve el indice justo despues del '>' que cierra la etiqueta.

    Respeta las comillas porque un atributo puede contener '>' (pasa en los
    `d=` de paths y en los data: URI de las imagenes embebidas).
    """
    i, comilla = inicio, None
    while i < len(svg):
        c = svg[i]
        if comilla:
            if c == comilla:
                comilla = None
        elif c in "\"'":
            comilla = c
        elif c == ">":
            return i + 1
        i += 1
    raise ValueError("etiqueta sin cerrar desde el offset %d" % inicio)


def localizar(svg, id_):
    """Ubica el elemento con ese id.

    Devuelve un dict con:
      inicio, fin      -- offsets del elemento completo
      tag              -- nombre de etiqueta
      apertura         -- texto de la etiqueta de apertura
      inicio_interior, fin_interior -- offsets del contenido (None si es vacio)
    """
    m = re.search(r'\sid="%s"' % re.escape(id_), svg)
    if not m:
        raise ElementoNoEncontrado(id_)

    inicio = svg.rfind("<", 0, m.start())
    if inicio < 0:
        raise ElementoNoEncontrado(id_)

    fin_apertura = _fin_etiqueta_apertura(svg, inicio)
    apertura = svg[inicio:fin_apertura]
    tag = re.match(r"<([A-Za-z_][\w:.-]*)", apertura).group(1)

    if apertura.rstrip().endswith("/>"):
        return {"inicio": inicio, "fin": fin_apertura, "tag": tag,
                "apertura": apertura,
                "inicio_interior": None, "fin_interior": None}

    # Etiqueta con contenido: hay que contar anidamiento del mismo tag.
    abre = re.compile(r"<%s\b" % re.escape(tag))
    cierra = re.compile(r"</%s\s*>" % re.escape(tag))
    nivel, i = 1, fin_apertura
    while nivel:
        ma, mc = abre.search(svg, i), cierra.search(svg, i)
        if mc is None:
            raise ValueError("elemento <%s id=\"%s\"> sin cierre" % (tag, id_))
        if ma and ma.start() < mc.start():
            # Un self-closing del mismo tag no abre nivel.
            if not svg[ma.start():_fin_etiqueta_apertura(svg, ma.start())].rstrip().endswith("/>"):
                nivel += 1
            i = ma.end()
            continue
        nivel -= 1
        i = mc.end()

    return {"inicio": inicio, "fin": i, "tag": tag, "apertura": apertura,
            "inicio_interior": fin_apertura, "fin_interior": i - len(mc.group(0))}


def existe(svg, id_):
    return re.search(r'\sid="%s"' % re.escape(id_), svg) is not None


def reemplazar_elemento(svg, id_, nuevo):
    """Sustituye el elemento completo (etiqueta incluida) por `nuevo`."""
    e = localizar(svg, id_)
    return svg[:e["inicio"]] + nuevo + svg[e["fin"]:]


def reemplazar_interior(svg, id_, nuevo):
    """Sustituye solo el contenido, conservando la etiqueta y sus atributos.

    Si el elemento venia vacio (`<g id="x"/>`), lo convierte en un par
    abierto/cerrado para poder alojar el contenido.
    """
    e = localizar(svg, id_)
    if e["inicio_interior"] is None:
        apertura = e["apertura"].rstrip()
        apertura = apertura[:-2].rstrip() + ">"
        return (svg[:e["inicio"]] + apertura + nuevo + "</%s>" % e["tag"]
                + svg[e["fin"]:])
    return svg[:e["inicio_interior"]] + nuevo + svg[e["fin_interior"]:]


def eliminar_elemento(svg, id_, si_existe=False):
    """Borra el elemento. Con si_existe=True no falla si no esta."""
    if si_existe and not existe(svg, id_):
        return svg
    e = localizar(svg, id_)
    return svg[:e["inicio"]] + svg[e["fin"]:]


def leer_atributo(svg, id_, attr):
    e = localizar(svg, id_)
    m = re.search(r'\s%s="([^"]*)"' % re.escape(attr), e["apertura"])
    return m.group(1) if m else None


def fijar_atributo(svg, id_, attr, valor):
    """Escribe (o agrega) un atributo en la etiqueta de apertura."""
    e = localizar(svg, id_)
    apertura = e["apertura"]
    pat = re.compile(r'(\s%s=")([^"]*)(")' % re.escape(attr))
    if pat.search(apertura):
        nueva = pat.sub(lambda m: m.group(1) + str(valor) + m.group(3), apertura, count=1)
    else:
        cierre = "/>" if apertura.rstrip().endswith("/>") else ">"
        nueva = (apertura.rstrip()[:-len(cierre)].rstrip()
                 + ' %s="%s"' % (attr, valor) + cierre)
    fin_apertura = e["inicio"] + len(e["apertura"])
    return svg[:e["inicio"]] + nueva + svg[fin_apertura:]


def insertar_en_defs(svg, fragmento):
    """Agrega definiciones (degradados, clips) al bloque <defs>.

    Si la plantilla no trae <defs>, lo crea justo despues de la etiqueta <svg>.
    """
    if "</defs>" in svg:
        return svg.replace("</defs>", fragmento + "</defs>", 1)
    fin = _fin_etiqueta_apertura(svg, svg.index("<svg"))
    return svg[:fin] + "<defs>" + fragmento + "</defs>" + svg[fin:]


def antes_de_cierre(svg, fragmento):
    """Inserta un fragmento justo antes de </svg> (queda sobre todo lo demas)."""
    return svg.replace("</svg>", fragmento + "</svg>", 1)


def escapar(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
