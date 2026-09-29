#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vuelca los encuadres resueltos al JSON de la escuela.

Borra primero las expansiones y focales anteriores de cada carrera, para que un
recalculo no deje mezclados parametros viejos con nuevos -- que es la forma mas
facil de terminar con un encuadre que no corresponde a ninguna corrida.

    python 00-Scripts/aplicar_encuadres.py 02-Datos/escuela-salud.json 02-Datos/encuadres-salud.json
"""
import os, sys, json

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def abs_ruta(p):
    return p if os.path.isabs(p) else os.path.join(REPO, p)


if __name__ == "__main__":
    escuela = abs_ruta(sys.argv[1])
    encuadres = json.load(open(abs_ruta(sys.argv[2]), encoding="utf-8"))
    data = json.load(open(escuela, encoding="utf-8"))

    for c in data["carreras"]:
        e = encuadres.get(c["carpeta"])
        if not e:
            continue
        for k in list(c):
            if k.startswith("expandir_") or k.startswith("focal") or k.startswith("zoom"):
                del c[k]
        c.update(e)

    json.dump(data, open(escuela, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    for c in data["carreras"]:
        marca = "ok " if c.get("focal_post") else "-- "
        print("%s%-42s %s" % (marca, c["carpeta"], c["sede"]))
