#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Resuelve el Post con barrido fino cuando el grueso no encuentra nada.

El solver recorre `arriba` y `abajo` de 0,02 en 0,02. Cuando el rostro es
grande, la franja de valores validos llega a ser mas angosta que ese paso y la
busqueda pasa por encima sin verla: Minas, Operaciones de Planta Minera e
Informatica y Ciberseguridad daban SIN SOLUCION por eso, no por la fotografia.

Aca se repite el barrido con paso 0,005 sobre los tres ejes.
"""
import os, sys, json
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "00-Scripts"))
import solver_encuadre as sol

ancho, alto = int(sys.argv[1]), int(sys.argv[2])
pelo, menton, cara_x = float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5])
techo = int(sys.argv[6])

z = sol.POST
m = {"ancho": ancho, "alto": alto, "pelo": pelo, "menton": menton,
     "cara_x": cara_x, "titulo_post": techo}
aire_min = (sol.AIRE_DOS_LINEAS if techo < z["titulo"] else sol.AIRE)["post"]
objetivo = sum(z["silueta"]) / 2.0

mejor = None
for li in range(0, 301, 5):
    lados = li / 100.0
    for ai in range(0, 1201, 5):
        arriba = ai / 1000.0
        for bi in range(0, 1601, 5):
            abajo = bi / 1000.0
            nw1, nh3, extra_l, extra_a = sol.expandir(ancho, alto, lados, arriba, abajo)
            if nw1 * nh3 > sol.MAX_PIXELES:
                continue
            s = max(z["cw"] / nw1, z["ch"] / nh3)
            sw, sh = nw1 * s, nh3 * s
            fx = (extra_l + cara_x * ancho) / nw1
            tx = min(0.0, max(z["cw"] - sw, objetivo - sw * fx))
            ty = min(0.0, max(z["ch"] - sh, z["ch"] - sh))
            p = ty + (pelo * alto + extra_a) * s
            mt = ty + (menton * alto + extra_a) * s
            cara = tx + sw * fx
            if p < z["pelo_min"] or techo - mt < aire_min:
                continue
            if not (z["silueta"][0] <= cara <= z["silueta"][1]):
                continue
            if mejor is None or s > mejor[0]:
                mejor = (s, lados, arriba, abajo, p, mt, cara)

if not mejor:
    print("SIN SOLUCION ni con paso fino")
else:
    s, lados, arriba, abajo, p, mt, cara = mejor
    print("post  lados %.2f arriba %.3f abajo %.3f -> pelo %4d menton %4d "
          "caraX %4d (aire %d)" % (lados, arriba, abajo, p, mt, cara, techo - mt))
    out = {}
    if lados: out["expandir_lados_post"] = lados
    if arriba: out["expandir_arriba_post"] = arriba
    if abajo: out["expandir_abajo_post"] = abajo
    out["focal_post"] = list(sol.focal(m, z, lados, arriba, abajo))
    print(json.dumps(out, ensure_ascii=False))
