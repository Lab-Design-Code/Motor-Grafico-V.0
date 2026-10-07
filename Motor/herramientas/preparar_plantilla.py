#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Convierte una plantilla de Illustrator en una plantilla estable.

El problema
-----------
Illustrator numera las clases CSS **por exportacion**: `cls-14` hoy puede ser
`cls-9` manana. Un motor que localice los elementos por clase se rompe entero
la primera vez que el disenador vuelve a exportar, y se rompe en silencio,
porque el selector simplemente no encuentra nada.

La solucion
-----------
Estampar un `id` estable sobre cada elemento que el motor necesita tocar. Esto
se hace UNA vez por plantilla. Despues, el motor ya no mira clases.

A futuro conviene saltarse este paso: si el disenador nombra las capas en
Illustrator ("m-nombre", "m-cuota"), el exportador escribe esos nombres como
`id` y la plantilla ya sale preparada.

Uso:
    python herramientas/preparar_plantilla.py plantillas/ipg-2027/receta.json
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from motor import svgdoc  # noqa: E402


def _buscar(svg, spec):
    """Localiza el span de un elemento segun la receta. Devuelve (inicio, fin)."""
    if "regex" in spec:
        m = re.search(spec["regex"], svg, re.S)
        if not m:
            raise LookupError("el regex no encontro nada: %s" % spec["regex"][:70])
        return m.start(), m.end()

    tag = spec.get("tag", "[A-Za-z]+")
    partes = [r"<%s\b" % tag]
    cond = []
    if "clase" in spec:
        cond.append(r'class="%s"' % re.escape(spec["clase"]))
    for k, v in (spec.get("attrs") or {}).items():
        cond.append(r'%s="%s"' % (re.escape(k), re.escape(str(v))))
    if "transform" in spec:
        cond.append(r'transform="translate\(%s\)"' % re.escape(spec["transform"]))

    # Los atributos pueden venir en cualquier orden: se exige que todos esten
    # dentro de la misma etiqueta de apertura.
    patron = partes[0] + r"[^>]*?" + r"[^>]*?".join(cond) + r"[^>]*>"
    m = re.search(patron, svg)
    if not m:
        # Segundo intento con las condiciones en orden inverso.
        patron = partes[0] + r"[^>]*?" + r"[^>]*?".join(reversed(cond)) + r"[^>]*>"
        m = re.search(patron, svg)
    if not m:
        raise LookupError("no encontre <%s> con %s" % (tag, cond))
    return m.start(), m.end()


def _balance_g(fragmento):
    """Cuantos </g> sobran en un fragmento (cierres menos aperturas).

    Las capas de Illustrator suelen venir dentro de grupos anidados, asi que el
    span que hay que sustituir cierra mas grupos de los que abre. Si se
    reemplaza por algo balanceado, el documento queda con grupos sin cerrar y
    el render sale mal de formas dificiles de diagnosticar. Contando el balance
    se repone exactamente lo que falta.
    """
    aperturas = len([m for m in re.finditer(r"<g\b[^>]*>", fragmento)
                     if not m.group(0).rstrip().endswith("/>")])
    cierres = len(re.findall(r"</g\s*>", fragmento))
    return cierres - aperturas


def preparar(receta, raiz):
    origen = receta["origen"]
    destino = receta["destino"]
    if not os.path.isabs(origen):
        origen = os.path.normpath(os.path.join(raiz, origen))
    if not os.path.isabs(destino):
        destino = os.path.normpath(os.path.join(raiz, destino))

    with open(origen, encoding="utf-8") as f:
        svg = f.read()

    informe = []
    # De atras hacia adelante: cada sustitucion corre los offsets posteriores.
    marcas = []
    for marca in receta["marcas"]:
        try:
            ini, fin = _buscar(svg, marca["buscar"])
        except LookupError as e:
            informe.append(("FALLA", marca["id"], str(e)))
            continue
        marcas.append((ini, fin, marca))

    for ini, fin, marca in sorted(marcas, key=lambda t: -t[0]):
        id_ = marca["id"]
        if marca.get("placeholder"):
            sobrantes = _balance_g(svg[ini:fin])
            nuevo = '<g id="%s"/>' % id_ + "</g>" * max(0, sobrantes)
            svg = svg[:ini] + nuevo + svg[fin:]
            informe.append(("placeholder", id_,
                            "%d bytes reemplazados, %d </g> repuestos"
                            % (fin - ini, sobrantes)))
        else:
            apertura = svg[ini:fin]
            if re.search(r'\sid="', apertura):
                apertura = re.sub(r'\sid="[^"]*"', ' id="%s"' % id_, apertura, count=1)
            else:
                cierre = "/>" if apertura.rstrip().endswith("/>") else ">"
                apertura = (apertura.rstrip()[:-len(cierre)].rstrip()
                            + ' id="%s"' % id_ + cierre)
            svg = svg[:ini] + apertura + svg[fin:]
            informe.append(("id", id_, apertura[:64].replace("\n", " ")))

    # xlink es necesario para las imagenes embebidas y Illustrator no siempre lo declara.
    if "xmlns:xlink" not in svg:
        svg = re.sub(r"(<svg\b)", r'\1 xmlns:xlink="http://www.w3.org/1999/xlink"',
                     svg, count=1)

    os.makedirs(os.path.dirname(destino), exist_ok=True)
    with open(destino, "w", encoding="utf-8") as f:
        f.write(svg)

    # Verificacion: todo id declarado tiene que ser localizable por el motor.
    errores = []
    for marca in receta["marcas"]:
        try:
            svgdoc.localizar(svg, marca["id"])
        except Exception as e:
            errores.append("  %s -> %s" % (marca["id"], str(e).splitlines()[0]))

    return destino, informe, errores


def main(ruta_receta):
    raiz = os.path.dirname(os.path.abspath(ruta_receta))
    with open(ruta_receta, encoding="utf-8") as f:
        recetas = json.load(f)
    if isinstance(recetas, dict):
        recetas = [recetas]

    fallo = 0
    for receta in recetas:
        destino, informe, errores = preparar(receta, raiz)
        print("\n=== %s" % os.path.basename(destino))
        for tipo, id_, detalle in informe:
            print("  %-12s %-22s %s" % (tipo, id_, detalle))
        if errores:
            fallo = 1
            print("\n  NO VERIFICAN:")
            print("\n".join(errores))
        else:
            print("  todos los ids verifican")
    return fallo


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    sys.exit(main(sys.argv[1]))
