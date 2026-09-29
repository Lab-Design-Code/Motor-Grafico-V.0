#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Resuelve el encuadre de una foto contra las zonas seguras.

Replica exactamente la aritmetica de capa_fotos_ipg -- incluidos los int() de
cada expansion, que redondean hacia abajo -- y busca la combinacion de
expansiones y punto focal que cumple las tres restricciones:

  1. el tope del pelo cae bajo el bloque del logo,
  2. el menton queda sobre la primera linea del titulo,
  3. la cabeza cae dentro de la caja de silueta, que en ambos formatos esta
     corrida a la derecha para dejar libre el margen izquierdo.

De todas las combinaciones validas elige la de mayor escala, es decir la que
deja el rostro lo mas grande posible.

Dos trampas que el solver contempla y que a mano se olvidan:

- Cuando el nombre no cabe en una linea el generador parte el titulo en dos y
  sube el bloque completo una interlinea (~73 px en Post, ~85 en Story), asi
  que el techo del menton baja otro tanto. Se declara con dos_lineas=True.
- `expandir_lados` no solo achica al sujeto: es lo unico que da recorrido
  horizontal. Sin ancho sobrante el cover no puede correr la foto lo suficiente
  para llevar la cabeza hasta la caja de silueta, y el clamp la deja a medio
  camino contra el borde.

Uso:
    python 00-Scripts/solver_encuadre.py 02-Datos/medidas-salud.json
"""
import os, sys, json

# El aire entre el menton y la primera linea del titulo. 30 px cumplian la regla
# pero se leian como texto pegado a la mandibula: el rostro tiene que quedar
# visiblemente despejado, no apenas fuera de la caja de texto.
#
# Se pide menos aire cuando el titulo va a dos lineas, y no por comodidad: ese
# titulo sube el bloque ~73 px y deja una ventana vertical de 116 px contra los
# 190 de un titulo corto. Exigir el mismo aire ahi obliga a achicar tanto al
# sujeto que queda como una figura lejana -- peor que el problema que resuelve.
AIRE = {"post": 70, "story": 90}
AIRE_DOS_LINEAS = {"post": 50, "story": 70}

# Tope de pixeles de la foto expandida.
#
# Existia por el metodo por reflejo: ese construye la foto expandida entera en
# memoria, y pasado cierto tamano la imagen es casi todo relleno y Pillow la
# rechaza como decompression bomb.
#
# Con expansion generativa (Firefly) el lienzo se genera sobre una version
# reducida de la foto —unos 2400 px de alto— y lo unico que viaja es la
# PROPORCION de la expansion, no su tamano absoluto. Ahi el tope no corresponde
# y ademas descarta encuadres perfectamente validos: Podologia daba SIN
# SOLUCION en el Post solo por esto, cuando en realidad se resuelve con 72 px
# de aire (lienzo teorico de 230 MP, que Firefly nunca tiene que materializar).
#
# Se deja alto. Quien use el camino por reflejo debe bajarlo a 180_000_000.
MAX_PIXELES = 1_000_000_000

# `titulo` es el techo del bloque de texto cuando el nombre entra en una linea.
# En la V.2 ese techo ya no es la primera linea del titulo sino el borde
# superior de la pastilla de modalidad, que cuelga sobre el prefijo: 433 en el
# Post y 700 en el Story, medidos con medir_titulo.py sobre la pieza sin foto.
# Contra la V.1 (465 y 763) la ventana se achico 32 y 63 px respectivamente, y
# por eso los encuadres de la campana anterior quedan todos justos.
POST = {
    "cw": 1080, "ch": 1080, "ancla": 1,
    "pelo_min": 205, "titulo": 433, "silueta": (600, 960),
}
STORY = {
    "cw": 1080, "ch": 1920, "ancla": 0,
    "pelo_min": 300, "titulo": 700, "silueta": (445, 1015),
}


def expandir(nw, nh, lados, arriba, abajo):
    """Devuelve el tamano expandido y cuanto se corrio el origen."""
    extra_l = int(nw * lados / 2) if lados else 0
    nw1 = nw + 2 * extra_l
    extra_a = int(nh * arriba) if arriba else 0
    nh2 = nh + extra_a
    extra_b = int(nh2 * abajo) if abajo else 0
    return nw1, nh2 + extra_b, extra_l, extra_a


def techo_menton(m, z, tag):
    """Hasta donde puede bajar el menton en este formato.

    Sale de la posicion real del titulo -- medida por medir_titulo.py sobre la
    pieza renderizada sin foto -- menos el aire exigido. No se estima, porque un
    nombre que se parte en dos lineas sube el bloque completo una interlinea que
    a su vez depende del cuerpo ya autoajustado.
    """
    titulo = m.get("titulo_" + tag, z["titulo"])
    dos_lineas = titulo < z["titulo"]
    aire = (AIRE_DOS_LINEAS if dos_lineas else AIRE)[tag]
    return titulo - aire


def evaluar(m, z, lados, arriba, abajo, dos_lineas):
    nw, nh = m["ancho"], m["alto"]
    nw1, nh3, extra_l, extra_a = expandir(nw, nh, lados, arriba, abajo)
    if nw1 * nh3 > MAX_PIXELES:
        return False, 0, 0, 0, 0, 0

    s = max(z["cw"] / nw1, z["ch"] / nh3)
    sw, sh = nw1 * s, nh3 * s

    # el punto focal se mide sobre la imagen YA expandida
    fx = (extra_l + m["cara_x"] * nw) / nw1

    objetivo = sum(z["silueta"]) / 2.0
    tx = objetivo - sw * fx                      # tx que dejaria la cara en el objetivo
    tx = min(0.0, max(z["cw"] - sw, tx))         # el cover no permite huecos
    cara_x = tx + sw * fx

    fy = fyt = z["ancla"]
    ty = min(0.0, max(z["ch"] - sh, z["ch"] * fyt - sh * fy))
    pelo = ty + (m["pelo"] * nh + extra_a) * s
    menton = ty + (m["menton"] * nh + extra_a) * s

    techo = techo_menton(m, z, "post" if z["ch"] == 1080 else "story")
    sx, sx2 = z["silueta"]
    ok = (pelo >= z["pelo_min"] and menton <= techo
          and sx <= cara_x <= sx2)
    return ok, s, pelo, menton, cara_x, (objetivo + sw * fx - sw * fx)


def resolver(m, z, dos_lineas, tolerancia=70):
    """Entre los encuadres validos prefiere los que dejan la cabeza centrada en
    la silueta, y solo entre esos maximiza la escala.

    Maximizar la escala a secas no basta: el clamp del cover permite soluciones
    donde la cara apenas entra por el borde izquierdo de la caja, tecnicamente
    validas pero descentradas. Centrar cuesta ancho -- es decir `lados` -- y
    por lo tanto escala, asi que el orden de preferencia tiene que ser
    explicito. Si nada cae dentro de la tolerancia se relaja a la caja completa.
    """
    objetivo = sum(z["silueta"]) / 2.0
    centrados, cualquiera = None, None
    for lados in [i / 100 for i in range(0, 301, 5)]:
        for arriba in [i / 100 for i in range(0, 121, 2)]:
            for abajo in [i / 100 for i in range(0, 81, 2)]:
                ok, s, pelo, menton, cara_x, _ = evaluar(
                    m, z, lados, arriba, abajo, dos_lineas)
                if not ok:
                    continue
                r = {"escala": s, "lados": lados, "arriba": arriba,
                     "abajo": abajo, "pelo": pelo, "menton": menton,
                     "cara_x": cara_x}
                if cualquiera is None or s > cualquiera["escala"]:
                    cualquiera = r
                if abs(cara_x - objetivo) <= tolerancia:
                    if centrados is None or s > centrados["escala"]:
                        centrados = r
    return centrados or cualquiera


def focal(m, z, lados, arriba, abajo):
    nw, nh = m["ancho"], m["alto"]
    nw1, _, extra_l, _ = expandir(nw, nh, lados, arriba, abajo)
    fx = (extra_l + m["cara_x"] * nw) / nw1
    fxt = (sum(z["silueta"]) / 2.0) / z["cw"]
    return round(fx, 4), z["ancla"], round(fxt, 4), z["ancla"]


if __name__ == "__main__":
    ruta = sys.argv[1]
    if not os.path.isabs(ruta):
        ruta = os.path.join(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))), ruta)
    medidas = json.load(open(ruta, encoding="utf-8"))

    salida = {}
    for nombre, m in medidas.items():
        if nombre.startswith("_"):
            continue
        bloque = {}
        for tag, z in (("post", POST), ("story", STORY)):
            r = resolver(m, z, m.get("dos_lineas", False))
            if not r:
                print("%-42s %-5s SIN SOLUCION" % (nombre, tag))
                continue
            if r["lados"]:
                bloque["expandir_lados_" + tag] = r["lados"]
            if r["arriba"]:
                bloque["expandir_arriba_" + tag] = r["arriba"]
            if r["abajo"]:
                bloque["expandir_abajo_" + tag] = r["abajo"]
            bloque["focal_" + tag] = list(
                focal(m, z, r["lados"], r["arriba"], r["abajo"]))
            print("%-42s %-5s lados %.2f arriba %.2f abajo %.2f -> pelo %4d menton %4d cara_x %4d"
                  % (nombre, tag, r["lados"], r["arriba"], r["abajo"],
                     r["pelo"], r["menton"], r["cara_x"]))
        salida[nombre] = bloque

    # el nombre de salida se deriva del de entrada: tenerlo fijo hacia que
    # resolver una escuela pisara los encuadres de otra
    base = os.path.basename(ruta)
    sufijo = base.split("-", 1)[1] if "-" in base else base
    destino = os.path.join(os.path.dirname(ruta), "encuadres-" + sufijo)
    json.dump(salida, open(destino, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print("\nescrito:", destino)
