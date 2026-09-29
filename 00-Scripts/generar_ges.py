#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera las piezas de Salud en V.2-0 con las fotos expandidas por Firefly.

Cada carrera tiene un archivo por formato en 03-Fotografias/_generadas/, con el
lienzo ya resuelto. Entran al pipeline con expansion 0: el focal que calculo el
solver sigue siendo valido porque las proporciones de la expansion son las
mismas que se le pidieron a Firefly.

Las carreras sin foto generada caen al camino normal (expansion por reflejo),
para que la escuela quede completa aunque falte alguna.
"""
import os, sys, json

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "00-Scripts"))
os.chdir(REPO)
import generar_graficas_ipg as gen
import capa_fotos_ipg as capa
import lote_graficas_ipg as lote

GEN = os.path.join(REPO, "03-Fotografias", "_generadas")
SALIDA = os.path.join(REPO, "Gráficas Meta 2027", "V.2-0")
FOTOS = os.path.join(REPO, "03-Fotografias")

data = json.load(open(os.path.join(REPO, "02-Datos", "escuela-gestion.json"),
                      encoding="utf-8"))
escuela = data["escuela"]
hechas = 0

for c in data["carreras"]:
    carpeta = lote.ruta_pieza(escuela, c, SALIDA)
    os.makedirs(carpeta, exist_ok=True)
    for cfg, tag, zonas in ((gen.POST, "Post", capa.ZONAS_POST),
                            (gen.STORY, "Story", capa.ZONAS_STORY)):
        low = tag.lower()
        generada = os.path.join(GEN, "%s-%s.jpg" % (c["carpeta"], low))
        d = dict(c)
        if os.path.exists(generada):
            for k in list(d):
                if k.startswith("expandir_"):
                    del d[k]
            foto = generada
        else:
            foto = d.get("foto_" + low) or d.get("foto")
            if foto and not os.path.isabs(foto):
                foto = os.path.join(FOTOS, foto)
            if foto:
                foto = lote.foto_expandida(
                    foto,
                    d.get("expandir_arriba_" + low) or d.get("expandir_arriba"),
                    d.get("expandir_lados_" + low) or d.get("expandir_lados"),
                    d.get("expandir_abajo_" + low) or d.get("expandir_abajo"))

        svg = gen.construir(cfg, d)
        if foto:
            focal = d.get("focal_" + low) or d.get("focal") or (0.5, 0.38, 0.5, 0.33)
            svg = capa.poner_foto(svg, zonas, foto, tuple(focal))

        nombre = "%s-IPG_2027-%s" % (tag, c["slug"])
        png = os.path.join(carpeta, nombre + ".png")
        tmp = os.path.join(carpeta, nombre + ".svg")
        open(tmp, "w", encoding="utf-8").write(svg)
        try:
            lote.render_png(tmp, png)
            hechas += 1
        finally:
            if os.path.exists(tmp):
                os.remove(tmp)
    marca = "FIREFLY" if os.path.exists(
        os.path.join(GEN, "%s-post.jpg" % c["carpeta"])) else "reflejo "
    print("ok  %-8s %-42s %s" % (marca, c["carpeta"], c["sede"]))

print("\n%d graficas -> %s" % (hechas, SALIDA))
