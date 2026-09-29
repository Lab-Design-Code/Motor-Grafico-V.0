#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Propaga foto y parametros de encuadre a todas las sedes de una misma carrera.

La decision del proyecto es una foto por carrera, no por carrera+sede: las
sedes comparten imagen y encuadre, y solo cambia la pastilla de sede. Calibrar
una vez y copiar evita que se desalineen entre sedes.

    python 00-Scripts/propagar_fotos.py 02-Datos/escuela-salud.json
"""
import os, sys, json, collections

CLAVES = ("foto", "_shutterstock", "zoom", "focal")
PREFIJOS = ("foto_", "expandir_", "focal_", "zoom_")


def es_de_foto(k):
    return k in CLAVES or any(k.startswith(p) for p in PREFIJOS)


if __name__ == "__main__":
    ruta = sys.argv[1]
    if not os.path.isabs(ruta):
        ruta = os.path.join(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))), ruta)
    data = json.load(open(ruta, encoding="utf-8"))

    fuente = {}
    for c in data["carreras"]:
        if c.get("foto") and c["carpeta"] not in fuente:
            fuente[c["carpeta"]] = {k: v for k, v in c.items() if es_de_foto(k)}

    tocadas = collections.Counter()
    for c in data["carreras"]:
        base = fuente.get(c["carpeta"])
        if not base or c.get("foto"):
            continue
        c.pop("_foto_pendiente", None)
        c.update(base)
        tocadas[c["carpeta"]] += 1

    json.dump(data, open(ruta, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

    sin_foto = [c["slug"] for c in data["carreras"] if not c.get("foto")]
    for carpeta, n in tocadas.items():
        print("%-42s +%d sedes" % (carpeta, n))
    print("sin foto:", ", ".join(sin_foto) if sin_foto else "ninguna")
