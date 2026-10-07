# -*- coding: utf-8 -*-
"""Solver de encuadre: busca expansiones y focal que cumplan las zonas seguras.

El encuadre se resuelve, no se tantea. Se miden dos puntos del rostro sobre la
foto original -- tope del pelo y menton, mas el centro horizontal de la cabeza --
y se busca la combinacion de expansiones que cumple las tres restricciones:

  1. el pelo queda BAJO el bloque del logo,
  2. el menton queda SOBRE la primera linea del titulo, con aire suficiente,
  3. la cabeza cae dentro de la caja de silueta.

De las combinaciones validas se prefieren las que dejan la cabeza centrada en
la silueta y, solo entre esas, la de mayor escala. Maximizar escala a secas no
sirve: el clamp del cover admite soluciones donde la cara apenas entra por el
borde de la caja, tecnicamente validas pero visiblemente descentradas.

La aritmetica replica exactamente la de foto.py, incluidos los int() de cada
expansion. Si divergen, el solver aprueba encuadres que el render no reproduce.
"""
from . import foto

# Tope de pixeles de la foto expandida. Las expansiones grandes son legitimas,
# pero pasado este punto la imagen es casi toda relleno difuminado.
MAX_PIXELES = 180_000_000

# Rejilla de busqueda. Gruesa por velocidad: resuelve la enorme mayoria de los
# casos en una fraccion del tiempo.
REJILLA = {
    "lados": [i / 100 for i in range(0, 301, 5)],
    "arriba": [i / 100 for i in range(0, 121, 2)],
    "abajo": [i / 100 for i in range(0, 81, 2)],
}

# Rejilla fina, que solo se usa cuando la gruesa no encuentra nada.
#
# Durante un tiempo aca decia que el paso fino "no cambia el resultado porque la
# escala varia suavemente". Es falso y costo caro: con rostros grandes la franja
# de valores validos de `arriba` llega a ser mas angosta que el paso de 0,02 y
# la busqueda pasa por encima sin verla. En la campana IPG 2027 tres carreras
# —Minas, Operaciones de Planta Minera e Informatica y Ciberseguridad— daban SIN
# SOLUCION por esto, no por la fotografia, y las tres se resolvieron a 0,005.
#
# Se deja como reintento y no como rejilla unica a proposito: si la gruesa
# encuentra algo, el resultado es identico al de siempre y no se rompe ninguna
# entrega ya aprobada.
REJILLA_FINA = {
    "lados": [i / 100 for i in range(0, 401, 5)],
    "arriba": [i / 1000 for i in range(0, 1601, 5)],
    "abajo": [i / 1000 for i in range(0, 1201, 5)],
}


class SinSolucion(RuntimeError):
    def __init__(self, motivo):
        super().__init__(motivo)


def expandir(nw, nh, lados, arriba, abajo):
    """Tamano final y corrimiento del origen. Mismo orden y mismos int() que foto.py."""
    extra_l = int(nw * lados / 2) if lados else 0
    nw1 = nw + 2 * extra_l
    extra_a = int(nh * arriba) if arriba else 0
    nh2 = nh + extra_a
    extra_b = int(nh2 * abajo) if abajo else 0
    return nw1, nh2 + extra_b, extra_l, extra_a


def techo_menton(zonas, titulo_y=None, dos_lineas=False):
    """Hasta donde puede bajar el menton.

    Sale de la posicion REAL del titulo en esta pieza -- medida sobre el render
    sin foto -- menos el aire exigido. No se estima: un nombre que se parte en
    dos lineas sube el bloque una interlinea que a su vez depende del cuerpo ya
    autoajustado.

    Se pide menos aire con titulo de dos lineas y no por comodidad: ese titulo
    achica la ventana vertical disponible, y exigir el mismo aire obliga a
    encoger tanto al sujeto que queda como una figura lejana -- peor que el
    problema que resuelve.
    """
    y = titulo_y if titulo_y is not None else zonas["titulo"]
    aire = zonas.get("aire", {})
    clave = "2" if (dos_lineas or (titulo_y is not None and titulo_y < zonas["titulo"])) else "1"
    return y - float(aire.get(clave, aire.get("1", 70)))


def evaluar(medidas, zonas, canvas, lados, arriba, abajo, titulo_y=None, dos_lineas=False):
    """Simula un encuadre y devuelve si cumple, mas donde quedan pelo/menton/cara."""
    cw, ch = canvas
    nw, nh = medidas["ancho"], medidas["alto"]
    nw1, nh3, extra_l, extra_a = expandir(nw, nh, lados, arriba, abajo)
    if nw1 * nh3 > MAX_PIXELES:
        return None

    ancla = zonas.get("ancla", 1)
    fx = (extra_l + medidas["cara_x"] * nw) / nw1
    objetivo = sum(zonas["silueta"]) / 2.0
    fxt = objetivo / cw

    s, tx, ty = foto.cover(nw1, nh3, cw, ch, fx, ancla, fxt, ancla)
    cara_x = tx + nw1 * s * fx
    pelo = ty + (medidas["pelo"] * nh + extra_a) * s
    menton = ty + (medidas["menton"] * nh + extra_a) * s

    sx, sx2 = zonas["silueta"]
    ok = (pelo >= zonas["pelo_min"]
          and menton <= techo_menton(zonas, titulo_y, dos_lineas)
          and sx <= cara_x <= sx2)
    return {"ok": ok, "escala": s, "pelo": pelo, "menton": menton, "cara_x": cara_x,
            "lados": lados, "arriba": arriba, "abajo": abajo,
            "focal": (round(fx, 4), ancla, round(fxt, 4), ancla)}


def _candidatos(medidas, zonas, canvas, titulo_y, dos_lineas, rejilla=None):
    rejilla = rejilla or REJILLA
    for lados in rejilla["lados"]:
        for arriba in rejilla["arriba"]:
            for abajo in rejilla["abajo"]:
                r = evaluar(medidas, zonas, canvas, lados, arriba, abajo,
                            titulo_y, dos_lineas)
                if r and r["ok"]:
                    yield r


def _mejor(medidas, zonas, canvas, titulo_y, dos_lineas, tolerancia, rejilla):
    """Centrado primero, escala despues, dentro de una rejilla."""
    objetivo = sum(zonas["silueta"]) / 2.0
    centrados, cualquiera = None, None
    for r in _candidatos(medidas, zonas, canvas, titulo_y, dos_lineas, rejilla):
        if cualquiera is None or r["escala"] > cualquiera["escala"]:
            cualquiera = r
        if abs(r["cara_x"] - objetivo) <= tolerancia:
            if centrados is None or r["escala"] > centrados["escala"]:
                centrados = r
    return centrados or cualquiera


def resolver(medidas, zonas, canvas, titulo_y=None, dos_lineas=False, tolerancia=70):
    """Mejor encuadre: centrado primero, escala despues.

    Si la rejilla gruesa no encuentra nada, reintenta con la fina antes de
    declarar SIN SOLUCION: ver el comentario de REJILLA_FINA.
    """
    elegido = _mejor(medidas, zonas, canvas, titulo_y, dos_lineas,
                     tolerancia, REJILLA)
    if elegido is None:
        elegido = _mejor(medidas, zonas, canvas, titulo_y, dos_lineas,
                         tolerancia, REJILLA_FINA)
    if elegido is None:
        raise SinSolucion(diagnosticar(medidas, zonas, canvas, titulo_y, dos_lineas))
    return elegido


def variantes(medidas, zonas, canvas, titulo_y=None, dos_lineas=False, n=3,
              separacion=0.06):
    """Devuelve hasta N encuadres validos y visiblemente distintos entre si.

    Sirve para pruebas A/B: mismo dato y misma foto, encuadres alternativos.
    Se exige una separacion minima de escala para que las variantes no sean la
    misma imagen con un pixel de diferencia.
    """
    validos = sorted(_candidatos(medidas, zonas, canvas, titulo_y, dos_lineas),
                     key=lambda r: -r["escala"])
    elegidos = []
    for r in validos:
        if all(abs(r["escala"] - e["escala"]) / e["escala"] >= separacion
               for e in elegidos):
            elegidos.append(r)
        if len(elegidos) >= n:
            break
    return elegidos


def prever(medidas, canvas, expansiones, focal, zoom=1.0):
    """Donde caen pelo, menton y cara con los parametros REALMENTE aplicados.

    `resolver` calcula el encuadre que propone; esto calcula el que se aplico,
    que puede ser otro si alguien lo edito a mano en el proyecto. Es aritmetica
    exacta sobre las mismas formulas que usa la capa fotografica, asi que sirve
    para verificar sin volver a detectar nada -- que es justo lo que no se puede
    hacer con fiabilidad sobre una pieza ya recortada y con degradado encima.
    """
    cw, ch = canvas
    nw, nh = medidas["ancho"], medidas["alto"]
    exp = expansiones or {}
    nw1, nh3, extra_l, extra_a = expandir(
        nw, nh, exp.get("lados", 0), exp.get("arriba", 0), exp.get("abajo", 0))
    s, tx, ty = foto.cover(nw1, nh3, cw, ch, *focal, zoom=zoom)
    return {
        "escala": s,
        "pelo": ty + (medidas["pelo"] * nh + extra_a) * s,
        "menton": ty + (medidas["menton"] * nh + extra_a) * s,
        "cara_x": tx + nw1 * s * focal[0],
    }


def diagnosticar(medidas, zonas, canvas, titulo_y=None, dos_lineas=False):
    """Explica POR QUE no hay solucion, en vez de decir solo 'SIN SOLUCION'.

    Casi siempre la causa es la misma: el rostro ocupa demasiado alto de la
    foto. La ventana entre el bloque del logo y el titulo es estrecha, y un
    primer plano no entra con ninguna combinacion de expansiones. Cuando pasa,
    la salida no es calibrar mas: es cambiar la foto.
    """
    alto_rostro = medidas["menton"] - medidas["pelo"]
    techo = techo_menton(zonas, titulo_y, dos_lineas)
    ventana = techo - zonas["pelo_min"]
    _, ch = canvas

    motivos = ["No hay encuadre que cumpla las zonas seguras."]
    motivos.append("  ventana util: %d px (del pelo_min %d al techo de menton %d)"
                   % (ventana, zonas["pelo_min"], techo))
    motivos.append("  el rostro ocupa %.3f del alto de la foto" % alto_rostro)

    fraccion_max = ventana / float(ch)
    if alto_rostro > fraccion_max:
        motivos.append(
            "  -> CAUSA: el rostro es demasiado grande en la toma. Para esta pieza\n"
            "     no puede pasar de ~%.2f del alto y mide %.2f. Ninguna expansion\n"
            "     lo arregla: hay que reemplazar la fotografia por un plano mas abierto."
            % (fraccion_max, alto_rostro))
    else:
        motivos.append(
            "  -> El tamano daria, asi que el problema es horizontal: la cabeza no\n"
            "     alcanza la caja de silueta %s. Suele resolverse permitiendo mas\n"
            "     expansion lateral, que es lo unico que da recorrido en x."
            % (zonas["silueta"],))
    return "\n".join(motivos)
