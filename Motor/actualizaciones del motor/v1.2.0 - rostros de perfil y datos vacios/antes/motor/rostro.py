# -*- coding: utf-8 -*-
"""Medicion automatica del rostro: tope del pelo, menton y centro horizontal.

Por que importa
---------------
Este era el unico paso del pipeline que no escalaba: habia que abrir cada foto,
superponer una grilla y leer a ojo tres valores. Y es ademas el paso donde un
error chico sale caro -- 0,05 del alto son ~50 px en el lienzo, suficiente para
que el menton termine bajo el titulo aunque el solver diga que el encuadre
cumple.

Como se mide
------------
Se usa el mejor backend disponible, en este orden:

  1. mediapipe FaceMesh  -- 468 puntos; menton y frente son landmarks reales.
  2. OpenCV (Haar)       -- solo una caja de rostro; menton y frente se derivan.
  3. manual              -- valores escritos a mano en el JSON de datos.

El tope del pelo NO es un landmark en ninguna libreria: el pelo no tiene
geometria estable. Se estima sobre la altura del rostro y por eso **siempre hay
que mirar la imagen de verificacion** antes de dar por buena una medicion. Es
exactamente el paso que se saltaron las seis fotos que hubo que rehacer.
"""
import os

from PIL import Image, ImageDraw

Image.MAX_IMAGE_PIXELS = None

# Cuanto pelo hay sobre la frente, como fraccion del alto del rostro. Es una
# estimacion: cabello recogido queda por debajo, un peinado voluminoso por
# encima. Se puede afinar por foto con "pelo_factor" en los datos.
PELO_SOBRE_FRENTE = 0.28

# Lado mas largo al que se reduce la imagen antes de detectar. Detectar sobre
# la foto completa de 9000 px es lento y no mas preciso; el resultado se
# devuelve siempre en fracciones, asi que la escala de trabajo es indiferente.
LADO_DETECCION = 1600


class SinRostro(RuntimeError):
    pass


def _miniatura(ruta):
    im = Image.open(ruta).convert("RGB")
    ancho, alto = im.size
    escala = min(1.0, LADO_DETECCION / float(max(ancho, alto)))
    if escala < 1.0:
        im = im.resize((int(ancho * escala), int(alto * escala)), Image.LANCZOS)
    return im, ancho, alto


def _elegir(cajas, sujeto):
    """Elige entre varios rostros detectados.

    Cuando la foto trae mas de una persona, encuadrar el punto medio deja a una
    centrada y a la otra partida contra el borde. Hay que elegir un sujeto
    unico, y por defecto se toma el mas grande (el que domina la composicion).
    """
    if not cajas:
        raise SinRostro("no se detecto ningun rostro")
    if sujeto == "izquierda":
        return min(cajas, key=lambda c: c[0])
    if sujeto == "derecha":
        return max(cajas, key=lambda c: c[0] + c[2])
    return max(cajas, key=lambda c: c[2] * c[3])


RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELOS = os.path.join(RAIZ, "modelos")


def _modelo(*nombres):
    """Busca un archivo de modelo en modelos/. Devuelve None si no esta.

    Los modelos no se descargan solos a proposito: bajar archivos es una
    decision del usuario, no del motor. Sin modelo, el backend se salta y se
    usa el siguiente, que funciona sin descargar nada.
    """
    for n in nombres:
        ruta = os.path.join(MODELOS, n)
        if os.path.exists(ruta):
            return ruta
    return None


def _por_mediapipe(im, sujeto):
    """FaceLandmarker de mediapipe: 478 puntos, menton y frente son reales.

    Es el backend mas preciso. Desde mediapipe 1.0 la API `solutions` ya no
    existe y hay que usar `tasks`, que necesita el bundle face_landmarker.task
    en modelos/.
    """
    import numpy as np
    from mediapipe.tasks import python as mp_python
    from mediapipe.tasks.python import vision
    import mediapipe as mp

    ruta = _modelo("face_landmarker.task", "face_landmarker_v2_with_blendshapes.task")
    if ruta is None:
        raise SinRostro("falta modelos/face_landmarker.task")

    arr = np.asarray(im)
    opciones = vision.FaceLandmarkerOptions(
        base_options=mp_python.BaseOptions(model_asset_path=ruta),
        num_faces=5, running_mode=vision.RunningMode.IMAGE)
    with vision.FaceLandmarker.create_from_options(opciones) as det:
        res = det.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=arr))
    if not res.face_landmarks:
        raise SinRostro("mediapipe no detecto rostros")

    h, w = arr.shape[:2]
    caras = []
    for lm in res.face_landmarks:
        xs = [p.x * w for p in lm]
        frente = lm[10].y * h    # alto de la frente
        menton = lm[152].y * h   # punta del menton
        caras.append({"x": min(xs), "y": frente, "w": max(xs) - min(xs),
                      "h": menton - frente, "frente": frente,
                      "menton": menton, "centro": lm[1].x * w})

    clave = _elegir([(c["x"], c["y"], c["w"], c["h"]) for c in caras], sujeto)
    return next(c for c in caras
                if (c["x"], c["y"], c["w"], c["h"]) == clave), "mediapipe"


def _por_yunet(im, sujeto):
    """YuNet (OpenCV DNN). Es el unico detector de OpenCV 5, que elimino Haar."""
    import cv2
    import numpy as np

    if not hasattr(cv2, "FaceDetectorYN"):
        raise SinRostro("esta version de OpenCV no trae YuNet")
    ruta = _modelo("face_detection_yunet_2023mar.onnx", "face_detection_yunet.onnx")
    if ruta is None:
        raise SinRostro("falta modelos/face_detection_yunet_2023mar.onnx")

    arr = np.asarray(im)[:, :, ::-1]  # YuNet espera BGR
    h, w = arr.shape[:2]
    det = cv2.FaceDetectorYN.create(ruta, "", (w, h), 0.6)
    _, caras = det.detect(np.ascontiguousarray(arr))
    if caras is None or len(caras) == 0:
        raise SinRostro("YuNet no detecto rostros")

    cajas = [tuple(float(v) for v in c[:4]) for c in caras]
    x, y, cw, ch = _elegir(cajas, sujeto)
    return {"x": x, "y": y, "w": cw, "h": ch, "frente": y,
            "menton": y + ch, "centro": x + cw / 2.0}, "yunet"


def _por_haar(im, sujeto):
    """Clasificador Haar de OpenCV 4.x.

    Es el menos preciso de los tres, pero el unico que no necesita descargar
    nada: los XML vienen dentro del propio paquete. Para retratos de banco de
    imagenes -- una persona, frontal, bien iluminada -- alcanza de sobra.
    """
    import cv2
    import numpy as np

    if not hasattr(cv2, "CascadeClassifier"):
        raise SinRostro("OpenCV %s ya no expone CascadeClassifier" % cv2.__version__)

    arr = np.asarray(im)
    gris = cv2.equalizeHist(cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY))
    cascada = cv2.CascadeClassifier(
        os.path.join(cv2.data.haarcascades, "haarcascade_frontalface_default.xml"))
    cajas = cascada.detectMultiScale(gris, scaleFactor=1.08, minNeighbors=6,
                                     minSize=(60, 60))
    if len(cajas) == 0:
        raise SinRostro("Haar no detecto rostros frontales")

    x, y, w, h = _elegir([tuple(int(v) for v in c) for c in cajas], sujeto)
    # La caja de Haar arranca sobre las cejas y termina cerca del menton.
    return {"x": x, "y": y, "w": w, "h": h, "frente": y,
            "menton": y + h, "centro": x + w / 2.0}, "haar"


BACKENDS = [("mediapipe", _por_mediapipe), ("yunet", _por_yunet), ("haar", _por_haar)]


def medir(ruta, sujeto="mayor", pelo_factor=None, backend=None):
    """Mide un rostro y devuelve fracciones listas para el solver.

    Devuelve dict con ancho, alto (px reales de la foto), pelo, menton
    (fraccion del alto) y cara_x (fraccion del ancho), mas el backend usado.
    """
    im, ancho_real, alto_real = _miniatura(ruta)
    h_mini = im.size[1]
    w_mini = im.size[0]

    intentos = [(n, fn) for n, fn in BACKENDS if backend in (None, n)]
    if not intentos:
        raise SinRostro("backend desconocido: %r (usa %s)"
                        % (backend, ", ".join(n for n, _ in BACKENDS)))

    errores = []
    cara = motor_usado = None
    for nombre, fn in intentos:
        try:
            cara, motor_usado = fn(im, sujeto)
            break
        except ImportError as e:
            errores.append("%-10s no instalado (%s)" % (nombre, e))
        except SinRostro as e:
            errores.append("%-10s %s" % (nombre, e))
        except Exception as e:  # un backend roto no debe tumbar al siguiente
            errores.append("%-10s %s: %s" % (nombre, type(e).__name__, e))

    if cara is None:
        raise SinRostro(
            "No pude medir el rostro de %s\n  %s\n\n"
            "Opciones, de mas simple a mejor:\n"
            "  pip install \"opencv-python<5\"   -> Haar, funciona sin descargar nada\n"
            "  modelos/face_detection_yunet_2023mar.onnx   -> mejor deteccion\n"
            "  modelos/face_landmarker.task (mediapipe)    -> menton real, la mas precisa\n"
            "O escribe las medidas a mano en la pieza del proyecto:\n"
            '  "medidas": {"ancho": 5333, "alto": 3000, "pelo": 0.05, '
            '"menton": 0.30, "cara_x": 0.55}'
            % (os.path.basename(ruta), "\n  ".join(errores)))

    factor = PELO_SOBRE_FRENTE if pelo_factor is None else float(pelo_factor)
    pelo_px = max(0.0, cara["frente"] - cara["h"] * factor)

    return {
        "ancho": ancho_real,
        "alto": alto_real,
        "pelo": round(pelo_px / h_mini, 4),
        "menton": round(cara["menton"] / h_mini, 4),
        "cara_x": round(cara["centro"] / w_mini, 4),
        "_backend": motor_usado,
        "_caja": [round(cara["x"] / w_mini, 4), round(cara["y"] / h_mini, 4),
                  round(cara["w"] / w_mini, 4), round(cara["h"] / h_mini, 4)],
    }


def verificacion(ruta, medidas, destino, lado=1000):
    """Escribe una imagen con las medidas dibujadas encima.

    No es opcional en la practica: el tope del pelo es una estimacion y esta
    imagen es la unica forma barata de confirmarla antes de generar 20 piezas
    sobre una medida mala.
    """
    im = Image.open(ruta).convert("RGB")
    w, h = im.size
    escala = min(1.0, lado / float(max(w, h)))
    im = im.resize((int(w * escala), int(h * escala)), Image.LANCZOS)
    w, h = im.size
    d = ImageDraw.Draw(im)

    y_pelo = medidas["pelo"] * h
    y_menton = medidas["menton"] * h
    x_cara = medidas["cara_x"] * w

    d.line([(0, y_pelo), (w, y_pelo)], fill=(0, 224, 255), width=3)
    d.line([(0, y_menton), (w, y_menton)], fill=(255, 204, 0), width=3)
    d.line([(x_cara, 0), (x_cara, h)], fill=(255, 0, 51), width=3)
    d.text((8, max(0, y_pelo - 18)), "PELO %.3f" % medidas["pelo"], fill=(0, 224, 255))
    d.text((8, y_menton + 6), "MENTON %.3f" % medidas["menton"], fill=(255, 204, 0))
    d.text((min(w - 90, x_cara + 6), 8), "X %.3f" % medidas["cara_x"], fill=(255, 0, 51))

    os.makedirs(os.path.dirname(os.path.abspath(destino)), exist_ok=True)
    im.save(destino, quality=90)
    return destino
