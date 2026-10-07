# Meta IPG-2027 — cómo replicar la campaña completa

Generador de las gráficas de Meta para la Admisión IPG 2027: **43 carreras ·
83 piezas · 166 gráficas** por versión, en Post 1080×1080 y Story 1080×1920.

Este archivo es el punto de entrada. Si vas a retomar el proyecto en otra
máquina o con otra persona, empieza acá.

| Documento | Para qué |
|---|---|
| **este archivo** | puesta en marcha, versiones, pipeline completo |
| [`00-Scripts/LEEME.md`](00-Scripts/LEEME.md) | qué hace cada uno de los scripts |
| [`00-Scripts/CONTEXTO-graficas-admision-2027.md`](00-Scripts/CONTEXTO-graficas-admision-2027.md) | por qué las plantillas se comportan como se comportan |
| [`Gráficas Meta 2027/LEEME.md`](Gráficas%20Meta%202027/LEEME.md) | qué hay en cada carpeta de entrega |
| [`03-Fotografias/CALCE-Fotos-V3.md`](03-Fotografias/CALCE-Fotos-V3.md) | qué foto quedó en qué carrera |
| [`02-Datos/perfiles-fotograficos.json`](02-Datos/perfiles-fotograficos.json) | el perfil fotográfico de cada carrera |
| [`Motor/README.md`](Motor/README.md) | el motor genérico (v1.3.0), reutilizable con otras marcas |
| [`Motor/actualizaciones del motor/`](Motor/actualizaciones%20del%20motor/LEEME.md) | qué cambió en cada versión del motor genérico |

> **Ámbito.** Este proyecto es **la campaña IPG 2027**. El motor genérico —la
> versión reutilizable con otras marcas— vive en la carpeta [`Motor/`](Motor/README.md),
> con documentación propia y su registro de versiones. Los dos se mantienen
> alineados pero no se mezclan: los scripts de esta campaña no importan `Motor/`.

---

## 1. Puesta en marcha en una máquina nueva

```bash
pip install -r requirements.txt
```

El código está en GitHub, en `Lab-Design-Code/Motor-Grafico-V.0`, sin fotografías
ni gráficas (ver `.gitignore`). Los scripts calculan la raíz del repositorio a
partir de su propia ubicación, así que se puede clonar en cualquier carpeta.

Además hace falta:

| Requisito | Dónde | Cómo se comprueba |
|---|---|---|
| **Montserrat** Black, ExtraBold y Medium | instalada en el sistema, en `fuentes/` o en la variable `IPG_FUENTES` | `python 00-Scripts/medir_titulo.py 02-Datos/escuela-salud.json` no debe fallar |
| **Inkscape** | en el `PATH`, en `C:\Program Files\Inkscape\bin\inkscape.exe` o en la variable `INKSCAPE` | genera un PNG de prueba |
| **Conector de Adobe (Firefly)** | sesión de Claude con el conector activo | sólo para expandir fotos |
| **Chrome con sesión de Shutterstock** | sólo para buscar fotos nuevas | |

Los dos últimos no hacen falta para **regenerar** lo que ya existe: las fotos
expandidas están en `03-Fotografias/_generadas/` y el pipeline las reutiliza.

### Comprobación rápida de que todo está en su lugar

```bash
python 00-Scripts/verificar_encuadres.py 02-Datos/escuela-salud.json
```

Debe imprimir una línea por pieza con `ok`. Si dice `CHOCA` o `justo`, algo se
movió.

---

## 2. Las cuatro versiones

Cada una vive en su carpeta y **ninguna pisa a la anterior**. La razón es que
cada versión fue aprobada en su momento y hay que poder volver.

| Carpeta | Qué es | Gráficas |
|---|---|---|
| `Gráficas Meta 2027/` (raíz) | **V.1** — plantilla original, expansión por reflejo | 166 |
| `Gráficas Meta 2027/V.2/` | **V.2** — plantilla nueva de Illustrator, con pastilla de modalidad | 166 |
| `Gráficas Meta 2027/V.2-0/` | **V.2-0** — mismas piezas, fotos expandidas con Firefly en vez de reflejo | 166 |
| `Gráficas Meta 2027/V.3/` | **V.3** — selección fotográfica por perfil | 166 + `Modificadas/` |
| `Gráficas Meta 2027/V.3/Modificadas/` | sólo lo que cambió en la última tanda, para revisar rápido | 100 |

### Qué cambió en cada salto

**V.1 → V.2.** Plantilla nueva. Illustrator dejó de emitir `<tspan>` por
fragmento de kerning y pasó a emitir **un `<text>` por fragmento**, así que el
reemplazo de texto se reescribió por *runs*: se agrupan los fragmentos que
comparten baseline, se deja el texto completo en el primero y se borran los
demás. Además apareció la pastilla de modalidad («Estudia | Sede X»), que
**bajó el techo del título**: de 465 a 433 px en el Post y de 763 a 700 en el
Story. Todos los encuadres de V.1 quedaron justos y hubo que rehacerlos.

**V.2 → V.2-0.** La expansión de lienzo dejó de hacerse por reflejo y pasó a
**Firefly** (`image_generative_expand`). El reflejo duplicaba elementos en
planos abiertos —en Rehabilitación aparecían dos sujetos— y dejaba una franja
que se leía como difuminado.

**V.2-0 → V.3.** Selección fotográfica guiada por el Excel de perfiles de
Marketing, con una regla de cascos propia. 18 carreras con foto nueva en la
primera tanda y 6 más después.

---

## 3. El pipeline, de punta a punta

Es el mismo desde V.2-0. Nueve pasos.

```
foto → medir → resolver → píxeles → Firefly → bajar → aplicar → generar → revisar
```

### 3.1 Instalar la foto

```bash
python 00-Scripts/una_instalar.py <n> <Carpeta-Carrera> "<Escuela>"
```

Copia la foto a `03-Fotografias/<Escuela>/<Carrera>/<Carrera>.jpg`, respalda la
anterior en `_V2-0-sin-retoque/` y deja una grilla en centésimas para medirla.

### 3.2 Medir el rostro — **a ojo, sobre la grilla**

Tres números, en fracciones de la foto original: **pelo** (tope de la cabeza),
**mentón** y **cara_x** (centro horizontal).

No se usa el detector automático. Se probó sobre las 18 fotos de V.3 y falló en
ocho: Haar elige la cara más grande, que en estas fotos suele ser el
acompañante en primer plano —en Rehabilitación eligió a la persona de la
derecha, en Farmacias a la clienta, en Parvularia a un niño—, y en
Instrumentación no encontró ninguna.

Cuando hay varias personas se elige **una**, nunca el punto medio: encuadrar el
promedio deja a una centrada y a la otra partida contra el borde.

### 3.3 Resolver el encuadre

```bash
python 00-Scripts/una_resolver.py <Carrera> "<Escuela>" <pelo> <menton> <cara_x>
```

Devuelve, por formato, las tres expansiones y el punto focal, más las
cantidades ya convertidas a **píxeles** para Firefly.

### 3.4 Expandir con Firefly

Tres llamadas al conector de Adobe, por archivo:

1. `asset_initialize_file_upload` — path, tamaño en bytes y `image/jpeg`
2. `curl -X PUT` al *transfer href*, con `--retry 2`
3. `asset_finalize_file_upload` — se le devuelve el *transfer document* completo

y después `image_generative_expand` con `expandPixels: {left, right, top, bottom}`.

Post y Story parten de la misma foto: **se sube una vez y se expande dos**.

### 3.5 Bajar, aplicar y generar

```bash
python 00-Scripts/una_cerrar.py <escuela.json> <Carrera> <uid-post> <w> <h> <uid-story> <w> <h>
python 00-Scripts/generar_v3.py <escuela.json> <Carrera>
python 00-Scripts/copiar_una.py <escuela.json> <Carrera>
```

`una_cerrar` baja las dos expansiones a `03-Fotografias/_generadas/`,
**verifica que el tamaño coincida** con lo que declaró Firefly y escribe el
encuadre en el JSON de escuela. `generar_v3` produce las piezas en `V.3`, y
`copiar_una` las suma a `V.3/Modificadas`.

> Cuando la foto ya está en `_generadas/`, el generador **elimina las claves
> `expandir_*`** y entra con expansión 0: el lienzo ya viene resuelto y el
> `focal` del solver sigue siendo válido porque las proporciones de la
> expansión son exactamente las que se le pidieron a Firefly.

### 3.6 Para una escuela completa

Los mismos pasos en lote: `grillar.py`, `resolver_v3.py`, `preparar_v3.py`,
`bajar_v3.py`, `aplicar_v3.py`, `generar_v3.py`, `modificadas.py`.

---

## 4. Las reglas del encuadre

Están en `00-Scripts/solver_encuadre.py` y son la razón de que el encuadre se
resuelva en vez de tantearse.

| | Post 1080×1080 | Story 1080×1920 |
|---|---|---|
| Logo + sello CNA, sin cabezas ni brazos | x 20–700, y 20–185 | x 40–720, y 70–240 |
| Banda de rostros | y 200–430 | y 270–700 |
| Zona de texto, sólo cuerpo o fondo | y ≥ 432 | y ≥ 699 |
| **Silueta: el sujeto va aquí dentro** | **x 600–960** | **x 445–1015** |
| Tope del pelo | ≥ 205 | ≥ 300 |
| Techo del título (una línea) | 433 | 700 |
| Techo del título (dos líneas) | ~359 | ~615 |
| Aire mínimo mentón → título | 70 px (50 a dos líneas) | 90 px (70 a dos líneas) |

La silueta está corrida a la derecha **a propósito**: deja libre el margen
izquierdo para el logo arriba y el título abajo. Es la restricción que más se
olvida y la que más se nota cuando falta.

**La regla del 0,30.** Si el rostro ocupa más del 30 % del alto de la
fotografía, no hay encuadre posible en el Post con ninguna combinación de
expansiones. Se comprueba **antes de licenciar**, con
`00-Scripts/prevalidar_fotos.py` sobre la miniatura pública.

---

## 5. Lo que cuesta caro aprender

Todo esto ya está resuelto en el código. Está escrito para no volver a
deducirlo.

### Del solver y la expansión

**Las tres expansiones van siempre en el orden `lados → arriba → abajo`,** y
cada fracción se lee sobre el tamaño **en ese punto de la cadena**, no sobre el
original. El `int()` de cada paso es parte del contrato: `capa_fotos_ipg.py`
trunca y el solver replica esa aritmética. Si divergen, el solver aprueba
encuadres que el render no reproduce.

**Con la foto anclada abajo, achicar al sujeto lo baja.** El único recurso que
lo sube sin agrandarlo es `expandir_abajo`.

**`expandir_lados` no es cosmético: es lo único que da recorrido horizontal.**
Sin ancho sobrante el cover no puede llevar la cabeza hasta la silueta y el
clamp la deja a medio camino contra el borde. Gestión de Seguridad necesitó
1,80 —1800 px por lado— porque el operador estaba en 0,24.

**El paso de 0,02 del solver es demasiado grueso para rostros grandes.** La
franja de valores válidos de `arriba` llega a ser más angosta que el paso y la
búsqueda pasa por encima sin verla. Les pasó a Minas, Operaciones de Planta
Minera e Informática y Ciberseguridad: las tres daban SIN SOLUCIÓN y las tres
se resolvieron repitiendo el barrido a 0,005. No era la fotografía.

**El barrido fino hay que vectorizarlo.** Tres bucles anidados en Python puro
son ~10 millones de combinaciones por carrera y no termina. `resolver_v3.py`
barre `lados` y `arriba` en Python y **`abajo` entero con numpy**.

**El tope de 180 megapíxeles ya no aplica.** Existía por el método de reflejo,
que construía la imagen completa en memoria y Pillow la rechazaba como
decompression bomb. Firefly genera sobre una copia reducida y lo único que
viaja es la *proporción*. Está en 1.000 MP. Podología daba SIN SOLUCIÓN en el
Post sólo por ese tope.

**En el Story el recorte lateral sólo puede comerse margen generado.** El
criterio correcto no es limitar el recorte a un número fijo de píxeles, sino
exigir que la ventana visible no invada la fotografía original, con 8 px de
holgura. La primera versión de ese criterio dejaba dos carreras sin solución.

### De Firefly

**Máximo 4096 px de expansión por lado.** Cuando el solver pide más, se reduce
la copia de trabajo hasta que los cuatro lados entren. Lo que viaja es la
proporción; la resolución final sigue siendo de sobra para 1080 px.

**No hay relleno generativo, sólo expansión de lienzo.** Agregar un objeto que
no existe —un casco sobre alguien que no lo lleva— o borrar uno —un delantal—
es composición y borrado de objetos, y eso no está disponible. Recolorear algo
que ya existe sí se puede. Gestión Logística se resolvió con foto nueva por
esto.

### De la medición y la comparación de imágenes

**Nunca estimar las medidas sobre una miniatura.** Un error de 0,05 del alto
son ~50 px en el lienzo, suficiente para que el mentón termine bajo el título
aunque el solver diga que cumple. Las seis fotos de Salud se midieron así y las
seis quedaron mal: Enfermería tenía anotado mentón 0,13 cuando el real es 0,30.

**El prevalidador es un prefiltro, no una medición.** Sirve para no gastar una
licencia en algo imposible. Si dice que sirve, hay que medir igual sobre el
archivo comprado.

**Comparar fotos por huella: el umbral es 1,0, no 300.** Con huellas de 32×32
normalizadas (media 0, desviación 1), dos imágenes **sin relación** dan una
distancia cuadrática media de ≈ **2,0** —el máximo útil de esa métrica es ~4—.
Dos copias de la misma foto dan 0,0–0,3. Un 1,5 **no** es la misma foto. Este
error llevó a afirmar que dos fotos distintas de Transporte Marítimo eran la
misma.

### Del recoloreo de EPP

Está en `00-Scripts/recolorear_casco.py`, y tres cosas salieron mal antes de
salir bien:

1. **Máscara al tamaño de trabajo.** Pedirla sobre una copia de 1600 px y
   ampliarla a 5472 es un factor de 3,4× y deja el borde blando. Se pide sobre
   la copia de 3600 px que ya se usa para Firefly.
2. **No dilatar.** Dilatar 18 px para tapar un canto de color derrama el blanco
   sobre la piel: eso era el velo gris sobre la frente.
3. **Ganancia multiplicativa, no estiramiento de rango.** Estirar la luminancia
   a [152, 248] lleva también la sombra bajo el ala a gris claro y el casco se
   lee como una visera translúcida. Un casco blanco no aclara las sombras:
   refleja más luz. La ganancia es la razón de reflectancias —0,85/0,68 ≈ 1,25
   para el amarillo, 0,85/0,36 ≈ 2,35 para el naranjo— con una rodilla en 200
   para no quemar los altos.

Y una vía que **no** funciona: separar el plástico del casco de la piel por
umbral de saturación. El plástico mide 0,72 de media y la piel 0,46, pero son
medias y las distribuciones se solapan; con 0,60 la cara sale blanqueada a
manchones.

### De Windows y las rutas

**`cv2.imread` no abre rutas con caracteres no ASCII.** La ruta del repositorio
lleva «Diseño», así que devuelve `None` en todos los archivos. Hay que leer los
bytes con Python y decodificar con `cv2.imdecode`.

**`Set-Content -Encoding UTF8` de PowerShell rompe la ñ** (`Diseño` →
`DiseÃ±o`). Para escribir cualquier archivo que contenga la ruta del repo, usar
`io.open(..., encoding='utf-8')` desde Python.

**Inkscape devuelve 0 aunque no escriba el PNG.** La única verificación válida
es que el archivo exista y tenga fecha nueva. Nunca el exit code. Y hay que
entrecomillar siempre los argumentos: la ruta tiene espacios y sin comillas
Inkscape los toma como archivos de entrada distintos.

**El `font-size` de la clase CSS gana al atributo.** El único override que
funciona es `style="font-size:..."` inline.

### De Shutterstock

**El filtro del plan es `enableUnlimitedFilter=true`** en la URL. Sin él
aparecen fotos fuera de la suscripción.

**La grilla de resultados es `[data-automation="AssetGrids_MosaicAssetGrid_div"]`.**
Cualquier otro selector agarra los carruseles promocionales, que traen
fotografías de comida griega y playas.

**20 resultados por página**, con `&page=N`.

**El slug de la miniatura es indiferente:** `image.shutterstock.com` la sirve
por el id, así que basta guardar el número.

**La licencia editorial no la detecta ningún filtro.** La `2663900595` decía
«uso editorial únicamente» y habría sido inservible para pauta. Antes de
descargar hay que abrir la ficha y confirmar que diga «Usa tu plan: Descargas
ilimitadas», sin aviso amarillo.

---

## 6. Estructura del proyecto

```
Meta IPG-2027/
  00-Scripts/          el pipeline · ver 00-Scripts/LEEME.md
  01-Plantillas/       Post y Story .svg  ·  _V1/ con las versiones anteriores
  02-Datos/            escuela-*.json (fuente de verdad) · medidas · perfiles
  03-Fotografias/      <Escuela>/<Carrera>/<Carrera>.jpg
    _generadas/        fotos ya expandidas con Firefly — es lo que consume el generador
    _expandidas/       caché del método por reflejo (V.1/V.2)
    _V1-*/             respaldos por escuela
    _V2-0-sin-retoque/ fotos anteriores a V.3
  06-Documentacion/    el manual .docx
  Gráficas Meta 2027/  entregables · una carpeta por versión
  Zonas seguras/       mapas de zonas
  Motor/               motor genérico v1.3.0 (otras marcas) · ver Motor/README.md
```

**`02-Datos/escuela-*.json` es la única fuente de verdad de cada lote:** texto,
beca, cuota, sede, foto y parámetros de encuadre. Cambiar un dato ahí y volver
a correr el generador reescribe la pieza.

---

## 7. Qué sigue abierto

1. **Cuatro carreras por rehacer en V.3.** Instrumentación Industrial y
   Educación Básica y Parvularia por error de medición; Educación Parvularia y
   Comercio Exterior porque el problema está en la fotografía —en una la
   educadora va de espaldas, en la otra el rostro ocupa 0,10 del alto—.
2. **Auditoría de licencias** de las fotos ya compradas.
3. **Visto bueno de Marketing** sobre los nombres y prefijos reescritos, y
   sobre el texto de la pastilla de modalidad.
4. **Nombres largos.** El título se topa con `nombre_maxw` (1011 px en Post,
   968 en Story) y el motor lo achica. Mantenimiento Industrial e
   Instrumentación Industrial quedan con 13 px de margen derecho contra 55,9
   del izquierdo. Acortarlos subiría el techo del mentón de 359 a 433.
5. **Módulo 1** —armar el JSON de escuela directamente desde el Excel— nunca se
   construyó. Los cuatro se arman a mano.
