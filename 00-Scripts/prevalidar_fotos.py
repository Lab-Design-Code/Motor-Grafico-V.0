#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Descarta candidatas de banco ANTES de gastar la licencia.

El problema que resuelve: a lo largo de la campana se compraron seis fotos que
no tenian encuadre posible en el Post y hubo que reemplazarlas con la licencia
ya consumida. La regla del 0,30 se puede evaluar sobre la miniatura publica,
que es gratis, y eso basta para descartar lo imposible.

Toma la miniatura de 260 px que Shutterstock sirve abierta, detecta el rostro,
deduce las medidas que pide el solver y le pregunta si existe encuadre para el
Post y para el Story de esa carrera.

    python 00-Scripts/prevalidar_fotos.py <carpeta-carrera> <archivo-con-nombres>

QUE TAN FIABLE ES
-----------------
Es un **prefiltro, no una medicion**. El detector devuelve una caja que va de
la frente al menton, no del pelo al menton, asi que el tope del pelo se estima
restando un cuarto de la altura de la caja. El propio LEEME advierte que
estimar estas medidas a ojo fue lo que dejo el prefijo cruzando la mandibula
en varias piezas.

Sirve para lo que sirve: si aqui sale SIN SOLUCION, comprarla es tirar la
licencia. Si sale OK, hay que medirla igual con grilla_fina.py sobre el
archivo comprado antes de dar el encuadre por bueno.
"""
import os, sys, json, glob

BASE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(BASE)
sys.path.insert(0, BASE)

import solver_encuadre as sol

# La caja del detector arranca en la frente. El pelo sube aproximadamente un
# cuarto de la altura de la caja por encima de ese borde.
PELO_SOBRE_CAJA = 0.25


def medir(path):
    """(pelo, menton, cara_x) en fracciones de la imagen, o None."""
    import cv2
    im = cv2.imread(path)
    if im is None:
        return None
    h, w = im.shape[:2]
    gris = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    gris = cv2.equalizeHist(gris)
    casc = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    caras = casc.detectMultiScale(gris, scaleFactor=1.08, minNeighbors=6,
                                  minSize=(int(h * 0.06), int(h * 0.06)))
    if len(caras) == 0:
        return None
    # cuando hay varias, manda la mas grande: es el sujeto principal
    x, y, cw, ch = max(caras, key=lambda c: c[2] * c[3])
    pelo = max(0.0, (y - ch * PELO_SOBRE_CAJA) / h)
    menton = min(1.0, (y + ch) / h)
    return {"ancho": w, "alto": h, "pelo": round(pelo, 4),
            "menton": round(menton, 4), "cara_x": round((x + cw / 2.0) / w, 4),
            "rostro_frac": round(ch * (1 + PELO_SOBRE_CAJA) / h, 3),
            "n_caras": len(caras)}


def evaluar(m, titulo_post, titulo_story):
    """Corre el solver para los dos formatos con los techos de esta carrera."""
    out = {}
    for tag, z, techo in (("post", sol.POST, titulo_post),
                          ("story", sol.STORY, titulo_story)):
        mm = dict(m)
        mm["titulo_" + tag] = techo
        r = sol.resolver(mm, z, techo < sol.POST["titulo"] if tag == "post"
                         else techo < sol.STORY["titulo"])
        out[tag] = r
    return out


def veredicto(m, res):
    if m["rostro_frac"] > 0.30:
        return "RECHAZA", "rostro %.2f del alto (regla del 0,30)" % m["rostro_frac"]
    faltan = [t for t in ("post", "story") if not res[t]]
    if faltan:
        return "RECHAZA", "sin encuadre en " + "+".join(faltan)
    if m["n_caras"] > 1:
        return "REVISAR", "%d rostros: hay que elegir sujeto" % m["n_caras"]
    return "SIRVE", "post y story resueltos"


if __name__ == "__main__":
    carpeta = sys.argv[1]
    lista = sys.argv[2]
    tp = int(sys.argv[3]) if len(sys.argv) > 3 else 433
    ts = int(sys.argv[4]) if len(sys.argv) > 4 else 700

    fotos = sorted(glob.glob(os.path.join(carpeta, "*.jpg")))
    print("%-24s %-7s %-7s %-7s %-6s %-8s %s" %
          ("id", "rostro", "pelo", "menton", "caraX", "estado", "motivo"))
    salida = {}
    for p in fotos:
        ident = os.path.basename(p).replace(".jpg", "").split("-")[-1]
        m = medir(p)
        if not m:
            print("%-24s %s" % (ident, "sin rostro detectado"))
            salida[ident] = {"estado": "SIN ROSTRO"}
            continue
        res = evaluar(m, tp, ts)
        est, motivo = veredicto(m, res)
        print("%-24s %-7.2f %-7.2f %-7.2f %-6.2f %-8s %s" %
              (ident, m["rostro_frac"], m["pelo"], m["menton"], m["cara_x"],
               est, motivo))
        salida[ident] = {"estado": est, "motivo": motivo, "medidas": m}

    destino = os.path.join(carpeta, "_veredicto.json")
    json.dump(salida, open(destino, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    sirven = sum(1 for v in salida.values() if v.get("estado") == "SIRVE")
    print("\n%d candidatas · %d sirven · veredicto en %s"
          % (len(salida), sirven, destino))
