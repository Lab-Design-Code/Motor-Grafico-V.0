#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Baja las 36 expansiones de V.3 a 03-Fotografias/_generadas/.

Verifica el tamano contra lo que declaro Firefly: si no calza, el encuadre que
resolvio el solver no aplica y hay que rehacer esa pieza.
"""
import io, os, shutil, urllib.request
from PIL import Image

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEN = os.path.join(REPO, "03-Fotografias", "_generadas")
RESP = os.path.join(REPO, "03-Fotografias", "_generadas-V2-0")
for d in (GEN, RESP):
    if not os.path.isdir(d):
        os.makedirs(d)

B = "https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:"
SALIDAS = {
 "Administracion-Publica-post":                  ("deec0c36-a3d3-4aa5-8d35-c31b2a13598b", 2600, 2583),
 "Administracion-Publica-story":                 ("b4c96852-c170-4968-a785-885f3c05f907", 2000, 3543),
 "Administracion-de-Centros-de-Salud-post":      ("01ca9d36-a86d-491b-bf16-628a1ef40c18", 2300, 2243),
 "Administracion-de-Centros-de-Salud-story":     ("a9825c8b-1cef-4220-8df6-33538774f27f", 2000, 3542),
 "Comercio-Exterior-post":                       ("fdff5604-566c-4c94-9f2a-20421af8d81d", 2000, 1260),
 "Comercio-Exterior-story":                      ("de316cf0-da58-48e4-883a-bd11956b12d0", 2000, 3542),
 "Educacion-Basica-post":                        ("c713f4e8-1d2a-46e4-a369-b5b68d80d309", 2900, 2822),
 "Educacion-Basica-story":                       ("e87de820-8b28-47ce-aa56-2f51d89d22e3", 2000, 3547),
 "Educacion-Basica-y-Parvularia-post":           ("0a409471-0bfb-4da6-9143-17f3a67d5c50", 2700, 2659),
 "Educacion-Basica-y-Parvularia-story":          ("03dea731-8b58-46f5-90b7-26063c79ead2", 2000, 3545),
 "Educacion-Diferencial-post":                   ("7676809f-00f8-4a70-8c68-cf7cca6a9d7c", 2000, 2000),
 "Educacion-Diferencial-story":                  ("efae6b77-2d3d-4077-8eb9-4c95607eab39", 1334, 2360),
 "Educacion-Parvularia-post":                    ("d6ce5fe7-891b-4c13-b3cb-7d107e98c9ab", 2000, 1428),
 "Educacion-Parvularia-story":                   ("df5294e1-9d8b-4849-857d-e518503bb485", 2000, 3543),
 "Enfermeria-post":                              ("93a312f4-d02b-40db-8501-42267325a569", 4361, 3721),
 "Enfermeria-story":                             ("33979129-38c5-42f9-9a20-f7332a4c88e9", 2007, 3472),
 "Farmacias-post":                               ("ac7f7851-d9da-4d2d-9f6d-dbf7988ac6b3", 2500, 2475),
 "Farmacias-story":                              ("a8ad541e-d512-4230-bdec-a2bf4b39c496", 2000, 3552),
 "Gestion-Comercial-y-Ventas-post":              ("85e027e2-4ff0-4036-a0cb-c3e2bc5bbba3", 2000, 1557),
 "Gestion-Comercial-y-Ventas-story":             ("71b062d3-e340-415b-beb1-88e212bab457", 2000, 3542),
 "Ingenieria-Industrial-post":                   ("7480d381-d69b-41b1-b722-2c128e46e1c8", 3100, 2239),
 "Ingenieria-Industrial-story":                  ("9769bb0c-9631-4a67-b406-48a0861e40d6", 2400, 3898),
 "Instrumentacion-Industrial-post":              ("c8c428aa-4a11-4df2-ad9f-2814af2e182b", 2000, 2066),
 "Instrumentacion-Industrial-story":             ("8fd9aeed-2d38-4b1f-8ca0-d22670760681", 2000, 3545),
 "Inteligencia-Artificial-post":                 ("41eb7136-a4d1-4fdb-8fad-fb49d4c6d6c6", 2800, 2308),
 "Inteligencia-Artificial-story":                ("a726bd88-c91e-4352-b91f-18ad05334163", 2000, 3545),
 "Podologia-post":                               ("65db62f0-a3fe-4079-8474-b3c987eb4d70", 2600, 2109),
 "Podologia-story":                              ("b9c58d9c-bc23-4a84-a9ed-cbf359102746", 2000, 3549),
 "Prevencion-de-Riesgos-post":                   ("c069e25f-615f-47bb-a0ed-36ab2b529df1", 2000, 1973),
 "Prevencion-de-Riesgos-story":                  ("a4c51aff-d2ed-47ed-8b01-6e03c9239fe0", 2000, 3542),
 "Psicopedagogia-post":                          ("0c264462-07a8-4b6a-a985-ad9d805f17a1", 2700, 2104),
 "Psicopedagogia-story":                         ("def040fe-5f32-4303-b9ce-03b7519fe2f7", 2000, 3543),
 "Rehabilitacion-de-Dependencia-de-Drogas-post": ("0cba4cb4-8079-494f-b9be-eabff1bbb0fd", 2500, 2101),
 "Rehabilitacion-de-Dependencia-de-Drogas-story":("83e7b600-66e7-4f7a-8834-8465275d2ccf", 2000, 3542),
 "Trabajo-Social-post":                          ("5e953c78-1717-4438-ad2d-d2dc1c03e8a7", 2400, 2342),
 "Trabajo-Social-story":                         ("d99038f2-8c85-414d-b1c3-585e41fc1507", 2000, 3545),
}

malas = []
for nombre in sorted(SALIDAS):
    uid, aw, ah = SALIDAS[nombre]
    destino = os.path.join(GEN, nombre + ".jpg")
    copia = os.path.join(RESP, nombre + ".jpg")
    if os.path.exists(destino) and not os.path.exists(copia):
        shutil.copy2(destino, copia)
    urllib.request.urlretrieve(B + uid, destino)
    w, h = Image.open(destino).size
    ok = (w, h) == (aw, ah)
    if not ok:
        malas.append(nombre)
    print("%-48s %5dx%-5d %s" % (nombre, w, h,
                                 "ok" if ok else "NO CALZA (%dx%d)" % (aw, ah)))

print("\nbajadas: %d de %d" % (len(SALIDAS) - len(malas), len(SALIDAS)))
if malas:
    print("revisar: " + ", ".join(malas))
