#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Recoge varias descargas de Shutterstock y las reparte por carrera.

Recoger una por una obliga a alternar navegador y consola en cada foto. Aca se
descargan todas seguidas y se asignan despues, en el mismo orden en que se
bajaron: se ordenan los JPEG nuevos por fecha de modificacion y se emparejan
con la lista de carreras.

Brave a veces deja el archivo como .tmp sin renombrarlo aunque este completo,
asi que se valida abriendolo, no por la extension.

    python 00-Scripts/recoger_descargas.py "Escuela de X" Carrera1 Carrera2 ...
    python 00-Scripts/recoger_descargas.py "Escuela de X" --minutos 30 Carrera1 ...
"""
import os, sys, io, time, shutil
from PIL import Image

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
Image.MAX_IMAGE_PIXELS = None

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOTOS = os.path.join(REPO, "03-Fotografias")
DESCARGAS = os.path.join(os.environ["USERPROFILE"], "Downloads")


def jpegs_recientes(desde):
    out = []
    for n in os.listdir(DESCARGAS):
        p = os.path.join(DESCARGAS, n)
        if not os.path.isfile(p) or os.path.getmtime(p) <= desde:
            continue
        try:
            Image.open(p).verify()
        except Exception:
            continue
        out.append((os.path.getmtime(p), p))
    return [p for _, p in sorted(out)]


if __name__ == "__main__":
    escuela = sys.argv[1]
    resto = sys.argv[2:]
    minutos = 60
    if resto and resto[0] == "--minutos":
        minutos = float(resto[1])
        resto = resto[2:]
    carreras = resto
    if not carreras:
        raise SystemExit(__doc__)

    archivos = jpegs_recientes(time.time() - minutos * 60)
    if len(archivos) != len(carreras):
        print("Hay %d descargas nuevas y %d carreras. Se emparejan por orden:"
              % (len(archivos), len(carreras)))
        for i, p in enumerate(archivos):
            print("   %2d. %s" % (i + 1, os.path.basename(p)))
        if len(archivos) < len(carreras):
            raise SystemExit("Faltan descargas; no asigno nada para no cruzarlas.")
        archivos = archivos[-len(carreras):]

    for carrera, src in zip(carreras, archivos):
        w, h = Image.open(src).size
        destino = os.path.join(FOTOS, escuela, carrera, "%s.jpg" % carrera)
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        shutil.move(src, destino)
        print("ok  %-38s %5d x %-5d" % (carrera, w, h))
