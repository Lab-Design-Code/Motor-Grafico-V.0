#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Convierte las fracciones del solver en pixeles para Firefly.

La cadena es siempre lados -> arriba -> abajo, y cada fraccion es relativa al
tamano EN ESE PUNTO de la cadena, no al original. El int() de cada paso es
parte del contrato: capa_fotos_ipg redondea hacia abajo y el solver replica esa
aritmetica, asi que aca hay que repetirla igual o el encuadre se corre.

Estas fotos llegan en 2000 px, asi que no hay que reducirlas: se expanden tal
cual y ningun lado pasa del limite de 4096 px de Firefly.
"""
import io, os, json, glob, shutil
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOTOS = os.path.join(REPO, "03-Fotografias")
SALIDA = os.path.join(AQUI, "gen")
if not os.path.isdir(SALIDA):
    os.makedirs(SALIDA)

enc = json.load(io.open(os.path.join(AQUI, "encuadres-v3.json"), encoding="utf-8"))
escuela_de = {}
for r in sorted(glob.glob(os.path.join(REPO, "02-Datos", "escuela-*.json"))):
    d = json.load(io.open(r, encoding="utf-8"))
    for c in d["carreras"]:
        escuela_de[c["carpeta"]] = d["escuela"]

LIMITE = 4096
plan = {}
print("%-42s %-6s %-11s %s" % ("carrera", "pieza", "origen", "L/R  arriba  abajo"))
for carrera in sorted(enc):
    origen = os.path.join(FOTOS, escuela_de[carrera], carrera, carrera + ".jpg")
    im = Image.open(origen).convert("RGB")
    W, H = im.size
    for tag in ("post", "story"):
        lados = enc[carrera].get("expandir_lados_" + tag, 0) or 0
        arriba = enc[carrera].get("expandir_arriba_" + tag, 0) or 0
        abajo = enc[carrera].get("expandir_abajo_" + tag, 0) or 0

        extra_l = int(W * lados / 2) if lados else 0
        extra_a = int(H * arriba) if arriba else 0
        nh2 = H + extra_a
        extra_b = int(nh2 * abajo) if abajo else 0

        if max(extra_l, extra_a, extra_b) > LIMITE:
            print("%-42s %-6s EXCEDE %d px" % (carrera, tag,
                                               max(extra_l, extra_a, extra_b)))
            continue

        clave = "%s-%s" % (carrera, tag)
        destino = os.path.join(SALIDA, clave + ".jpg")
        im.save(destino, quality=95, subsampling=0)
        plan[clave] = {
            "archivo": destino, "bytes": os.path.getsize(destino),
            "left": extra_l, "right": extra_l, "top": extra_a, "bottom": extra_b,
            "salida": [W + 2 * extra_l, nh2 + extra_b],
        }
        print("%-42s %-6s %-11s %d/%d  %d  %d" % (
            carrera, tag, "%dx%d" % (W, H), extra_l, extra_l, extra_a, extra_b))

json.dump(plan, io.open(os.path.join(AQUI, "plan-gen.json"), "w",
                        encoding="utf-8"), ensure_ascii=False, indent=2)
print("\n%d piezas listas para expandir" % len(plan))
