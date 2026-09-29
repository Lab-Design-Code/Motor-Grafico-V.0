#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Baja las dos expansiones de una carrera suelta y aplica su encuadre.

    python una_cerrar.py <escuela.json> <Carpeta-Carrera> <uid-post> <ancho> <alto> <uid-story> <ancho> <alto>
"""
import io, os, sys, json, shutil, urllib.request
from PIL import Image

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AQUI = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(REPO, "03-Fotografias", "_generadas")
RESP = os.path.join(REPO, "03-Fotografias", "_generadas-V2-0")
os.makedirs(RESP, exist_ok=True)
B = "https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:"

archivo, carrera = sys.argv[1], sys.argv[2]
S = {carrera + "-post":  (sys.argv[3], int(sys.argv[4]), int(sys.argv[5])),
     carrera + "-story": (sys.argv[6], int(sys.argv[7]), int(sys.argv[8]))}

for n, (u, aw, ah) in S.items():
    d = os.path.join(GEN, n + ".jpg")
    c = os.path.join(RESP, n + ".jpg")
    if os.path.exists(d) and not os.path.exists(c):
        shutil.copy2(d, c)
    urllib.request.urlretrieve(B + u, d)
    w, h = Image.open(d).size
    print("%-48s %dx%d %s" % (n, w, h,
                              "ok" if (w, h) == (aw, ah) else "NO CALZA"))

enc = json.load(io.open(os.path.join(AQUI, "encuadres-una.json"),
                        encoding="utf-8"))
p = os.path.join(REPO, "02-Datos", archivo)
d = json.load(io.open(p, encoding="utf-8"))
n = 0
for c in d["carreras"]:
    if c["carpeta"] not in enc:
        continue
    for k in list(c):
        if k.startswith("expandir_") or k.startswith("focal"):
            del c[k]
    c.update(enc[c["carpeta"]])
    n += 1
json.dump(d, io.open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("encuadre aplicado a %d pieza(s)" % n)
