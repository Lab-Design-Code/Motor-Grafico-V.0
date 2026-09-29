#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Deja solo la ultima version de cada grafica.

Borra las carpetas de trabajo -- 04-Post-Story y 05-Pruebas -- y purga del
cache de fotos expandidas todo lo que ya no corresponde a los parametros
vigentes. Nada de esto es original: las piezas se rehacen con
lote_graficas_ipg.py desde el JSON de la escuela, y las expansiones se
recalculan solas en la proxima corrida.

Por defecto solo informa. Hay que pasar --borrar para que actue.

    python 00-Scripts/limpiar_versiones.py 02-Datos/escuela-salud.json --borrar
"""
import os, sys, json, shutil

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRABAJO = ("04-Post-Story", "05-Pruebas")


def cache_vigente(data):
    """Nombres de _expandidas que los parametros actuales todavia usan."""
    vivos = set()
    for c in data["carreras"]:
        foto = c.get("foto")
        if not foto:
            continue
        base, ext = os.path.splitext(os.path.basename(foto))
        for tag in ("post", "story"):
            arriba = c.get("expandir_arriba_" + tag) or c.get("expandir_arriba")
            lados = c.get("expandir_lados_" + tag) or c.get("expandir_lados")
            abajo = c.get("expandir_abajo_" + tag) or c.get("expandir_abajo")
            if not (arriba or lados or abajo):
                continue
            vivos.add("%s-a%s-l%s%s%s" % (base, arriba or 0, lados or 0,
                                          ("-b%s" % abajo) if abajo else "", ext))
    return vivos


if __name__ == "__main__":
    ruta = sys.argv[1]
    if not os.path.isabs(ruta):
        ruta = os.path.join(REPO, ruta)
    borrar = "--borrar" in sys.argv
    data = json.load(open(ruta, encoding="utf-8"))

    objetivos = []
    for carpeta in TRABAJO:
        d = os.path.join(REPO, carpeta)
        if os.path.isdir(d):
            n = sum(len(f) for _, _, f in os.walk(d))
            objetivos.append((d, n, "carpeta de trabajo"))

    exp = os.path.join(REPO, "03-Fotografias", "_expandidas")
    vivos = cache_vigente(data)
    if os.path.isdir(exp):
        for f in sorted(os.listdir(exp)):
            if f not in vivos:
                objetivos.append((os.path.join(exp, f), 1, "cache obsoleto"))

    total = 0
    for p, n, motivo in objetivos:
        total += n
        rel = os.path.relpath(p, REPO)
        if borrar:
            shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
            print("borrado  %-62s %s" % (rel, motivo))
        else:
            print("borraria %-62s %s (%d archivos)" % (rel, motivo, n))

    print()
    print("%s %d archivos" % ("borrados:" if borrar else "se borrarian:", total))
    if not borrar:
        print("(pasa --borrar para ejecutar)")
    print("cache vigente que se conserva:", len(vivos), "archivos")
