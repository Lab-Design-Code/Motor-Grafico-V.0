#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Baja las 36 expansiones de Ingenieria a 03-Fotografias/_generadas/.

Verifica que lo bajado tenga el tamano que Firefly declaro; si no coincide, se
avisa en vez de dejar un archivo a medias.
"""
import os
import urllib.request
from PIL import Image

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(REPO, "03-Fotografias", "_generadas")
if not os.path.isdir(DEST):
    os.makedirs(DEST)

B = "https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:"

# carrera-pieza: (id de salida, ancho esperado, alto esperado)
SALIDAS = {
    "Construccion-Civil-post":                    ("89f83b90-f493-4aab-889c-5d9e993fa34e", 6120, 4134),
    "Construccion-Civil-story":                   ("c2082fad-2104-454a-96c6-56c0b68ac345", 3780, 6552),
    "Ingenieria-Industrial-post":                 ("331baaa4-ced1-4b3d-8a20-1952dbeef1ae", 5580, 4300),
    "Ingenieria-Industrial-story":                ("76925e7c-cd12-4e09-a541-4dcf4be1baa4", 3600, 6393),
    "Electricidad-post":                          ("a4ddb33f-061d-4966-8f54-724acd44d277", 6656, 7266),
    "Electricidad-story":                         ("674408ee-d49f-4922-a51a-e8226305cc43", 3598, 6425),
    "Prevencion-de-Riesgos-post":                 ("ed007c58-61b4-4290-a6d8-8cb25f3e4a0d", 6656, 4171),
    "Prevencion-de-Riesgos-story":                ("84f5a8ba-8a41-48ae-9c76-f12fbcf687fc", 4046, 6475),
    "Automatizacion-y-Control-Industrial-post":   ("77f8cad2-e748-4c95-9772-c1082c6fa9b2", 9900, 5861),
    "Automatizacion-y-Control-Industrial-story":  ("2b7f1b55-bb34-43fe-85cb-d21e2a1d7919", 4956, 6990),
    "Ciberseguridad-post":                        ("5f566b2a-a130-40e8-9b0a-a2421d90d555", 3956, 3923),
    "Ciberseguridad-story":                       ("73657a5b-09af-423a-ba08-7cc9ee0ac125", 3598, 6393),
    "Ciencia-de-Datos-post":                      ("6c7cc7d7-c72f-40a0-b759-eae778686772", 6297, 5365),
    "Ciencia-de-Datos-story":                     ("703f7418-e11e-4c1b-add9-e465080b1262", 3599, 6425),
    "Gestion-de-Seguridad-y-Vigilancia-Privada-post":  ("976350e5-6dba-4af9-8eb7-a3c98cba6878", 6653, 4095),
    "Gestion-de-Seguridad-y-Vigilancia-Privada-story": ("b4b3d33a-ccab-4ca3-a868-ebfd7f9e152b", 4495, 7188),
    "Informatica-post":                           ("76140623-48fd-432a-aeb5-356976f1040f", 4551, 3392),
    "Informatica-story":                          ("86c82844-0133-4a45-840a-4d589a7a5a58", 3686, 6549),
    "Informatica-y-Ciberseguridad-post":          ("99f48b85-80d8-454b-80c2-e992c890095c", 8814, 7095),
    "Informatica-y-Ciberseguridad-story":         ("65f33588-01ea-48b5-8153-49b2fe7729b5", 4136, 6884),
    "Inteligencia-Artificial-post":               ("a17e0232-743b-49e4-8778-7c592de80db7", 4777, 4302),
    "Inteligencia-Artificial-story":              ("6aa6cf6b-ce61-4189-b1af-f6e6e3bbf47f", 3686, 6549),
    "Mantenimiento-Industrial-post":              ("95d19f1a-aea9-49b9-ba14-2befc70265cd", 7281, 3379),
    "Mantenimiento-Industrial-story":             ("c2cb67cd-73c1-4d1b-85f2-27e2f0096732", 4348, 6008),
    "Minas-post":                                 ("541b066a-51ef-488b-82d8-58469445a142", 7200, 6100),
    "Minas-story":                                ("721081ca-d578-4143-8ee9-d254fcb789d5", 3600, 6397),
    "Operaciones-de-Planta-Minera-post":          ("b1d3f689-d735-418c-bb74-f058f0b629ac", 7740, 6745),
    "Operaciones-de-Planta-Minera-story":         ("6d7de639-97f6-401b-bb44-de45095410bc", 4140, 7056),
    "Instrumentacion-Industrial-post":            ("c5090f31-d93b-4f9a-84f3-aa2ceed0b56a", 4551, 2832),
    "Instrumentacion-Industrial-story":           ("db512d66-e458-4d0e-8fef-303cae35b348", 3686, 6549),
    "Procesos-Industriales-post":                 ("2f793301-4564-4a1d-8a57-57d19f8d01a5", 4267, 2903),
    "Procesos-Industriales-story":                ("06147387-166c-401d-9e7e-582ed4b7b2bf", 4267, 7584),
    "Procesos-Mineros-post":                      ("c13beb93-4d19-48ae-8571-13c3c3fd8224", 7557, 5577),
    "Procesos-Mineros-story":                     ("57313358-21fd-4a94-a68e-2cb1bfd49b3c", 3599, 6425),
    "Programacion-post":                          ("a1b2d5b8-4266-4e71-b76e-0c888d27f57a", 4640, 3504),
    "Programacion-story":                         ("b7e590b8-ebb3-489e-921c-773dc6dc6727", 2080, 3696),
}

malas = []
for nombre in sorted(SALIDAS):
    uid, aw, ah = SALIDAS[nombre]
    destino = os.path.join(DEST, nombre + ".jpg")
    urllib.request.urlretrieve(B + uid, destino)
    w, h = Image.open(destino).size
    ok = (w == aw and h == ah)
    if not ok:
        malas.append(nombre)
    print("%-52s %5dx%-5d %s" % (nombre, w, h, "ok" if ok else "NO CALZA (%dx%d)" % (aw, ah)))

print("")
print("bajadas: %d de %d" % (len(SALIDAS) - len(malas), len(SALIDAS)))
if malas:
    print("revisar: " + ", ".join(malas))
