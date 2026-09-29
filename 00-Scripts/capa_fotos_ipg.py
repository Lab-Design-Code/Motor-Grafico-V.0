#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Capa de fotografia para las graficas de admision IPG 2027 — plantillas V.2.

- sustituye la plancha gris de la plantilla por una foto de fondo a sangre
- dibuja el mapa de zonas seguras para encuadrar rostros y brazos

QUE CAMBIO EN LA V.2 (22-09-2026)
---------------------------------
La V.1 traia un grupo de fotos de Illustrator —tres paneles recortados en el
Post, uno fuera del lienzo en el Story— con el degradado inferior *dentro*
del grupo. Habia que localizar ese grupo, reemplazarlo entero y volver a
pintar el degradado, ademas de inventar uno propio arriba para que el logo
no se perdiera sobre fondos claros.

En la V.2 no hay grupo de fotos: la plantilla trae la plancha gris y, como
hermanos suyos dibujados encima, los dos degradados —superior e inferior— ya
resueltos por diseno. Asi que esto se reduce a una sola operacion: poner la
foto en el lugar exacto que ocupa la plancha. Todo lo que va encima
—degradados, textos, pastillas, logo— se pinta despues sin tocarlo.

Los `clipPath` de los tres paneles siguen declarados en el Post pero ya no
los usa nadie; la decision del 15-09-2026 de ir con una sola foto a sangre
sigue vigente.
"""
import re, base64, os

try:
    from PIL import Image as _Image
    # Las fotos expandidas llegan a superar los 100 MP y Pillow las rechaza por
    # defecto como decompression bomb. Son archivos propios generados por este
    # mismo modulo, no entrada de terceros.
    _Image.MAX_IMAGE_PIXELS = None
except ImportError:
    pass

# --------------------------------------------------- expansion de lienzo
# Las tres funciones de abajo agrandan el lienzo de la foto antes de
# encuadrarla. Se aplican SIEMPRE en este orden —lados, arriba, abajo— y cada
# `frac` se lee sobre el tamano que trae la imagen en ese punto de la cadena.
# La aritmetica de tamanos es intocable: los encuadres de las 43 carreras se
# resolvieron contra ella y cambiar un solo int() los invalida a todos.
#
# LO QUE SI CAMBIO (22-09-2026): de que esta hecho el relleno.
#
# Hasta ahora cada expansion tomaba una tira de 1% del borde, la estiraba
# hasta cubrir toda la zona nueva y la difuminaba. Eso produce vetas
# verticales u horizontales planas: a ojo se lee como un fondo pintado, no
# como fotografia, y en los encuadres grandes —Enfermeria lleva 1,90 de
# expansion lateral— esa zona ocupa mas de la mitad del cuadro.
#
# Ahora el lienzo nuevo se rellena **reflejando la propia fotografia**. El
# pixel que toca la costura es el mismo que estaba al lado, asi que el empalme
# es invisible, y lo que aparece son texturas, formas y luces reales de la
# escena: pasillo, pared, instrumental, profundidad de campo.
#
# Pero reflejar la foto *entera* no sirve: con 1,90 de expansion lateral el
# espejo trae al sujeto de vuelta dentro del cuadro y aparecen dos enfermeras.
# Lo que se refleja es solo una **banda del borde** —el 22% exterior, que en
# una foto bien elegida es fondo: pasillo, pared, taller— y esa banda se
# replica hacia afuera. Asi la zona nueva es fondo real de la misma escena y
# nunca una copia de la persona.
#
# Encima va una rampa de suavizado: nitido en la costura, cada vez mas blando
# hacia afuera hasta disolverse. Cerca del sujeto se ve fotografia de verdad;
# lejos, un fondo desenfocado que no compite ni delata la repeticion. Es el
# mismo efecto de profundidad de campo que usan los avisos de referencia.
_BANDA = 0.22        # fraccion del borde que se toma como material
_RAMPA = 0.22        # a que fraccion de la zona nueva el suavizado es total
_REDUCCION = 14      # cuanto se achica para generar la capa blanda
_RADIO = 7           # desenfoque sobre esa miniatura


def _capa_blanda(banda):
    """Version desenfocada de una banda, por reduccion y reescalado.

    Difuminar directo una banda de 40 MP con GaussianBlur de radio grande es
    inviable; achicar, desenfocar poco y volver a escalar da el mismo aspecto
    a una fraccion del costo.
    """
    from PIL import Image, ImageFilter
    w, h = banda.size
    chica = banda.resize((max(1, w // _REDUCCION), max(1, h // _REDUCCION)),
                         Image.LANCZOS)
    chica = chica.filter(ImageFilter.GaussianBlur(radius=_RADIO))
    return chica.resize((w, h), Image.BILINEAR)


def _continuar(a, n, eje, inicio):
    """n pixeles de continuacion del borde, reflejando la banda exterior.

    Se refleja con mode="reflect", que no repite el pixel del borde: la
    columna (o fila) que toca la costura es la vecina inmediata de la
    original, asi que el empalme no se ve. Si n supera la banda, numpy sigue
    reflejando y el motivo se repite — para eso esta la rampa de suavizado.
    """
    import numpy as np

    lado = a.shape[eje]
    b = max(2, min(lado, int(lado * _BANDA)))
    if eje == 1:
        banda = a[:, :b] if inicio else a[:, lado - b:]
        ancho = ((0, 0), (n, 0) if inicio else (0, n), (0, 0))
    else:
        banda = a[:b] if inicio else a[lado - b:]
        ancho = ((n, 0) if inicio else (0, n), (0, 0), (0, 0))

    ext = np.pad(banda, ancho, mode="reflect")
    ext = ext[:, :n] if eje == 1 and inicio else \
          ext[:, b:] if eje == 1 else \
          ext[:n] if inicio else ext[b:]
    return _suavizar_hacia_afuera(np.ascontiguousarray(ext), eje, inicio)


def _suavizar_hacia_afuera(ext, eje, inicio):
    """Mezcla la extension con su version blanda segun la distancia a la costura.

    La costura esta al final de la extension cuando crece hacia el inicio de
    la imagen, y al principio cuando crece hacia el final. Se procesa por
    tramos para no levantar un float32 del tamano de la extension entera.
    """
    import numpy as np
    from PIL import Image

    n = ext.shape[eje]
    if n == 0:
        return ext
    blanda = np.asarray(_capa_blanda(Image.fromarray(ext)))

    d = np.arange(n, dtype=np.float32)
    if inicio:                      # costura al final: la distancia crece hacia 0
        d = n - 1 - d
    t = np.clip(d / max(1.0, n * _RAMPA), 0.0, 1.0)

    otro = ext.shape[1 - eje]
    paso = 512
    for i in range(0, otro, paso):
        j = min(i + paso, otro)
        if eje == 1:
            tr = t[None, :, None]
            ext[i:j] = (ext[i:j].astype(np.float32) * (1 - tr)
                        + blanda[i:j].astype(np.float32) * tr).astype(np.uint8)
        else:
            tr = t[:, None, None]
            ext[:, i:j] = (ext[:, i:j].astype(np.float32) * (1 - tr)
                           + blanda[:, i:j].astype(np.float32) * tr).astype(np.uint8)
    return ext


def _crecer(a, antes, despues, eje):
    import numpy as np
    partes = []
    if antes:
        partes.append(_continuar(a, antes, eje, inicio=True))
    partes.append(a)
    if despues:
        partes.append(_continuar(a, despues, eje, inicio=False))
    return np.concatenate(partes, axis=eje) if len(partes) > 1 else a


def _expandir(path_in, path_out, izq, der, arriba, abajo):
    """Agranda el lienzo con fondo reflejado de la propia foto."""
    import numpy as np
    from PIL import Image

    a = np.asarray(Image.open(path_in).convert("RGB"))
    if izq or der:
        a = _crecer(a, izq, der, eje=1)
    if arriba or abajo:
        a = _crecer(a, arriba, abajo, eje=0)
    Image.fromarray(a).save(path_out, quality=93)


def expandir_foto_arriba(path_in, path_out, frac=0.15):
    """Agranda el lienzo hacia arriba: aire de techo sobre la cabeza, para que
    el sujeto no invada la franja del logo al recortar."""
    from PIL import Image
    nh = Image.open(path_in).size[1]
    _expandir(path_in, path_out, 0, 0, int(nh * frac), 0)


def expandir_foto_abajo(path_in, path_out, frac=0.05):
    """Agranda el lienzo hacia abajo: mas piso, para subir al sujeto sin
    agrandarlo.

    El cover del Post ancla la foto al borde inferior (fy=1, fy_destino=1) y
    el ancho calza exacto, asi que no queda holgura vertical para desplazar:
    cada pixel que se agrega abajo empuja al sujeto hacia arriba en la misma
    proporcion. Es el unico lever que le da aire al menton sin achicar la cara.
    """
    from PIL import Image
    nh = Image.open(path_in).size[1]
    _expandir(path_in, path_out, 0, 0, 0, int(nh * frac))


def expandir_foto_lados(path_in, path_out, frac=0.4):
    """Agranda el lienzo a los lados. frac es el ancho extra total como
    fraccion del ancho original y se reparte mitad a cada lado.

    No es cosmetico: es lo unico que da recorrido horizontal. Sin ancho
    sobrante el cover no puede correr la foto lo suficiente para llevar la
    cabeza hasta la caja de silueta.
    """
    from PIL import Image
    nw = Image.open(path_in).size[0]
    extra = int(nw * frac / 2)
    _expandir(path_in, path_out, extra, extra, 0, 0)

# ----------------------------------------------------------------- zonas
# Post 1080x1080
ZONAS_POST = {
    "canvas": (1080, 1080),
    # bloque logo IPG + sello CNA: nada de cabezas ni brazos aqui
    "logo":   (20, 20, 700, 185),
    # desde aqui hacia abajo entra el degradado + todo el texto. En la V.2 el
    # bloque ya no empieza en el prefijo sino en la pastilla de modalidad, que
    # cuelga 7 px mas arriba (y=432,5). Con titulo a dos lineas sube otro tanto.
    "texto_y": 432,
    # banda recomendada para que caigan los rostros
    "rostros": (200, 425),
    # caja donde va el sujeto: el lado izquierdo queda libre para el logo
    # arriba y para el titulo abajo, asi que la persona se corre a la derecha
    "silueta": (600, 210, 960, 1080),
    "plancha_re": r'<rect class="st28"[^>]*/>',
}

# Story 1080x1920
ZONAS_STORY = {
    "canvas": (1080, 1920),
    "logo":   (40, 70, 720, 240),
    # La pastilla de modalidad arranca en y=699,4: el texto empieza antes que
    # en la V.1 (740) y antes tambien que el degradado inferior de la
    # plantilla, que no se activa hasta y=1036,9.
    "texto_y": 699,
    "rostros": (270, 660),
    "silueta": (445, 305, 1015, 1920),
    "plancha_re": r'<rect class="st28"[^>]*/>',
}


def _mime(path):
    ext = os.path.splitext(path)[1].lower()
    return {".jpg": "image/jpeg", ".jpeg": "image/jpeg",
            ".png": "image/png", ".webp": "image/webp"}.get(ext, "image/jpeg")


def _cover(nw, nh, cw, ch, fx, fy, fxt, fyt, zoom=1.0):
    """Escala la imagen para cubrir el lienzo y alinea el punto focal.

    zoom > 1 sobre-escala mas alla del minimo que cubre el lienzo, dejando
    margen en la dimension que de otro modo quedaria sin holgura (p.ej.
    la vertical cuando la foto es mas ancha que el lienzo). Sin ese margen
    fy/fyt no tienen ningun efecto: el encuadre vertical queda fijo y no
    se puede alejar la cabeza de la franja del logo.
    """
    s = max(cw / nw, ch / nh) * zoom
    sw, sh = nw * s, nh * s
    tx = cw * fxt - sw * fx
    ty = ch * fyt - sh * fy
    tx = min(0.0, max(cw - sw, tx))
    ty = min(0.0, max(ch - sh, ty))
    return s, tx, ty


def poner_foto(svg, z, foto, focal=(0.5, 0.38, 0.5, 0.33), zoom=1.0):
    """Sustituye la plancha gris por la foto de fondo.

    focal = (fx, fy, fx_destino, fy_destino).

    La foto ocupa el sitio exacto de la plancha, que es el primer elemento
    pintado del SVG. Los degradados de la plantilla son hermanos posteriores,
    asi que caen encima sin intervencion. La plantilla V.2 declara xlink en el
    <svg>, de modo que el href del <image> resuelve sin anadir namespaces.
    """
    from PIL import Image
    nw, nh = Image.open(foto).size
    cw, ch = z["canvas"]
    s, tx, ty = _cover(nw, nh, cw, ch, *focal, zoom=zoom)
    b64 = base64.b64encode(open(foto, "rb").read()).decode("ascii")

    capa = ('<g><image width="%d" height="%d" transform="translate(%.2f %.2f) scale(%.5f)" '
            'xlink:href="data:%s;base64,%s"/></g>') % (
                nw, nh, tx, ty, s, _mime(foto), b64)

    m = re.search(z["plancha_re"], svg)
    if not m:
        raise SystemExit("No encontre la plancha gris de la plantilla")
    return svg[:m.start()] + capa + svg[m.end():]


def mapa_zonas(svg, z):
    """Superpone el mapa de zonas seguras sobre la grafica."""
    cw, ch = z["canvas"]
    lx, ly, lx2, ly2 = z["logo"]
    r0, r1 = z["rostros"]
    ov = ['<g id="zonas" opacity="0.9">']
    ov.append('<rect x="%d" y="%d" width="%d" height="%d" fill="#ff0033" fill-opacity="0.28" '
              'stroke="#ff0033" stroke-width="4"/>' % (lx, ly, lx2 - lx, ly2 - ly))
    ov.append('<rect x="0" y="%d" width="%d" height="%d" fill="#00e0ff" fill-opacity="0.10"/>'
              % (r0, cw, r1 - r0))
    ov.append('<line x1="0" y1="%d" x2="%d" y2="%d" stroke="#00e0ff" stroke-width="4" '
              'stroke-dasharray="18 12"/>' % (r0, cw, r0))
    ov.append('<line x1="0" y1="%d" x2="%d" y2="%d" stroke="#00e0ff" stroke-width="4" '
              'stroke-dasharray="18 12"/>' % (r1, cw, r1))
    ov.append('<rect x="0" y="%d" width="%d" height="%d" fill="#ffcc00" fill-opacity="0.16"/>'
              % (z["texto_y"], cw, ch - z["texto_y"]))
    if "silueta" in z:
        sx, sy, sx2, sy2 = z["silueta"]
        ov.append('<rect x="%d" y="%d" width="%d" height="%d" fill="none" '
                  'stroke="#ffffff" stroke-width="5"/>' % (sx, sy, sx2 - sx, sy2 - sy))
        ov.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#ffffff" '
                  'stroke-width="3" stroke-dasharray="14 10"/>'
                  % ((sx + sx2) / 2, sy, (sx + sx2) / 2, sy2))
    f = 30 if ch == 1080 else 36
    ov.append('<text x="%d" y="%d" font-family="Montserrat" font-weight="800" font-size="%d" '
              'fill="#ff0033">SIN CABEZAS NI BRAZOS</text>' % (lx + 14, ly2 - 16, f - 6))
    ov.append('<text x="24" y="%d" font-family="Montserrat" font-weight="800" font-size="%d" '
              'fill="#00e0ff">BANDA DE ROSTROS</text>' % (r0 + f + 4, f))
    ov.append('<text x="24" y="%d" font-family="Montserrat" font-weight="800" font-size="%d" '
              'fill="#ffcc00">ZONA DE TEXTO — SOLO CUERPO/FONDO</text>'
              % (z["texto_y"] + f + 4, f))
    if "silueta" in z:
        sx, sy, sx2, sy2 = z["silueta"]
        ov.append('<text x="%d" y="%d" font-family="Montserrat" font-weight="800" '
                  'font-size="%d" fill="#ffffff">SILUETA</text>' % (sx + 12, sy + f, f))
    ov.append('</g>')
    return svg.replace("</svg>", "".join(ov) + "</svg>")


if __name__ == "__main__":
    import sys, json
    cfg = json.load(open(sys.argv[1], encoding="utf-8"))
    base = os.path.dirname(os.path.abspath(__file__))
    repo = os.path.dirname(base)
    out_dir = os.path.join(repo, "04-Post-Story", cfg["slug"])
    fotos_dir = os.path.join(repo, "03-Fotografias")
    for tag, z in (("Post", ZONAS_POST), ("Story", ZONAS_STORY)):
        src = os.path.join(out_dir, "%s-IPG_2027-%s.svg" % (tag, cfg["slug"]))
        svg = open(src, encoding="utf-8").read()
        if cfg.get("foto_" + tag.lower()) or cfg.get("foto"):
            f = cfg.get("foto_" + tag.lower()) or cfg["foto"]
            if not os.path.isabs(f):
                f = os.path.join(fotos_dir, f)
            arriba = cfg.get("expandir_arriba_" + tag.lower()) or cfg.get("expandir_arriba")
            lados = cfg.get("expandir_lados_" + tag.lower()) or cfg.get("expandir_lados")
            abajo = cfg.get("expandir_abajo_" + tag.lower()) or cfg.get("expandir_abajo")
            if arriba or lados or abajo:
                base_name, ext_name = os.path.splitext(os.path.basename(f))
                tag_exp = "%s-a%s-l%s%s-r%s" % (base_name, arriba or 0, lados or 0,
                                                ("-b%s" % abajo) if abajo else "",
                                                ext_name)
                f_exp = os.path.join(fotos_dir, "_expandidas", tag_exp)
                os.makedirs(os.path.dirname(f_exp), exist_ok=True)
                if not os.path.exists(f_exp):
                    paso, temporales = f, []
                    for frac, fn in ((lados, expandir_foto_lados),
                                     (arriba, expandir_foto_arriba),
                                     (abajo, expandir_foto_abajo)):
                        if not frac:
                            continue
                        destino = "%s.%s.jpg" % (f_exp, fn.__name__)
                        fn(paso, destino, frac=frac)
                        paso = destino
                        temporales.append(destino)
                    if paso == f:
                        raise SystemExit("No hay expansion que aplicar")
                    os.replace(paso, f_exp)
                    for t in temporales:
                        if os.path.exists(t):
                            os.remove(t)
                f = f_exp
            foc = cfg.get("focal_" + tag.lower()) or cfg.get("focal") or (0.5, 0.38, 0.5, 0.33)
            zoom = cfg.get("zoom_" + tag.lower()) or cfg.get("zoom") or 1.0
            svg = poner_foto(svg, z, f, tuple(foc), zoom=zoom)
            open(os.path.join(out_dir, "%s-IPG_2027-%s-FOTO.svg" % (tag, cfg["slug"])), "w",
                 encoding="utf-8").write(svg)
        open(os.path.join(out_dir, "%s-IPG_2027-%s-ZONAS.svg" % (tag, cfg["slug"])), "w",
             encoding="utf-8").write(mapa_zonas(svg, z))
        print("ok", tag)
