# Gráficas Meta 2027 — entregables

Acá viven las gráficas finales. Todo lo demás de la carpeta madre —plantillas,
datos, fotografías, scripts— es material de trabajo.

El punto de entrada del proyecto es [`../LEEME.md`](../LEEME.md).

---

## Las cuatro versiones

**Ninguna pisa a la anterior.** Cada una fue aprobada en su momento y hay que
poder volver a cualquiera.

| Carpeta | Qué es | PNG |
|---|---|---|
| esta carpeta, en la raíz | **V.1** — plantilla original, expansión por reflejo | 166 |
| `V.2/` | plantilla nueva, con pastilla de modalidad | 166 |
| `V.2-0/` | mismas piezas, fotos expandidas con Firefly | 166 |
| `V.3/` | selección fotográfica por perfil · **es la versión vigente** | 166 |
| `V.3/Modificadas/` | sólo lo que cambió en la última tanda | 100 |

`Modificadas` es un atajo de revisión: se vacía y se vuelve a llenar en cada
tanda, así que nunca mezcla lo nuevo con lo anterior. Lleva su propio LEEME con
el detalle de qué carrera cambió y por qué.

### Qué cambió en cada salto

**V.1 → V.2.** Plantilla nueva de Illustrator. El exportador pasó de emitir
`<tspan>` por fragmento de kerning a emitir **un `<text>` por fragmento**, así
que el reemplazo de texto se reescribió por *runs*. Apareció la pastilla de
modalidad («Estudia | Sede X» / «Estudia | 100% Online»), que **bajó el techo
del título**: de 465 a 433 px en el Post y de 763 a 700 en el Story. Todos los
encuadres de V.1 quedaron justos y hubo que rehacerlos.

**V.2 → V.2-0.** La expansión de lienzo pasó de reflejo a **Firefly**. El
reflejo duplicaba elementos en planos abiertos —en Rehabilitación aparecían dos
sujetos— y dejaba una franja que se leía como difuminado. Con expansión
generativa el área nueva es fotografía continua: sombras, fondo y perspectiva
siguen el original.

**V.2-0 → V.3.** Selección fotográfica guiada por el Excel de perfiles de
Marketing (`../02-Datos/perfiles-fotograficos.json`), con la regla de cascos del
25-09-2026: ingenierías blanco, técnicos naranjo, salvo que la carrera sólo
exista como TNS.

---

## Estructura

```
<Versión>/
  <Escuela>/
    <Carrera>/
      Presencial/
        <Sede>/
          Post-IPG_2027-<carrera>-<sede>.png     1080×1080
          Story-IPG_2027-<carrera>-<sede>.png    1080×1920
      Online/
          Post-IPG_2027-<carrera>-Online.png
          Story-IPG_2027-<carrera>-Online.png
```

Presencial y Online se separan porque son campañas distintas: la presencial se
pauta por región y la online a nivel nacional. Online no abre nivel de sede
—sólo tiene una— porque daría `Online/Online`. La modalidad se deduce de la
sede, no de una columna: la única virtual es «Sede Online».

Una pieza por **carrera + sede**. Las jornadas diurna y vespertina se agrupan,
porque la plantilla no muestra jornada. Las sedes **no son versiones**: cambia
la pastilla y a veces la cuota.

---

## Cómo se regeneran

```bash
python 00-Scripts/generar_v3.py escuela-<nombre>.json
```

Sin argumentos extra genera la escuela completa; con nombres de carrera, sólo
ésas. Para dejar también el SVG editable —con la foto incrustada en base64, por
eso pesa 10–20 MB— el camino V.1/V.2 sigue disponible:

```bash
python 00-Scripts/lote_graficas_ipg.py 02-Datos/escuela-<x>.json --con-svg
```

> Ojo en el explorador: Windows oculta las extensiones, así que con `--con-svg`
> **cada pieza aparece dos veces con el mismo nombre**. No son dos versiones —el
> pesado es el SVG—.

El JSON de escuela es la única fuente de verdad: texto, beca, cuota, sede, foto
y parámetros de encuadre.

---

## Cómo leer una pieza gris

Una pieza con plancha gris uniforme es una pieza **sin fotografía asignada**: el
texto ya es definitivo, falta la imagen. En cuanto se agregue la foto al JSON,
el mismo comando la reemplaza.

---

## Estado por escuela

| Escuela | Carreras | Piezas | Gráficas |
|---|---|---|---|
| Salud | 6 | 14 | 28 |
| Educación y Desarrollo Social | 6 | 23 | 46 |
| Gestión, Negocios y Marítima | 13 | 19 | 38 |
| Ingeniería y Tecnología | 18 | 27 | 54 |
| **Total** | **43** | **83** | **166** |

---

## Supuestos de datos

Son decisiones de IPG. Están acá porque explican por qué dos piezas de la misma
carrera muestran cifras distintas.

- **Cuota.** Se redondea **a la decena** — se dedujo del post de Ingeniería en
  Minas online, que muestra $82.920 para un cálculo de $82.916,67. Cuando la
  jornada diurna y la vespertina difieren se usa **la menor**, porque la
  plantilla dice «Cuotas desde»: afecta a Enfermería en Arauco y La Unión
  ($110.000 frente a $115.000). Panguipulli sólo tiene vespertina, así que queda
  en $115.000.
- **Beca.** 40 % en presencial y 50 % en online, de la columna de descuento.
- **Sede.** Del prefijo del código de carrera: AR Arauco, CC Concepción, LU La
  Unión, PG Panguipulli. Online sale de la hoja virtual.
- **Nombres.** El Excel viene sin tildes y con nomenclatura administrativa
  («TECNICO EN ENFERMERIA DE NIVEL SUPERIOR»). Se reescribieron a la forma de
  marketing: prefijo «Técnico de Nivel Superior en» + núcleo («ENFERMERÍA»). La
  excepción es Farmacias, que quedó como «Técnico en FARMACIAS» por no tener una
  forma larga natural. **Pendiente del visto bueno de Marketing.**
- **Fotografía.** Una por carrera, compartida por todas sus sedes.

---

## Respaldo

Hay una copia íntegra del estado del 21-09-2026 —V.1— en
`C:\Users\IPG\Documents\Arieh\_Respaldos\IPG-2027_2026-09-21\`, comprobada
archivo por archivo con hash: los 1.169 archivos coinciden bit a bit. **No
incluye V.2, V.2-0 ni V.3.**
