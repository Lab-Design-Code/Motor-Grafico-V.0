#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Instala una foto suelta y deja la grilla para medirla.

    python una_instalar.py <numero de imagen> <Carpeta-Carrera> <Escuela>
"""
import os, sys, shutil
from PIL import Image, ImageDraw

AQUI = os.path.dirname(os.path.abspath(__file__))
IMGS = os.path.join(os.path.dirname(os.path.dirname(AQUI)), "images")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOTOS = os.path.join(REPO, "03-Fotografias")
RESP = os.path.join(FOTOS, "_V2-0-sin-retoque")
os.makedirs(RESP, exist_ok=True)

num, carrera, escuela = sys.argv[1], sys.argv[2], sys.argv[3]

origen = None
for ext in (".jpg", ".jpeg", ".png"):
    p = os.path.join(IMGS, num + ext)
    if os.path.exists(p):
        origen = p
        break
if not origen:
    raise SystemExit("no esta la imagen %s" % num)

carpeta = os.path.join(FOTOS, escuela, carrera)
os.makedirs(carpeta, exist_ok=True)
destino = os.path.join(carpeta, carrera + ".jpg")
copia = os.path.join(RESP, carrera + ".jpg")
if os.path.exists(destino) and not os.path.exists(copia):
    shutil.copy2(destino, copia)

im = Image.open(origen).convert("RGB")
im.save(destino, quality=95, subsampling=0)
print("%s  %dx%d  %d bytes" % (carrera, im.size[0], im.size[1],
                               os.path.getsize(destino)))

g = im.copy()
g.thumbnail((900, 900), Image.LANCZOS)
W, H = g.size
d = ImageDraw.Draw(g, "RGBA")
for k in range(1, 20):
    f = k / 20.0
    gr = (k % 2 == 0)
    col = (255, 255, 0, 210) if gr else (255, 255, 255, 110)
    y = int(H * f)
    d.line([(0, y), (W, y)], fill=col, width=2 if gr else 1)
    x = int(W * f)
    d.line([(x, 0), (x, H)], fill=col, width=2 if gr else 1)
    if gr:
        d.rectangle([0, y - 8, 32, y + 8], fill=(0, 0, 0, 180))
        d.text((2, y - 6), "%.2f" % f, fill=(255, 255, 0, 255))
        d.rectangle([x - 16, 0, x + 16, 15], fill=(0, 0, 0, 180))
        d.text((x - 13, 1), "%.2f" % f, fill=(255, 255, 0, 255))
ruta = os.path.join(AQUI, "grilla-%s.jpg" % carrera)
g.save(ruta, quality=92)
print(ruta)
