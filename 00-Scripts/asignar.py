#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Instala las fotos que cargo Marketing en la carpeta de cada carrera.

El calce viene del nombre con que Marketing subio cada archivo, no de mi
lectura de la imagen: la numero 10 parecia de puerto y era Prevencion de
Riesgos. Los nombres se perdieron en el adjunto y se recuperaron del
pantallazo de la carpeta.

Respalda siempre lo que habia, en _V2-0-sin-retoque.
"""
import io, os, json, glob, shutil
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
NUEVAS = os.path.join(AQUI, "nuevas")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOTOS = os.path.join(REPO, "03-Fotografias")
RESPALDO = os.path.join(FOTOS, "_V2-0-sin-retoque")

# numero de la hoja -> (carpeta de carrera, nombre con que la subio Marketing)
CALCE = {
    "01": ("Rehabilitacion-de-Dependencia-de-Drogas", "Rehabilitacion"),
    "02": ("Educacion-Basica-y-Parvularia",           "Educación Básica y Parvularia"),
    "03": ("Educacion-Parvularia",                    "Educación Parvularia"),
    "04": ("Psicopedagogia",                          "shutterstock_2725574919"),
    "06": ("Educacion-Basica",                        "Educación Básica"),
    "08": ("Podologia",                               "Podologia"),
    "09": ("Enfermeria",                              "Enfermeria"),
    "10": ("Prevencion-de-Riesgos",                   "Prevencion de riesgo"),
    "11": ("Inteligencia-Artificial",                 "Inteligencia Artificial Aplicada"),
    "12": ("Instrumentacion-Industrial",              "Instrumentacion Industrial"),
    "13": ("Ingenieria-Industrial",                   "Ingeniero industrial"),
    "14": ("Farmacias",                               "Farmacia"),
    "15": ("Administracion-de-Centros-de-Salud",      "Administración de Centros de Salud"),
    "16": ("Gestion-Comercial-y-Ventas",              "Gestion comercial"),
    "17": ("Educacion-Diferencial",                   "Ed diferecial"),
    "18": ("Comercio-Exterior",                       "Comercio exterior"),
    "19": ("Administracion-Publica",                  "Admin publica"),
    "20": ("Trabajo-Social",                          "Trabajo social"),
}

# Fuera del lote, con su motivo:
#   07  Transporte maritimo    llego en 213x192, es una miniatura
#   05  shutterstock_2247024375 sin carrera asignada, queda de repuesto
APARTE = {
    "07": "Transporte Maritimo — llego en 213x192 px, inservible",
    "05": "shutterstock_2247024375 — sin carrera, queda de repuesto",
}

# carrera -> escuela, leido de los JSON para no escribir rutas a mano
escuela_de = {}
for ruta in sorted(glob.glob(os.path.join(REPO, "02-Datos", "escuela-*.json"))):
    d = json.load(io.open(ruta, encoding="utf-8"))
    for c in d["carreras"]:
        escuela_de[c["carpeta"]] = d["escuela"]

if not os.path.isdir(RESPALDO):
    os.makedirs(RESPALDO)

print("%-4s %-42s %-9s %s" % ("n", "carrera", "tamano", "estado"))
instaladas = []
for n in sorted(CALCE):
    carpeta, _nombre = CALCE[n]
    if carpeta not in escuela_de:
        print("%-4s %-42s %-9s %s" % (n, carpeta, "-", "CARRERA DESCONOCIDA"))
        continue
    origen = os.path.join(NUEVAS, n + ".jpg")
    destino_dir = os.path.join(FOTOS, escuela_de[carpeta], carpeta)
    os.makedirs(destino_dir, exist_ok=True)
    destino = os.path.join(destino_dir, carpeta + ".jpg")

    copia = os.path.join(RESPALDO, carpeta + ".jpg")
    if os.path.exists(destino) and not os.path.exists(copia):
        shutil.copy2(destino, copia)
    shutil.copy2(origen, destino)
    im = Image.open(destino)
    instaladas.append(carpeta)
    print("%-4s %-42s %-9s %s" % (n, carpeta, "%dx%d" % im.size, "instalada"))

print("")
for n in sorted(APARTE):
    print("fuera del lote · %s" % APARTE[n])
print("")
print("%d carreras con foto nueva" % len(instaladas))
json.dump(instaladas, io.open(os.path.join(AQUI, "instaladas.json"), "w",
                              encoding="utf-8"), ensure_ascii=False, indent=2)
