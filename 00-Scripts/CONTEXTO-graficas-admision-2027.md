# Contexto de traspaso — Gráficas Admisión IPG 2027

Documento de handoff para retomar el trabajo en Claude Code, donde sí hay acceso al
sistema de archivos local y a la carpeta de fotografías.

> **Documento histórico — describe la plantilla V.1.**
>
> Este archivo se escribió el 11-09-2026, antes de que existiera el pipeline, y
> se actualizó por última vez el 21-09-2026.
>
> **Las secciones 3 a 7 describen la plantilla V.1, que ya no es la vigente.**
> Se conservan porque siguen siendo la mejor explicación de *por qué* las
> plantillas se comportan como se comportan, y porque la V.1 está entregada y
> hay que poder volver a ella. Pero el mapa de clases de la sección 4 y la
> geometría de la sección 5 **no corresponden a la plantilla actual**: la V.2
> renumeró las clases y movió los elementos. Ver la sección 11.
>
> La referencia vigente para operar es, en este orden:
> 1. `../LEEME.md` — puesta en marcha, versiones y pipeline completo.
> 2. `../00-Scripts/LEEME.md` — qué hace cada script.
> 3. `../Gráficas Meta 2027/LEEME.md` — qué hay en cada carpeta de entrega.
>
> El `.docx` de `../06-Documentacion/` también quedó congelado en V.1.
>
> **Ámbito:** este documento cubre solo la campaña IPG 2027. El motor genérico
> —la versión reutilizable con otras marcas— es un proyecto aparte, en
> `../../../Personal/Motor-Graficas/`, y tiene documentación propia. No se
> mezclan.

---

## 1. Objetivo

Replicar las plantillas `Post-IPG_2027-Plantilla.svg` (1080×1080) y
`Story-IPG_2027-Plantilla.svg` (1080×1920) por cada carrera del
`Documento Admisión 2027`, reemplazando nombre de carrera, tipo(s) de título,
porcentaje de beca, cuota mensual y sede, más una fotografía de fondo acorde a la
temática de cada carrera.

---

## 2. Archivos de origen

| Archivo | Rol |
|---|---|
| `Post-IPG_2027-Plantilla.svg` | Plantilla cuadrada, sin fotos |
| `Story-IPG_2027-Plantilla.svg` | Plantilla vertical, sin fotos |
| `Post-IPG_2027.png` | Arte final con fotos (referencia de composición) |
| `Story-IPG_2027.png` | Arte final sin fotos |
| `Documento_Admisio_n_2027__1_.xlsx` | Datos: carreras, sedes, aranceles, descuentos, cuotas |

Fotografías: `C:\Users\IPG\Desktop\MALLAS IPG 2027\Fotografias Mallas IPG`
(carpeta definida por Luis; en esta sesión no fue accesible).

---

## 3. Hallazgos técnicos sobre las plantillas

Esto es lo que costó descubrir y conviene no volver a deducir.

### 3.1 El texto es editable
Las plantillas son export de Illustrator con `<text>` vivo, no vectorizado. Cada
palabra viene partida en `<tspan>` con `x` manual por kerning. Al reemplazar,
conviene rescribir el `<text>` completo con un solo `<tspan x="0" y="0">`; se pierde
el kerning fino de Illustrator pero el resultado es idéntico a ojo.

### 3.2 El `font-size` de la clase CSS gana al atributo
Las plantillas definen el cuerpo en `<style>` (`.cls-14 { font-size: 68.06px }`).
Un atributo `font-size="60px"` en el `<text>` **es ignorado**. Hay que usar
`style="font-size:60px"` inline. Este fue el bug que hacía desbordar los títulos
largos del Story.

### 3.3 Hay una plancha gris tapando las fotos
Ambas plantillas traen un rectángulo opaco `#606060` dibujado **encima** de la capa
de fotografía. Por eso se ven grises. Para que aparezca la foto hay que eliminarlo:

- Post: `<rect class="cls-21" x="-13.01" y="-14.81" width="1107.78" height="1106.59"/>`
- Story: `<rect class="cls-23" x="-39.25" y="-21.64" width="1165.15" height="1972.04"/>`

### 3.4 La capa de fotos del Post funciona; la del Story no
El Post tiene un grupo `<g class="cls-51">` con tres paneles verticales recortados:

| Panel | clipPath | x | ancho |
|---|---|---|---|
| Izquierdo | `clippath-3` | −3.19 | 360.15 |
| Central | `clippath-1` | 366.92 | 352.13 |
| Derecho | `clippath-2` | 728.60 | 355.59 |

Las imágenes apuntan a archivos externos que **no vinieron** en la entrega:
`shutterstock_2492758865.jpg`, `shutterstock_2508732693.jpg`, `shutterstock_2727587367.jpg`.

Sobre las fotos va el degradado inferior `Degradado_sin_nombre_15-2`
(transparente en y=404.88 → negro en y=1333.41), que es lo que mantiene legible todo
el bloque de texto. Ese degradado se reaplica tal cual.

En el Story, en cambio, el grupo `<g class="cls-47">` quedó **fuera del lienzo**
(x ≈ −1284), es decir inservible. Se reconstruyó una capa equivalente con un
degradado propio `GradFotoStory`: transparente en y=694 → negro en y=1800. Calibrado
para que la atenuación sobre los badges sea equivalente a la del Post (≈0.25).

### 3.5 Tipografía
Montserrat en tres pesos: Medium (500), Black (800) y ExtraBold (700, solo para la
bajada del logo). Sin la fuente instalada, cualquier render sale mal.

---

## 4. Mapa de clases CSS → elemento

| Elemento | Post | Story |
|---|---|---|
| Prefijo ("Ingeniería en") | `cls-10`, 53px | `cls-1`, 61.28px |
| Nombre de carrera | `cls-14`, 68.06px | `cls-3`, 78.7px |
| Badges de título | `cls-13`, 21.64px | `cls-6`, 25.03px |
| "BECA" | `cls-12`, 38.88px | `cls-5`, 43.09px |
| "DE HASTA xx%" | `cls-4`, 50.13px | `cls-8`, 55.55px |
| "Cuotas desde" | `cls-6`, 44.72px | `cls-2`, 49.56px |
| Monto | `cls-5`, 62.24px | `cls-7`, 68.97px |
| "¡En el arancel…!" | `cls-3`, 36.62px | `cls-9`, 51.71px |
| Sede | `cls-1`, 32.32px | `cls-10`, 41.76px |

---

## 5. Geometría (coordenadas del viewBox)

### Post 1080×1080
- Prefijo: `translate(34.22 506.81)`
- Subrayado: `rect.cls-11 x=-104.17 y=511.05 w=541.71 h=2.17` — el ancho se recalcula
- Nombre: `translate(34.22 585.03)`
- Badges: rects en x 34.22 / 283.25 / 532.28, y 608.09, w 238.92, h 43.44
  (textos en x 50.01 / 300.86 / 569.33, baselines 636.31 / 636.31 / 637.18)
- BECA `translate(136.65 750.01)` · DE HASTA `translate(114.22 801.4)`
- Cuotas desde `translate(656.85 753.09)` · Monto `translate(673.41 819.12)`,
  pastilla blanca x 634.27 → 991.74 (el monto se centra ahí)
- Sede: texto `translate(106.0127 1048.5224)`, pastilla `rect.cls-11 x=57.15 y=1014.89 w=264.34`

### Story 1080×1920
- Prefijo: `translate(55.86 811.86)`
- Subrayado: `rect.cls-4 x=-104.17 y=816.76 w=626.42 h=2.5`
- Nombre: `translate(55.86 902.32)`
- Badges: rects en x 55.86 / 343.84 / 631.81, y 928.98, w 276.28, h 50.23
  (textos en x 74.12 / 364.19 / 674.65, baselines 961.61 / 961.61 / 962.62)
- BECA `translate(119.0249 1128.2842)` · DE HASTA `translate(94.1635 1185.2314)`
- Cuotas desde `translate(643.5112 1131.6973)` · Monto `translate(661.8549 1204.8701)`,
  pastilla x 618.48 → 1014.59
- Sede: texto `translate(138.7395 1608.3502)`, pastilla `rect.cls-4 x=75.61 y=1564.9 w=341.5`

---

## 6. Zonas seguras para la fotografía

Medidas sobre la gráfica real, no estimadas.

| | Post 1080×1080 | Story 1080×1920 |
|---|---|---|
| Logo IPG + sello CNA — sin cabezas ni brazos | x 20–700, y 20–185 | x 40–720, y 70–240 |
| Banda recomendada para rostros | y 200–430 | y 270–700 |
| Zona de texto — solo cuerpo o fondo | y ≥ 440 | y ≥ 740 |

Criterios de selección de la foto: horizontal para Post (mínimo 2160 px de ancho),
vertical o cuadrada grande para Story; sujeto desplazado al centro-derecha con el
tercio superior izquierdo despejado; sin brazos levantados del lado izquierdo;
fondo con profundidad y poco contraste duro.

Holgura mínima contra el texto: al menos 30 px entre el mentón y el tope de las
letras del prefijo, que en el Post está en y 463.

### 6.1 Caso calibrado: Enfermería — Sede La Unión (Post)

Medido sobre el render del 14-09-2026, sirve de referencia para calibrar carreras
nuevas.

| | Antes | Después |
|---|---|---|
| `expandir_lados_post` / `expandir_abajo_post` | 0.74 / — | 0.79 / 0.045 |
| Foto expandida | 9379 × 9500 px | 9649 × 9927 px |
| Tope del pelo | y 219 | y 200 |
| Mentón | y 462 | y 432 |
| Tope de la "T" del título | y 463 | y 463 |
| Aire mentón → letras | 1 px | 31 px |

Sensibilidad: cada `0.01` de `expandir_abajo_post` sube al sujeto ~7 px. Pasado
`0.06` el pelo llega a y ≈ 190 y roza la franja del logo, así que de ahí en adelante
hay que compensar con `expandir_lados_post`.

### 6.2 Caso calibrado: Educación Parvularia — Sede Arauco (Post)

El caso difícil: el pelo estaba en y 173, **dentro** de la franja del logo, y el
mentón en y 445, a 18 px de las letras. Bajar la cabeza y subir el mentón son
direcciones opuestas para un desplazamiento puro, así que la única salida era achicar
al sujeto — es el límite físico del encuadre: el rostro medía 272 px y el hueco
disponible entre y 185 e y 433 es de 248 px.

| | Antes | Después |
|---|---|---|
| `expandir_lados_post` / `arriba` / `abajo` | 0.57 / 0.07 / — | 0.78 / 0.09 / 0.09 |
| Foto expandida | 8640 × 8833 px | 9796 × 9808 px |
| Tope del pelo | y 173 | y 191 |
| Mentón | y 445 | y 430 |
| Aire mentón → letras | 18 px | 33 px |
| Alto del rostro | 272 px | 240 px (−12 %) |

Método: en vez de tantear, conviene resolverlo sobre la fórmula. Se miden dos puntos
del rostro en coordenadas de la **foto original** (tope del pelo y mentón), se
replica la aritmética de `capa_fotos_ipg.py` — incluidos los `int()` de cada
expansión — y se busca la combinación que cumpla las dos restricciones maximizando la
escala, es decir dejando el rostro lo más grande posible. Para deducir esos dos
puntos a partir de un render ya hecho: `y_original = (1080 − y_canvas) / escala`
medido desde el borde inferior, restando la expansión superior.

---

## 7. Lógica implementada

### `generar_graficas_ipg.py`
Entrada: un JSON por carrera. Salida: `Post-…svg` y `Story-…svg`.

```json
{
  "slug": "Educacion-Parvularia-Arauco",
  "prefijo": "Técnico de Nivel Superior en",
  "nombre": "EDUCACIÓN PARVULARIA",
  "badges": ["Título Técnico"],
  "sede": "Sede Arauco"
}
```

Lo que recalcula:
- Ancho del subrayado según el largo del prefijo.
- Badges: elimina las pastillas sobrantes cuando hay 1 o 2 títulos; centra el texto
  en cada pastilla (ancho fijo, no se redimensionan).
- Nombre: mide con métricas reales de la fuente (fontTools). Si no cabe, achica hasta
  el 82% del cuerpo; si aún no cabe, corta en dos líneas balanceadas con interlínea
  `size × 1.08` y sube el bloque completo (prefijo + subrayado incluidos).
  Ancho máximo: 1011 px en Post, 968 px en Story.
- Monto: se recentra en la pastilla blanca y se achica si no cabe.
- Pastilla de sede: se redimensiona al texto.

### `capa_fotos_ipg.py`
Quita la plancha gris, reemplaza el grupo de fotos por una foto a sangre embebida en
base64, reaplica el degradado y ofrece `mapa_zonas()` para superponer las zonas
seguras. El encuadre usa `cover` con punto focal configurable
`(fx, fy, fx_destino, fy_destino)` — por defecto `(0.5, 0.38, 0.5, 0.33)`.

**Expansión de lienzo.** Tres funciones agrandan la foto antes de encuadrarla, y se
aplican siempre en este orden: `expandir_foto_lados` → `expandir_foto_arriba` →
`expandir_foto_abajo`. Cada `frac` es fracción del tamaño que trae la imagen *en ese
punto de la cadena*, no del original. El resultado se cachea en
`03-Fotografias/_expandidas/<foto>-a<arriba>-l<lados>[-b<abajo>].jpg`; el sufijo `-b`
sólo aparece cuando hay expansión inferior, para no invalidar los caché antiguos.

**Por qué existe `expandir_abajo` (añadido 14-09-2026).** En el Post, `focal_post`
usa `fy = 1, fy_destino = 1`: la foto va anclada al borde inferior. Si además el
ancho calza exacto (es el caso cuando la foto expandida queda más alta que ancha,
porque entonces `max()` lo gana la razón del ancho), no queda recorrido vertical
alguno: mover `fy` no hace nada. Las opciones son subir `zoom` — que agranda también
la cabeza y la mete en la franja del logo — o agregar piso. `expandir_abajo` estira y
difumina una tira del borde inferior: cada píxel de piso empuja al sujeto hacia
arriba **sin agrandarlo**. La tira cae bajo el degradado negro del pie, detrás de la
pastilla de sede, así que no necesita ser exacta.

Regla práctica de calibración del Post: `expandir_abajo` sube al sujeto entero, y el
pelo sube tanto como el mentón. Si al ganar aire contra el título la cabeza invade la
zona del logo, hay que acompañar con un poco más de `expandir_lados`, que achica al
sujeto y hace que el pelo suba menos que el mentón.

**Decidido (15-09-2026):** el Post lleva **una sola foto a sangre**, no el tríptico
de tres paneles del arte original. Los `clipPath` de 3.4 quedaron sin uso y se
documentan aquí solo por si alguna vez se quiere volver atrás.

---

## 8. Entorno necesario en Claude Code

- Python 3 con `fonttools` y `Pillow`.
- Montserrat instalada (Black, ExtraBold, Medium como mínimo). En
  `generar_graficas_ipg.py` la ruta está fija en `~/.fonts/Montserrat-*.ttf`:
  hay que apuntarla a `C:\Windows\Fonts` o a la carpeta del proyecto.
- Un renderizador SVG → PNG. En esta sesión se usó `rsvg-convert` (librsvg);
  en Windows sirve Inkscape (`inkscape --export-type=png`) o `resvg`.
  Confirmado en Windows: `C:\Program Files\Inkscape\bin\inkscape.exe`, versión 1.4.4.
  **Entrecomillar siempre los argumentos**: la ruta del repositorio tiene espacios
  ("Meta IPG-2027") y, sin comillas, Inkscape interpreta cada fragmento como un
  archivo de entrada distinto, aborta con *"Can't use '--export-filename' with
  multiple input files"* y **devuelve 0 igual**, sin escribir el PNG. Verificar
  siempre que el archivo de salida exista y tenga fecha nueva, nunca el exit code.
- Los scripts asumen las plantillas en el directorio de trabajo.

Validación recomendada: renderizar a PNG y comparar la extensión de tinta del título
contra los márgenes. Así se detectó el desborde del Story.

---

## 9. Reglas de datos

*Eran supuestos al escribir este documento. Al 21-09-2026 los seis se aplicaron
en las cuatro escuelas; sigue faltando el visto bueno formal de Marketing sobre
los puntos 3, 4 y 6.*

1. **Hoja fuente:** `OA Presencial` y `OA Online 27`, cada una con su columna de descuento. La hoja
   `OA 2027` se descarta: no trae descuento ni cuota.
2. **Unidad de réplica:** una gráfica por carrera + sede, agrupando los tipos de
   título. Es lo que explica que la plantilla de Gestión Logística muestre tres
   badges: en el Excel existen tres filas de esa familia. Alternativa: una gráfica
   por fila, lo que sube de ~70 a ~123 piezas.
3. **Tipo de título:** se deriva del nombre, porque no hay columna.
   `PLAN CONTINUIDAD` → Plan Continuidad; `TÉCNICO DE NIVEL SUPERIOR` o `TÉCNICO EN`
   → Título Técnico; el resto → Título Profesional.
4. **Nombre:** se parte en prefijo + núcleo ("Ingeniería en" + "GESTIÓN LOGÍSTICA").
5. **Sede:** `Sede Arauco / Concepción / La Unión / Panguipulli` en presencial,
   `Sede Online` en virtual. La jornada no aparece en la plantilla.
6. **Tildes:** el Excel viene sin acentos en la mayoría de las filas. Hoy se corrigen
   a mano.

---

## 10. Cómo cerró cada pendiente

Al 21-09-2026 la campaña está entregada: 4 escuelas, 43 carreras, 83 piezas,
166 gráficas. Lo que en septiembre eran bloqueantes se resolvió así.

| Pendiente de origen | Cómo cerró |
|---|---|
| Las fotografías | **Resuelto.** Una foto por carrera, en resolución máxima, compartida por todas sus sedes. 43 archivos en `03-Fotografias/<Escuela>/<Carrera>/` |
| Regla de redondeo de la cuota | **Resuelto, pero distinto de lo propuesto acá.** No se trunca al millar: se redondea **a la decena**. |
| ¿Foto por carrera o por escuela? | **Por carrera.** Cambia la pastilla de sede, no la imagen |
| ¿Tríptico de tres paneles o foto única? | **Foto única a sangre.** Los `clipPath` de §3.4 quedaron sin uso |
| ¿Una gráfica por carrera+sede con jornadas distintas? | **Sí, agrupadas.** La plantilla no muestra jornada. Cuando las cuotas difieren se usa la menor, porque dice «Cuotas desde» |
| Listado oficial de nombres con tildes | **Sigue abierto.** El Excel viene sin acentos; cada escuela lleva sus reescrituras anotadas en `_supuestos_a_confirmar` y falta el visto bueno de Marketing |

**Lo que quedó abierto en este proyecto**

Solo dos cosas, y ninguna es técnica:

1. La revisión final de Marketing sobre los nombres y prefijos reescritos.
2. El Módulo 1 —extraer el JSON de escuela directamente del Excel— nunca se
   construyó. Hoy los cuatro JSON se arman a mano.

**Una advertencia que se ganó en el camino**

La regla del 0,30: si el rostro ocupa más del 30 % del alto de la fotografía, no
hay encuadre posible en el Post. La ventana entre el bloque del logo y el título
es demasiado estrecha. Pasó con seis fotos y las seis hubo que reemplazarlas,
con la licencia ya consumida. El criterio se aplica sobre la miniatura, **antes**
de descargar.

---

## 11. Lo que pasó después — V.2, V.2-0 y V.3

Esta sección existe para que lo de arriba no se lea como el estado actual. El
detalle completo está en [`../LEEME.md`](../LEEME.md); acá va sólo lo que
invalida o corrige algo escrito más arriba.

### 11.1 La plantilla cambió (22-09-2026)

Marketing entregó plantillas nuevas y **las secciones 4 y 5 dejaron de
aplicar**:

- **El exportador cambió de forma.** Illustrator pasó de emitir `<tspan>` por
  fragmento de kerning a emitir **un `<text>` por fragmento**. El reemplazo de
  texto se reescribió por *runs*: se agrupan los fragmentos que comparten
  baseline —y opcionalmente rango de x—, se deja el texto completo en el
  primero y se borran los demás.
- **Las clases se renumeraron y son por archivo.** En el Post `.st22` es azul y
  `.st25` blanco; en el Story `.st22` es blanco y `.st24` azul. Localizar por
  clase entre archivos distintos es un error.
- **Apareció la pastilla de modalidad** («Estudia | Sede X» / «Estudia | 100%
  Online»), que cuelga sobre el prefijo. El techo del bloque de texto ya no es
  la primera línea del título sino el borde superior de esa pastilla: **433 px
  en el Post y 700 en el Story**, contra 465 y 763 de la V.1. La ventana se
  achicó 32 y 63 px, y por eso todos los encuadres de la V.1 quedaron justos.
- **El degradado del Story empezaba demasiado abajo** (y = 1036,9 cuando el
  texto empieza en 699,4) y lavaba los títulos. Se corrigió en la plantilla; la
  original quedó en `../01-Plantillas/_V1/`.

Las tres restricciones de la sección 6 siguen vigentes en su idea, pero con
cifras nuevas y una cuarta que la V.1 no tenía: **la caja de silueta**, x
600–960 en el Post y 445–1015 en el Story. Está corrida a la derecha a
propósito, para dejar libre el margen izquierdo.

### 11.2 La expansión de lienzo ya no es por reflejo (23-09-2026)

La sección 7 describe `expandir_foto_lados/arriba/abajo`, que reflejan y
difuminan una banda del borde. Eso produjo dos defectos visibles: **duplicaba
elementos** en planos abiertos —en Rehabilitación aparecían dos sujetos— y
dejaba una franja que se leía como difuminado.

Desde V.2-0 la expansión la hace **Firefly** (`image_generative_expand`) y el
área nueva es fotografía continua. Consecuencias sobre lo escrito arriba:

- **El tope de 180 megapíxeles ya no aplica.** Existía porque el reflejo
  construía la imagen completa en memoria y Pillow la rechazaba como
  decompression bomb. Firefly genera sobre una copia reducida y lo único que
  viaja es la *proporción*. Está en 1.000 MP. Podología daba SIN SOLUCIÓN en el
  Post sólo por ese tope.
- **Máximo 4096 px de expansión por lado.** Cuando el solver pide más, se
  reduce la copia de trabajo hasta que los cuatro lados entren.
- **No hay relleno generativo, sólo expansión de lienzo.** Agregar un objeto
  que no existe o borrar uno no está disponible. Recolorear algo que ya existe,
  sí.

El orden `lados → arriba → abajo` y el `int()` de cada paso **no cambiaron**:
siguen siendo el contrato entre `capa_fotos_ipg.py` y el solver.

### 11.3 El solver necesitó paso fino y vectorización

El barrido de 0,02 es demasiado grueso para rostros grandes: la franja de
valores válidos de `arriba` llega a ser más angosta que el paso. Minas,
Operaciones de Planta Minera e Informática y Ciberseguridad daban SIN SOLUCIÓN
por eso, no por la fotografía. Con 0,005 se resolvieron las tres.

A ese paso, tres bucles anidados en Python puro son ~10 millones de
combinaciones por carrera y no terminan. `resolver_v3.barrer()` barre `lados` y
`arriba` en Python y **`abajo` entero con numpy**.

### 11.4 La medición automática no sirve para estas fotos

La sección 6.2 propone resolver sobre la fórmula en vez de tantear, y eso sigue
siendo correcto. Lo que no funciona es **obtener los dos puntos del rostro
automáticamente**: se probó Haar sobre los archivos a resolución plena de las 18
fotos de V.3 y falló en ocho. El detector elige la cara más grande, que en estas
fotos suele ser el acompañante en primer plano —en Rehabilitación eligió a la
persona de la derecha, en Farmacias a la clienta, en Parvularia a un niño— y en
Instrumentación no encontró ninguna.

El método vigente es el de la sección 6.2 pero con los tres números leídos **a
ojo sobre una grilla en centésimas** (`grillar.py`). Cuando hay varias personas
se elige una, nunca el punto medio.

### 11.5 La selección fotográfica tiene perfil (25-09-2026)

Marketing entregó un Excel de perfiles por carrera, traducido a
[`../02-Datos/perfiles-fotograficos.json`](../02-Datos/perfiles-fotograficos.json):
perfil A/B/C/D, casting, vestuario, acción, locación, keywords y qué evitar,
para las 43 carreras.

Incluye una **regla de cascos** propia, del 25-09-2026: todas las ingenierías
con casco blanco y los técnicos con naranjo, salvo que la carrera no tenga
versión profesional y sólo se dicte como TNS, en cuyo caso va blanco igual.
Cada emparejamiento queda escrito en `casco_motivo`.
