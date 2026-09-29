#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Driver de lote para las graficas definitivas de admision IPG 2027.

Lee un JSON de escuela (02-Datos/escuela-*.json), genera Post y Story de cada
carrera+sede y los deja separados por modalidad y sede:

    Graficas Meta 2027/<Escuela>/<Carrera>/Presencial/<Sede>/<Post|Story>-...png
    Graficas Meta 2027/<Escuela>/<Carrera>/Online/<Post|Story>-...png

Online no abre un nivel de sede porque solo tiene una; abrirlo daria
"Online/Online".

A diferencia de los scripts sueltos, aqui todo corre en proceso: se importa
`construir` del generador de texto y `poner_foto` de la capa fotografica, y el
PNG se rasteriza con Inkscape invocado por lista de argumentos (nunca por shell),
porque la ruta del repositorio trae ñ, & y espacios.

En la carpeta de entrega queda **solo el PNG**. El SVG intermedio se escribe en
una carpeta temporal y se borra: con las extensiones ocultas de Windows el par
PNG/SVG aparece como dos archivos del mismo nombre y se lee como si hubiera dos
versiones de la pieza. El SVG se rehace en segundos con --con-svg.

Uso:
    python 00-Scripts/lote_graficas_ipg.py 02-Datos/escuela-salud.json
    python 00-Scripts/lote_graficas_ipg.py 02-Datos/escuela-salud.json --con-svg
    python 00-Scripts/lote_graficas_ipg.py 02-Datos/escuela-salud.json --solo-svg
    python 00-Scripts/lote_graficas_ipg.py 02-Datos/escuela-salud.json --salida "Gráficas Meta 2027/V.2"

--salida permite escribir un lote completo fuera de la carpeta de entrega, que
es como convive la V.2 con las 166 graficas ya publicadas de la V.1 sin
pisarlas. La ruta es relativa al repositorio salvo que sea absoluta.
"""
import os, sys, json, subprocess, shutil, tempfile

BASE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(BASE)
sys.path.insert(0, BASE)

import generar_graficas_ipg as gen
import capa_fotos_ipg as capa

SALIDA = os.path.join(REPO, "Gráficas Meta 2027")
FOTOS = os.path.join(REPO, "03-Fotografias")

INKSCAPE = gen.INKSCAPE


def foto_expandida(foto, arriba, lados, abajo):
    """Replica el cache de expansiones de capa_fotos_ipg.__main__.

    El orden lados -> arriba -> abajo es parte del contrato: cada frac se lee
    sobre el tamano que trae la imagen en ese punto de la cadena, asi que
    alterarlo cambia el encuadre. El sufijo -b solo se escribe cuando hay
    expansion inferior, para no invalidar los cache anteriores a esa funcion.

    El sufijo -r marca las expansiones hechas por reflejo de la fotografia
    (22-09-2026). Los tamanos son identicos a los del metodo anterior, asi que
    sin esa marca el cache viejo —relleno difuminado— se reusaria en silencio
    y las graficas saldrian con el aspecto que justamente se quiso cambiar.
    """
    if not (arriba or lados or abajo):
        return foto
    nombre, ext = os.path.splitext(os.path.basename(foto))
    tag = "%s-a%s-l%s%s-r%s" % (nombre, arriba or 0, lados or 0,
                                ("-b%s" % abajo) if abajo else "", ext)
    destino = os.path.join(FOTOS, "_expandidas", tag)
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    if os.path.exists(destino):
        return destino
    paso, temporales = foto, []
    for frac, fn in ((lados, capa.expandir_foto_lados),
                     (arriba, capa.expandir_foto_arriba),
                     (abajo, capa.expandir_foto_abajo)):
        if not frac:
            continue
        inter = "%s.%s.jpg" % (destino, fn.__name__)
        fn(paso, inter, frac=frac)
        paso = inter
        temporales.append(inter)
    os.replace(paso, destino)
    for t in temporales:
        if os.path.exists(t):
            os.remove(t)
    return destino


def render_png(svg, png):
    """SVG -> PNG. Inkscape devuelve 0 aunque no escriba nada, asi que la
    unica verificacion valida es que el archivo exista despues."""
    if os.path.exists(png):
        os.remove(png)
    subprocess.run([INKSCAPE, svg, "--export-type=png",
                    "--export-filename=" + png], check=False,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if not os.path.exists(png):
        raise SystemExit("Inkscape no escribio " + png)


def ruta_pieza(escuela, c, salida=None):
    """Carpeta de destino: carrera, modalidad y sede.

    La modalidad sale de la sede, no de una columna aparte: la unica virtual es
    "Sede Online". Se separan porque son campanas distintas -- la presencial se
    pauta por region y la online a nivel nacional -- y mezclarlas en una sola
    carpeta obliga a leer el nombre de archivo para saber cual es cual.
    """
    raiz = salida or SALIDA
    sede = c["sede"].replace("Sede ", "").strip()
    if sede.lower() == "online":
        return os.path.join(raiz, escuela, c["carpeta"], "Online")
    return os.path.join(raiz, escuela, c["carpeta"], "Presencial", sede)


def procesar(c, escuela, solo_svg=False, con_svg=False, salida=None):
    carpeta = ruta_pieza(escuela, c, salida)
    os.makedirs(carpeta, exist_ok=True)
    hechos = []
    for cfg, tag, zonas in ((gen.POST, "Post", capa.ZONAS_POST),
                            (gen.STORY, "Story", capa.ZONAS_STORY)):
        svg = gen.construir(cfg, c)
        low = tag.lower()
        foto = c.get("foto_" + low) or c.get("foto")
        if foto:
            if not os.path.isabs(foto):
                foto = os.path.join(FOTOS, foto)
            foto = foto_expandida(
                foto,
                c.get("expandir_arriba_" + low) or c.get("expandir_arriba"),
                c.get("expandir_lados_" + low) or c.get("expandir_lados"),
                c.get("expandir_abajo_" + low) or c.get("expandir_abajo"))
            focal = c.get("focal_" + low) or c.get("focal") or (0.5, 0.38, 0.5, 0.33)
            zoom = c.get("zoom_" + low) or c.get("zoom") or 1.0
            svg = capa.poner_foto(svg, zonas, foto, tuple(focal), zoom=zoom)
        nombre = "%s-IPG_2027-%s" % (tag, c["slug"])
        png = os.path.join(carpeta, nombre + ".png")

        if solo_svg or con_svg:
            destino = os.path.join(carpeta, nombre + ".svg")
            open(destino, "w", encoding="utf-8").write(svg)
            hechos.append(destino)
            if not solo_svg:
                render_png(destino, png)
                hechos.append(png)
            continue

        # el SVG es insumo del render, no entregable: vive y muere en temporal
        tmp = os.path.join(tempfile.gettempdir(), nombre + ".svg")
        open(tmp, "w", encoding="utf-8").write(svg)
        try:
            render_png(tmp, png)
        finally:
            if os.path.exists(tmp):
                os.remove(tmp)
        hechos.append(png)
    return hechos


if __name__ == "__main__":
    ruta = sys.argv[1]
    if not os.path.isabs(ruta):
        ruta = os.path.join(REPO, ruta)
    solo_svg = "--solo-svg" in sys.argv
    con_svg = "--con-svg" in sys.argv
    salida = None
    if "--salida" in sys.argv:
        salida = sys.argv[sys.argv.index("--salida") + 1]
        if not os.path.isabs(salida):
            salida = os.path.join(REPO, salida)
    data = json.load(open(ruta, encoding="utf-8"))
    escuela = data["escuela"]
    for c in data["carreras"]:
        procesar(c, escuela, solo_svg, con_svg, salida)
        estado = "con foto" if (c.get("foto") or c.get("foto_post")) else "SIN FOTO"
        print("ok  %-38s %-16s %s" % (c["carpeta"], c["sede"], estado))
    print("\n%d carreras -> %s"
          % (len(data["carreras"]), os.path.join(salida or SALIDA, escuela)))
