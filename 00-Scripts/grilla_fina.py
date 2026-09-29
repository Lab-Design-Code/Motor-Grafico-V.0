#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dibuja una grilla en centesimas sobre la zona del rostro de una foto.

Es la herramienta con que se leen los tres valores que necesita el solver:
tope del pelo, menton y centro horizontal de la cabeza, todos como fraccion de
la foto original.

No sirve estimarlos mirando una miniatura. Las seis fotos de la Escuela de
Salud se midieron primero asi y las seis quedaron mal: un error de 0,05 del
alto son ~50 px en el lienzo, suficiente para que el menton termine bajo el
titulo aunque el solver diga que el encuadre cumple.

    python 00-Scripts/grilla_fina.py "Escuela de Salud" Enfermeria salida.jpg
    python 00-Scripts/grilla_fina.py "Escuela de Salud" Enfermeria salida.jpg 0.05 0.45

Los dos ultimos argumentos acotan la franja vertical que se amplia. Si el
rostro no aparece completo, hay que ensancharla.
"""
import os, sys, io
from PIL import Image, ImageDraw

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
Image.MAX_IMAGE_PIXELS = None

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOTOS = os.path.join(REPO, "03-Fotografias")

ANCHO_SALIDA = 900
ROJO, ROSA = (255, 0, 60), (255, 170, 190)
AZUL, CELESTE = (0, 160, 255), (150, 215, 255)


def grilla(escuela, carrera, salida, y0=0.0, y1=0.55):
    origen = os.path.join(FOTOS, escuela, carrera, "%s.jpg" % carrera)
    if not os.path.exists(origen):
        raise SystemExit("No encontre la foto: " + origen)

    im = Image.open(origen).convert("RGB")
    w0, h0 = im.size
    recorte = im.crop((0, int(h0 * y0), w0, int(h0 * y1)))
    recorte = recorte.resize((ANCHO_SALIDA, int(recorte.height * ANCHO_SALIDA / w0)),
                             Image.LANCZOS)
    d = ImageDraw.Draw(recorte)

    # horizontales cada centesima del alto ORIGINAL, marcadas cada cinco
    k = y0
    while k <= y1 + 1e-9:
        y = (k - y0) / (y1 - y0) * recorte.height
        marcada = abs((k * 100) % 5) < 1e-6
        d.line([(0, y), (recorte.width, y)],
               fill=ROJO if marcada else ROSA, width=2 if marcada else 1)
        if marcada:
            d.text((4, y + 2), "%.2f" % k, fill=ROJO)
        k = round(k + 0.01, 4)

    # verticales cada veinteavo del ancho, para leer cara_x
    for j in range(1, 20):
        x = recorte.width * j / 20
        marcada = j % 2 == 0
        d.line([(x, 0), (x, recorte.height)],
               fill=AZUL if marcada else CELESTE, width=1)
        if marcada:
            d.text((x + 2, 4), "%.1f" % (j / 20), fill=(0, 120, 200))

    recorte.save(salida, quality=93)
    return w0, h0


if __name__ == "__main__":
    if len(sys.argv) < 4:
        raise SystemExit(__doc__)
    escuela, carrera, salida = sys.argv[1], sys.argv[2], sys.argv[3]
    y0 = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0
    y1 = float(sys.argv[5]) if len(sys.argv) > 5 else 0.55
    w, h = grilla(escuela, carrera, salida, y0, y1)
    print("%s / %s  %dx%d  franja %.2f-%.2f  ->  %s"
          % (escuela, carrera, w, h, y0, y1, salida))
