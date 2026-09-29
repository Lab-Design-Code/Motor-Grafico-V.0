#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reune en V.3\\Modificadas solo las piezas de las carreras con foto nueva.

Copia, no mueve: V.3 tiene que seguir siendo la campana completa de 166
graficas. Modificadas es un atajo de revision, no una version aparte.

Mantiene la estructura Escuela / Carrera / Presencial|Online / Sede, para que
el nombre de archivo siga diciendo a que sede pertenece cada pieza.
"""
import io, os, sys, json, glob, shutil

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "00-Scripts"))
import lote_graficas_ipg as lote

AQUI = os.path.dirname(os.path.abspath(__file__))
V3 = os.path.join(REPO, "Gráficas Meta 2027", "V.3")
DEST = os.path.join(V3, "Modificadas")

instaladas = set(json.load(io.open(os.path.join(AQUI, "instaladas.json"),
                                   encoding="utf-8")))

# se limpia antes, para que la carpeta nunca mezcle una tanda con la anterior
if os.path.isdir(DEST):
    shutil.rmtree(DEST)
os.makedirs(DEST)

copiadas = 0
porcarrera = {}
for ruta in sorted(glob.glob(os.path.join(REPO, "02-Datos", "escuela-*.json"))):
    d = json.load(io.open(ruta, encoding="utf-8"))
    for c in d["carreras"]:
        if c["carpeta"] not in instaladas:
            continue
        origen = lote.ruta_pieza(d["escuela"], c, V3)
        destino = lote.ruta_pieza(d["escuela"], c, DEST)
        os.makedirs(destino, exist_ok=True)
        for tag in ("Post", "Story"):
            f = "%s-IPG_2027-%s.png" % (tag, c["slug"])
            o = os.path.join(origen, f)
            if not os.path.exists(o):
                print("falta %s" % o)
                continue
            shutil.copy2(o, os.path.join(destino, f))
            copiadas += 1
            porcarrera[c["carpeta"]] = porcarrera.get(c["carpeta"], 0) + 1

print("%-42s %s" % ("carrera", "graficas"))
for k in sorted(porcarrera):
    print("%-42s %d" % (k, porcarrera[k]))
print("\n%d carreras · %d graficas -> %s" % (len(porcarrera), copiadas, DEST))
