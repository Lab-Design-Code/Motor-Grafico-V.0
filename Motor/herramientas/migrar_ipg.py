#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Convierte los JSON de escuela del proyecto IPG al esquema generico.

El esquema viejo mezclaba en un mismo nivel el dato de negocio (beca, cuota) y
el parametro tecnico (expandir_lados_post, focal_story), y ademas nombraba los
campos con el vocabulario de una sola industria. El esquema nuevo separa:

    campos    -> lo que se imprime en la pieza, mas lo que arma la ruta
    encuadre  -> los parametros tecnicos, por formato
    medidas   -> lo que se midio del rostro (auditable y corregible a mano)

Uso:
    python herramientas/migrar_ipg.py "../Meta IPG-2027/02-Datos" proyectos/ipg-2027/proyecto.json
"""
import glob
import json
import os
import sys

FORMATOS = ("post", "story")


def _encuadre(c, formato):
    exp = {}
    for clave in ("lados", "arriba", "abajo"):
        v = c.get("expandir_%s_%s" % (clave, formato)) or c.get("expandir_" + clave)
        if v:
            exp[clave] = v
    focal = c.get("focal_" + formato) or c.get("focal")
    zoom = c.get("zoom_" + formato) or c.get("zoom")

    bloque = {}
    if exp:
        bloque["expansiones"] = exp
    if focal:
        bloque["focal"] = list(focal)
    if zoom and float(zoom) != 1.0:
        bloque["zoom"] = zoom
    return bloque


def _medidas_de(carpeta_datos, ruta_escuela):
    """Lee medidas-<escuela>.json, si existe.

    Esas medidas son el trabajo mas caro del proyecto original -- tope del pelo,
    menton y centro de la cabeza leidos a mano sobre una grilla -- y son las que
    permiten verificar el encuadre por aritmetica. Perderlas en la migracion
    obligaria a volver a medir las 43 fotos.
    """
    sufijo = os.path.basename(ruta_escuela).split("-", 1)[1]
    ruta = os.path.join(carpeta_datos, "medidas-" + sufijo)
    if not os.path.exists(ruta):
        return {}
    with open(ruta, encoding="utf-8") as f:
        return {k: v for k, v in json.load(f).items() if not k.startswith("_")}


def convertir(carpeta_datos):
    piezas = []
    for ruta in sorted(glob.glob(os.path.join(carpeta_datos, "escuela-*.json"))):
        with open(ruta, encoding="utf-8") as f:
            data = json.load(f)
        escuela = data["escuela"]
        medidas_escuela = _medidas_de(carpeta_datos, ruta)

        for c in data["carreras"]:
            sede = c["sede"].replace("Sede ", "").strip()
            online = sede.lower() == "online"

            pieza = {
                "slug": c["slug"],
                "campos": {
                    "prefijo": c["prefijo"],
                    "nombre": c["nombre"],
                    "badges": c.get("badges", []),
                    "beca": c["beca"],
                    "cuota": c["cuota"],
                    "sede": c["sede"],
                    # campos de organizacion: arman la ruta de salida, no se imprimen
                    "escuela": escuela,
                    "carrera": c["carpeta"],
                    "modalidad": "Online" if online else "Presencial",
                    "sede_corta": "" if online else sede,
                },
            }
            if c.get("_codigo"):
                pieza["codigo"] = c["_codigo"]
            if c.get("foto"):
                pieza["foto"] = c["foto"]
            if c.get("sujeto"):
                pieza["sujeto"] = c["sujeto"]

            m = medidas_escuela.get(c["carpeta"])
            if m:
                pieza["medidas"] = {k: m[k] for k in
                                    ("ancho", "alto", "pelo", "menton", "cara_x")
                                    if k in m}

            encuadre = {f: _encuadre(c, f) for f in FORMATOS}
            encuadre = {k: v for k, v in encuadre.items() if v}
            if encuadre:
                pieza["encuadre"] = encuadre

            piezas.append(pieza)
    return piezas


def main(carpeta_datos, destino):
    piezas = convertir(carpeta_datos)
    proyecto = {
        "proyecto": "IPG Admision 2027",
        "plantilla": "../../plantillas/ipg-2027",
        "fotos": "fotos",
        "salida": "../../salida/ipg-2027",
        "_nota_ruta": ("Un campo vacio no abre carpeta: por eso Online, que tiene "
                       "una sola sede, no produce 'Online/Online'."),
        "ruta": "{escuela}/{carrera}/{modalidad}/{sede_corta}",
        "archivo": "{formato}-IPG_2027-{slug}",
        "piezas": piezas,
    }
    os.makedirs(os.path.dirname(os.path.abspath(destino)), exist_ok=True)
    with open(destino, "w", encoding="utf-8") as f:
        json.dump(proyecto, f, ensure_ascii=False, indent=2)

    con_foto = sum(1 for p in piezas if p.get("foto"))
    con_encuadre = sum(1 for p in piezas if p.get("encuadre"))
    con_medidas = sum(1 for p in piezas if p.get("medidas"))
    carreras = len({p["campos"]["carrera"] for p in piezas})
    print("%d piezas  (%d carreras)" % (len(piezas), carreras))
    print("%d con foto, %d con encuadre calibrado, %d con medidas de rostro"
          % (con_foto, con_encuadre, con_medidas))

    # Las medidas se guardaron contra una foto concreta. Si el archivo cambio de
    # tamano desde entonces, el encuadre calculado sobre ellas es otro: hay que
    # avisar, no arrastrar el desfase en silencio.
    dir_fotos = os.path.join(os.path.dirname(os.path.abspath(destino)), "fotos")
    desajustes = []
    try:
        from PIL import Image
        Image.MAX_IMAGE_PIXELS = None
        vistas = {}
        for p in piezas:
            m, f = p.get("medidas"), p.get("foto")
            if not m or not f or f in vistas:
                continue
            ruta = os.path.join(dir_fotos, f)
            if not os.path.exists(ruta):
                continue
            real = Image.open(ruta).size
            vistas[f] = real
            if real != (m.get("ancho"), m.get("alto")):
                desajustes.append("  %-46s medidas %sx%s  archivo %dx%d"
                                  % (os.path.basename(f), m.get("ancho"),
                                     m.get("alto"), real[0], real[1]))
    except ImportError:
        pass
    if desajustes:
        print("\nAVISO: las medidas no cuadran con el tamano real de la foto.")
        print("Vuelve a medirlas con 'encuadrar --sobrescribir' antes de confiar en el QA:")
        print("\n".join(desajustes))

    print("\nescrito:", destino)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
