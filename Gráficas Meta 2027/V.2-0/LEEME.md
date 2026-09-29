# V.2-0 — campaña completa con fotografías nuevas

166 gráficas, 83 piezas, 43 carreras. Misma plantilla y mismo motor que `V.2`;
lo que cambia es **la fotografía de las 43 carreras y cómo se expande**.

| Escuela | Carreras | Piezas | PNG |
|---|---|---|---|
| Salud | 6 | 14 | 28 |
| Educación y Desarrollo Social | 6 | 23 | 46 |
| Gestión, Negocios y Marítima | 13 | 19 | 38 |
| Ingeniería y Tecnología | 18 | 27 | 54 |
| **Total** | **43** | **83** | **166** |

Las 166 pasan la auditoría de encuadre (`verificar_encuadres.py`): ninguna choca
contra el título ni queda con el pelo sobre la zona del logo.

## Qué es distinto respecto de V.2

**La expansión del lienzo es generativa, no un reflejo.** En V.2 el área que
faltaba para llegar al 1:1 o al 9:16 se rellenaba reflejando la banda exterior
de la foto y suavizando la costura. Funciona, pero se nota: en planos abiertos
duplicaba elementos —en Rehabilitación aparecían dos sujetos— y en el resto
dejaba una franja que se lee como difuminado.

Acá el área nueva la genera Firefly (`image_generative_expand`) y es fotografía
continua: sombras, fondo y perspectiva siguen el original.

## El pipeline, de punta a punta

1. **Medir sobre el archivo real**, nunca sobre la miniatura
   (`grilla_fina.py`). Los valores van a `02-Datos/medidas-<escuela>.json`.
2. **Resolver el encuadre** (`solver_encuadre.py`). Entrega, por pieza,
   `expandir_lados / arriba / abajo` como fracciones y el `focal`.
3. **Convertir esas fracciones a píxeles** para Firefly (`preparar_gen.py` del
   scratchpad). La cadena es siempre `lados → arriba → abajo`, y cada fracción
   es relativa al tamaño *en ese punto de la cadena*, no al original.
4. **Subir, expandir y bajar.** El resultado queda en
   `03-Fotografias/_generadas/<Carrera>-<post|story>.jpg`.
5. **Generar con expansión 0.** La foto ya trae el lienzo resuelto, así que las
   claves `expandir_*` se eliminan antes de construir el SVG. El `focal` del
   solver sigue siendo válido porque las proporciones de la expansión son
   exactamente las que se le pidieron a Firefly.

## Tres cosas que hay que saber para repetirlo

**Firefly no acepta más de 4096 px por lado de expansión.** Cuando el solver
pide más, se reduce la copia de trabajo hasta que los cuatro lados entren, y se
expande sobre esa copia. Lo que viaja es la proporción; la resolución final
sigue siendo de sobra para 1080 px.

**El tope de 180 megapíxeles del solver dejó de aplicar.** Existía por el método
de reflejo, que construía la imagen completa en memoria con Pillow. Firefly
genera sobre la copia reducida, así que el límite se subió a 1.000 MP. Podología
Post decía *SIN SOLUCIÓN* sólo por ese tope.

**El paso del solver puede ser demasiado grueso.** Con rostros grandes la franja
de valores válidos de `arriba` llega a ser más angosta que el paso de 0,02 y la
búsqueda pasa por encima sin verla. Les pasó a Minas, Operaciones de Planta
Minera e Informática y Ciberseguridad: las tres se resolvieron repitiendo el
barrido a 0,005. No era la fotografía.

**En Story el recorte sólo puede comerse margen generado.** El criterio correcto
no es limitar el recorte a un número fijo de píxeles, sino exigir que la ventana
visible no invada la fotografía original (con 8 px de holgura). La primera
versión de ese criterio dejaba dos carreras sin solución.

## Fotografías reutilizadas

Minas y Operaciones de Planta Minera comparten la misma fotografía, con
encuadres y textos distintos. Es una decisión de marketing, no una omisión.

## Pendiente

- **Auditoría de licencias.** Al menos un candidato de Shutterstock
  (`2663900595`) era de **uso editorial únicamente** y se descartó antes de
  licenciarlo. El prevalidador comprueba encuadre, no tipo de licencia: conviene
  revisar una a una las fotos ya compradas antes de publicar.
- **Texto de la pastilla de modalidad** («Estudia | Sede X» / «Estudia | 100%
  Online»): falta visto bueno de Marketing.
- **Nombres largos.** El título se topa con `nombre_maxw` (1011 px en Post, 968
  en Story) y el motor lo achica para que quepa. Mantenimiento Industrial e
  Instrumentación Industrial quedan con 13 px de margen derecho contra 55,9 del
  izquierdo. Acortar el nombre subiría el techo del mentón de 359 a 433 px y
  permitiría sujetos más grandes.
