#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de graficas de admision IPG 2027 — plantillas V.2.

Toma las plantillas SVG (Post 1080x1080 / Story 1080x1920) y reemplaza:
  - nombre de carrera (prefijo + nombre principal)
  - badges de tipo de titulo (1 a 3 pastillas)
  - porcentaje de beca
  - cuota mensual
  - pastilla de modalidad ("Estudia | 100% Online" / "Estudia | Sede Arauco")
Auto-ajusta el ancho del subrayado, el de la pastilla de modalidad y el
tamano del titulo.

QUE CAMBIO EN LA V.2 (22-09-2026) y por que importa para este codigo
--------------------------------------------------------------------
1. Las clases pasaron de `cls-N` a `stN`, y **el mismo numero significa cosas
   distintas en cada plantilla**: en el Post `.st22` es azul y `.st25` blanco;
   en el Story es al reves (`.st22` blanco, `.st24` azul). No se puede
   compartir una sola tabla de clases entre las dos.

2. Illustrator ya no exporta un `<text>` con varios `<tspan>`: exporta **un
   `<text>` por fragmento de kerning**, cada uno con su propio translate. El
   titulo "GESTION LOGISTICA" son nueve elementos. Por eso aqui no se busca
   "el" nodo de un campo sino el *run*: todos los `<text>` que comparten
   baseline (y, opcionalmente, un rango de x). Se reescribe el primero con el
   texto completo y se borran los demas. Borrar elementos `<text>` sueltos es
   seguro; borrar el tramo entre el primero y el ultimo no lo seria, porque
   los badges 1 y 2 comparten baseline pero viven en `<g>` distintos.

3. Los titulos pasaron de Montserrat Black a ExtraBold. Medir con Black da
   anchos ~1,2% mayores y descalibra el subrayado y el auto-fit.

4. Desaparecio la pastilla de sede del pie y aparecio la de modalidad sobre
   el prefijo. Como esta *encima* del titulo, cuando el nombre se parte en dos
   lineas hay que subirla junto con el prefijo y el subrayado — en la V.1 no
   habia nada arriba que mover.

5. El degradado superior ahora viene en la plantilla; ya no lo inyecta
   capa_fotos_ipg.py.
"""
import re, os, shutil
from fontTools.ttLib import TTFont

BASE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(BASE)
PLANTILLAS = os.path.join(REPO, "01-Plantillas")
POST_STORY = os.path.join(REPO, "04-Post-Story")

# Carpetas donde se busca Montserrat, en orden. IPG_FUENTES manda si existe.
_FDIRS = [d for d in (
    os.environ.get("IPG_FUENTES"),
    os.path.join(REPO, "fuentes"),
    os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Windows", "Fonts"),
    os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts"),
    os.path.expanduser("~/Library/Fonts"), "/Library/Fonts",
    os.path.expanduser("~/.local/share/fonts"), os.path.expanduser("~/.fonts"),
    "/usr/share/fonts", "/usr/local/share/fonts",
) if d]

def _buscar_fuente(nombre):
    for d in _FDIRS:
        for raiz, _, archivos in os.walk(d):
            if nombre in archivos:
                return os.path.join(raiz, nombre)
    return os.path.join(_FDIRS[0], nombre)   # el error de TTFont dirá cuál falta

FONTS = {
    "black":     _buscar_fuente("Montserrat-Black.otf"),
    "extrabold": _buscar_fuente("Montserrat-ExtraBold.otf"),
    "medium":    _buscar_fuente("Montserrat-Medium.otf"),
}

# Inkscape: variable INKSCAPE, luego el PATH, luego la ruta estándar de Windows.
INKSCAPE = (os.environ.get("INKSCAPE") or shutil.which("inkscape")
            or r"C:\Program Files\Inkscape\bin\inkscape.exe")
_cache = {}

def _font(kind):
    if kind not in _cache:
        f = TTFont(FONTS[kind])
        cmap = f.getBestCmap()
        hmtx = f["hmtx"]
        upem = f["head"].unitsPerEm
        _cache[kind] = (cmap, hmtx, upem, f.getGlyphOrder())
    return _cache[kind]

def text_width(s, kind, size):
    cmap, hmtx, upem, _ = _font(kind)
    total = 0
    for ch in s:
        g = cmap.get(ord(ch))
        if g is None:
            g = cmap.get(ord("?"))
        total += hmtx[g][0]
    return total * size / upem

def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

# ---------------------------------------------------------------- geometria
# Cada campo se localiza por su baseline (`y`) y, cuando varios campos la
# comparten, por un rango de x. Los valores salen de la plantilla V.2 medidos
# sobre el SVG, no estimados.
POST = {
    "file": os.path.join(PLANTILLAS, "Post-IPG 2027-Plantilla.svg"),
    "prefijo":  {"cls": "st12", "y": 527.4, "x": 34.2, "size": 53.0, "kind": "extrabold"},
    "nombre":   {"cls": "st21", "y": 605.6, "x": 34.2, "size": 68.1, "kind": "extrabold"},
    "badges":   {"cls": "st9", "size": 21.6, "kind": "extrabold",
                 "ys": [656.9, 656.9, 657.8],
                 "xs": [(0.0, 283.2), (283.2, 532.3), (532.3, None)],
                 "rects": [(34.2, 238.9), (283.2, 238.9), (532.3, 238.9)],
                 "pill_re": [r'<rect class="st22" x="34\.2" y="628\.7"[^>]*/>',
                             r'<rect class="st22" x="283\.2" y="628\.7"[^>]*/>',
                             r'<rect class="st22" x="532\.3" y="628\.7"[^>]*/>']},
    "beca":     {"cls": "st15", "y": 812.0, "x": 153.6, "size": 45.5, "kind": "extrabold"},
    "cuota":    {"cls": "st6", "y": 828.0, "x": 661.1, "size": 56.5, "kind": "extrabold",
                 "pill": (625.5, 949.9)},
    # Pastilla de modalidad: el chip azul ("Estudia") es fijo; el blanco se
    # redimensiona al texto y se solapa 19.4 px sobre el azul, que es como
    # viene dibujado en la plantilla.
    "modalidad": {"cls": "st18", "y": 463.3, "x": 190.4, "size": 28.8, "kind": "black",
                  "chip_re": r'<rect class="st25" x="159\.1" y="([\d.]+)" width="([\d.]+)"',
                  "chip_x": 159.1, "pad_izq": 31.3, "pad_der": 14.4,
                  "fijo_cls": "st2", "fijo_y": 462.4, "fijo_x": 51.2,
                  "fijo_re": r'<rect class="st22" x="35\.4" y="([\d.]+)"'},
    "underline_re": r'<rect class="st25" x="-104\.2" y="([\d.]+)" width="([\d.]+)"',
    "underline_x0": -104.2, "underline_pad": 29.9,
    "nombre_maxw": 1011.0,
}

STORY = {
    "file": os.path.join(PLANTILLAS, "Story-IPG 2027-Plantilla.svg"),
    "prefijo":  {"cls": "st15", "y": 811.9, "x": 55.9, "size": 61.3, "kind": "extrabold"},
    "nombre":   {"cls": "st21", "y": 902.3, "x": 55.9, "size": 78.7, "kind": "extrabold"},
    "badges":   {"cls": "st0", "size": 25.0, "kind": "extrabold",
                 "ys": [961.6, 961.6, 962.6],
                 "xs": [(0.0, 343.9), (343.9, 631.8), (631.8, None)],
                 "rects": [(55.9, 276.3), (343.9, 276.3), (631.8, 276.3)],
                 # En el Story los badges son <path> con los extremos
                 # completamente redondeados, no <rect>.
                 "pill_re": [r'<path class="st24" d="M81,929h226[^"]*"/>',
                             r'<path class="st24" d="M369,929h226[^"]*"/>',
                             r'<path class="st24" d="M656\.9,929h226[^"]*"/>']},
    "beca":     {"cls": "st1", "y": 1185.2, "x": 94.1635, "size": 55.5, "kind": "extrabold"},
    "cuota":    {"cls": "st2", "y": 1204.9, "x": 661.8549, "size": 69.0, "kind": "extrabold",
                 "pill": (618.5, 1014.6)},
    "modalidad": {"cls": "st6", "y": 735.8, "x": 244.8, "size": 34.0, "kind": "black",
                  "chip_re": r'<rect class="st22" x="207\.8" y="([\d.]+)" width="([\d.]+)"',
                  "chip_x": 207.8, "pad_izq": 37.0, "pad_der": 17.2,
                  "fijo_cls": "st5", "fijo_y": 734.8, "fijo_x": 80.3,
                  "fijo_re": r'<rect class="st24" x="61\.7" y="([\d.]+)"'},
    "underline_re": r'<rect class="st22" x="-104\.2" y="([\d.]+)" width="([\d.]+)"',
    "underline_x0": -104.2, "underline_pad": 34.4,
    "nombre_maxw": 968.0,
}

# --------------------------------------------------------------- utilidades
# El [^>]* final es deliberado: los nodos que este mismo modulo reescribe
# llevan un style="font-size:..." inline, y sin el no se volverian a encontrar.
RE_TEXT = re.compile(
    r'<text class="([^"]+)" transform="translate\(([^)]*)\)"[^>]*>.*?</text>', re.S)

def _fragmentos(svg):
    """Todos los <text> del SVG en orden de documento, con clase y posicion."""
    out = []
    for m in RE_TEXT.finditer(svg):
        xy = m.group(2).split()
        out.append({"a": m.start(), "b": m.end(), "cls": m.group(1),
                    "x": float(xy[0]), "y": float(xy[1]) if len(xy) > 1 else 0.0})
    return out


def run(svg, y, x0=None, x1=None, tol=0.5):
    """Fragmentos que componen un campo: mismo baseline y (opcional) rango de x.

    La tolerancia es estrecha a proposito. Illustrator deja 0,9 px de
    diferencia entre baselines que a ojo son la misma linea — los badges 1-2
    contra el 3, o "Estudia" contra la modalidad — y una tolerancia holgada
    los mezclaria en un solo run.
    """
    fr = [f for f in _fragmentos(svg)
          if abs(f["y"] - y) <= tol
          and (x0 is None or f["x"] >= x0 - 0.5)
          and (x1 is None or f["x"] < x1)]
    return sorted(fr, key=lambda f: f["a"])


def escribir(svg, fr, texto, cls, x, y, size=None):
    """Deja el texto completo en el primer fragmento y borra los demas.

    Se borra de atras hacia adelante para no invalidar los offsets, y nunca
    el tramo entre el primero y el ultimo: los fragmentos de un mismo campo
    pueden estar repartidos en varios <g>.
    """
    if not fr:
        raise SystemExit("Run vacio: %s @ y=%s" % (cls, y))
    for f in reversed(fr[1:]):
        svg = svg[:f["a"]] + svg[f["b"]:]
    style = ' style="font-size:%.2fpx"' % size if size else ''
    nodo = ('<text class="%s" transform="translate(%.4f %.4f)"%s>'
            '<tspan x="0" y="0">%s</tspan></text>') % (cls, x, y, style, esc(texto))
    f0 = fr[0]
    return svg[:f0["a"]] + nodo + svg[f0["b"]:]


def borrar(svg, fr):
    for f in reversed(fr):
        svg = svg[:f["a"]] + svg[f["b"]:]
    return svg


def set_grupo(svg, pattern, valores):
    """Reescribe grupos capturados de un mismo match. valores: {n: numero}."""
    m = re.search(pattern, svg)
    if not m:
        raise SystemExit("No encontre el elemento: " + pattern)
    for n in sorted(valores, reverse=True):
        svg = svg[:m.start(n)] + ("%.2f" % valores[n]) + svg[m.end(n):]
    return svg


def quitar(svg, pattern):
    m = re.search(pattern, svg)
    if not m:
        raise SystemExit("No encontre el elemento a borrar: " + pattern)
    return svg[:m.start()] + svg[m.end():]


def fmt_miles(n):
    return "$" + format(int(n), ",d").replace(",", ".")


def modalidad_de(d):
    """Texto del chip blanco de la pastilla de modalidad.

    La V.2 elimino la pastilla de sede del pie y la reemplazo por esta. Para
    no perder el dato —la campana genera una pieza por carrera+sede— el chip
    lleva la sede tal cual, salvo la virtual, que en la plantilla original
    viene rotulada "100% Online".
    """
    if d.get("modalidad"):
        return d["modalidad"]
    sede = d.get("sede", "")
    return "100% Online" if "online" in sede.lower() else sede

# ------------------------------------------------------------------ armado
def construir(cfg, d):
    svg = open(cfg["file"], encoding="utf-8").read()

    # --- 1. titulo: se resuelve primero porque define cuanto sube el bloque --
    n = cfg["nombre"]
    size = n["size"]
    nombre = d["nombre"]
    maxw = cfg["nombre_maxw"]
    lineas = [nombre]
    if text_width(nombre, n["kind"], size) > maxw:
        req = maxw / text_width(nombre, n["kind"], size) * size
        if req >= size * 0.82:
            size = req
        else:
            pal = nombre.split()
            mejor, dif = 1, 1e9
            for i in range(1, len(pal)):
                a = text_width(" ".join(pal[:i]), n["kind"], n["size"])
                b = text_width(" ".join(pal[i:]), n["kind"], n["size"])
                if abs(a - b) < dif:
                    dif, mejor = abs(a - b), i
            lineas = [" ".join(pal[:mejor]), " ".join(pal[mejor:])]
            anchos = [text_width(l, n["kind"], size) for l in lineas]
            if max(anchos) > maxw:
                size = maxw / max(anchos) * size

    interlinea = size * 1.08
    shift = interlinea if len(lineas) == 2 else 0.0

    fr = run(svg, n["y"])
    svg = borrar(svg, fr[1:])
    nodo = ""
    for i, l in enumerate(lineas):
        nodo += ('<text class="%s" transform="translate(%.4f %.4f)" style="font-size:%.2fpx">'
                 '<tspan x="0" y="0">%s</tspan></text>') % (
                     n["cls"], n["x"], n["y"] - shift + i * interlinea, size, esc(l))
    svg = svg[:fr[0]["a"]] + nodo + svg[fr[0]["b"]:]

    # --- 2. prefijo + subrayado -------------------------------------------
    p = cfg["prefijo"]
    svg = escribir(svg, run(svg, p["y"]), d["prefijo"], p["cls"], p["x"], p["y"] - shift)
    w = text_width(d["prefijo"], p["kind"], p["size"])
    m = re.search(cfg["underline_re"], svg)
    svg = set_grupo(svg, cfg["underline_re"], {
        1: float(m.group(1)) - shift,
        2: (p["x"] + w + cfg["underline_pad"]) - cfg["underline_x0"]})

    # --- 3. pastilla de modalidad -----------------------------------------
    # Va sobre el prefijo, asi que sube lo mismo que el. El chip azul es fijo
    # ("Estudia") y solo cambia de y; el blanco ademas se ajusta al texto.
    md = cfg["modalidad"]
    texto_mod = modalidad_de(d)
    m = re.search(md["fijo_re"], svg)
    y_chip = float(m.group(1)) - shift
    svg = set_grupo(svg, md["fijo_re"], {1: y_chip})
    svg = escribir(svg, run(svg, md["fijo_y"], x1=md["chip_x"]), "Estudia",
                   md["fijo_cls"], md["fijo_x"], md["fijo_y"] - shift)
    wm = text_width(texto_mod, md["kind"], md["size"])
    svg = set_grupo(svg, md["chip_re"], {
        1: y_chip,
        2: md["pad_izq"] + wm + md["pad_der"]})
    svg = escribir(svg, run(svg, md["y"], x0=md["chip_x"]), texto_mod,
                   md["cls"], md["chip_x"] + md["pad_izq"], md["y"] - shift)

    # --- 4. badges ---------------------------------------------------------
    b = cfg["badges"]
    for i in range(3):
        rx, rw = b["rects"][i]
        x0, x1 = b["xs"][i]
        fr = run(svg, b["ys"][i], x0=x0, x1=x1)
        if i < len(d["badges"]):
            etiqueta = d["badges"][i]
            tw = text_width(etiqueta, b["kind"], b["size"])
            svg = escribir(svg, fr, etiqueta, b["cls"],
                           rx + (rw - tw) / 2.0, b["ys"][i])
        else:
            svg = borrar(svg, fr)
            svg = quitar(svg, b["pill_re"][i])

    # --- 5. beca % ---------------------------------------------------------
    bb = cfg["beca"]
    svg = escribir(svg, run(svg, bb["y"]), "DE HASTA %d%%" % d["beca"],
                   bb["cls"], bb["x"], bb["y"])

    # --- 6. cuota (centrada en la pastilla) --------------------------------
    c = cfg["cuota"]
    txt = fmt_miles(d["cuota"])
    size_c = c["size"]
    p0, p1 = c["pill"]
    disp = (p1 - p0) - 40.0
    if text_width(txt, c["kind"], size_c) > disp:
        size_c = disp / text_width(txt, c["kind"], size_c) * size_c
    nx = p0 + ((p1 - p0) - text_width(txt, c["kind"], size_c)) / 2.0
    svg = escribir(svg, run(svg, c["y"]), txt, c["cls"], nx, c["y"],
                   size=(size_c if size_c != c["size"] else None))
    return svg


if __name__ == "__main__":
    import json, sys
    d = json.load(open(sys.argv[1], encoding="utf-8"))
    slug = d["slug"]
    out_dir = os.path.join(POST_STORY, slug)
    os.makedirs(out_dir, exist_ok=True)
    for cfg, tag in ((POST, "Post"), (STORY, "Story")):
        out = os.path.join(out_dir, "%s-IPG_2027-%s.svg" % (tag, slug))
        open(out, "w", encoding="utf-8").write(construir(cfg, d))
        print("ok", out)
