#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Resuelve Post y Story de las 18 fotos que cargo Marketing.

Las medidas se leyeron a ojo sobre la grilla, no con el detector: Haar elegia
al acompañante en primer plano en vez del protagonista en ocho de las 18.

El barrido va **vectorizado con numpy sobre el eje `abajo`**. La version con
tres bucles anidados en Python puro son unos 10 millones de combinaciones por
carrera y no termina: se dejo corriendo y no alcanzo a resolver ni la primera.

El Post usa paso fino en `arriba` (0,005): con rostros grandes la franja de
valores validos es mas angosta que el paso grueso de 0,02 y la busqueda pasa
por encima sin verla.

El Story usa el criterio corregido: el recorte lateral solo puede comerse
margen generado por Firefly, nunca la fotografia original, o parte a las
personas de los extremos.
"""
import io, os, sys, json, glob
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "00-Scripts"))
import solver_encuadre as sol

AQUI = os.path.dirname(os.path.abspath(__file__))
HOLGURA = 8

# carrera: (ancho, alto, pelo, menton, cara_x)
# Leidas sobre grillas/grilla-NN.jpg, eligiendo un solo sujeto por foto.
MED = {
  "Rehabilitacion-de-Dependencia-de-Drogas": (2000, 1055, 0.090, 0.280, 0.480),
  "Educacion-Basica-y-Parvularia":           (2000, 1333, 0.045, 0.235, 0.820),
  "Educacion-Parvularia":                    (2000, 1055, 0.045, 0.240, 0.790),
  "Psicopedagogia":                          (2000, 1334, 0.100, 0.330, 0.420),
  "Educacion-Basica":                        (2000, 1491, 0.045, 0.320, 0.710),
  "Podologia":                               (2000, 1335, 0.320, 0.530, 0.460),
  "Enfermeria":                              (1385, 2000, 0.040, 0.310, 0.420),
  "Prevencion-de-Riesgos":                   (2000, 1125, 0.145, 0.400, 0.790),
  "Inteligencia-Artificial":                 (2000, 1333, 0.190, 0.355, 0.455),
  "Instrumentacion-Industrial":              (2000, 1333, 0.435, 0.550, 0.720),
  "Ingenieria-Industrial":                   (2000, 1331, 0.040, 0.285, 0.360),
  "Farmacias":                               (2000, 2000, 0.125, 0.305, 0.780),
  "Administracion-de-Centros-de-Salud":      (2000, 1125, 0.275, 0.465, 0.570),
  "Gestion-Comercial-y-Ventas":              (2000, 1125, 0.125, 0.325, 0.820),
  "Educacion-Diferencial":                   (1334, 2000, 0.190, 0.320, 0.710),
  "Comercio-Exterior":                       (2000, 1055, 0.300, 0.400, 0.740),
  "Administracion-Publica":                  (2000, 1292, 0.060, 0.350, 0.690),
  "Trabajo-Social":                          (2000, 1333, 0.075, 0.330, 0.780),
}

TECHOS = {}
for r in glob.glob(os.path.join(REPO, "02-Datos", "medidas-*.json")):
    for k, v in json.load(io.open(r, encoding="utf-8")).items():
        if isinstance(v, dict) and "titulo_post" in v:
            TECHOS[k] = (v["titulo_post"], v["titulo_story"])


def barrer(m, z, techo, tag, lados_max, paso_lados, arr_max, paso_arr,
           ab_max, paso_ab):
    """Barre lados y arriba en Python, y abajo entero con numpy."""
    aire_min = (sol.AIRE_DOS_LINEAS if techo < z["titulo"] else sol.AIRE)[tag]
    w, h = m["ancho"], m["alto"]
    objetivo = sum(z["silueta"]) / 2.0
    abajo = np.arange(0.0, ab_max + 1e-9, paso_ab)

    mejor = None
    lados = 0.0
    while lados <= lados_max + 1e-9:
        extra_l = int(w * lados / 2) if lados else 0
        nw1 = w + 2 * extra_l
        fx = (extra_l + m["cara_x"] * w) / float(nw1)
        arriba = 0.0
        while arriba <= arr_max + 1e-9:
            extra_a = int(h * arriba) if arriba else 0
            nh2 = h + extra_a
            nh3 = nh2 + (nh2 * abajo).astype(np.int64)

            grandes = nw1 * nh3 > sol.MAX_PIXELES
            s = np.maximum(z["cw"] / float(nw1), z["ch"] / nh3.astype(np.float64))
            sw = nw1 * s
            sh = nh3 * s

            if tag == "post":
                tx = np.minimum(0.0, np.maximum(z["cw"] - sw, objetivo - sw * fx))
                ty = np.minimum(0.0, z["ch"] - sh)
            else:
                tx = np.minimum(0.0, np.maximum(z["cw"] - sw,
                                                z["cw"] * 0.6759 - sw * fx))
                ty = np.minimum(0.0, np.maximum(z["ch"] - sh, 0.0))

            pelo = ty + (m["pelo"] * h + extra_a) * s
            menton = ty + (m["menton"] * h + extra_a) * s
            cara = tx + sw * fx

            ok = (~grandes) & (pelo >= z["pelo_min"]) & (techo - menton >= aire_min)
            ok &= (cara >= z["silueta"][0]) & (cara <= z["silueta"][1])
            if tag == "story":
                x0 = -tx / s
                x1 = x0 + z["cw"] / s
                ok &= (x0 <= extra_l + HOLGURA) & (x1 >= extra_l + w - HOLGURA)

            if ok.any():
                i = int(np.argmax(np.where(ok, s, -1.0)))
                if mejor is None or s[i] > mejor[0]:
                    mejor = (float(s[i]), lados, arriba, float(abajo[i]),
                             float(pelo[i]), float(menton[i]), float(cara[i]))
            arriba += paso_arr
        lados += paso_lados
    return mejor


salida = {}
faltan = []
for nombre in sorted(MED):
    w, h, pelo, menton, cx = MED[nombre]
    tp, ts = TECHOS.get(nombre, (433, 700))
    m = {"ancho": w, "alto": h, "pelo": pelo, "menton": menton, "cara_x": cx,
         "titulo_post": tp, "titulo_story": ts}
    b = {}

    r = barrer(m, sol.POST, tp, "post", 4.0, 0.05, 1.6, 0.005, 2.0, 0.005)
    if r:
        s, lados, arriba, abajo, p, mt, cara = r
        if lados: b["expandir_lados_post"] = round(lados, 3)
        if arriba: b["expandir_arriba_post"] = round(arriba, 3)
        if abajo: b["expandir_abajo_post"] = round(abajo, 3)
        b["focal_post"] = list(sol.focal(m, sol.POST, lados, arriba, abajo))
        print("%-42s post  l%.2f a%.3f b%.3f  pelo %3d menton %3d aire %3d"
              % (nombre, lados, arriba, abajo, p, mt, tp - mt))
    else:
        print("%-42s post  SIN SOLUCION" % nombre)
        faltan.append(nombre + " post")

    c = barrer(m, sol.STORY, ts, "story", 2.5, 0.05, 2.5, 0.02, 4.0, 0.02)
    if c:
        s, lados, arriba, abajo, p, mt, cara = c
        if lados: b["expandir_lados_story"] = round(lados, 3)
        if arriba: b["expandir_arriba_story"] = round(arriba, 3)
        if abajo: b["expandir_abajo_story"] = round(abajo, 3)
        b["focal_story"] = list(sol.focal(m, sol.STORY, lados, arriba, abajo))
        print("%-42s story l%.2f a%.2f b%.2f  pelo %3d menton %3d aire %3d"
              % ("", lados, arriba, abajo, p, mt, ts - mt))
    else:
        print("%-42s story SIN SOLUCION" % "")
        faltan.append(nombre + " story")
    salida[nombre] = b

json.dump(salida, io.open(os.path.join(AQUI, "encuadres-v3.json"), "w",
                          encoding="utf-8"), ensure_ascii=False, indent=2)
print("\n%d carreras · %d piezas sin solucion" % (len(salida), len(faltan)))
if faltan:
    print("  " + ", ".join(faltan))
