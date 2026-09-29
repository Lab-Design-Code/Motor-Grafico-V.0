# Auditoría de las 43 fotos vigentes contra los perfiles v2

Contraste de lo que hay hoy en `V.2-0` con la ficha
`02-Datos/perfiles-fotograficos.json`, que traduce el Excel
`Perfiles_fotograficos_carreras_IPG_v2.xlsx` más la regla de cascos del
24-09-2026.

**Regla de cascos aplicada** (Marketing, 24-09-2026). Todas las ingenierías van
con **casco blanco** y los técnicos con **casco naranjo**, salvo que la carrera
no tenga versión profesional y sólo se dicte como TNS: ahí va blanco igual.
Sustituye al criterio del Excel («casco blanco para jefaturas; amarillo, naranjo
o azul para técnicos»).

De las 16 carreras con EPP quedan **5 en naranjo** — Electricidad,
Instrumentación Industrial, Operaciones Portuarias, Procesos Industriales y
Procesos Mineros — y **11 en blanco**. Conviene mirar dos consecuencias:

- **Minas y Operaciones de Planta Minera pasan a casco blanco**, porque son
  ingenierías. El naranjo queda marcando nivel técnico, no rubro minero.
- **Comercio Exterior, Transporte Marítimo y Maquinaria Naval quedan blancos**
  siendo TNS, porque no existe la ingeniería equivalente.

Cada emparejamiento queda escrito en `casco_motivo` dentro de la ficha, para
poder corregirlo de a uno.

## Resumen

| | Carreras |
|---|---|
| Sirven como están | 7 |
| Falla menor — mejorables | 10 |
| Falla de fondo — reemplazar | 26 |
| **Total** | **43** |

Alcance acordado: se reemplazan las 26 que fallan de fondo, **menos
Rehabilitación de Dependencia de Drogas**, que se mantiene por decisión tuya.
Quedan **25 carreras a buscar**.

Las tres causas de rechazo más frecuentes, en este orden:

1. **Más de un protagonista** (11 casos). La regla pide una persona nítida y el
   resto de espaldas, de lado o desenfocado. Hay fotos de tres y cuatro personas
   de frente.
2. **Casting distinto al del perfil** (10 casos). Sobre todo género invertido:
   la ficha pide mujer y hay hombre, o al revés.
3. **Color de casco** (5 casos), ahora que la regla cambió.

## Perfil A · profesional en terreno

| Carrera | Casco pedido | Qué pasa hoy | Veredicto |
|---|---|---|---|
| Construcción Civil | blanco | Casco **amarillo**, brazos cruzados, sin planos | Reemplazar |
| Ingeniería Industrial | blanco | Casco **amarillo**, sin tablet, sala eléctrica en vez de planta | Reemplazar |
| Electricidad | blanco | Casco blanco ✔, buena acción y fondo; falta chaleco naranjo | Sirve |
| Prevención de Riesgos | blanco | **Tres personas** de frente, casco amarillo | Reemplazar |
| Automatización y Control | blanco | **Tres personas** de frente | Reemplazar |
| Minas | naranjo | Casco naranjo ✔, faena ✔; la ficha pide mujer y hay hombre | Mejorable |
| Operaciones de Planta Minera | naranjo | Casco naranjo ✔, faena ✔ — pero es la misma foto que Minas | Mejorable |
| Instrumentación Industrial | blanco | **Dos personas** lejanas frente a un robot, plano abierto | Reemplazar |
| Procesos Industriales | blanco | **Dos personas** | Reemplazar |
| Procesos Mineros | naranjo | Casco **blanco** y no es faena minera | Reemplazar |
| Mantenimiento Industrial | blanco | Casco blanco ✔, planta ✔; la ficha pide hombre y hay mujer | Mejorable |
| Comercio Exterior | blanco | Casco blanco ✔ pero sin chaleco, bodega en vez de contenedores, y la ficha pide hombre | Reemplazar |
| Operaciones Portuarias | blanco | Casco blanco ✔, puerto ✔; la ficha pide mujer y hay hombre | Mejorable |
| Gestión Logística | sin casco | Delantal de bodeguero, sin chaleco: lee a operario, no a supervisor | Reemplazar |
| Gestión Logística Portuaria | blanco | Plano abierto, la persona queda diminuta | Reemplazar |
| Maquinaria Naval | blanco | Sala de máquinas **sin protagonista** reconocible | Reemplazar |
| Transporte Marítimo | blanco | Uniforme naval con radio en el puente ✔ | Sirve |

## Perfil B · oficina / gestión

| Carrera | Qué pasa hoy | Veredicto |
|---|---|---|
| Administración Pública | La ficha pide **hombre 40-50 con canas y lentes**; hay una mujer joven | Reemplazar |
| Contador Auditor | Mismo perfil senior; el hombre actual es joven y con barba | Mejorable |
| Administración de Empresas | Foto muy apaisada, el plano queda lejano | Mejorable |
| Administración de RRHH | Blazer, papeles, la otra persona de espaldas ✔ | Sirve |
| Contabilidad General | Habla por **teléfono** en vez de trabajar en planilla; fondo rosado muy claro | Mejorable |
| Gestión Comercial y Ventas | Locación confusa (parece sala de exhibición de sanitarios) | Reemplazar |
| Marketing Digital | De perfil y lejano | Mejorable |
| Ciberseguridad | Sala azul ✔, acompañante de espaldas ✔ | Sirve |
| Ciencia de Datos | Lentes, camisa, tablet ✔; falta el fondo tech azul | Sirve |
| Informática | La ficha pide **mujer**; hay hombre | Reemplazar |
| Informática y Ciberseguridad | **Dos protagonistas** de frente | Reemplazar |
| Inteligencia Artificial | **Cuatro personas**, plano abierto de oficina | Reemplazar |
| Gestión de Seguridad y Vigilancia | La ficha pide mujer con traje en sala azul; hay un hombre mayor ante monitores de CCTV | Reemplazar |
| Programación | Casting y acción ✔; falta el fondo tech azul | Sirve |
| Administración de Centros de Salud | Bata y notebook entre **tulipanes**, fondo de mármol: no lee a gestión de salud | Reemplazar |

## Perfil C · oficio en acción

| Carrera | Qué pasa hoy | Veredicto |
|---|---|---|
| Enfermería | De pie con tablet, **sin paciente ni acción clínica** | Reemplazar |
| Estética Integral | De pie en una cabina **vacía**, sin tratamiento ni clienta | Reemplazar |
| Farmacias | Brazos cruzados, sin acción; la ficha pide mujer | Mejorable |
| Podología | Sí es podología (sostiene plantillas ortopédicas), pero hace el **gesto de «ok» a cámara** —pose de catálogo, que el checklist prohíbe— sobre estanterías blancas; la ficha pide mujer con guantes e instrumental, concentrada en su trabajo | Reemplazar |

## Perfil D · social y humano

| Carrera | Qué pasa hoy | Veredicto |
|---|---|---|
| Educación Básica | La ficha pide **hombre con lentes**; hay una mujer | Reemplazar |
| Educación Parvularia | **Señala a cámara** (pose de catálogo) y no hay niño en la escena | Reemplazar |
| Educación Diferencial | Sola de pie; falta el apoyo uno a uno | Mejorable |
| Educación Básica y Parvularia | Con tablet en sala de párvulos; falta el niño | Mejorable |
| Psicopedagogía | Plano abierto sentada en el suelo: la cabeza queda demasiado chica para el encuadre IPG | Reemplazar |
| Rehabilitación de Dependencia de Drogas | La protagonista queda **de espaldas** | Reemplazar |
| Trabajo Social | **Cinco personas** de frente | Reemplazar |

## Una que no se toca sin tu confirmación

**Rehabilitación de Dependencia de Drogas.** La elegiste a propósito porque
«representa mejor la carrera». Falla contra el perfil sólo porque la
protagonista queda de espaldas, que es justo lo que el perfil D pide del
acompañante, no del protagonista. Queda como está mientras no digas otra cosa.

## Lo que el Excel no cubre

Nueve carreras del catálogo no tienen fila propia y su ficha se dedujo del
perfil base más la carrera más cercana. Quedan marcadas con `_derivado` en el
JSON, para que se puedan corregir de una pasada:

Administración de Centros de Salud · Educación Básica y Parvularia · Farmacias ·
Gestión Comercial y Ventas · Gestión Logística Portuaria · Informática y
Ciberseguridad · Instrumentación Industrial · Inteligencia Artificial ·
Mantenimiento Industrial
