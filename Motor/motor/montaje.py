# -*- coding: utf-8 -*-
"""Montaje automatico de una marca: SVG exportado de Illustrator + Excel.

Por que existe
--------------
Pedirle al disenador que nombre cada capa `m-algo` casi nunca ocurre. Lo que si
llega siempre es el arte con un TEXTO DE EJEMPLO ("GESTION LOGISTICA", "Sede
Online", "$00.000") y un Excel con los datos. Ese texto de ejemplo ya dice que
capa es que dato: basta con buscarlo en las columnas del Excel.

Que resuelve solo
-----------------
  - que texto del arte corresponde a que columna (igual, o contenido: "DE
    HASTA 50%" -> "DE HASTA {beca}%");
  - como se comporta cada texto: pastilla que se estira, boton de ancho fijo,
    subrayado, parrafo de varias lineas, titular que se parte en dos;
  - columnas numeradas (badge_1, badge_2...) como una serie de pastillas;
  - la capa de foto: la imagen mas grande del arte;
  - las zonas seguras, APRENDIDAS de la foto de ejemplo del disenador: donde
    puso la cara es donde la quiere.

Lo que devuelve es un punto de partida revisable, no una verdad: el informe
dice que decidio y por que, y todo queda en plantilla.json para corregirlo.
"""
import csv
import html
import json
import os
import re
import tempfile
import unicodedata

from . import entorno, render, rostro, texto
from . import zonas as _zonas

# --------------------------------------------------------------- utilidades

def clave(s):
    """'Nombre Carrera' -> 'nombre_carrera'. Sin tildes ni simbolos."""
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return re.sub(r"[^a-z0-9]+", "_", s).strip("_") or "campo"


def _plano(s):
    """Texto comparable: sin entidades, espacios colapsados, minusculas.

    Se usa lower() y no casefold() porque conserva el largo del texto, y las
    posiciones de un calce se trasladan tal cual al texto original.
    """
    s = unicodedata.normalize("NFC", html.unescape(str(s)))
    s = s.replace("’", "'").replace(" ", " ")
    return re.sub(r"\s+", " ", s).strip()


def _miles(n):
    return format(int(n), ",d").replace(",", ".")


def _num(v):
    """Numero si el valor lo es (incluido '1234567' escrito como texto)."""
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return int(v) if float(v).is_integer() else v
    if isinstance(v, str) and re.fullmatch(r"-?\d+", v.strip()):
        return int(v.strip())
    return None


def _formas(v):
    """Como puede aparecer un valor en el arte: (texto, filtro)."""
    n = _num(v)
    if n is not None and isinstance(n, int):
        out = [(str(n), None)]
        if abs(n) >= 1000:
            out.append((_miles(n), "miles"))
        return out
    s = _plano(v).lower()
    return [(s, None)] if s else []


# ------------------------------------------------------------------- tabla

COLS_FOTO = ("foto", "imagen", "fotografia", "photo", "image", "archivo_foto")
COLS_SLUG = ("slug", "id", "codigo", "code")
COLS_SUJETO = ("sujeto",)


def leer_tabla(ruta):
    """Lee .xlsx o .csv. Devuelve (claves, nombres_originales, filas)."""
    ext = os.path.splitext(ruta)[1].lower()
    if ext in (".xlsx", ".xlsm"):
        import openpyxl
        wb = openpyxl.load_workbook(ruta, data_only=True, read_only=True)
        crudas = [list(r) for r in wb.worksheets[0].iter_rows(values_only=True)]
    else:
        with open(ruta, encoding="utf-8-sig", newline="") as f:
            muestra = f.read(4096)
            f.seek(0)
            dialecto = csv.Sniffer().sniff(muestra, delimiters=";,\t")
            crudas = list(csv.reader(f, dialecto))

    crudas = [r for r in crudas if any(c not in (None, "") for c in r)]
    if not crudas:
        raise ValueError("La tabla %s esta vacia" % ruta)
    nombres = [str(c).strip() if c is not None else "" for c in crudas[0]]
    claves, vistas = [], {}
    for n in nombres:
        k = clave(n) if n else "col"
        vistas[k] = vistas.get(k, 0) + 1
        claves.append(k if vistas[k] == 1 else "%s_%d" % (k, vistas[k]))

    filas = []
    for r in crudas[1:]:
        fila = {}
        for k, v in zip(claves, list(r) + [None] * (len(claves) - len(r))):
            if v is None:
                v = ""
            elif isinstance(v, float) and v.is_integer():
                v = int(v)
            elif isinstance(v, str):
                v = v.strip()
            fila[k] = v
        filas.append(fila)
    return claves, nombres, filas


# --------------------------------------------------------------- lectura SVG

_TEXT_RE = re.compile(r"<text\b([^>]*)>(.*?)</text>", re.S)
_TSPAN_RE = re.compile(r"<tspan\b([^>]*)>(.*?)</tspan>", re.S)
_TRANSLATE_RE = re.compile(r"^\s*translate\(\s*([-\d.eE]+)(?:[\s,]+([-\d.eE]+))?\s*\)\s*$")


def _attr(tag, nombre):
    m = re.search(r'\s%s="([^"]*)"' % re.escape(nombre), tag)
    return m.group(1) if m else None


def _f(v, defecto=0.0):
    try:
        return float(v)
    except (TypeError, ValueError):
        return defecto


def lienzo(svg):
    vb = _attr(re.search(r"<svg\b[^>]*>", svg).group(0), "viewBox")
    if vb:
        _, _, w, h = [float(x) for x in re.split(r"[\s,]+", vb.strip())]
        return w, h
    tag = re.search(r"<svg\b[^>]*>", svg).group(0)
    return _f(re.sub(r"[^\d.]", "", _attr(tag, "width") or "")), \
        _f(re.sub(r"[^\d.]", "", _attr(tag, "height") or ""))


def _props(tag, clases, reglas):
    """Propiedades efectivas: style inline > atributo > clases."""
    p = {}
    for c in clases:
        for k, v in reglas.get(c, {}).items():
            p.setdefault(k, v)
    for k in ("font-family", "font-size"):
        a = _attr(tag, k)
        if a:
            p[k] = a
    st = _attr(tag, "style") or ""
    for par in st.split(";"):
        if ":" in par:
            k, v = par.split(":", 1)
            p[k.strip()] = v.strip()
    return p


def textos(svg, reglas):
    """Todos los <text> del arte con posicion, lineas, fuente y cuerpo."""
    out = []
    for m in _TEXT_RE.finditer(svg):
        apertura = "<text" + m.group(1) + ">"
        interior = m.group(2)
        reg = {"inicio": m.start(), "fin_apertura": m.start() + len(apertura),
               "apertura": apertura, "problema": None}
        t = _attr(apertura, "transform") or ""
        mt = _TRANSLATE_RE.match(t) if t else None
        if t and not mt:
            reg["problema"] = "texto rotado o escalado (transform=%s)" % t[:40]
        x0 = float(mt.group(1)) if mt else _f(_attr(apertura, "x"))
        y0 = float(mt.group(2) or 0) if mt else _f(_attr(apertura, "y"))
        if not t and (_attr(apertura, "x") is not None):
            reg["problema"] = "texto posicionado con x/y (no es exportacion de Illustrator)"

        lineas, clases_tspan = [], []
        tspans = list(_TSPAN_RE.finditer(interior))
        if tspans:
            for ts in tspans:
                a = ts.group(1)
                contenido = html.unescape(re.sub(r"<[^>]+>", "", ts.group(2)))
                dy = _f(_attr(a, "y"))
                if not clases_tspan:
                    clases_tspan = (_attr(a, "class") or "").split()
                if lineas and abs(lineas[-1][0] - dy) < 0.5:
                    lineas[-1][1] += contenido
                else:
                    lineas.append([dy, contenido])
        else:
            lineas = [[0.0, html.unescape(re.sub(r"<[^>]+>", "", interior))]]
        lineas = [(dy, re.sub(r"\s+", " ", s).strip()) for dy, s in lineas]
        lineas = [l for l in lineas if l[1]]
        if not lineas:
            continue

        clases = (_attr(apertura, "class") or "").split()
        props = _props(apertura, clases + clases_tspan, reglas)
        familia = (props.get("font-family") or "").split(",")[0].strip().strip("'\"")
        size = _f(re.sub(r"[^\d.]", "", props.get("font-size", "")), 0.0)
        if not size and not reg["problema"]:
            reg["problema"] = "sin cuerpo tipografico legible"

        # Si la familia viene solo en la clase de un tspan, al reescribir el
        # nodo se perderia: hay que subir esa clase al <text>.
        propias = _props(apertura, clases, reglas)
        reg["clase_extra"] = [c for c in clases_tspan if c not in clases] \
            if "font-family" not in propias else []

        reg.update(x=x0, y=y0, lineas=lineas, familia=familia, size=size,
                   texto=" ".join(s for _, s in lineas))
        out.append(reg)
    return out


def rects(svg):
    out = []
    for m in re.finditer(r"<rect\b[^>]*?/?>", svg):
        tag = m.group(0)
        if _attr(tag, "transform"):
            continue
        out.append({"inicio": m.start(), "fin": m.end(), "tag": tag,
                    "x": _f(_attr(tag, "x")), "y": _f(_attr(tag, "y")),
                    "w": _f(_attr(tag, "width")), "h": _f(_attr(tag, "height")),
                    "rx": _f(_attr(tag, "rx"))})
    return out


def imagenes(svg):
    out = []
    for m in re.finditer(r"<image\b[^>]*?(?:/>|>.*?</image>)", svg, re.S):
        apertura = re.match(r"<image\b[^>]*?/?>", m.group(0)).group(0)
        w, h = _f(_attr(apertura, "width")), _f(_attr(apertura, "height"))
        t = _attr(apertura, "transform") or ""
        esc = 1.0
        ms = re.search(r"scale\(\s*([-\d.eE]+)(?:[\s,]+([-\d.eE]+))?", t)
        mm = re.search(r"matrix\(\s*([-\d.eE]+)[\s,]+[-\d.eE]+[\s,]+[-\d.eE]+[\s,]+([-\d.eE]+)", t)
        if ms:
            esc = abs(float(ms.group(1)) * float(ms.group(2) or ms.group(1)))
        elif mm:
            esc = abs(float(mm.group(1)) * float(mm.group(2)))
        out.append({"inicio": m.start(), "fin": m.end(), "area": w * h * esc})
    return out


# ------------------------------------------------------------------ calce

def _grupos(claves):
    """Columnas numeradas: badge_1, badge_2 -> {'badge': [badge_1, badge_2]}."""
    g = {}
    for k in claves:
        m = re.match(r"^(.+?)_?(\d+)$", k)
        if m:
            g.setdefault(m.group(1), []).append((int(m.group(2)), k))
    return {b: [k for _, k in sorted(v)] for b, v in g.items() if len(v) >= 2}


def _indice(claves, filas, excluir):
    """columna -> {forma_normalizada: filtro} con todos los valores de la tabla."""
    idx = {}
    for k in claves:
        if k in excluir:
            continue
        formas = {}
        for f in filas:
            for s, filtro in _formas(f.get(k, "")):
                formas.setdefault(s, filtro)
        idx[k] = formas
    return idx


def calzar(reg, idx, nombres_por_clave, manual):
    """Busca a que columna(s) corresponde un texto del arte, por su VALOR.

    Devuelve ("campo", col) si el texto ES el valor, ("plantilla", patron) si
    lo CONTIENE, o None si es texto fijo del arte.
    """
    original = _plano(reg["texto"])
    bajo = original.lower()

    if bajo in manual:
        destino = manual[bajo]
        return ("plantilla", destino) if "{" in destino else ("campo", clave(destino))

    exactas = [k for k, formas in idx.items() if bajo in formas and formas[bajo] is None]
    if exactas:
        return ("campo", exactas[0])

    calces = []
    for k, formas in idx.items():
        for s, filtro in formas.items():
            es_num = bool(re.fullmatch(r"-?[\d.]+", s))
            if not es_num and len(s) < 3:
                continue
            borde = r"(?<![\d.,])%s(?![\d.,])" if es_num else r"(?<!\w)%s(?!\w)"
            for m in re.finditer(borde % re.escape(s), bajo):
                calces.append((m.end() - m.start(), m.start(), m.end(), k, filtro))
    if not calces:
        return None

    elegidos = []
    for largo, a, b, k, filtro in sorted(calces, key=lambda c: (-c[0], c[1])):
        if all(b <= x[0] or a >= x[1] for x in elegidos):
            elegidos.append((a, b, k, filtro))
    elegidos.sort()
    if len(elegidos) == 1 and elegidos[0][:2] == (0, len(bajo)) and not elegidos[0][3]:
        return ("campo", elegidos[0][2])

    patron, pos = "", 0
    for a, b, k, filtro in elegidos:
        patron += original[pos:a] + "{%s%s}" % (k, ":" + filtro if filtro else "")
        pos = b
    return ("plantilla", patron + original[pos:])


def rescatar(reg, libres, idx, nombres_por_clave, filas):
    """Segunda pasada, solo para columnas que el arte no uso por valor.

    El texto de ejemplo del disenador no siempre esta en el Excel ("$00.000"
    cuando ninguna cuota vale 78000). Se reconoce por FORMA:
      - un numero del arte cuya magnitud cae en el rango de una columna
        numerica libre (y solo de una);
      - un marcador con el nombre de la columna: "NOMBRE", "{nombre}", "[Sede]".
    Se reporta como calce por forma, para revisarlo.
    """
    original = _plano(reg["texto"])
    bajo = original.lower()
    marcador = re.sub(r"^[\[{<(]\s*|\s*[\]}>)]$", "", bajo)
    for k in libres:
        if marcador and (marcador == nombres_por_clave[k].lower() or marcador == k):
            return ("campo", k), "marcador con el nombre de la columna"

    for m in re.finditer(r"(?<![\d.,])(\d{1,3}(?:\.\d{3})+|\d+)(?![\d.,])", original):
        n = int(m.group(1).replace(".", ""))
        candidatas = []
        for k in libres:
            nums = [_num(f.get(k)) for f in filas]
            nums = [x for x in nums if isinstance(x, int)]
            if nums and min(nums) / 2 <= n <= max(nums) * 2:
                candidatas.append(k)
        if len(candidatas) == 1:
            k = candidatas[0]
            filtro = ":miles" if "." in m.group(1) else ""
            patron = original[:m.start()] + "{%s%s}" % (k, filtro) + original[m.end():]
            if patron == "{%s}" % k:
                return ("campo", k), "numero del ejemplo en el rango de la columna"
            return ("plantilla", patron), "numero del ejemplo en el rango de la columna"
    return None, None


# ----------------------------------------------------------- comportamiento

def _ancho(txt, fuente, size, avisos):
    try:
        return texto.ancho(txt, fuente, size)
    except entorno.EntornoIncompleto:
        avisos.add("falta la fuente %s: copia su archivo a fuentes/ (se estima el ancho)" % fuente)
        return 0.56 * size * len(txt)


def _cap(fuente, size):
    try:
        return texto.alto_mayusculas(fuente, size)
    except entorno.EntornoIncompleto:
        return 0.72 * size


def _contenedor(reg, cajas, W, H):
    """El rect mas chico que envuelve al texto (pastilla o boton)."""
    x0, x1 = reg["x"], reg["x"] + reg["ancho"]
    y1 = reg["y"]
    y0 = y1 - reg["cap"]
    candidatos = [r for r in cajas
                  if r["x"] - 2 <= x0 and x1 <= r["x"] + r["w"] + 2
                  and r["y"] - 2 <= y0 and y1 <= r["y"] + r["h"] + 2
                  and r["w"] * r["h"] < 0.3 * W * H]
    return min(candidatos, key=lambda r: r["w"] * r["h"]) if candidatos else None


def _eje_comun(reg, regs):
    """Otro texto, justo arriba o abajo, centrado en el mismo eje.

    Si dos textos apilados comparten el centro pero no el borde izquierdo, el
    disenador los centro (tipico: "Cuotas desde" sobre "$00.000" en un recuadro
    que es un trazado, no un rect). El dato debe quedar centrado en ese eje.
    """
    c = reg["x"] + reg["ancho"] / 2
    for o in regs:
        if o is reg or o.get("problema") or "ancho" not in o or len(o["lineas"]) > 1:
            continue
        if abs(o["y"] - reg["y"]) > 2.5 * max(reg["size"], o["size"]) or o["y"] == reg["y"]:
            continue
        if abs(o["x"] + o["ancho"] / 2 - c) <= 4 and abs(o["x"] - reg["x"]) > 4:
            return o
    return None


def _subrayado(reg, cajas):
    """Rect delgado justo bajo la linea base que termina donde termina el texto."""
    s = reg["size"]
    fin = reg["x"] + reg["ancho"]
    for r in cajas:
        if (r["h"] <= 0.2 * s and 0 <= r["y"] - reg["y"] <= 0.5 * s
                and r["x"] < fin and r["x"] + r["w"] > reg["x"]
                and abs((r["x"] + r["w"]) - fin) <= 1.5 * s):
            return r
    return None


# ------------------------------------------------------------------ zonas

def _render(svg, W, H):
    tmp = tempfile.mktemp(suffix=".png")
    render.cadena_a_png(svg, tmp, W, H)
    return tmp


def _banda_logo(svg_arte, W, H):
    """Primera banda de tinta desde arriba (logo), sobre el arte sin foto."""
    png = _render(svg_arte, W, H)
    try:
        filas, w, h = _zonas._filas_con_tinta(png)
    finally:
        os.remove(png)
    y0 = next((i for i, f in enumerate(filas) if f), None)
    if y0 is None:
        return None
    y1, hueco = y0, 0
    for i in range(y0, h):
        if filas[i]:
            y1, hueco = i, 0
        else:
            hueco += 1
            if hueco > 12:
                break
    banda = [f for f in filas[y0:y1 + 1] if f]
    return [min(f[0] for f in banda), y0, max(f[1] for f in banda), y1]


def _rostro_en_imagen(svg, carpeta, W, H):
    """Mide la cara sobre la foto de ejemplo incrustada, a resolucion completa,
    y la lleva a coordenadas del lienzo con el transform de la imagen.

    Es mas fiable que medir la pieza renderizada: ahi la cara esta recortada y
    bajo el degradado, que es justo donde los detectores fallan.
    """
    import base64
    fotos = sorted(imagenes(svg), key=lambda i: -i["area"])
    if not fotos:
        return None
    tag = re.match(r"<image\b[^>]*?/?>", svg[fotos[0]["inicio"]:fotos[0]["fin"]]).group(0)
    href = _attr(tag, "xlink:href") or _attr(tag, "href") or ""
    tmp = tempfile.mktemp(suffix=".img")
    if href.startswith("data:"):
        with open(tmp, "wb") as f:
            f.write(base64.b64decode(href.split(",", 1)[1]))
        ruta = tmp
    else:
        ruta = os.path.join(carpeta, href)
        if not os.path.exists(ruta):
            return None
    try:
        m = rostro.medir(ruta)
    except Exception:
        return None
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)

    w, h = _f(_attr(tag, "width")), _f(_attr(tag, "height"))
    ix, iy = _f(_attr(tag, "x")), _f(_attr(tag, "y"))
    t = _attr(tag, "transform") or ""
    a, d, e, f_ = 1.0, 1.0, 0.0, 0.0
    mm = re.search(r"matrix\(([^)]*)\)", t)
    if mm:
        v = [float(x) for x in re.split(r"[\s,]+", mm.group(1).strip())]
        if abs(v[1]) > 1e-6 or abs(v[2]) > 1e-6:
            return None                        # imagen rotada: no se traslada
        a, d, e, f_ = v[0], v[3], v[4], v[5]
    else:
        mt = re.search(r"translate\(\s*([-\d.eE]+)(?:[\s,]+([-\d.eE]+))?", t)
        ms = re.search(r"scale\(\s*([-\d.eE]+)(?:[\s,]+([-\d.eE]+))?", t)
        if mt:
            e, f_ = float(mt.group(1)), float(mt.group(2) or 0)
        if ms:
            a = float(ms.group(1))
            d = float(ms.group(2) or ms.group(1))
    X = lambda fx: e + a * (ix + fx * w)
    Y = lambda fy: f_ + d * (iy + fy * h)
    cara = dict(m, pelo=Y(m["pelo"]) / H, menton=Y(m["menton"]) / H, cara_x=X(m["cara_x"]) / W)
    return cara


def _plausible(cara, W, H, logo):
    """Descarta detecciones imposibles en una pieza: fuera del lienzo, bajo el
    logo o diminutas. Con el detector Haar sobre fotos oscuras pasa seguido."""
    if cara is None:
        return False
    if not (0.02 <= cara["cara_x"] <= 0.98 and 0 <= cara["pelo"] < cara["menton"] <= 1.05):
        return False
    if (cara["menton"] - cara["pelo"]) < 0.04:
        return False
    centro_y = (cara["pelo"] + cara["menton"]) / 2 * H
    if logo and centro_y <= logo[3] and logo[0] <= cara["cara_x"] * W <= logo[2]:
        return False
    return True


def _rostro_ejemplo(svg_original, W, H, carpeta=".", logo=None):
    """Donde puso el disenador la cara: primero en la pieza de ejemplo
    renderizada (lo que el ve), si no en la foto incrustada."""
    png = _render(svg_original, W, H)
    try:
        cara = rostro.medir(png)
    except rostro.SinRostro:
        cara = None
    finally:
        os.remove(png)
    if _plausible(cara, W, H, logo):
        return cara
    cara = _rostro_en_imagen(svg_original, carpeta, W, H)
    return cara if _plausible(cara, W, H, logo) else None


def _hueco_mayor(regs, cajas, logo, W, H, celda=20):
    """El rectangulo libre mas grande del lienzo: sin texto, logo ni botones.

    Es donde un disenador pondria a la persona cuando no hay ejemplo del que
    aprenderlo. Se pide un minimo de alto y ancho para que quepa una cabeza.
    """
    cols, filas = int(W // celda) + 1, int(H // celda) + 1
    ocupado = [[False] * cols for _ in range(filas)]

    def marcar(x0, y0, x1, y1):
        for fy in range(max(0, int(y0 // celda)), min(filas, int(y1 // celda) + 1)):
            for fx in range(max(0, int(x0 // celda)), min(cols, int(x1 // celda) + 1)):
                ocupado[fy][fx] = True

    if logo:
        marcar(0, 0, W, logo[3])   # la cabeza va bajo el logo, nunca a su lado ni encima
    for r in regs:
        if "techo" in r:
            fondo = r["y"] + r["lineas"][-1][0] + 0.25 * r["size"]
            marcar(r["x"], r["techo"], r["x"] + r["ancho"], fondo)
    for c in cajas:
        if c["w"] * c["h"] < 0.3 * W * H and c["h"] > 4:
            marcar(c["x"], c["y"], c["x"] + c["w"], c["y"] + c["h"])

    # Rectangulos maximos sobre histograma, fila por fila. Gana el mas
    # "cuadrado" (mayor lado menor): una cabeza necesita alto Y ancho, y una
    # franja larga y angosta pegada al borde no sirve aunque tenga mas area.
    mejor, alturas = ((0, 0), (0, 0, W, H)), [0] * cols
    for fy in range(filas):
        alturas = [0 if ocupado[fy][fx] else alturas[fx] + 1 for fx in range(cols)]
        pila = []
        for fx in range(cols + 1):
            h = alturas[fx] if fx < cols else 0
            inicio = fx
            while pila and pila[-1][1] >= h:
                inicio, alto = pila.pop()
                ancho = fx - inicio
                nota = (min(alto, ancho), alto * ancho)
                if nota > mejor[0]:
                    mejor = (nota, (inicio * celda, (fy - alto + 1) * celda,
                                    min(W, fx * celda), min(H, (fy + 1) * celda)))
            pila.append((inicio, h))
    return tuple(int(v) for v in mejor[1])


def aprender_zonas(svg_original, svg_arte, regs, W, H, avisos, carpeta=".", cajas=()):
    zonas = {"ancla": 1}
    logo = _banda_logo(svg_arte, W, H)
    if logo and logo[3] < 0.6 * H:
        m = int(W * 0.02)
        zonas["logo"] = [max(0, logo[0] - m), max(0, logo[1] - m),
                         min(int(W), logo[2] + m), min(int(H), logo[3] + m)]

    cara = _rostro_ejemplo(svg_original, W, H, carpeta, zonas.get("logo")) if svg_original else None
    if cara is None:
        hueco = _hueco_mayor(regs, cajas, zonas.get("logo"), W, H)
        x0, y0, x1, y1 = hueco
        avisos.add("no encontre una cara fiable en el ejemplo: la persona va al hueco mas grande "
                   "que deja el diseno (x %d-%d, y %d-%d). Revisalo con `generar --zonas`"
                   % (x0, x1, y0, y1))
        c, mitad = (x0 + x1) / 2.0, (x1 - x0) * 0.25
        zonas.update(pelo_min=int(y0 + 10), titulo=int(y1),
                     aire={"1": int(min(60, (y1 - y0) * 0.08)), "2": int(min(45, (y1 - y0) * 0.06))},
                     silueta=[int(c - mitad), int(c + mitad)], rostros=[int(y0), int(y1)])
        if y1 < H:
            zonas["texto_y"] = int(y1)
        return zonas, None

    pelo, menton = cara["pelo"] * H, cara["menton"] * H
    cx = cara["cara_x"] * W
    medio_ancho = max((menton - pelo) * 0.45, W * 0.05)

    debajo = [r for r in regs
              if "techo" in r and r["techo"] >= menton - 5
              and r["x"] < cx + medio_ancho and r["x"] + r["ancho"] > cx - medio_ancho]
    techo = min((r["techo"] for r in debajo), default=float(H))
    bloque = [r["id"] for r in debajo if r.get("id") and r.get("mapeado")
              and abs(r["techo"] - techo) < 2]

    tope_logo = zonas["logo"][3] + 10 if "logo" in zonas else pelo - 10
    aire = max(10.0, min(80.0, (techo - menton) * 0.8))
    zonas.update(
        pelo_min=int(max(0, min(tope_logo, pelo - 2))),
        titulo=int(techo),
        aire={"1": int(aire), "2": int(aire * 0.75)},
        silueta=[int(max(0, cx - W * 0.12)), int(min(W, cx + W * 0.12))],
        rostros=[int(pelo), int(techo)],
    )
    if techo < H:
        zonas["texto_y"] = int(techo)
    if bloque:
        zonas["bloque_titulo"] = bloque
    return zonas, cara


# ---------------------------------------------------------------- montaje

def _poner_id(tag, id_):
    if re.search(r'\sid="', tag):
        return re.sub(r'\sid="[^"]*"', ' id="%s"' % id_, tag, count=1)
    cierre = "/>" if tag.rstrip().endswith("/>") else ">"
    return tag.rstrip()[:-len(cierre)].rstrip() + ' id="%s"' % id_ + cierre


def montar_formato(nombre, ruta_svg, claves, nombres, filas, manual=None):
    """Analiza un SVG contra la tabla. Devuelve (svg_preparado, cfg_formato, informe)."""
    with open(ruta_svg, encoding="utf-8") as f:
        svg = f.read()
    W, H = lienzo(svg)
    reglas = _estilos(svg)
    avisos, informe = set(), []

    especiales = set(COLS_FOTO + COLS_SLUG + COLS_SUJETO)
    grupos = _grupos([k for k in claves if k not in especiales])
    en_grupo = {k: b for b, ks in grupos.items() for k in ks}
    idx = _indice(claves, filas, especiales)
    nombres_por_clave = dict(zip(claves, nombres))
    manual = {_plano(t).lower(): clave(c) for t, c in (manual or {}).items()}

    regs = textos(svg, reglas)
    cajas = rects(svg)
    for r in regs:
        if r["problema"]:
            continue
        r["ancho"] = max(_ancho(s, r["familia"], r["size"], avisos) for _, s in r["lineas"])
        r["cap"] = _cap(r["familia"], r["size"])
        r["techo"] = r["y"] + r["lineas"][0][0] - r["cap"]

    usados, ediciones, elementos = set(), [], []

    def nuevo_id(base):
        base = "m-" + base.replace("_", "-")
        i, id_ = 1, base
        while id_ in usados or ('id="%s"' % id_) in svg:
            i += 1
            id_ = "%s-%d" % (base, i)
        usados.add(id_)
        return id_

    # ---- 1. calce de cada texto contra la tabla
    for r in regs:
        if r["problema"]:
            if re.search(r"\w", r.get("texto", "") or ""):
                informe.append(("omitido", r.get("texto", "?"), r["problema"]))
            continue
        c = calzar(r, idx, nombres_por_clave, manual)
        r["calce"] = c
        r["mapeado"] = c is not None

    def _cols(c):
        return {c[1]} if c[0] == "campo" else set(re.findall(r"\{(\w+)", c[1]))

    usadas = set()
    for r in regs:
        if r.get("calce"):
            usadas |= _cols(r["calce"])
    usadas |= {k for b, ks in grupos.items() if usadas & set(ks) for k in ks}
    for r in regs:
        if r["problema"] or r.get("calce"):
            continue
        libres = [k for k in idx if k not in usadas]
        c, motivo = rescatar(r, libres, idx, nombres_por_clave, filas)
        if c:
            r["calce"], r["mapeado"], r["motivo"] = c, True, motivo
            usadas |= _cols(c)

    # ---- 2. series (badge_1, badge_2...) -> un elemento "repetido"
    for base, cols in grupos.items():
        miembros = [r for r in regs if r.get("calce") and r["calce"][0] == "campo"
                    and r["calce"][1] in cols and len(r["lineas"]) == 1]
        if len(miembros) < 2:
            continue
        slots = []
        for r in sorted(miembros, key=lambda r: (round(r["y"] / 10), r["x"])):
            r["id"] = nuevo_id(base)
            caja = _contenedor(r, cajas, W, H)
            slot = {"texto_id": r["id"]}
            if caja:
                caja.setdefault("id", nuevo_id(base + "-caja"))
                slot["rect_id"] = caja["id"]
            else:
                slot.update(x=round(r["x"], 2), ancho=round(r["ancho"], 2))
            slots.append(slot)
            r["en_serie"] = base
        elementos.append({"tipo": "repetido", "campo": base, "fuente": miembros[0]["familia"],
                          "slots": slots})
        informe.append(("serie", " / ".join(r["texto"] for r in miembros),
                        "%s (%d pastillas, columnas %s)" % (base, len(slots), ", ".join(cols))))

    # ---- 3. comportamiento de cada texto mapeado
    mapeados = [r for r in regs if r.get("calce") and not r.get("en_serie")]
    sueltos = [r for r in mapeados if len(r["lineas"]) == 1]
    # El titular es el texto de PALABRAS mas grande (un precio grande no lo es),
    # y solo si destaca sobre el resto.
    palabras = [r for r in sueltos if re.search(r"[^\W\d_]{3}", r["texto"])]
    titular = max(palabras, key=lambda r: r["size"]) if palabras else None
    if titular and len(sueltos) > 1:
        otros = sorted(r["size"] for r in sueltos if r is not titular)
        if titular["size"] < 1.15 * otros[len(otros) // 2]:
            titular = None

    por_id = {}
    # El titular al final: los elementos que arrastra ya tienen su id definitivo.
    for r in sorted(mapeados, key=lambda r: r is titular):
        tipo_calce, valor = r["calce"]
        base = valor if tipo_calce == "campo" else clave(re.findall(r"\{(\w+)", valor)[0])
        if tipo_calce == "campo" and valor in en_grupo:
            base = valor
        r["id"] = nuevo_id(base)
        el = {"id": r["id"], "fuente": r["familia"], "size": round(r["size"], 2)}
        el.update({"campo": valor} if tipo_calce == "campo" else {"plantilla": valor})
        margen_lat = max(0.0, min(r["x"], 60.0))
        libre = W - r["x"] - margen_lat

        if len(r["lineas"]) > 1:
            difs = [b[0] - a[0] for a, b in zip(r["lineas"], r["lineas"][1:])]
            el.update(tipo="titulo", crece="abajo", max_lineas=len(r["lineas"]),
                      max_ancho=round(r["ancho"] * 1.05, 1), min_escala=0.82,
                      interlinea=round(sum(difs) / len(difs) / r["size"], 3))
            como = "parrafo de %d lineas, crece hacia abajo" % len(r["lineas"])
        else:
            caja = _contenedor(r, cajas, W, H)
            sub = None if caja else _subrayado(r, cajas)
            if caja:
                izq = r["x"] - caja["x"]
                der = caja["x"] + caja["w"] - (r["x"] + r["ancho"])
                caja.setdefault("id", nuevo_id(base + "-caja"))
                centrado = abs(izq - der) <= max(0.2 * (izq + der), 4)
                # Texto corrido a un lado (hay un icono) o pastilla ajustada al
                # texto: la pastilla se estira. Texto centrado con holgura: boton.
                if not centrado or izq + der < 1.2 * caja["h"]:
                    el.update(tipo="texto", pastilla={"id": caja["id"], "pad": round(max(der, 0), 2)},
                              max_ancho=round(max(r["ancho"], libre - max(der, 0)), 1))
                    como = "pastilla que se estira con el texto"
                else:
                    el.update(tipo="centrado", caja_id=caja["id"],
                              margen=round(min(izq + der, 0.12 * caja["w"]), 1))
                    como = "centrado en un boton de ancho fijo"
            elif sub:
                sub.setdefault("id", nuevo_id(base + "-subrayado"))
                el.update(tipo="texto", max_ancho=round(max(r["ancho"], libre), 1),
                          pastilla={"id": sub["id"],
                                    "pad": round(sub["x"] + sub["w"] - (r["x"] + r["ancho"]), 2)})
                como = "texto con subrayado que se estira"
            elif r is titular:
                arr = []
                for o in regs + cajas:
                    if o is r:
                        continue
                    if "lineas" in o:
                        if o.get("problema") or o.get("en_serie"):
                            continue
                        top, bot = o["techo"], o["y"]
                        x0, x1 = o["x"], o["x"] + o["ancho"]
                    else:
                        top, bot, x0, x1 = o["y"], o["y"] + o["h"], o["x"], o["x"] + o["w"]
                        if o["w"] * o["h"] > 0.3 * W * H:
                            continue
                    if (r["techo"] - 2.2 * r["size"] <= top and bot <= r["techo"] + 2
                            and x0 < r["x"] + libre and x1 > r["x"]):
                        o.setdefault("id", nuevo_id("arrastra"))
                        arr.append(o["id"])
                el.update(tipo="titulo", max_ancho=round(max(r["ancho"], libre), 1),
                          min_escala=0.82, interlinea=1.08, max_lineas=2)
                if arr:
                    el["arrastra"] = arr
                como = "titular: se achica y si no cabe se parte en 2 lineas hacia arriba"
            elif abs(r["x"] + r["ancho"] / 2 - W / 2) <= 0.015 * W and r["x"] > 0.05 * W:
                m = min(r["x"], W - r["x"] - r["ancho"], 0.08 * W)
                el.update(tipo="centrado", caja=[round(m, 2), round(W - m, 2)], margen=0)
                como = "centrado en el lienzo"
            elif _eje_comun(r, regs):
                vecino = _eje_comun(r, regs)
                c = r["x"] + r["ancho"] / 2
                mitad = min(max(r["ancho"], vecino["ancho"]) / 2 + 0.05 * W, c, W - c)
                el.update(tipo="centrado", caja=[round(c - mitad, 2), round(c + mitad, 2)], margen=0)
                como = "centrado sobre el eje de \"%s\"" % vecino["texto"][:24]
            else:
                el.update(tipo="texto", max_ancho=round(max(r["ancho"], libre), 1))
                como = "texto que se achica si no cabe"
        por_id[r["id"]] = el
        informe.append(("mapeado" if not r.get("motivo") else "REVISAR", r["texto"], "%s -> %s%s" % (
            "{%s}" % valor if tipo_calce == "campo" else valor, como,
            " [calce por forma: %s]" % r["motivo"] if r.get("motivo") else "")))

    # Orden: lo que arrastra el titular va antes que el titular.
    arrastrados = {a for el in por_id.values() for a in el.get("arrastra", [])}
    orden = sorted(por_id.values(), key=lambda el: (el["id"] not in arrastrados,
                                                    el.get("arrastra") is not None))
    elementos = orden + elementos

    no_usadas = [nombres_por_clave[k] for k in claves
                 if k not in especiales
                 and not any((r.get("calce") or ("", ""))[1] == k or
                             "{%s" % k in (r.get("calce") or ("", ""))[1] or
                             r.get("en_serie") == en_grupo.get(k) and k in en_grupo
                             for r in regs)]

    # ---- 4. capa de foto: la imagen mas grande
    fotos = sorted(imagenes(svg), key=lambda i: -i["area"])
    foto_cfg = {}
    for r in regs:
        if r.get("id"):
            nuevo = _poner_id(r["apertura"], r["id"])
            if r.get("clase_extra"):
                c = _attr(nuevo, "class")
                nuevo = re.sub(r'\sclass="[^"]*"', ' class="%s"' % " ".join(
                    (c or "").split() + r["clase_extra"]), nuevo, count=1) if c is not None \
                    else nuevo[:-1] + ' class="%s">' % " ".join(r["clase_extra"])
            ediciones.append((r["inicio"], r["fin_apertura"], nuevo))
    for c in cajas:
        if c.get("id"):
            ediciones.append((c["inicio"], c["fin"], _poner_id(c["tag"], c["id"])))
    if fotos:
        ediciones.append((fotos[0]["inicio"], fotos[0]["fin"], '<g id="m-capa-foto"/>'))
        foto_cfg = {"capa_id": "m-capa-foto", "quitar": [], "degradados": []}
    else:
        avisos.add("el arte no trae foto de ejemplo: las piezas saldran sin foto")

    preparado = svg
    for a, b, nuevo in sorted(ediciones, key=lambda e: -e[0]):
        preparado = preparado[:a] + nuevo + preparado[b:]
    if "xmlns:xlink" not in preparado:
        preparado = re.sub(r"(<svg\b)", r'\1 xmlns:xlink="http://www.w3.org/1999/xlink"',
                           preparado, count=1)

    # ---- 5. zonas aprendidas del ejemplo
    arte = re.sub(r"<rect\b[^>]*?/?>",
                  lambda m: "" if _f(_attr(m.group(0), "width")) * _f(_attr(m.group(0), "height"))
                  >= 0.85 * W * H else m.group(0), preparado)
    zonas_cfg, cara = aprender_zonas(svg if fotos else None, arte, regs, W, H, avisos,
                                     os.path.dirname(os.path.abspath(ruta_svg)), cajas)
    if cara:
        informe.append(("zonas", "cara del ejemplo",
                        "pelo y=%d menton y=%d x=%d (detector %s) -> silueta %s, techo del texto y=%d"
                        % (cara["pelo"] * H, cara["menton"] * H, cara["cara_x"] * W,
                           cara["_backend"], zonas_cfg["silueta"], zonas_cfg["titulo"])))

    cfg = {"archivo": "%s.svg" % nombre, "ancho": int(round(W)), "alto": int(round(H)),
           "elementos": elementos, "zonas": zonas_cfg}
    if foto_cfg:
        cfg["foto"] = foto_cfg
    for a in sorted(avisos):
        informe.append(("aviso", "", a))
    for n in no_usadas:
        informe.append(("sin-uso", n, "esta columna no aparece en el arte de %s" % nombre))
    return preparado, cfg, informe


def _estilos(svg):
    from .plantilla import estilos
    return estilos(svg)


def construir_proyecto(marca, claves, nombres, filas, grupos, cols_mapeadas):
    col = lambda opciones: next((k for k in claves if k in opciones), None)
    c_slug, c_foto, c_sujeto = col(COLS_SLUG), col(COLS_FOTO), col(COLS_SUJETO)
    base_slug = c_slug or next((k for k in claves if k in cols_mapeadas), claves[0])

    piezas, vistos = [], {}
    for i, f in enumerate(filas, 1):
        s = clave(f.get(base_slug) or "pieza-%d" % i).replace("_", "-")[:60] or "pieza-%d" % i
        vistos[s] = vistos.get(s, 0) + 1
        if vistos[s] > 1:
            s = "%s-%d" % (s, vistos[s])
        campos = {k: v for k, v in f.items() if k not in (c_foto, c_slug, c_sujeto)}
        for b, ks in grupos.items():
            campos[b] = [f[k] for k in ks if f.get(k) not in ("", None)]
        pieza = {"slug": s, "campos": campos}
        if c_foto and f.get(c_foto):
            pieza["foto"] = str(f[c_foto])
        if c_sujeto and f.get(c_sujeto):
            pieza["sujeto"] = f[c_sujeto]
        piezas.append(pieza)

    return {"proyecto": marca, "plantilla": "../../plantillas/%s" % marca,
            "fotos": "fotos", "salida": "../../salida/%s" % marca,
            "ruta": "", "archivo": "{formato}-{slug}", "piezas": piezas}


def montar(raiz, marca, svgs, ruta_tabla, manual=None, sobrescribir=False):
    """Crea plantillas/<marca>/ y proyectos/<marca>/ a partir del arte y la tabla."""
    dir_pl = os.path.join(raiz, "plantillas", marca)
    dir_pr = os.path.join(raiz, "proyectos", marca)
    if not sobrescribir and (os.path.exists(os.path.join(dir_pl, "plantilla.json"))
                             or os.path.exists(os.path.join(dir_pr, "proyecto.json"))):
        raise FileExistsError("Ya existe la marca '%s'. Usa --sobrescribir para rehacerla." % marca)

    claves, nombres, filas = leer_tabla(ruta_tabla)
    especiales = set(COLS_FOTO + COLS_SLUG + COLS_SUJETO)
    grupos = _grupos([k for k in claves if k not in especiales])

    formatos, informes = {}, {}
    os.makedirs(dir_pl, exist_ok=True)
    for nombre, ruta in svgs.items():
        svg, cfg, inf = montar_formato(nombre, ruta, claves, nombres, filas, manual)
        with open(os.path.join(dir_pl, cfg["archivo"]), "w", encoding="utf-8") as f:
            f.write(svg)
        formatos[nombre] = cfg
        informes[nombre] = inf

    usados = set()
    for cfg in formatos.values():
        for el in cfg["elementos"]:
            if el.get("campo"):
                usados.add(el["campo"])
            usados.update(re.findall(r"\{(\w+)", el.get("plantilla", "")))
    grupos_usados = {b: ks for b, ks in grupos.items() if b in usados}

    campos = {}
    for k in claves:
        if k in especiales:
            continue
        b = next((b for b, ks in grupos_usados.items() if k in ks), None)
        if b:
            campos[b] = {"tipo": "lista", "max": len(grupos_usados[b])}
        elif k in usados:
            numerico = all(_num(f.get(k)) is not None for f in filas if f.get(k) not in ("", None))
            campos[k] = {"tipo": "numero" if numerico else "texto"}

    plantilla = {"nombre": marca, "version": 1,
                 "_nota": ["Generado por `graficas.py montar` a partir del arte y la tabla.",
                           "Es un punto de partida: revisa tipos, anchos y zonas contra una pieza real."],
                 "campos": campos, "formatos": formatos}
    with open(os.path.join(dir_pl, "plantilla.json"), "w", encoding="utf-8") as f:
        json.dump(plantilla, f, ensure_ascii=False, indent=2)

    proyecto = construir_proyecto(marca, claves, nombres, filas, grupos_usados, usados)
    os.makedirs(os.path.join(dir_pr, "fotos"), exist_ok=True)
    with open(os.path.join(dir_pr, "proyecto.json"), "w", encoding="utf-8") as f:
        json.dump(proyecto, f, ensure_ascii=False, indent=2)
    return dir_pl, dir_pr, informes, len(proyecto["piezas"])
