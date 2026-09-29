#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mide en que Y empieza realmente el titulo de cada pieza.

El techo del menton no se puede asumir: depende del largo del nombre. Si no
cabe en una linea el generador parte el titulo y sube el bloque completo una
interlinea, y esa interlinea se calcula sobre el cuerpo del nombre ya
autoajustado -- que tambien varia. Estimarlo a ojo fue lo que dejo el prefijo
cruzando la mandibula en varias piezas.

Aca se renderiza la pieza SIN foto y se busca el primer pixel blanco del
titulo. El fondo sin foto es la plancha gris #606060 de la plantilla, asi que
el texto blanco se separa sin ambiguedad.

    python 00-Scripts/medir_titulo.py 02-Datos/escuela-salud.json
"""
import os, sys, json, subprocess, tempfile

BASE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(BASE)
sys.path.insert(0, BASE)

import generar_graficas_ipg as gen
import capa_fotos_ipg as capa

INKSCAPE = gen.INKSCAPE

# Franja donde puede caer el titulo. Empieza bajo el bloque del logo para no
# confundirse con el logo blanco, y termina antes de las pastillas de beca.
BANDA = {"Post": (250, 700), "Story": (450, 1100)}
# Margen horizontal: el titulo arranca en x 34 (Post) / 56 (Story).
COLUMNAS = (20, 1060)


def primer_pixel_titulo(png, tag):
    from PIL import Image
    im = Image.open(png).convert("RGB")
    y0, y1 = BANDA[tag]
    x0, x1 = COLUMNAS
    px = im.load()
    for y in range(y0, min(y1, im.height)):
        for x in range(x0, min(x1, im.width), 2):
            r, g, b = px[x, y]
            if r > 235 and g > 235 and b > 235:
                return y
    return None


def medir(c):
    out = {}
    for cfg, tag in ((gen.POST, "Post"), (gen.STORY, "Story")):
        svg = gen.construir(cfg, c)
        tmp = os.path.join(tempfile.gettempdir(), "_titulo.svg")
        png = tmp[:-4] + ".png"
        open(tmp, "w", encoding="utf-8").write(svg)
        if os.path.exists(png):
            os.remove(png)
        subprocess.run([INKSCAPE, tmp, "--export-type=png",
                        "--export-filename=" + png], check=False,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if not os.path.exists(png):
            raise SystemExit("Inkscape no escribio " + png)
        out[tag.lower()] = primer_pixel_titulo(png, tag)
        os.remove(png)
        os.remove(tmp)
    return out


if __name__ == "__main__":
    ruta = sys.argv[1]
    if not os.path.isabs(ruta):
        ruta = os.path.join(REPO, ruta)
    data = json.load(open(ruta, encoding="utf-8"))

    vistas, salida = set(), {}
    for c in data["carreras"]:
        if c["carpeta"] in vistas:
            continue
        vistas.add(c["carpeta"])
        m = medir(c)
        salida[c["carpeta"]] = m
        print("%-42s titulo Post y=%s  Story y=%s"
              % (c["carpeta"], m["post"], m["story"]))

    destino = os.path.join(os.path.dirname(ruta),
                           "titulos-" + os.path.basename(ruta).split("-", 1)[1])
    json.dump(salida, open(destino, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print("\nescrito:", destino)
