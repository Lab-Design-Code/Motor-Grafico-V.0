#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Linea de comandos del motor de graficas.

`<marca>` y `<proyecto>` son nombres de carpeta cualesquiera: el motor no
conoce ninguna marca. La marca vive en plantillas/<marca>/plantilla.json.

    python graficas.py diagnostico
    python graficas.py zonas     plantillas/<marca> <formato>
    python graficas.py filtrar   plantillas/<marca> candidatas/*.jpg
    python graficas.py encuadrar proyectos/<proyecto>/proyecto.json --verificacion revisar/
    python graficas.py generar   proyectos/<proyecto>/proyecto.json --qa
    python graficas.py qa        proyectos/<proyecto>/proyecto.json --informe qa.txt
    python graficas.py variantes proyectos/<proyecto>/proyecto.json <slug> <formato>
"""
import argparse
import glob
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from motor import entorno, lote, plantilla as _plantilla, zonas  # noqa: E402


def _lista(v):
    return [x.strip() for x in v.split(",")] if v else None


def cmd_diagnostico(a):
    print(entorno.diagnostico())
    return 0


def cmd_generar(a):
    p = lote.Proyecto(a.proyecto)
    print("proyecto: %s\nplantilla: %s\nsalida: %s\n"
          % (p.nombre, p.plantilla.nombre, p.dir_salida))
    escritos = lote.generar(p, formatos=_lista(a.formatos), con_svg=a.con_svg,
                            solo_svg=a.solo_svg, con_qa=a.qa or a.qa_rostro,
                            con_zonas=a.zonas, filtro=a.solo, informe=a.informe,
                            qa_rostro=a.qa_rostro)
    print("\n%d archivos -> %s" % (len(escritos), p.dir_salida))
    return 0


def cmd_qa(a):
    p = lote.Proyecto(a.proyecto)
    errores = lote.verificar(p, formatos=_lista(a.formatos), con_rostro=a.rostro,
                             filtro=a.solo, informe=a.informe)
    return 1 if errores else 0


def cmd_encuadrar(a):
    p = lote.Proyecto(a.proyecto)
    _, fallidas = lote.resolver_encuadres(
        p, formatos=_lista(a.formatos), sobrescribir=a.sobrescribir,
        dir_verificacion=a.verificacion)
    if a.verificacion:
        print("\nRevisa las imagenes de %s antes de generar el lote:\n"
              "el tope del pelo es una estimacion y es el dato que mas duele "
              "cuando esta mal." % a.verificacion)
    return 1 if fallidas else 0


def cmd_filtrar(a):
    pl = _plantilla.cargar(a.plantilla)
    rutas = []
    for patron in a.fotos:
        rutas.extend(sorted(glob.glob(patron)) or [patron])
    filas = lote.filtrar_fotos(pl, rutas, formatos=_lista(a.formatos))

    for f in filas:
        estado = "SIRVE " if f["ok"] else "DESCARTAR"
        print("%-9s %-38s %s" % (estado, f["foto"], f.get("rostro", f.get("error", ""))))
        for k, v in f.get("detalle", {}).items():
            print("          %-8s %s" % (k, v))
        for m in f.get("motivos", []):
            print("          %s" % m.replace("\n", "\n          "))
    sirven = sum(1 for f in filas if f["ok"])
    print("\n%d de %d fotos admiten encuadre" % (sirven, len(filas)))
    return 0


def cmd_variantes(a):
    p = lote.Proyecto(a.proyecto)
    salidas = lote.generar_variantes(p, a.slug, a.formato, n=a.n)
    print("\n%d variantes -> %s" % (len(salidas), os.path.dirname(salidas[0]) if salidas else "-"))
    return 0


def cmd_montar(a):
    from motor import montaje
    svgs = {}
    for arg in a.arte:
        nombre, _, ruta = arg.rpartition("=")
        nombre = nombre or os.path.splitext(os.path.basename(ruta))[0]
        svgs[montaje.clave(nombre).replace("_", "-")] = ruta
    manual = dict(m.split("=", 1) for m in (a.mapa or []))
    raiz = os.path.dirname(os.path.abspath(__file__))
    dir_pl, dir_pr, informes, n = montaje.montar(raiz, a.marca, svgs, a.datos,
                                                 manual=manual, sobrescribir=a.sobrescribir)
    for formato, inf in informes.items():
        print("\n=== %s" % formato)
        for tipo, txt, detalle in inf:
            print("  %-9s %-34s %s" % (tipo, ("\"%s\"" % txt[:32]) if txt else "", detalle))
    print("\nplantilla: %s\nproyecto:  %s  (%d piezas)" % (dir_pl, dir_pr, n))
    print("\nSiguiente: copia las fotos a %s y corre\n"
          "  python graficas.py encuadrar %s --verificacion revisar/\n"
          "  python graficas.py generar   %s --qa"
          % (os.path.join(dir_pr, "fotos"), os.path.join(dir_pr, "proyecto.json"),
             os.path.join(dir_pr, "proyecto.json")))
    return 0


def cmd_zonas(a):
    pl = _plantilla.cargar(a.plantilla)
    f = pl[a.formato]
    propuesta = zonas.derivar(f)
    nota = propuesta.pop("_derivado")
    print(json.dumps(propuesta, ensure_ascii=False, indent=2))
    print("\nMedido del arte:   %s" % ", ".join(nota["medido"]))
    print("Convencion a revisar: %s" % ", ".join(nota["convencion_revisar"]))
    print(nota["nota"])
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Motor de graficas: plantilla + datos -> piezas verificadas.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("diagnostico", help="que encuentra el motor en esta maquina")
    s.set_defaults(fn=cmd_diagnostico)

    s = sub.add_parser("generar", help="genera el lote de piezas")
    s.add_argument("proyecto")
    s.add_argument("--formatos", help="lista separada por comas (por defecto, todos)")
    s.add_argument("--con-svg", action="store_true", help="deja tambien el SVG editable")
    s.add_argument("--solo-svg", action="store_true", help="no rasteriza a PNG")
    s.add_argument("--qa", action="store_true", help="verifica cada pieza generada")
    s.add_argument("--qa-rostro", action="store_true",
                   help="ademas re-detecta el rostro en el PNG (lento y solo "
                        "orientativo: sirve para pillar la foto con dos personas)")
    s.add_argument("--zonas", action="store_true", help="superpone el mapa de zonas (depuracion)")
    s.add_argument("--solo", help="genera solo las piezas cuyo slug contenga este texto")
    s.add_argument("--informe", help="escribe las observaciones de QA en este archivo")
    s.set_defaults(fn=cmd_generar)

    s = sub.add_parser("qa", help="revisa una entrega ya generada, sin rasterizar")
    s.add_argument("proyecto")
    s.add_argument("--formatos")
    s.add_argument("--solo")
    s.add_argument("--rostro", action="store_true",
                   help="ademas re-detecta el rostro en cada PNG (lento, orientativo)")
    s.add_argument("--informe")
    s.set_defaults(fn=cmd_qa)

    s = sub.add_parser("encuadrar", help="mide rostros y resuelve los encuadres")
    s.add_argument("proyecto")
    s.add_argument("--formatos")
    s.add_argument("--sobrescribir", action="store_true",
                   help="vuelve a medir aunque ya haya medidas guardadas")
    s.add_argument("--verificacion", help="carpeta donde dejar las imagenes de control")
    s.set_defaults(fn=cmd_encuadrar)

    s = sub.add_parser("filtrar", help="descarta fotos candidatas antes de licenciarlas")
    s.add_argument("plantilla")
    s.add_argument("fotos", nargs="+")
    s.add_argument("--formatos")
    s.set_defaults(fn=cmd_filtrar)

    s = sub.add_parser("variantes", help="N encuadres alternativos de una pieza (A/B)")
    s.add_argument("proyecto")
    s.add_argument("slug")
    s.add_argument("formato")
    s.add_argument("-n", type=int, default=3)
    s.set_defaults(fn=cmd_variantes)

    s = sub.add_parser("montar", help="monta una marca nueva desde el SVG de Illustrator y el Excel, "
                                      "sin nombrar capas")
    s.add_argument("marca", help="nombre de la carpeta de la marca")
    s.add_argument("datos", help="Excel (.xlsx) o .csv con una fila por pieza")
    s.add_argument("arte", nargs="+", help="SVG exportado de Illustrator; formato=ruta.svg para nombrarlo")
    s.add_argument("--mapa", action="append",
                   help="fuerza un calce: \"texto del arte=columna\" (repetible)")
    s.add_argument("--sobrescribir", action="store_true")
    s.set_defaults(fn=cmd_montar)

    s = sub.add_parser("zonas", help="deriva las zonas seguras del arte de la plantilla")
    s.add_argument("plantilla")
    s.add_argument("formato")
    s.set_defaults(fn=cmd_zonas)

    a = ap.parse_args(argv)
    try:
        return a.fn(a)
    except entorno.EntornoIncompleto as e:
        print("\n%s" % e, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())

