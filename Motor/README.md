# Motor de Gráficas · motor genérico v1.3.0

> **© 2026 Ariel Garay Pavez. Todos los derechos reservados.** Mismos términos
> que el resto del repositorio: ver [`../LICENSE`](../LICENSE).
>
> Esta carpeta es el **motor genérico**, reutilizable con otras marcas. Los
> scripts de la campaña Meta IPG 2027 siguen en [`../00-Scripts`](../00-Scripts).
> La interfaz web local (plataforma de producción) **no está incluida**.
> Novedades de cada versión: [`actualizaciones del motor/`](actualizaciones%20del%20motor/LEEME.md).

Genera lotes de piezas gráficas a partir de **una plantilla + una planilla de
datos**, resolviendo el encuadre de cada fotografía contra las zonas seguras de
la marca y verificando cada pieza antes de entregarla.

**El motor no conoce ninguna marca.** No hay nombres de cliente en el código: la
marca entera vive en un `plantillas/<marca>/plantilla.json` y los datos en un
`proyectos/<proyecto>/proyecto.json`. Montar un cliente nuevo es escribir esos
dos archivos; no se toca Python.

---

## Índice

1. [Qué necesita una máquina nueva](#1-qué-necesita-una-máquina-nueva)
2. [Montar una marca](#2-montar-una-marca) ← **empieza acá**
3. [Los ocho comandos](#3-los-ocho-comandos)
4. [`plantilla.json` — el contrato de la marca](#4-plantillajson--el-contrato-de-la-marca)
5. [`proyecto.json` — los datos del lote](#5-proyectojson--los-datos-del-lote)
6. [Qué verifica el QA](#6-qué-verifica-el-qa)
7. [Lo que cuesta caro aprender](#7-lo-que-cuesta-caro-aprender)
8. [Expansión de lienzo: reflejo o generativa](#8-expansión-de-lienzo-reflejo-o-generativa)
9. [Windows: dos trampas de codificación](#9-windows-dos-trampas-de-codificación)
10. [Qué NO incluye](#10-qué-no-incluye)
11. [Estructura](#11-estructura)
12. [Caso de validación](#12-caso-de-validación)

> **Dónde vive cada cosa.** Este README documenta **la herramienta**. Los
> supuestos de cada cliente —cómo se redondea un precio, cómo se nombran las
> sedes, por qué tal foto lleva tal sujeto— van en el `LEEME.md` de su proyecto.
> Mezclarlos es lo que vuelve una herramienta inservible para el siguiente
> cliente.

| | |
|---|---|
| Cómo se arma una marca | [`plantillas/LEEME.md`](plantillas/LEEME.md) |
| Cómo se arma un lote | [`proyectos/LEEME.md`](proyectos/LEEME.md) |
| Lo comercial | [`Web/README.md`](Web/README.md) |

---

## 1. Qué necesita una máquina nueva

```bash
pip install -r requirements.txt
python graficas.py diagnostico
```

`diagnostico` dice qué encontró y qué falta. **No hay archivo de
configuración**: las fuentes y el rasterizador se buscan en el orden habitual
del sistema.

**Fuentes.** Se busca primero en `fuentes/` dentro de esta carpeta. Dejar ahí
los `.otf` de la marca es lo que hace portable al motor: deja de depender de que
la fuente esté instalada en la máquina.

**Rasterizador.** Hace falta `resvg` (recomendado: un solo binario y varias
veces más rápido) o Inkscape. Si está en una ruta rara, `MOTOR_RASTERIZADOR`
apunta al ejecutable.

**Detector de rostro.** Tres backends; se usa el primero disponible.

| Backend | Precisión | Qué necesita |
|---|---|---|
| mediapipe FaceLandmarker | mejor: mentón y frente son puntos reales | `modelos/face_landmarker.task` |
| YuNet (OpenCV DNN) | buena | `modelos/face_detection_yunet_2023mar.onnx` |
| Haar (OpenCV) | suficiente para retratos de banco | **nada**: viene en el paquete |

> **Ojo con la versión de OpenCV.** La serie 5 eliminó `CascadeClassifier` de
> los bindings de Python y sólo deja YuNet, que exige descargar un modelo. Por
> eso `requirements.txt` pide `opencv-python<5`: es lo que hace que el motor
> funcione recién instalado, sin descargar nada. Los modelos **no se bajan
> solos** a propósito — descargar archivos es decisión del usuario.

Sin ningún detector el motor sigue funcionando: se escriben las `medidas` a mano
en el proyecto.

---

## 2. Montar una marca

### Camino rápido: sin nombrar capas

Lo habitual es recibir el arte de Illustrator con **textos de ejemplo** y un
**Excel** con los datos, no un archivo con capas nombradas. Para ese caso:

```bash
python graficas.py montar <marca> datos.xlsx post=arte-post.svg story=arte-story.svg
```

El arte se exporta una vez desde Illustrator: *Archivo › Exportar › Exportar
como › SVG*, con **CSS interno**, texto como **SVG** (no contornos) e imágenes
**incrustadas**. El Excel lleva una fila por pieza, con encabezados en la
primera fila; una columna `foto` (nombre del archivo) y una `slug` son
opcionales.

`montar` hace solo lo que antes eran los pasos 1 a 3:

- **Reconoce cada texto por su contenido**: si el arte dice «Sede Online» y ese
  valor está en la columna `Sede`, esa capa es `{sede}`. Un texto que *contiene*
  un dato queda como patrón («DE HASTA 00%» → `DE HASTA {beca}%`). Si el
  ejemplo no está en el Excel, un número se reconoce por su magnitud y se marca
  **REVISAR**.
- **Deduce el comportamiento**: pastilla que se estira, botón de ancho fijo,
  subrayado, párrafo de varias líneas, texto centrado, titular que se parte en
  dos arrastrando lo que tiene encima. Columnas numeradas (`badge 1`,
  `badge 2`…) se vuelven una serie de pastillas.
- **Aprende las zonas seguras** de la foto de ejemplo: donde el diseñador puso
  la cara es donde la quiere. Si no encuentra una cara fiable, ubica a la
  persona en el hueco más grande que deja el diseño, bajo el logo.

Escribe `plantillas/<marca>/` y `proyectos/<marca>/proyecto.json`, e imprime qué
decidió y por qué. **Es un punto de partida**: se revisa la primera pieza con
`generar --solo <slug> --zonas` y se corrige lo que haga falta en
`plantilla.json`. Si un texto no se reconoce, se fuerza con
`--mapa "texto del arte=columna"` (o `--mapa "$00.000=${cuota:miles}"`).

Validado contra la campaña IPG sin nombrar ninguna capa: las 166 piezas salen
con los mismos textos y cortes de línea que la plantilla hecha a mano (desvío
máximo 0,03 px; 4 px en el centrado de la cuota; pastillas ±8 px).

### Camino manual

Cuando se quiere control total, o el arte no sale de Illustrator. Cuatro pasos.

### Paso 1 · Preparar la plantilla

El diseñador entrega el arte en SVG. El motor localiza cada elemento por su
`id`, **no por su clase CSS**, y la razón es dura: Illustrator **renumera las
clases en cada exportación**. Un motor que busque `cls-14` se rompe entero la
primera vez que el diseñador vuelve a exportar, y se rompe en silencio — el
selector simplemente no encuentra nada.

Hay un atajo permanente: **si el diseñador nombra la capa `m-nombre` en
Illustrator, el exportador escribe ese nombre como `id`** y la plantilla sale
lista, sin paso de preparación. Vale la pena pedírselo una vez.

Para plantillas que ya existen, se escribe una `receta.json` que traduce los
selectores viejos y se corre una vez:

```bash
python herramientas/preparar_plantilla.py plantillas/<marca>/receta.json
```

Verifica sola: si un `id` no queda localizable, lo dice.

### Paso 2 · Derivar las zonas seguras

```bash
python graficas.py zonas plantillas/<marca> <formato>
```

Devuelve **medidos del arte** el bloque de logo, la Y del título y la zona de
texto, más una propuesta de silueta y aire.

Los tres primeros se pegan tal cual. **La silueta y el aire son decisiones de
composición** —dónde se quiere a la persona, cuánto respiro debajo del mentón—
y hay que revisarlas contra una pieza real. No hay valor universal: dependen de
dónde puso el diseñador el logo y el bloque de texto.

### Paso 3 · Escribir el `plantilla.json`

Un elemento por dato que cambia. Lo único obligatorio es `id`, `tipo`, de dónde
sale el dato y con qué fuente se mide: la posición y el cuerpo tipográfico los
lee del propio SVG.

### Paso 4 · Armar el proyecto y correr

```bash
python graficas.py encuadrar proyectos/<proyecto>/proyecto.json --verificacion revisar/
python graficas.py generar   proyectos/<proyecto>/proyecto.json --qa
```

`--verificacion` deja una imagen por pieza con los puntos medidos dibujados
encima. Vale la pena mirarla la primera vez con cada marca.

### Antes de comprar fotos

```bash
python graficas.py filtrar plantillas/<marca> candidatas/*.jpg
```

Descarta lo que **no tiene encuadre posible** con las zonas de esa marca, sobre
la miniatura pública y antes de gastar una licencia. El mensaje distingue si el
problema es el tamaño del rostro o su posición horizontal.

---

## 3. Los ocho comandos

```bash
# qué encuentra el motor en esta máquina
python graficas.py diagnostico

# monta una marca desde el arte de Illustrator y el Excel, sin nombrar capas
python graficas.py montar <marca> datos.xlsx post=arte-post.svg

# propone las zonas seguras leyendo el arte de la plantilla
python graficas.py zonas plantillas/<marca> <formato>

# descarta fotos candidatas ANTES de licenciarlas
python graficas.py filtrar plantillas/<marca> candidatas/*.jpg

# mide rostros y resuelve el encuadre de todas las piezas
python graficas.py encuadrar proyectos/<proyecto>/proyecto.json --verificacion revisar/

# genera el lote y lo verifica
python graficas.py generar proyectos/<proyecto>/proyecto.json --qa

# revisa una entrega ya generada, sin volver a rasterizar
python graficas.py qa proyectos/<proyecto>/proyecto.json --informe qa.txt

# N encuadres alternativos de una pieza, para prueba A/B
python graficas.py variantes proyectos/<proyecto>/proyecto.json <slug> <formato>
```

Opciones útiles de `generar`: `--solo <texto>` para una pieza suelta,
`--con-svg` para dejar el editable, `--zonas` para superponer el mapa de zonas
cuando algo se ve mal, `--informe archivo.txt` para guardar el QA.

---

## 4. `plantilla.json` — el contrato de la marca

```jsonc
{
  "campos": { "nombre": {"tipo":"texto","requerido":true} },
  "formatos": {
    "<formato>": {
      "archivo": "<formato>.svg", "ancho": 1080, "alto": 1080,
      "elementos": [ ... ],
      "foto":  { "capa_id": "...", "quitar": [...], "degradados": [...] },
      "zonas": { ... }
    }
  }
}
```

### Tipos de elemento

| Tipo | Qué hace |
|---|---|
| `texto` | reemplaza el contenido; opcionalmente estira una `pastilla` detrás |
| `titulo` | autoajusta el cuerpo, parte en líneas balanceadas y **arrastra** hacia arriba los elementos que lo acompañan |
| `centrado` | centra dentro de una caja y achica si no cabe |
| `repetido` | serie de pastillas; centra las que se usan y **elimina las sobrantes** |

El contenido sale de `"campo": "nombre"` o de `"plantilla": "${precio:miles}"`.
Filtros disponibles: `miles`, `entero`, `mayus`, `minus`, `capital`.

**Los nombres de campo son libres.** `nombre`, `precio`, `sede`, `descuento`,
`sucursal` — el motor no conoce ninguno: los declara la plantilla y los llena el
proyecto.

### `zonas`

| Clave | Qué significa |
|---|---|
| `logo` | `[x0,y0,x1,y1]` — sin cabezas ni brazos |
| `pelo_min` | el pelo no puede subir de aquí |
| `titulo` | Y del título con nombre corto (se recalcula por pieza) |
| `silueta` | `[x0,x1]` — rango donde puede caer el centro de la cara |
| `aire` | `{"1": 70, "2": 50}` — píxeles entre mentón y título, según líneas del título |
| `ancla` | `1` foto pegada abajo, `0` pegada arriba |
| `bloque_titulo` | ids cuyo techo define dónde empieza el texto |

**Todos estos valores son de la marca, no del motor.** `aire` en dos líneas se
pide menor que en una a propósito: un título de dos líneas sube el bloque una
interlínea y deja una ventana vertical mucho más angosta. Exigirle el mismo aire
obliga a achicar tanto al sujeto que queda como una figura lejana — peor que el
problema que resuelve.

### Agregar un formato

Es agregar una entrada en `formatos` con su SVG y su binding. **El motor no
tiene noción de "post" ni de "story"**: son nombres del archivo de plantilla. Un
4:5, un 1.91:1 o un banner entran igual.

---

## 5. `proyecto.json` — los datos del lote

```jsonc
{
  "plantilla": "../../plantillas/<marca>",
  "fotos": "fotos",
  "salida": "../../salida/<proyecto>",
  "ruta":    "{grupo}/{subgrupo}/{modalidad}/{lugar}",
  "archivo": "{formato}-{marca}-{slug}",
  "piezas": [{
    "slug": "<identificador-unico>",
    "campos":   { "nombre": "...", "precio": 0, "lugar": "..." },
    "foto":     "<ruta relativa a fotos/>",
    "sujeto":   "mayor",
    "medidas":  { "ancho": 5391, "alto": 7787, "pelo": 0.055, "menton": 0.30, "cara_x": 0.42 },
    "encuadre": { "<formato>": { "expansiones": {"lados":1.9,"arriba":0.22,"abajo":0.18},
                                 "focal": [0.4724, 1, 0.7222, 1] } }
  }]
}
```

`ruta` y `archivo` son plantillas sobre los campos: la jerarquía de carpetas la
decide el proyecto, no el motor. **Un campo vacío no abre carpeta**, así que un
nivel que tiene un solo valor no produce `X/X`.

`medidas` y `encuadre` los escribe `encuadrar`, pero se pueden corregir a mano y
quedan ahí: son el **registro auditable** de por qué cada pieza quedó así.

`medidas` son fracciones de la foto **original**, no del lienzo, salvo `ancho` y
`alto`, que van en píxeles y sirven además de control: si el archivo cambia de
tamaño, el encuadre calculado sobre esas medidas ya no corresponde.

### Caché de fotos expandidas

Se guardan en `<fotos>/_expandidas/` con el nombre codificando los parámetros:
`<foto>-lat1.9-sup0.22-inf0.18.jpg`. Las siglas son explícitas y no la inicial
de cada clave, porque *arriba* y *abajo* empiezan igual y dos expansiones
distintas con el mismo valor terminaban compartiendo archivo. Se puede borrar la
carpeta entera cuando estorbe: se regenera sola.

---

## 6. Qué verifica el QA

Tres capas, de más a menos fiable. **Sólo las dos primeras declaran errores.**

| Capa | Mide | Puede fallar por |
|---|---|---|
| Texto sobre el SVG | anchos con la métrica real de la fuente | nada: es exacto |
| Aritmética del encuadre | recalcula dónde caen pelo, mentón y cara con los parámetros aplicados | medidas de rostro equivocadas |
| Re-detección sobre el PNG (`--qa-rostro`) | vuelve a buscar la cara en la pieza terminada | seguido: está recortada y bajo el degradado |

La tercera está **apagada por defecto y nunca declara error**, y eso se decidió
con datos: al correrla como error sobre una campaña completa marcó 21 piezas ya
aprobadas, con desvíos de hasta 250 px que no eran ruido de medición sino
detecciones directamente erróneas. Un QA que marca en rojo lo que el cliente ya
firmó deja de leerse a los tres días. Sirve, eso sí, para lo que la aritmética
no puede ver: que el sujeto detectado no sea el que se eligió.

> El umbral de contraste está calibrado sobre una campaña real de 166 piezas. Al
> montar una marca con una paleta muy distinta, conviene revisarlo contra las
> primeras piezas aprobadas en vez de darlo por bueno.

---

## 7. Lo que cuesta caro aprender

Esto ya está resuelto en el código. Está escrito para no volver a deducirlo.
Donde aparece un número concreto viene de una campaña real; **el número es de
esa marca, el criterio es de todas.**

**El encuadre se resuelve, no se tantea.** Se miden dos puntos del rostro y el
solver busca en ~150.000 combinaciones. Prefiere centrado y *después* escala:
maximizar escala a secas da caras que apenas entran por el borde de la silueta,
válidas para el solver y visiblemente mal.

**Cuando el solver dice SIN SOLUCIÓN, sospechar del paso antes que de la foto.**
Con rostros grandes la franja de valores válidos de `arriba` llega a ser más
angosta que el paso de 0,02 y la búsqueda pasa por encima sin verla. En una
campaña real tres piezas daban SIN SOLUCIÓN por esto y las tres se resolvieron a
0,005. Por eso `resolver()` **reintenta con `REJILLA_FINA`** antes de
declararlo: si la gruesa encuentra algo, el resultado es idéntico al de siempre.

**Nunca estimar las medidas a ojo sobre una miniatura.** Un error de 0,05 del
alto son ~50 px en el lienzo. Seis fotos de una misma escuela se midieron así y
las seis quedaron mal. Por eso `encuadrar --verificacion` existe: **el tope del
pelo es una estimación** —ninguna librería lo marca, el pelo no tiene geometría
estable— y esa imagen es la única forma barata de confirmarla.

**Hay un tamaño máximo de rostro, y depende de la plantilla.** Si el rostro
ocupa más que la ventana entre el bloque de logo y el título, no entra con
ninguna combinación de expansiones. En una plantilla cuadrada con logo arriba y
texto desde la mitad, ese límite cayó en **~0,30 del alto de la foto**. Es un
número de *esa* marca: se recalcula con `zonas` para cada plantilla nueva.
`filtrar` lo aplica antes de comprar la licencia.

**Con la foto anclada abajo, achicar al sujeto lo baja.** El único recurso que
lo sube sin agrandarlo es `expandir_abajo`.

**`expandir_lados` no es cosmético: es lo único que da recorrido horizontal.**
Sin ancho sobrante el encuadre no puede llevar la cabeza hasta la silueta y el
clamp la deja a medio camino contra el borde. Un sujeto muy descentrado llegó a
necesitar 1,80 — 1800 px por lado.

**Las tres expansiones se aplican siempre en el orden `lados → arriba →
abajo`**, y cada fracción se lee sobre el tamaño en ese punto de la cadena. El
solver replica esa aritmética incluidos los `int()`; si divergen, aprueba
encuadres que el render no reproduce.

**Elegir el sujeto cuando hay más de una persona.** Encuadrar el punto medio
deja a una centrada y a la otra partida contra el borde. `"sujeto"` acepta
`mayor` (por defecto), `izquierda` o `derecha`. El detector automático toma
siempre la cara más grande, así que cuando la composición pide otra, hay que
declararlo en la pieza.

**Y hay fotos donde ningún detector sirve.** Sobre una tanda de 18 fotografías
de escenas con varias personas, Haar falló en ocho: eligió al acompañante en
primer plano en vez del protagonista —en una escena de terapia, a la persona de
la derecha; en una farmacia, a la clienta; en una sala de párvulos, a un niño— y
en una no encontró ninguna cara. Cuando la protagonista no es la más grande,
medir a ojo sobre una grilla en centésimas sale más barato que pelear con
`"sujeto"`.

**Comparar dos fotos por huella: el umbral es 1,0, no 300.** Con huellas de
32×32 normalizadas (media 0, desviación 1), dos imágenes **sin relación** dan
una distancia cuadrática media de ≈ **2,0** — el máximo útil de la métrica es
~4 —. Dos copias de la misma foto dan 0,0–0,3. Un 1,5 **no** es la misma foto.
Leerlo al revés llevó a afirmar que dos fotografías distintas eran la misma.

**Inkscape devuelve 0 aunque no escriba el PNG.** La única verificación válida
es que el archivo exista. Nunca el exit code.

**El `font-size` de la clase CSS gana al atributo.** El único override que
funciona es `style="font-size:..."` inline.

---

## 8. Expansión de lienzo: estirado, reflejo o generativa

Cuando la foto no alcanza a cubrir el formato, el solver pide agrandar el lienzo
(`lados → arriba → abajo`). Desde **v1.3.0** hay tres maneras de rellenarlo, y
las tres usan la misma aritmética de tamaños, así que el encuadre no cambia:

| Método | Cómo se elige | Qué hace |
|---|---|---|
| **estirado** (por omisión) | `"expansion": "estirado"` en `proyecto.json` | Estira el borde y lo difumina. Parejo y rápido. La costura no pasa del 3 % del lado: en fotos chicas ya no cae sobre la cara. |
| **reflejo** | `"expansion": "reflejo"` (o `MG_EXPANSION=reflejo`) | Refleja el 22 % exterior del borde con una rampa de suavizado (método de Meta V.2). Más textura; en planos abiertos puede duplicar elementos. |
| **generativa** (Adobe Firefly) | pieza con `"expandidas"` | Se usa una foto ya expandida por fuera del motor. |

**Fotos pre-expandidas.** Una pieza puede traer, por formato:

```json
"expandidas": {"post": {"archivo": "_firefly/enfermeria-post.jpg",
                        "expansiones": {"lados": 1.9, "arriba": 0.22, "abajo": 0.18}}}
```

El motor la usa **solo si esas expansiones son exactamente las del encuadre
vigente**: la foto trae las proporciones que el solver supuso y el mismo
`focal` sigue valiendo (como `generar_v3.py` en Meta). Si el encuadre cambió, se
ignora y se vuelve al relleno propio.

Lo que hay que saber al generar con Firefly (`image_generative_expand`):

- **La proporción es lo único que viaja.** Se expande una copia reducida; lo
  mejor es ampliar el resultado y pegar encima la foto original en alta.
- **Hay un tope de 4096 px por lado.** Si el solver pide más, se reduce la copia
  de trabajo hasta que los cuatro lados entren.
- **`MAX_PIXELES` deja de tener sentido** con expansión generativa (el tope
  existe porque el relleno local construye la imagen en memoria).
- **En formatos verticales el recorte lateral sólo debería comerse margen
  generado.** Pendiente en el solver (ver `actualizaciones del motor/v1.3.0`).
- **Expansión de lienzo no es relleno generativo.** Agregar o borrar objetos es
  otra capacidad.

---

## 9. Windows: dos trampas de codificación

Valen para cualquier repositorio en una ruta con acentos o espacios.

**`cv2.imread` devuelve `None` con rutas no ASCII.** Hay que leer los bytes con
Python y decodificar con `cv2.imdecode`. No lanza error: devuelve `None` y el
script sigue como si la foto no existiera.

**`Set-Content -Encoding UTF8` de PowerShell rompe los acentos** (`Diseño` →
`DiseÃ±o`). Para escribir cualquier archivo que contenga una ruta con acentos,
`io.open(..., encoding='utf-8')` desde Python.

Y una tercera, de siempre: **entrecomillar los argumentos**. Una ruta con
espacios sin comillas hace que Inkscape los tome como archivos de entrada
distintos, aborte y **devuelva 0 igual**.

---

## 10. Qué NO incluye

- **Interfaz web, cola de render, aprobación del cliente y salida a la
  plataforma de anuncios.** Eso es construir un producto, no una herramienta
  local.
- **Plantillas nuevas.** El motor automatiza *una* plantilla; dibujarla sigue
  siendo trabajo de diseño. Agregar un formato necesita su SVG.
- **Expansión generativa.** Ver la sección 8.
- **Licencias de las fotografías.** Las imágenes de `proyectos/*/fotos` vienen
  con la licencia con que se compraron. Revisar los términos antes de reusarlas
  para otro cliente o para pauta pagada.

---

## 11. Estructura

```
Motor-Graficas/
  graficas.py              CLI
  motor/
    entorno.py             descubre fuentes y rasterizador
    svgdoc.py              manipulación de SVG por id
    texto.py               métricas de fuente y autoajuste
    plantilla.py           esquema declarativo y dibujo de elementos
    foto.py                expansiones, encuadre cover, degradados
    rostro.py              medición automática (mediapipe / YuNet / Haar)
    zonas.py               derivación de zonas seguras
    montaje.py             monta una marca desde arte + Excel, sin nombrar capas
    solver.py              solver de encuadre
    render.py              SVG → PNG
    qa.py                  verificación de la pieza final
    lote.py                proyectos y generación por lote
  herramientas/
    preparar_plantilla.py  estampa ids sobre una plantilla de Illustrator
    migrar_ipg.py          migrador de un cliente concreto — ejemplo, no parte del motor
  plantillas/<marca>/      los SVG, plantilla.json, receta.json
  proyectos/<proyecto>/    proyecto.json, LEEME.md, fotos/
  fuentes/                 .otf que viajan con el motor
  modelos/                 modelos opcionales de detección
  salida/                  entregables
  actualizaciones del motor/  registro de cada versión: antes, después y diff
```

**Nada de `motor/` conoce una marca.** Donde aparece el nombre de un cliente en
un comentario es como *evidencia* de una decisión de calibración —"este umbral
se fijó contra estas 166 piezas"—, nunca como condición. Si al montar una marca
nueva hace falta editar algo de `motor/`, eso es una señal de que falta un campo
en `plantilla.json`.

Cada proyecto lleva su propio `LEEME.md` con los supuestos de esa campaña. Eso
**no va en este README**.

---

## 12. Caso de validación

El motor se validó reproduciendo una campaña completa ya entregada y aprobada:
**43 carreras → 83 piezas → 166 gráficas**, en `proyectos/ipg-2027/`.

Con los mismos datos y encuadres se regeneraron las 166 y se compararon una a
una contra las originales:

- **90 de 166 son bit-idénticas.**
- En el resto, la diferencia máxima de canal es **16 sobre 255** —
  imperceptible, y propia del antialiasing al reescribir el nodo de texto. Un
  corrimiento real de 1 px daría diferencias de 200+.
- El peor caso son 367 píxeles sobre 2.073.600 (0,018 %), y es un título a dos
  líneas con tres badges: el camino más difícil del motor.
- Las 166 pasan el QA con **0 errores y 0 avisos**.

```bash
python graficas.py generar proyectos/ipg-2027/proyecto.json --qa
python graficas.py qa      proyectos/ipg-2027/proyecto.json --informe qa.txt
```

Qué cambió respecto de aquel pipeline original, que estaba escrito a la medida
de esa marca:

| | Antes | Ahora |
|---|---|---|
| Binding de la marca | ~110 constantes dentro del `.py` | un `plantilla.json`, y la mayoría se lee del propio SVG |
| Localización de elementos | clase CSS de Illustrator (`cls-14`) | `id` estable |
| Vocabulario de datos | campos fijos en el código | campos libres, declarados por plantilla |
| Medición del rostro | a ojo sobre una grilla, 3 valores por foto | automática, con imagen de verificación |
| Zonas seguras | medidas a mano sobre el arte | derivadas de la plantilla |
| Posición del título | render a PNG + escaneo de píxeles | calculada desde la métrica de la fuente |
| Verificación | revisión visual pieza por pieza | QA automático con informe |
| Fotos candidatas | se licenciaban y después se veía si servían | se filtran antes de comprar |
| Rutas de fuentes / rasterizador | fijas en el código | descubiertas en el orden habitual |
| Variantes A/B | no existía | `variantes` |

> **Ese proyecto reproduce una versión congelada de la campaña**, que después
> siguió evolucionando por su cuenta. El detalle está en
> [`proyectos/ipg-2027/LEEME.md`](proyectos/ipg-2027/LEEME.md). Sirve como
> referencia de implementación y como prueba de regresión, no como entrega
> vigente.
