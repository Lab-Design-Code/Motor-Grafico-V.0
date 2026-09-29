#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Escribe en el JSON de escuela la ruta de la foto de cada carrera.

La ruta es deterministica -- 03-Fotografias/<Escuela>/<Carrera>/<Carrera>.jpg --
asi que no hay razon para teclearla carrera por carrera, que es como se hizo en
la Escuela de Salud y donde es facil dejar una sede sin foto.

Solo asigna cuando el archivo existe; informa las carreras que siguen sin foto.

    python 00-Scripts/asignar_fotos.py 02-Datos/escuela-educacion.json
"""
import os, sys, json

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOTOS = os.path.join(REPO, "03-Fotografias")

if __name__ == "__main__":
    ruta = sys.argv[1]
    if not os.path.isabs(ruta):
        ruta = os.path.join(REPO, ruta)
    data = json.load(open(ruta, encoding="utf-8"))
    escuela = data["escuela"]

    asignadas, faltan = set(), set()
    for c in data["carreras"]:
        rel = "%s/%s/%s.jpg" % (escuela, c["carpeta"], c["carpeta"])
        if os.path.exists(os.path.join(FOTOS, rel.replace("/", os.sep))):
            c["foto"] = rel
            asignadas.add(c["carpeta"])
        else:
            faltan.add(c["carpeta"])

    json.dump(data, open(ruta, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

    for n in sorted(asignadas):
        print("ok      %s" % n)
    for n in sorted(faltan):
        print("FALTA   %s  ->  03-Fotografias/%s/%s/%s.jpg"
              % (n, escuela, n, n))
    print("\n%d carreras con foto, %d sin foto" % (len(asignadas), len(faltan)))
