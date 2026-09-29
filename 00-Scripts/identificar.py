#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Identifica cada descarga comparandola con las miniaturas candidatas.

recoger_descargas.py empareja por orden de descarga, y eso basta cuando la
tanda salio limpia. Cuando hubo reintentos —clics que no dispararon, archivos
repetidos— el orden deja de ser confiable y una foto puede terminar en la
carrera equivocada. Aca se compara el contenido: ambas imagenes se reducen a
una huella de 32x32 en gris y se mide la diferencia media.
"""
import os, sys, glob
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
LADO = 32


def huella(path):
    im = Image.open(path).convert("L").resize((LADO, LADO), Image.LANCZOS)
    px = list(im.getdata())
    m = sum(px) / len(px)
    d = (sum((p - m) ** 2 for p in px) / len(px)) ** 0.5 or 1.0
    return [(p - m) / d for p in px]


def distancia(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b)) / len(a)


candidatos = {}
for p in glob.glob(os.path.join(sys.argv[1], "**", "*.jpg"), recursive=True):
    n = os.path.basename(p)
    if "-260nw-" not in n:
        continue
    candidatos[n.replace(".jpg", "").split("-")[-1]] = huella(p)

print("%-46s %-12s %-10s %s" % ("archivo", "id", "distancia", "2do mejor"))
for p in sys.argv[2:]:
    if not os.path.exists(p):
        print("%-46s NO EXISTE" % os.path.basename(p))
        continue
    try:
        h = huella(p)
    except Exception as e:
        print("%-46s ilegible: %s" % (os.path.basename(p), e))
        continue
    orden = sorted(candidatos.items(), key=lambda kv: distancia(h, kv[1]))
    d0 = distancia(h, orden[0][1])
    d1 = distancia(h, orden[1][1]) if len(orden) > 1 else 9.9
    print("%-46s %-12s %-10.4f %s (%.4f)"
          % (os.path.basename(p)[:44], orden[0][0], d0, orden[1][0], d1))
