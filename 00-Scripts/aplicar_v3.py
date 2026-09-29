#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Escribe los encuadres de V.3 en los JSON de escuela.

Respalda cada JSON antes de tocarlo, en 02-Datos/_V2-0/.

El focal se escribe en TODAS las sedes de la carrera, no solo en una: la foto
es la misma para las cinco sedes de Construccion Civil o las cuatro de
Enfermeria, y lo unico que cambia entre ellas es la pastilla.
"""
import io, os, json, glob, shutil

AQUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATOS = os.path.join(REPO, "02-Datos")
RESP = os.path.join(DATOS, "_V2-0")
if not os.path.isdir(RESP):
    os.makedirs(RESP)

enc = json.load(io.open(os.path.join(AQUI, "encuadres-v3.json"), encoding="utf-8"))

tocadas = 0
for ruta in sorted(glob.glob(os.path.join(DATOS, "escuela-*.json"))):
    copia = os.path.join(RESP, os.path.basename(ruta))
    if not os.path.exists(copia):
        shutil.copy2(ruta, copia)
    d = json.load(io.open(ruta, encoding="utf-8"))
    cambios = 0
    for c in d["carreras"]:
        if c["carpeta"] not in enc:
            continue
        for k in list(c):
            if k.startswith("expandir_") or k.startswith("focal"):
                del c[k]
        c.update(enc[c["carpeta"]])
        cambios += 1
    if cambios:
        json.dump(d, io.open(ruta, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
        tocadas += cambios
        print("%-40s %d piezas actualizadas" % (os.path.basename(ruta), cambios))

print("\n%d piezas con encuadre nuevo" % tocadas)
