#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Copia a Modificadas las piezas de las carreras que se indiquen.

    python copiar_una.py <escuela.json> <Carpeta-Carrera> [...]

Sirve para sumar carreras sueltas sin rehacer toda la carpeta, que es lo que
hace modificadas.py.
"""
import io, os, sys, json, shutil

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "00-Scripts"))
import lote_graficas_ipg as lote

V3 = os.path.join(REPO, "Gráficas Meta 2027", "V.3")
DEST = os.path.join(V3, "Modificadas")

d = json.load(io.open(os.path.join(REPO, "02-Datos", sys.argv[1]),
                      encoding="utf-8"))
pedidas = set(sys.argv[2:])
n = 0
for c in d["carreras"]:
    if c["carpeta"] not in pedidas:
        continue
    o = lote.ruta_pieza(d["escuela"], c, V3)
    t = lote.ruta_pieza(d["escuela"], c, DEST)
    os.makedirs(t, exist_ok=True)
    for tag in ("Post", "Story"):
        f = "%s-IPG_2027-%s.png" % (tag, c["slug"])
        shutil.copy2(os.path.join(o, f), os.path.join(t, f))
        n += 1
    print("ok  %-42s %s" % (c["carpeta"], c["sede"]))
print("\n%d graficas -> Modificadas" % n)
