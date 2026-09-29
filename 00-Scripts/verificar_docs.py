#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Comprueba que los enlaces relativos de la documentacion resuelvan.

Un enlace roto en un handoff es peor que no tenerlo: manda a alguien a buscar
un archivo que no existe.
"""
import io, os, re, urllib.parse

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = [os.path.join(REPO, *p.split("/")) for p in (
    "LEEME.md",
    "00-Scripts/LEEME.md",
    "00-Scripts/CONTEXTO-graficas-admision-2027.md",
    "Gráficas Meta 2027/LEEME.md",
    "Gráficas Meta 2027/V.3/Modificadas/LEEME.md",
)]
# El motor genérico vive fuera de este repositorio; se revisa sólo si está al lado.
MOTOR = os.path.join(REPO, "..", "..", "Personal", "Motor-Graficas")
if os.path.isdir(MOTOR):
    DOCS += [os.path.join(MOTOR, *p.split("/")) for p in (
        "README.md", "plantillas/LEEME.md", "proyectos/LEEME.md",
        "proyectos/ipg-2027/LEEME.md")]

RE = re.compile(r'\[[^\]]+\]\(([^)]+)\)')
malos = 0
for doc in DOCS:
    if not os.path.exists(doc):
        print("FALTA EL DOC  %s" % doc)
        malos += 1
        continue
    base = os.path.dirname(doc)
    texto = io.open(doc, encoding="utf-8").read()
    rotos = []
    for m in RE.finditer(texto):
        destino = m.group(1)
        if destino.startswith(("http://", "https://", "#")):
            continue
        ruta = urllib.parse.unquote(destino.split("#")[0])
        if not os.path.exists(os.path.join(base, ruta.replace("/", os.sep))):
            rotos.append(destino)
    marca = "ok" if not rotos else "ROTOS: " + ", ".join(rotos)
    malos += len(rotos)
    print("%-52s %s" % (os.path.relpath(doc, os.path.dirname(REPO)), marca))

print("\n%d enlaces rotos" % malos)
