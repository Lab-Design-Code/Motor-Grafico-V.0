#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Resuelve una carrera suelta y deja las cifras en pixeles para Firefly.

    python una_resolver.py <Carpeta-Carrera> <Escuela> <pelo> <menton> <cara_x>
"""
import io, os, sys, json, glob
from PIL import Image

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(REPO, "00-Scripts"))
sys.path.insert(0, AQUI)
import solver_encuadre as sol
from resolver_v3 import barrer

carrera, escuela = sys.argv[1], sys.argv[2]
pelo, menton, cx = (float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]))

FOTO = os.path.join(REPO, "03-Fotografias", escuela, carrera, carrera + ".jpg")
W, H = Image.open(FOTO).size

TECHOS = {}
for r in glob.glob(os.path.join(REPO, "02-Datos", "medidas-*.json")):
    for k, v in json.load(io.open(r, encoding="utf-8")).items():
        if isinstance(v, dict) and "titulo_post" in v:
            TECHOS[k] = (v["titulo_post"], v["titulo_story"])
tp, ts = TECHOS.get(carrera, (433, 700))

m = {"ancho": W, "alto": H, "pelo": pelo, "menton": menton, "cara_x": cx,
     "titulo_post": tp, "titulo_story": ts}
print("\n%s  %dx%d  peso %d  techos %d / %d"
      % (carrera, W, H, os.path.getsize(FOTO), tp, ts))

b = {}
r = barrer(m, sol.POST, tp, "post", 4.0, 0.05, 1.6, 0.005, 2.0, 0.005)
if not r:
    print("post  SIN SOLUCION")
    lp = ap = bp = 0
else:
    s, lp, ap, bp, p, mt, ca = r
    if lp: b["expandir_lados_post"] = round(lp, 3)
    if ap: b["expandir_arriba_post"] = round(ap, 3)
    if bp: b["expandir_abajo_post"] = round(bp, 3)
    b["focal_post"] = list(sol.focal(m, sol.POST, lp, ap, bp))
    print("post  l%.2f a%.3f b%.3f  pelo %3d menton %3d aire %3d"
          % (lp, ap, bp, p, mt, tp - mt))

c = barrer(m, sol.STORY, ts, "story", 2.5, 0.05, 2.5, 0.02, 4.0, 0.02)
if not c:
    print("story SIN SOLUCION")
    ls = asy = bs = 0
else:
    s, ls, asy, bs, p2, mt2, ca2 = c
    if ls: b["expandir_lados_story"] = round(ls, 3)
    if asy: b["expandir_arriba_story"] = round(asy, 3)
    if bs: b["expandir_abajo_story"] = round(bs, 3)
    b["focal_story"] = list(sol.focal(m, sol.STORY, ls, asy, bs))
    print("story l%.2f a%.2f b%.2f  pelo %3d menton %3d aire %3d"
          % (ls, asy, bs, p2, mt2, ts - mt2))

json.dump({carrera: b}, io.open(os.path.join(AQUI, "encuadres-una.json"), "w",
                                encoding="utf-8"), ensure_ascii=False, indent=2)
print("")
for tag, (ll, aa, bb) in (("post", (lp, ap, bp)), ("story", (ls, asy, bs))):
    el = int(W * ll / 2) if ll else 0
    ea = int(H * aa) if aa else 0
    nh2 = H + ea
    eb = int(nh2 * bb) if bb else 0
    print("%-6s L/R %4d  arriba %4d  abajo %4d -> %dx%d"
          % (tag, el, ea, eb, W + 2 * el, nh2 + eb))
