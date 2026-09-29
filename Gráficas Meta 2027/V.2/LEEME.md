# Gráficas Meta 2027 — V.2

Campaña completa regenerada con la plantilla **V.2** del 22-09-2026.
43 carreras · 83 piezas · **166 gráficas** (Post 1080×1080 + Story 1080×1920).

La V.1 sigue intacta en la carpeta madre (`../`), con sus 166 PNG y 166 SVG.
Esta carpeta no la toca: se generó con `--salida`, precisamente para que
convivan.

## Estructura

```
V.2/
  <Escuela>/
    <Carrera>/
      Presencial/
        <Sede>/
          Post-IPG_2027-<Carrera>-<Sede>.png    1080×1080
          Story-IPG_2027-<Carrera>-<Sede>.png   1080×1920
      Online/
          Post-IPG_2027-<Carrera>-Online.png
          Story-IPG_2027-<Carrera>-Online.png
```

| Escuela | Carreras | Piezas | Presencial | Online | PNG |
|---|---|---|---|---|---|
| Salud | 6 | 14 | 11 | 3 | 28 |
| Educación y Desarrollo Social | 6 | 23 | 17 | 6 | 46 |
| Gestión, Negocios y Marítima | 13 | 19 | 8 | 11 | 38 |
| Ingeniería y Tecnología | 18 | 27 | 9 | 18 | 54 |
| **Total** | **43** | **83** | **45** | **38** | **166** |

Aquí hay **solo PNG**. El SVG editable se rehace en segundos con `--con-svg`.

## Cómo se regenera

```bash
python 00-Scripts/lote_graficas_ipg.py 02-Datos/escuela-<nombre>.json --salida "Gráficas Meta 2027/V.2"
```

El lote completo son unos 14 minutos: 166 rasterizados de Inkscape más la
expansión de las fotos que no estén en caché.

## Qué cambió respecto de la V.1

**En la plantilla** — clases `cls-*` → `st*`, títulos de Montserrat Black a
ExtraBold, texto repartido en un `<text>` por fragmento de kerning, logo y
sello CNA nuevos, claim «TRANSFORMANDO TU PASIÓN EN PROFESIÓN» arriba, y el
degradado superior ya incorporado.

**La pastilla de sede desapareció.** La reemplazó «Estudia | …» sobre el
título. Para no perder el dato —hay una pieza por carrera *y sede*— el chip
lleva la sede en presencial («Estudia | Sede Arauco») y «100% Online» en
virtual. **Falta el visto bueno de Marketing sobre este criterio.**

**El degradado inferior del Story está parcheado.** La V.2 lo traía
arrancando en y=1036,9, pero el bloque de texto empieza en y=699,4: el
título caía sobre foto cruda y se lavaba. Se subió el arranque a y=671,
replicando la relación que el Post tiene entre degradado y texto (~28 px de
anticipo). El archivo original sin parchear está en
`01-Plantillas/_V1/Story-IPG 2027-Plantilla-V.2-sin-degradado.svg`.

**La expansión de las fotos ya no es relleno difuminado.** Se refleja la
banda exterior de la propia fotografía y se suaviza hacia afuera. Ver
`03-Fotografias/BRIEF-Seleccion-Fotografica.md`.

## Los encuadres: qué se rehizo y qué queda

La V.2 subió el techo del bloque de texto —ahora manda la pastilla de
modalidad, no el título— **32 px en el Post y 63 px en el Story**. Los
encuadres de las 43 carreras se habían resuelto contra el techo de la V.1, así
que todos quedaron más justos de lo que pide la regla del proyecto (70/90 px
de aire a una línea, 50/70 a dos).

Se auditan con:

```bash
python 00-Scripts/verificar_encuadres.py --todas
```

**Ninguna pieza choca**: el mentón siempre queda sobre el texto. Lo que se
notaba eran los **títulos a dos líneas**, que suben el bloque completo una
interlínea y dejaban el aire en 7-15 px.

De esas 15 carreras se volvieron a resolver y regenerar **las 8 que tenían
solución completa** en ambos formatos — 12 piezas, 24 gráficas:

Administración de Empresas · Gestión Logística Portuaria · Operaciones
Portuarias · Automatización y Control Industrial · Gestión de Seguridad y
Vigilancia Privada · Mantenimiento Industrial · Instrumentación Industrial ·
Administración de Centros de Salud

**Quedan 7 carreras sin solución posible con la fotografía actual.** El
solver devuelve *SIN SOLUCIÓN*: la cara no cabe en la ventana que queda entre
el bloque del logo y el texto, en ningún punto del espacio de expansiones.

| Carrera | Formato sin solución |
|---|---|
| Educación Básica y Parvularia | Post |
| Administración de Recursos Humanos | Post |
| Gestión Comercial y Ventas | Story |
| Informática y Ciberseguridad | Post y Story |
| Inteligencia Artificial | Post |
| Operaciones de Planta Minera | Post |
| Rehabilitación de Dependencia de Drogas | Post |

Siguen publicadas con el encuadre de la V.1 —aire de 7 a 22 px— y es lo único
que falta cerrar. Dos caminos: **reemplazar la fotografía** siguiendo
`03-Fotografias/BRIEF-Seleccion-Fotografica.md` (lo correcto de fondo, cuesta
licencias) o **relajar el aire mínimo** en `solver_encuadre.py`, que las
resuelve a todas pero acerca el texto al mentón en el resto de la campaña.

Estado tras el re-encuadre: **17 encuadres ok, 69 justos, 0 choques**.
