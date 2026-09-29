#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Monta las piezas de una escuela en una sola hoja, para verificar de un vistazo.

Toma una sede por carrera: alcanza para juzgar el encuadre, porque las sedes de
una misma carrera comparten foto y parametros. Abrir los PNG uno por uno para
revisar veinte piezas es la forma segura de que se escape una.

    python 00-Scripts/hoja_contacto.py "Escuela de Salud" Post salida.jpg
    python 00-Scripts/hoja_contacto.py "Escuela de Salud" Story salida.jpg 640
"""
import os, sys, io
from PIL import Image, ImageDraw

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
Image.MAX_IMAGE_PIXELS = None

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA = os.path.join(REPO, "Gráficas Meta 2027")

PAD, ETIQUETA = 10, 22


def piezas(escuela, tag):
    raiz = os.path.join(SALIDA, escuela)
    out = []
    for carrera in sorted(os.listdir(raiz)):
        d = os.path.join(raiz, carrera)
        if not os.path.isdir(d):
            continue
        for sub, _, files in os.walk(d):
            elegido = next((f for f in sorted(files)
                            if f.startswith(tag) and f.endswith(".png")), None)
            if elegido:
                out.append((carrera, os.path.join(sub, elegido)))
                break
    return out


def montar(escuela, tag, salida, alto=560, por_fila=6):
    encontradas = piezas(escuela, tag)
    if not encontradas:
        raise SystemExit("No encontre piezas %s en %s" % (tag, escuela))

    ims = []
    for carrera, p in encontradas:
        im = Image.open(p).convert("RGB")
        im.thumbnail((alto, alto))
        ims.append((carrera, im))

    filas = [ims[i:i + por_fila] for i in range(0, len(ims), por_fila)]
    ancho = max(sum(i.width for _, i in f) + PAD * (len(f) + 1) for f in filas)
    altura = sum(max(i.height for _, i in f) + PAD + ETIQUETA for f in filas) + PAD

    hoja = Image.new("RGB", (ancho, altura), (250, 250, 250))
    d = ImageDraw.Draw(hoja)
    y = PAD
    for fila in filas:
        x = PAD
        alto_fila = max(i.height for _, i in fila)
        for carrera, im in fila:
            hoja.paste(im, (x, y))
            d.text((x + 2, y + im.height + 4), carrera[:38], fill=(40, 40, 40))
            x += im.width + PAD
        y += alto_fila + PAD + ETIQUETA
    hoja.save(salida, quality=93)
    return len(ims)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        raise SystemExit(__doc__)
    escuela, tag, salida = sys.argv[1], sys.argv[2], sys.argv[3]
    alto = int(sys.argv[4]) if len(sys.argv) > 4 else 560
    n = montar(escuela, tag, salida, alto)
    print("hoja: %s  -  %d piezas" % (salida, n))
