#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audita los encuadres vigentes contra el techo real de la plantilla V.2.

No resuelve nada: toma los parametros que YA estan en el JSON de escuela,
replica la aritmetica de capa_fotos_ipg y dice donde cae el pelo y el menton
de cada pieza. Sirve para saber cuales hay que volver a resolver despues de
un cambio de plantilla, sin tener que mirar 166 archivos a ojo.

Por que hace falta: la V.2 metio la pastilla de modalidad *encima* del
prefijo. El techo del bloque de texto ya no es la primera linea del titulo
sino esa pastilla, que ademas sube junto con el titulo cuando el nombre se
parte en dos lineas. Los encuadres de las 43 carreras se resolvieron contra
el techo de la V.1.

    python 00-Scripts/verificar_encuadres.py 02-Datos/escuela-salud.json
    python 00-Scripts/verificar_encuadres.py --todas
"""
import os, sys, json, glob

BASE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(BASE)
sys.path.insert(0, BASE)

import solver_encuadre as sol

# Techo por defecto cuando no hay medicion: el borde superior de la pastilla
# de modalidad en la plantilla V.2, con titulo de una linea.
TECHO = {"post": 433, "story": 700}


def medidas_de(escuela):
    ruta = os.path.join(REPO, "02-Datos", "medidas-%s.json" % escuela)
    if not os.path.exists(ruta):
        return {}
    return json.load(open(ruta, encoding="utf-8"))


def titulos_de(escuela):
    ruta = os.path.join(REPO, "02-Datos", "titulos-%s.json" % escuela)
    if not os.path.exists(ruta):
        return {}
    return json.load(open(ruta, encoding="utf-8"))


def evaluar(m, z, tag, lados, arriba, abajo, techo_txt):
    """Donde caen pelo, menton y centro de la cara con estos parametros."""
    nw, nh = m["ancho"], m["alto"]
    nw1, nh3, extra_l, extra_a = sol.expandir(nw, nh, lados, arriba, abajo)
    s = max(z["cw"] / nw1, z["ch"] / nh3)
    sw, sh = nw1 * s, nh3 * s
    fx = (extra_l + m["cara_x"] * nw) / nw1
    tx = min(0.0, max(z["cw"] - sw, sum(z["silueta"]) / 2.0 - sw * fx))
    fy = fyt = z["ancla"]
    ty = min(0.0, max(z["ch"] - sh, z["ch"] * fyt - sh * fy))
    return (ty + (m["pelo"] * nh + extra_a) * s,
            ty + (m["menton"] * nh + extra_a) * s,
            tx + sw * fx)


def auditar(ruta):
    data = json.load(open(ruta, encoding="utf-8"))
    escuela = os.path.basename(ruta).replace("escuela-", "").replace(".json", "")
    medidas, titulos = medidas_de(escuela), titulos_de(escuela)

    filas, vistas = [], set()
    for c in data["carreras"]:
        if c["carpeta"] in vistas:
            continue
        vistas.add(c["carpeta"])
        m = medidas.get(c["carpeta"])
        if not m or "pelo" not in m:
            filas.append((c["carpeta"], None, None, None, None, "sin medidas"))
            continue
        for tag, z in (("post", sol.POST), ("story", sol.STORY)):
            techo_txt = (titulos.get(c["carpeta"], {}) or {}).get(tag) or TECHO[tag]
            pelo, menton, cara_x = evaluar(
                m, z, tag,
                c.get("expandir_lados_" + tag) or 0,
                c.get("expandir_arriba_" + tag) or 0,
                c.get("expandir_abajo_" + tag) or 0,
                techo_txt)
            aire = techo_txt - menton
            minimo = sol.AIRE_DOS_LINEAS[tag] if techo_txt < TECHO[tag] - 20 \
                else sol.AIRE[tag]
            if aire < 0:
                estado = "CHOCA"
            elif aire < minimo:
                estado = "justo"
            elif pelo < z["pelo_min"]:
                estado = "pelo alto"
            else:
                estado = "ok"
            filas.append((c["carpeta"], tag, int(pelo), int(menton),
                          int(aire), estado))
    return escuela, filas


if __name__ == "__main__":
    rutas = (sorted(glob.glob(os.path.join(REPO, "02-Datos", "escuela-*.json")))
             if "--todas" in sys.argv else
             [os.path.join(REPO, sys.argv[1]) if not os.path.isabs(sys.argv[1])
              else sys.argv[1]])

    resumen = {}
    for ruta in rutas:
        escuela, filas = auditar(ruta)
        print("\n===== %s =====" % escuela)
        for carpeta, tag, pelo, menton, aire, estado in filas:
            if tag is None:
                print("%-42s %s" % (carpeta, estado))
                continue
            print("%-42s %-5s pelo %4d  menton %4d  aire %4d  %s"
                  % (carpeta, tag, pelo, menton, aire, estado))
            resumen[estado] = resumen.get(estado, 0) + 1

    print("\n--- resumen ---")
    for k in sorted(resumen):
        print("%-10s %d" % (k, resumen[k]))
