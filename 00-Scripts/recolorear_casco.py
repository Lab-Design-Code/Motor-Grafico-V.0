#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pasa un casco de color a blanco, sobre la foto a resolucion plena.

No hay relleno generativo en esta sesion, asi que el casco no se "reemplaza":
se recolorea. Adobe entrega la mascara y aca se aplica.

TRES COSAS QUE SE HICIERON MAL EN EL PRIMER INTENTO
---------------------------------------------------

1. **Mascara de 1600 px ampliada a 5472.** Un factor de 3,4x deja el borde
   blando: el contorno del casco quedaba difuminado contra el pelo y el fondo.
   Ahora la mascara se pide sobre la copia de 3600 px que ya se usa para
   Firefly, y el ampliado es de 1,5x.

2. **Dilatar la mascara.** Se dilataba 18 px para tapar un canto naranjo, y de
   paso el blanco se derramaba sobre la piel bajo el ala: eso era el velo gris
   sobre la frente y la ceja. No se dilata; el emplumado minimo basta.

3. **Estirar la luminancia a [152, 248].** Eso llevaba tambien la sombra bajo
   el ala y la banda interior oscura a gris claro, y el resultado se leia como
   una visera translucida. Un casco blanco no aclara las sombras: refleja mas
   luz. Por eso ahora se aplica una **ganancia multiplicativa**. Lo oscuro
   sigue oscuro.

La ganancia es la razon de reflectancias, no un percentil de la mascara: se
probo derivarla del percentil y falla, porque los reflejos especulares del
casco naranjo empujan los percentiles altos y la ganancia sale corta —el casco
quedaba gris metalico—. Un casco blanco refleja ~0,85 de la luz, uno amarillo
~0,68 y uno naranjo ~0,36, asi que las razones son ~1,25 y ~2,35.

Los altos se comprimen con una rodilla en 200 en vez de recortarse en 255: sin
eso la cascara al sol se satura en un blanco plano y se pierde el relieve.
"""
import io, os, sys, urllib.request
import numpy as np
from PIL import Image, ImageFilter

AQUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOTOS = os.path.join(REPO, "03-Fotografias")
TRABAJO = os.path.join(AQUI, "retoque")

# La base es siempre la foto sin retocar, respaldada al instalar la primera
# version: recolorear sobre lo ya recoloreado acumula error.
ORIG = os.path.join(FOTOS, "_V2-0-sin-retoque")

# carrera: (destino, url de la mascara de 3600 px, ganancia, dilatacion)
#
# La ganancia es blanco/color de origen en reflectancia: 0,85/0,68 para el
# amarillo y 0,85/0,36 para el naranjo.
#
# La dilatacion es el canto inferior del casco, que el segmentador deja fuera y
# que asomaba como una astilla naranja. Van 4 px, no 18: con 18 el blanco se
# derramaba sobre la frente.
TAREAS = {
    "Construccion-Civil": (
        os.path.join(FOTOS, "Escuela de Ingenieria y Tecnologia",
                     "Construccion-Civil", "Construccion-Civil.jpg"),
        "https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:3b58a072-13f4-40f2-a43d-ea36162f003b",
        1.25, 0),
    "Minas": (
        os.path.join(FOTOS, "Escuela de Ingenieria y Tecnologia",
                     "Minas", "Minas.jpg"),
        "https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:5e671fb0-f956-48e6-be34-35b598d7cd83",
        2.35, 9),
}

RODILLA = 200.0     # desde aca los altos se comprimen en vez de recortarse
PLUMA = 0.0006      # emplumado del borde, en fraccion del lado corto
CROMA = 0.05        # resto de color que se deja, para que no quede plano

# SOBRE LA BANDA INTERIOR DEL CASCO
# ---------------------------------
# El segmentador devuelve solo la cascara: el plastico interior que apoya en la
# frente queda fuera y asoma como una linea naranja bajo el casco blanco.
#
# Se intento agregarlo por color, con un umbral de saturacion: el plastico mide
# 0,72 de saturacion media y la piel de la frente 0,46, asi que 0,60 parecia
# separarlos. NO FUNCIONA. Esas son medias: buena parte de los pixeles de piel
# superan 0,60 y el resultado fue la cara blanqueada a manchones. Las dos
# distribuciones se solapan y ningun umbral global las separa.
#
# Queda la linea naranja. Es delgada, se lee como un detalle del casco —muchos
# cascos blancos traen banda de color— y a tamano de pieza publicada no se ve.
# Resolverla de verdad pide relleno generativo, que en esta sesion no hay.


def comprimir_altos(y):
    """Rodilla suave: por debajo de RODILLA no toca nada; arriba tiende a 255."""
    exceso = np.maximum(y - RODILLA, 0.0)
    techo = 255.0 - RODILLA
    return np.minimum(y, RODILLA) + exceso * techo / (techo + exceso)


def recolorear(nombre, destino, url_mascara, ganancia, dilata, previa):
    base = os.path.join(ORIG, nombre + ".jpg")
    foto = Image.open(base if os.path.exists(base) else destino).convert("RGB")
    W, H = foto.size

    bruta = os.path.join(TRABAJO, nombre + "-mask3600.png")
    if not os.path.exists(bruta):
        urllib.request.urlretrieve(url_mascara, bruta)
    m = Image.open(bruta).convert("L").resize((W, H), Image.LANCZOS)
    if dilata:
        m = m.filter(ImageFilter.MaxFilter(2 * dilata + 1))
    m = m.filter(ImageFilter.GaussianBlur(max(1, int(min(W, H) * PLUMA))))
    mask = np.asarray(m, dtype=np.float32) / 255.0

    img = np.asarray(foto, dtype=np.float32)
    lum = img @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)

    duro = mask > 0.6
    if duro.sum() < 500:
        raise SystemExit("mascara demasiado chica en %s" % nombre)
    # gris = la misma escena, desaturada y con mas reflectancia
    gris = comprimir_altos(lum * ganancia)
    nuevo = np.repeat(gris[:, :, None], 3, axis=2)
    nuevo = nuevo + (img - lum[:, :, None]) * CROMA

    a = mask[:, :, None]
    salida = np.clip(img * (1.0 - a) + nuevo * a, 0, 255).astype(np.uint8)
    Image.fromarray(salida).save(destino, quality=95, subsampling=0)

    ys, xs = np.where(duro)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    pad = int(max(y1 - y0, x1 - x0) * 0.55)
    caja = (max(0, x0 - pad), max(0, y0 - pad),
            min(W, x1 + pad), min(H, y1 + pad))
    antes = foto.crop(caja)
    desp = Image.fromarray(salida).crop(caja)
    for im in (antes, desp):
        im.thumbnail((560, 1680), Image.LANCZOS)
    par = Image.new("RGB", (antes.size[0] + desp.size[0] + 12,
                            max(antes.size[1], desp.size[1])), (245, 245, 248))
    par.paste(antes, (0, 0))
    par.paste(desp, (antes.size[0] + 12, 0))
    par.save(previa, quality=92)
    med = float(np.median(lum[duro]))
    print("%-22s lum mediana %3d -> %3d  ganancia %.2f  dilata %d" % (
        nombre, med, comprimir_altos(np.array([med * ganancia]))[0],
        ganancia, dilata))


for nombre, (destino, url, ganancia, dilata) in TAREAS.items():
    recolorear(nombre, destino, url, ganancia, dilata,
               os.path.join(TRABAJO, nombre + "-comparacion.jpg"))
