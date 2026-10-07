# -*- coding: utf-8 -*-
"""Proyectos y generacion por lote.

Un proyecto es un JSON con la lista de piezas. Es la unica fuente de verdad:
texto, foto y encuadre viven ahi, y volver a correr el lote reescribe la
entrega. No hay estado en otro lado y no hay pieza que se edite a mano, que es
lo que evita la carpeta llena de "final-v3-OK".
"""
import json
import os
import re

from . import foto as _foto
from . import plantilla as _plantilla
from . import qa as _qa
from . import render, rostro, solver, zonas

_SEG_RE = re.compile(r"\{([A-Za-z_][\w]*)\}")


class Proyecto:
    def __init__(self, ruta):
        self.ruta = os.path.abspath(ruta)
        self.carpeta = os.path.dirname(self.ruta)
        with open(self.ruta, encoding="utf-8") as f:
            self.cfg = json.load(f)
        self.nombre = self.cfg.get("proyecto", os.path.basename(self.carpeta))
        self.piezas = self.cfg["piezas"]

    def _abs(self, clave, defecto):
        v = self.cfg.get(clave, defecto)
        return v if os.path.isabs(v) else os.path.normpath(os.path.join(self.carpeta, v))

    @property
    def plantilla(self):
        if not hasattr(self, "_plantilla_cache"):
            self._plantilla_cache = _plantilla.cargar(self._abs("plantilla", "plantilla"))
        return self._plantilla_cache

    @property
    def dir_fotos(self):
        return self._abs("fotos", "fotos")

    @property
    def dir_salida(self):
        return self._abs("salida", "salida")

    @property
    def cache_fotos(self):
        return os.path.join(self.dir_fotos, "_expandidas")

    def formatos(self, pedidos=None):
        nombres = pedidos or self.cfg.get("formatos") or list(self.plantilla.formatos)
        faltan = [n for n in nombres if n not in self.plantilla.formatos]
        if faltan:
            raise KeyError("La plantilla no define el formato %s (tiene: %s)"
                           % (faltan, ", ".join(self.plantilla.formatos)))
        return [self.plantilla[n] for n in nombres]

    def ruta_foto(self, pieza):
        f = pieza.get("foto")
        if not f:
            return None
        return f if os.path.isabs(f) else os.path.join(self.dir_fotos, f)

    def carpeta_pieza(self, pieza):
        """Resuelve la plantilla de ruta contra los campos de la pieza.

        Un campo vacio no abre carpeta. Eso es lo que evita que la modalidad
        Online -- que tiene una sola sede -- produzca "Online/Online".
        """
        patron = self.cfg.get("ruta", "")
        if not patron:
            return self.dir_salida
        campos = pieza["campos"]
        partes = []
        for seg in patron.split("/"):
            resuelto = _SEG_RE.sub(lambda m: str(campos.get(m.group(1), "")).strip(), seg)
            resuelto = _limpiar(resuelto)
            if resuelto:
                partes.append(resuelto)
        return os.path.join(self.dir_salida, *partes)

    def nombre_archivo(self, pieza, formato):
        patron = self.cfg.get("archivo", "{formato}-{slug}")
        campos = dict(pieza["campos"])
        campos["formato"] = formato.nombre.capitalize()
        campos["slug"] = pieza["slug"]
        return _limpiar(_SEG_RE.sub(lambda m: str(campos.get(m.group(1), "")), patron))

    def guardar(self):
        with open(self.ruta, "w", encoding="utf-8") as f:
            json.dump(self.cfg, f, ensure_ascii=False, indent=2)


def _limpiar(s):
    """Quita lo que Windows no admite en nombres de archivo o carpeta."""
    return re.sub(r'[<>:"/\\|?*]', "", s).strip().rstrip(".")


# --------------------------------------------------------------- generacion

def construir_pieza(proyecto, formato, pieza, encuadre=None, con_zonas=False):
    """Devuelve el SVG de una pieza, con foto si la tiene."""
    svg = formato.construir(pieza["campos"])

    ruta = proyecto.ruta_foto(pieza)
    if ruta:
        enc = encuadre if encuadre is not None else \
            (pieza.get("encuadre") or {}).get(formato.nombre, {})
        expandida = _foto.preparar(ruta, enc.get("expansiones"), proyecto.cache_fotos)
        cfg = dict(formato.foto)
        cfg["_canvas"] = (formato.ancho, formato.alto)
        focal = tuple(enc.get("focal") or (0.5, 0.38, 0.5, 0.33))
        svg = _foto.poner(svg, cfg, expandida, focal, zoom=float(enc.get("zoom", 1.0)))

    if con_zonas:
        svg = _foto.mapa_zonas(svg, formato.zonas, (formato.ancho, formato.alto))
    return svg


def _elegida(pieza, filtro=None, slugs=None):
    """`filtro` busca texto dentro del slug; `slugs` exige el slug exacto.

    El filtro por contenido sirve en la consola, pero "Educacion-Basica" tambien
    elige "Educacion-Basica-y-Parvularia". Regenerar UNA pieza desde la interfaz
    necesita el calce exacto.
    """
    if slugs is not None and pieza["slug"] not in slugs:
        return False
    return not (filtro and filtro.lower() not in pieza["slug"].lower())


def _hallazgos_planos(hallazgos):
    return [{"nivel": h.nivel, "regla": h.regla, "mensaje": h.mensaje}
            for h in hallazgos if h.nivel != "ok"]


def generar(proyecto, formatos=None, con_svg=False, solo_svg=False,
            con_qa=False, con_zonas=False, filtro=None, informe=None,
            qa_rostro=False, slugs=None, progreso=None, continuar=False):
    """Genera el lote completo. Devuelve la lista de archivos escritos.

    `progreso(evento)` se llama tras cada pieza y formato con un dict: slug,
    formato, png, hallazgos, hechas y total. Es lo que permite mostrar el avance
    en vivo sin leer la salida de consola. Con `continuar=True` una pieza que
    falla se informa por `progreso` (clave "error") y el lote sigue.
    """
    escritos, problemas = [], []
    formatos = proyecto.formatos(formatos)
    elegidas = [p for p in proyecto.piezas if _elegida(p, filtro, slugs)]
    total, hechas = len(elegidas) * len(formatos), 0

    for pieza in elegidas:
        carpeta = proyecto.carpeta_pieza(pieza)
        os.makedirs(carpeta, exist_ok=True)

        estados = []
        for formato in formatos:
            base = os.path.join(carpeta, proyecto.nombre_archivo(pieza, formato))
            png = base + ".png"
            hallazgos = []
            try:
                svg = construir_pieza(proyecto, formato, pieza, con_zonas=con_zonas)
                if con_svg or solo_svg:
                    with open(base + ".svg", "w", encoding="utf-8") as f:
                        f.write(svg)
                    escritos.append(base + ".svg")
                if not solo_svg:
                    render.cadena_a_png(svg, png, formato.ancho, formato.alto)
                    escritos.append(png)
            except Exception as e:
                if not (continuar and progreso):
                    raise
                hechas += 1
                estados.append("%s FALLO" % formato.nombre)
                progreso({"etapa": "generar", "slug": pieza["slug"],
                          "formato": formato.nombre, "error": "%s: %s" % (type(e).__name__, e),
                          "hechas": hechas, "total": total})
                continue

            if con_qa:
                # El QA de texto y encuadre no necesita la foto: sobre el SVG con
                # la imagen incrustada (~20 MB) cada busqueda de id tarda segundos.
                hallazgos = _qa.revisar(formato.construir(pieza["campos"]),
                                        None if solo_svg else png, formato,
                                        pieza, con_rostro=qa_rostro)
                err, avi = _qa.resumen(hallazgos)
                estados.append("%s %s" % (formato.nombre,
                                          "OK" if not err else "%d ERROR" % err))
                for h in hallazgos:
                    if h.nivel != "ok":
                        problemas.append("%-28s %-6s %s"
                                         % (pieza["slug"], formato.nombre, h))
            else:
                estados.append(formato.nombre)

            hechas += 1
            if progreso:
                progreso({"etapa": "generar", "slug": pieza["slug"],
                          "formato": formato.nombre,
                          "png": None if solo_svg else png,
                          "svg": base + ".svg" if (con_svg or solo_svg) else None,
                          "hallazgos": _hallazgos_planos(hallazgos),
                          "hechas": hechas, "total": total})

        marca = "con foto" if pieza.get("foto") else "SIN FOTO"
        print("ok  %-34s %-10s %s" % (pieza["slug"], marca, " ".join(estados)))

    if problemas:
        print("\n--- QA: %d observaciones ---" % len(problemas))
        for p in problemas:
            print(p)
    if informe:
        with open(informe, "w", encoding="utf-8") as f:
            f.write("\n".join(problemas) if problemas else "sin observaciones\n")
        print("\ninforme QA:", informe)

    return escritos


def verificar(proyecto, formatos=None, con_rostro=False, filtro=None, informe=None):
    """Revisa una entrega ya generada, sin volver a rasterizar.

    Reconstruir el SVG es puro procesamiento de texto y cuesta milisegundos; lo
    caro es el PNG, que ya esta en disco. Asi se puede reverificar la campana
    entera -- por ejemplo tras cambiar un umbral de QA -- sin rehacerla.
    """
    formatos = proyecto.formatos(formatos)
    problemas, revisadas, faltantes = [], 0, 0

    for pieza in proyecto.piezas:
        if filtro and filtro.lower() not in pieza["slug"].lower():
            continue
        carpeta = proyecto.carpeta_pieza(pieza)
        for formato in formatos:
            png = os.path.join(carpeta, proyecto.nombre_archivo(pieza, formato) + ".png")
            if not os.path.exists(png):
                problemas.append("%-28s %-6s FALTA el PNG" % (pieza["slug"], formato.nombre))
                faltantes += 1
                continue
            svg = formato.construir(pieza["campos"])
            for h in _qa.revisar(svg, png, formato, pieza, con_rostro=con_rostro):
                if h.nivel != "ok":
                    problemas.append("%-28s %-6s %s" % (pieza["slug"], formato.nombre, h))
            revisadas += 1

    errores = sum(1 for p in problemas if "ERROR" in p)
    print("%d piezas revisadas, %d faltantes" % (revisadas, faltantes))
    print("%d errores, %d avisos" % (errores, len(problemas) - errores))
    if problemas:
        print()
        for p in problemas:
            print(p)
    if informe:
        with open(informe, "w", encoding="utf-8") as f:
            f.write("\n".join(problemas) if problemas else "sin observaciones\n")
        print("\ninforme:", informe)
    return errores


# ------------------------------------------------- encuadre automatico

def resolver_encuadres(proyecto, formatos=None, sobrescribir=False,
                       dir_verificacion=None, slugs=None, progreso=None):
    """Mide el rostro de cada foto y resuelve el encuadre de cada formato.

    Es el flujo que antes eran cuatro scripts y una lectura a ojo:
    grilla_fina -> medir_titulo -> solver_encuadre -> aplicar_encuadres.

    Las medidas se escriben en el proyecto para que queden auditables y para
    poder corregirlas a mano cuando la deteccion se equivoque.

    `slugs` limita el trabajo a esas piezas (calce exacto). `progreso(evento)`
    se llama una vez por pieza con: slug, ok, mensajes, medidas, verificacion,
    hechas y total.
    """
    formatos = proyecto.formatos(formatos)
    resueltas = fallidas = 0
    elegidas = [p for p in proyecto.piezas
                if proyecto.ruta_foto(p) and _elegida(p, slugs=slugs)]
    total = len(elegidas)

    def avisar(i, pieza, ok, mensajes, verificacion=None):
        if progreso:
            progreso({"etapa": "encuadre", "slug": pieza["slug"], "ok": ok,
                      "mensajes": mensajes, "medidas": pieza.get("medidas"),
                      "verificacion": verificacion, "hechas": i, "total": total})

    for i, pieza in enumerate(elegidas, 1):
        try:
            ruta = proyecto.ruta_foto(pieza)
            if not os.path.exists(ruta):
                print("!!  %-34s foto no encontrada: %s" % (pieza["slug"], ruta))
                fallidas += 1
                avisar(i, pieza, False, ["foto no encontrada: %s" % os.path.basename(ruta)])
                continue

            medidas = pieza.get("medidas")
            if medidas is None or sobrescribir:
                try:
                    medidas = rostro.medir(ruta, sujeto=pieza.get("sujeto", "mayor"),
                                           pelo_factor=pieza.get("pelo_factor"))
                except rostro.SinRostro as e:
                    print("!!  %-34s %s" % (pieza["slug"], str(e).splitlines()[0]))
                    fallidas += 1
                    avisar(i, pieza, False, [str(e).splitlines()[0]])
                    continue
                pieza["medidas"] = medidas

            destino = None
            if dir_verificacion:
                destino = os.path.join(dir_verificacion, pieza["slug"] + ".jpg")
                rostro.verificacion(ruta, medidas, destino)

            encuadre = pieza.setdefault("encuadre", {})
            mensajes, ok = [], True
            for formato in formatos:
                titulo_y = zonas.titulo_de_pieza(formato, pieza["campos"])
                try:
                    r = solver.resolver(medidas, formato.zonas,
                                        (formato.ancho, formato.alto), titulo_y)
                except solver.SinSolucion as e:
                    print("!!  %-34s %-6s SIN SOLUCION\n%s"
                          % (pieza["slug"], formato.nombre, e))
                    fallidas += 1
                    ok = False
                    mensajes.append("%s: SIN SOLUCION. %s" % (formato.nombre, e))
                    continue
                encuadre[formato.nombre] = {
                    "expansiones": {k: r[k] for k in ("lados", "arriba", "abajo") if r[k]},
                    "focal": list(r["focal"]),
                }
                print("ok  %-34s %-6s lados %.2f arriba %.2f abajo %.2f -> pelo %4d menton %4d x %4d"
                      % (pieza["slug"], formato.nombre, r["lados"], r["arriba"],
                         r["abajo"], r["pelo"], r["menton"], r["cara_x"]))
                mensajes.append("%s: ok (escala %.3f)" % (formato.nombre, r["escala"]))
                resueltas += 1
            avisar(i, pieza, ok, mensajes, destino)

        except Exception as e:
            # Sin progreso (consola) el error se ve completo; con progreso (interfaz)
            # se informa la pieza y el lote sigue.
            if not progreso:
                raise
            fallidas += 1
            print("!!  %-34s %s: %s" % (pieza["slug"], type(e).__name__, e))
            avisar(i, pieza, False, ["%s: %s" % (type(e).__name__, e)])
    proyecto.guardar()
    print("\n%d encuadres resueltos, %d sin resolver -> %s"
          % (resueltas, fallidas, proyecto.ruta))
    return resueltas, fallidas


def filtrar_fotos(plantilla, rutas, formatos=None, sujeto="mayor", progreso=None):
    """Dice que fotos candidatas admiten encuadre ANTES de licenciarlas.

    Correr esto sobre la preseleccion evita el caso caro: comprar una imagen,
    calibrarla y recien ahi descubrir que el rostro es demasiado grande y no
    hay expansion que la salve.

    `progreso(evento)` se llama tras cada foto con: foto, fila, hechas y total.
    """
    nombres = formatos or list(plantilla.formatos)
    resultados = []
    for i, ruta in enumerate(rutas, 1):
        fila = {"foto": os.path.basename(ruta), "ok": True, "detalle": {}}
        try:
            medidas = rostro.medir(ruta, sujeto=sujeto)
        except rostro.SinRostro as e:
            fila.update(ok=False, error=str(e).splitlines()[0])
            resultados.append(fila)
            if progreso:
                progreso({"etapa": "filtrar", "foto": fila["foto"], "fila": fila,
                          "hechas": i, "total": len(rutas)})
            continue
        fila["rostro"] = "%.3f del alto" % (medidas["menton"] - medidas["pelo"])
        for n in nombres:
            f = plantilla[n]
            try:
                r = solver.resolver(medidas, f.zonas, (f.ancho, f.alto))
                fila["detalle"][n] = "ok (escala %.3f)" % r["escala"]
            except solver.SinSolucion as e:
                fila["detalle"][n] = "SIN SOLUCION"
                fila["ok"] = False
                fila.setdefault("motivos", []).append("%s: %s" % (n, e))
        resultados.append(fila)
        if progreso:
            progreso({"etapa": "filtrar", "foto": fila["foto"], "fila": fila,
                      "hechas": i, "total": len(rutas)})
    return resultados


def generar_variantes(proyecto, pieza_slug, formato_nombre, n=3, destino=None):
    """Genera N encuadres alternativos de una pieza, para prueba A/B."""
    pieza = next(p for p in proyecto.piezas if p["slug"] == pieza_slug)
    formato = proyecto.plantilla[formato_nombre]
    medidas = pieza.get("medidas") or rostro.medir(
        proyecto.ruta_foto(pieza), sujeto=pieza.get("sujeto", "mayor"))
    titulo_y = zonas.titulo_de_pieza(formato, pieza["campos"])

    opciones = solver.variantes(medidas, formato.zonas,
                                (formato.ancho, formato.alto), titulo_y, n=n)
    destino = destino or os.path.join(proyecto.dir_salida, "_variantes")
    os.makedirs(destino, exist_ok=True)

    salidas = []
    for i, r in enumerate(opciones, 1):
        enc = {"expansiones": {k: r[k] for k in ("lados", "arriba", "abajo") if r[k]},
               "focal": list(r["focal"])}
        svg = construir_pieza(proyecto, formato, pieza, encuadre=enc)
        png = os.path.join(destino, "%s-%s-v%d.png" % (pieza_slug, formato_nombre, i))
        render.cadena_a_png(svg, png, formato.ancho, formato.alto)
        salidas.append(png)
        print("ok  variante %d  escala %.3f  lados %.2f arriba %.2f abajo %.2f"
              % (i, r["escala"], r["lados"], r["arriba"], r["abajo"]))
    return salidas
