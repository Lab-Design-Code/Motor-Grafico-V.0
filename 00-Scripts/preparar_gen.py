#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prepara una foto para expansion generativa de Firefly.

Traduce las fracciones que resolvio solver_encuadre a pixeles concretos sobre
una version reducida de la foto, respetando el tope de 4096 px por lado que
impone image_generative_expand.

La clave es que las PROPORCIONES se conserven: el focal que calculo el solver
—fx = (extra_izq + cara_x*ancho) / ancho_total— sigue siendo valido mientras
la razon entre lo agregado y el original sea la misma. Asi la foto expandida
por Firefly entra al pipeline con expansion 0 y el mismo focal de siempre.
"""
import os, sys, json
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOPE = 4096

foto_rel, alto_obj = sys.argv[1], int(sys.argv[2])
lados, arriba, abajo = float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5])
destino = sys.argv[6]

src = os.path.join(REPO, "03-Fotografias", foto_rel)
im = Image.open(src).convert("RGB")
W0, H0 = im.size

# reduccion que deje todas las expansiones bajo el tope
alto = alto_obj
while True:
    ancho = int(round(W0 * alto / H0))
    izq = der = int(ancho * lados / 2)
    top = int(alto * arriba)
    bot = int((alto + top) * abajo)
    if max(izq, der, top, bot) <= TOPE:
        break
    alto = int(alto * 0.9)

chica = im.resize((ancho, alto), Image.LANCZOS)
chica.save(destino, quality=95)

info = {"origen": "%dx%d" % (W0, H0), "reducida": "%dx%d" % (ancho, alto),
        "expandir": {"left": izq, "right": der, "top": top, "bottom": bot},
        "final": "%dx%d" % (ancho + izq + der, alto + top + bot),
        "bytes": os.path.getsize(destino)}
print(json.dumps(info, ensure_ascii=False))
