#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dibuja una grilla en centesimas sobre cada foto, para leer las medidas a ojo.

Por que a ojo y no con el detector: se probo medir las 18 con Haar sobre el
archivo a resolucion plena y fallo en ocho. El detector elige "la cara mas
grande", que en estas fotos suele ser el acompañante en primer plano y no el
protagonista —en Rehabilitacion eligio a la persona de la derecha, en Farmacias
a la clienta, en Parvularia a un niño—, y el refinado del tope del pelo se
escapaba al borde superior. En Instrumentacion no encontro ninguna.

La grilla es la misma idea de grilla_fina.py: lineas cada 0,05 del alto y del
ancho, rotuladas, y una mas marcada cada 0,10.
"""
import io, os, json, glob
from PIL import Image, ImageDraw

AQUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOTOS = os.path.join(REPO, "03-Fotografias")
SALIDA = os.path.join(AQUI, "grillas")
if not os.path.isdir(SALIDA):
    os.makedirs(SALIDA)

instaladas = json.load(io.open(os.path.join(AQUI, "instaladas.json"),
                               encoding="utf-8"))
escuela_de = {}
for ruta in sorted(glob.glob(os.path.join(REPO, "02-Datos", "escuela-*.json"))):
    d = json.load(io.open(ruta, encoding="utf-8"))
    for c in d["carreras"]:
        escuela_de[c["carpeta"]] = d["escuela"]

ANCHO = 620
PAR = 2   # fotos por hoja

hojas = []
for i in range(0, len(instaladas), PAR):
    grupo = instaladas[i:i + PAR]
    imgs = []
    for carrera in grupo:
        p = os.path.join(FOTOS, escuela_de[carrera], carrera, carrera + ".jpg")
        im = Image.open(p).convert("RGB")
        esc = ANCHO / float(im.size[0])
        im = im.resize((ANCHO, int(im.size[1] * esc)), Image.LANCZOS)
        W, H = im.size
        d = ImageDraw.Draw(im, "RGBA")
        for k in range(1, 20):
            f = k / 20.0
            grueso = (k % 2 == 0)
            col = (255, 255, 0, 210) if grueso else (255, 255, 255, 120)
            y = int(H * f)
            d.line([(0, y), (W, y)], fill=col, width=2 if grueso else 1)
            if grueso:
                d.rectangle([0, y - 8, 30, y + 8], fill=(0, 0, 0, 170))
                d.text((3, y - 6), "%.2f" % f, fill=(255, 255, 0, 255))
            x = int(W * f)
            d.line([(x, 0), (x, H)], fill=col, width=2 if grueso else 1)
            if grueso:
                d.rectangle([x - 15, 0, x + 15, 15], fill=(0, 0, 0, 170))
                d.text((x - 12, 1), "%.2f" % f, fill=(255, 255, 0, 255))
        cab = Image.new("RGB", (W, H + 22), (250, 250, 252))
        cab.paste(im, (0, 22))
        ImageDraw.Draw(cab).text((4, 5), carrera, fill=(10, 30, 77))
        imgs.append(cab)

    Wt = sum(x.size[0] for x in imgs) + 10 * (len(imgs) + 1)
    Ht = max(x.size[1] for x in imgs) + 20
    hoja = Image.new("RGB", (Wt, Ht), (236, 236, 240))
    x = 10
    for im in imgs:
        hoja.paste(im, (x, 10))
        x += im.size[0] + 10
    ruta = os.path.join(SALIDA, "grilla-%02d.jpg" % (i // PAR + 1))
    hoja.save(ruta, quality=90)
    hojas.append(ruta)
    print(ruta)

print("\n%d hojas" % len(hojas))
