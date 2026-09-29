# Brief fotográfico — Escuela de Salud

Cinco fotografías pendientes, una por carrera. Se guardan en
`03-Fotografias/Escuela de Salud/<Carrera>/<Carrera>.jpg`, en la **resolución
máxima** que entregue Shutterstock.

## Criterio común (vale para las cinco)

La referencia es la foto de Enfermería ya aprobada: una sola persona, plano de
medio cuerpo, sonrisa directa a cámara, uniforme sanitario, fondo desenfocado
con profundidad y luz suave. Que las cinco compartan ese registro es lo que hace
que el feed se lea como una sola campaña.

| | Post 1080×1080 | Story 1080×1920 |
|---|---|---|
| Orientación | Horizontal | Vertical o cuadrada grande |
| Ancho mínimo | 2160 px | 2160 px |

Puede servir la misma toma para ambos formatos si viene con margen suficiente:
el script expande el lienzo por los lados y por arriba antes de encuadrar.

**Composición.** Sujeto desplazado al centro-derecha, con el tercio superior
izquierdo despejado — ahí va el logo IPG y el sello CNA, y no puede haber ni
cabezas ni brazos. Sin brazos levantados del lado izquierdo. El rostro debe
caer en la banda alta del encuadre: en el Post, entre y 200 e y 430 de 1080.
Del mentón hacia abajo va el texto, así que el torso puede quedar tapado.

**Descartar.** Fondos con contraste duro o líneas que compitan con el texto;
grupos numerosos; planos muy cerrados de manos, pies o instrumental sin
persona; texto o marcas legibles en la imagen.

**Filtros en Shutterstock.** Tipo: Fotos. Orientación: Horizontal (y una pasada
aparte en Vertical si la toma no da para ambos). Personas: 1 persona.

---

## Estética Integral

Esteticista o cosmetóloga joven, delantal blanco o beige, en cabina de estética
o clínica de belleza. Instrumental sutil, nunca en primer plano.

> `esthetician smiling white uniform beauty clinic`
> `cosmetology student portrait spa treatment room`
> `beautician professional portrait skincare clinic`

## Podología

Podóloga con uniforme sanitario en box clínico. **El riesgo aquí es el banco de
imágenes**: la mayoría de resultados son primeros planos de pies, que no sirven
para la marca. Hay que insistir en retrato de la profesional.

> `podiatrist smiling portrait clinic uniform`
> `chiropodist professional portrait medical office`
> `foot care specialist portrait clinic`

Si no aparece nada usable, la salida es una profesional de la salud en box con
instrumental genérico, en el mismo registro que Enfermería.

## Administración de Centros de Salud

Profesional en admisión o recepción de un centro de salud, con tablet o
computador. Tenida formal o uniforme administrativo, no pijama quirúrgico —
conviene que se distinga de Enfermería a primera vista.

> `healthcare administrator hospital reception smiling`
> `medical office manager tablet clinic portrait`
> `health services administrator portrait office`

## Rehabilitación de Dependencia de Drogas

La más delicada de las cinco. Debe mostrar al **profesional que acompaña**, no a
la persona en consumo: terapeuta o consejero en sesión de orientación, tono
cálido y esperanzador.

> `counselor therapy session smiling supportive`
> `social worker counseling young adult office`
> `addiction counselor portrait community center`

**Nunca:** jeringas, pastillas, alcohol, personas en crisis, rostros ocultos,
imágenes que puedan leerse como estigma.

## Farmacias

Técnico o técnica en farmacia, delantal blanco, entre estanterías de
medicamentos o en mesón de atención.

> `pharmacy technician smiling white coat pharmacy`
> `pharmacist portrait drugstore shelves`
> `pharmacy assistant portrait counter`

---

## Después de descargar

Cada foto nueva entra al JSON de la escuela con su bloque de encuadre:

```json
"foto": "Escuela de Salud/Podologia/Podologia.jpg",
"expandir_arriba_post": 0.22,
"expandir_lados_post": 0.79,
"expandir_abajo_post": 0.045,
"focal_post": [0.47, 1, 0.52, 1]
```

Esos valores son los de Enfermería y sirven de punto de partida, no de receta:
hay que recalibrarlos foto por foto contra las zonas seguras. El
procedimiento está en `00-Scripts/CONTEXTO-graficas-admision-2027.md`, §6.
