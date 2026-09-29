# 00-Scripts — qué hace cada uno

Son 37 archivos y no todos están vivos. Esta tabla existe para no abrir cinco
antes de dar con el que sirve.

El punto de entrada del proyecto es [`../LEEME.md`](../LEEME.md).

---

## El núcleo — no se toca sin medir

Estos cuatro son el motor. Todo lo demás los llama.

| Script | Qué hace |
|---|---|
| `generar_graficas_ipg.py` | Construye el SVG de una pieza: texto, badges, pastillas, autoajuste del título. Es donde vive el mapa de la plantilla V.2 |
| `capa_fotos_ipg.py` | Reemplaza la plancha gris por la foto, aplica el encuadre *cover* con punto focal y define las zonas seguras |
| `solver_encuadre.py` | Las restricciones —pelo, mentón, silueta, aire— y el solver que busca la combinación de expansiones |
| `lote_graficas_ipg.py` | Recorre un JSON de escuela, arma las rutas Escuela/Carrera/Modalidad/Sede y rasteriza con Inkscape |

**`solver_encuadre.py` replica la aritmética de `capa_fotos_ipg.py`, incluidos
los `int()` de cada expansión.** Si divergen, el solver aprueba encuadres que el
render no reproduce.

---

## Pipeline V.3 — el que se usa hoy

En orden de uso. Los `una_*` trabajan sobre una carrera suelta; los otros, sobre
una escuela completa.

| Paso | Una carrera | Una escuela |
|---|---|---|
| 1 · instalar la foto y sacar la grilla | `una_instalar.py` | `asignar.py` + `grillar.py` |
| 2 · medir | — a ojo, sobre la grilla — | |
| 3 · resolver el encuadre | `una_resolver.py` | `resolver_v3.py` |
| 4 · convertir a píxeles Firefly | *(lo imprime el paso 3)* | `preparar_v3.py` |
| 5 · expandir | *(conector de Adobe)* | |
| 6 · bajar y aplicar | `una_cerrar.py` | `bajar_v3.py` + `aplicar_v3.py` |
| 7 · generar | `generar_v3.py` | `generar_v3.py` |
| 8 · reunir para revisar | `copiar_una.py` | `modificadas.py` |

```bash
# una carrera, de punta a punta
python 00-Scripts/una_instalar.py 97 Gestion-Logistica "Escuela de Gestion, Negocios y Maritima"
python 00-Scripts/una_resolver.py Gestion-Logistica "Escuela de Gestion, Negocios y Maritima" 0.110 0.410 0.420
#   … expandir con Firefly …
python 00-Scripts/una_cerrar.py escuela-gestion.json Gestion-Logistica <uid-post> 2798 2181 <uid-story> 2000 3542
python 00-Scripts/generar_v3.py escuela-gestion.json Gestion-Logistica
python 00-Scripts/copiar_una.py escuela-gestion.json Gestion-Logistica
```

`resolver_v3.py` además **exporta `barrer()`**, que es el barrido vectorizado
con numpy. `una_resolver.py` y los resolvedores sueltos lo importan en vez de
duplicarlo.

---

## Medición y control de calidad

| Script | Qué hace |
|---|---|
| `grillar.py` | Dibuja una grilla en centésimas sobre cada foto de una tanda, para medir a ojo |
| `grilla_fina.py` | Grilla ampliada sobre el recorte del rostro |
| `medir_titulo.py` | Renderiza cada pieza **sin foto** y mide en qué Y empieza el título. Depende del largo del nombre, así que no se estima |
| `verificar_encuadres.py` | Audita una escuela contra el techo del título y reporta `ok` / `justo` / `CHOCA` |
| `prevalidar_fotos.py` | Filtra candidatas de banco **antes** de licenciarlas, sobre la miniatura pública |
| `hoja_contacto.py` | Hoja de contacto de una tanda de candidatas |

> `medir_titulo.py` escribe `titulo_post` y `titulo_story` en
> `02-Datos/medidas-<escuela>.json`. Ese es el techo real que usa el solver; si
> cambia el nombre de una carrera hay que volver a correrlo.

---

## Retoque de fotografía

| Script | Qué hace |
|---|---|
| `recolorear_casco.py` | Pasa un casco de color a blanco, con ganancia por reflectancia. Lleva escritas las tres cosas que salieron mal antes |
| `identificar.py` | Asigna descargas a carreras **por contenido**, no por orden de llegada |

> **El umbral de la huella es 1,0, no 300.** `identificar.py` compara con
> huellas de 32×32 normalizadas. Dos imágenes sin relación dan ≈ 2,0 —el máximo
> útil de la métrica es ~4—; dos copias de la misma, 0,0–0,3. Un 1,5 no es la
> misma foto.

---

## Documentación

| Script | Qué hace |
|---|---|
| `verificar_docs.py` | Comprueba que los enlaces relativos entre los LEEME resuelvan |
| `generar_documentacion.py` | Genera el `.docx` de `06-Documentacion` — **congelado en V.1** |

---

## Histórico — funcionan, pero ya no son el camino

| Script | Por qué quedó atrás |
|---|---|
| `generar_v20.py`, `generar_edu.py`, `generar_ges.py`, `generar_ing.py` | uno por escuela; `generar_v3.py` los reemplaza a los cuatro |
| `bajar_ing.py`, `preparar_gen.py` | de la tanda de Ingeniería en V.2-0 |
| `resolver_fino.py` | barrido fino en Python puro; `resolver_v3.barrer()` lo hace vectorizado |
| `aplicar_encuadres.py`, `asignar_fotos.py`, `propagar_fotos.py` | del flujo V.1 |
| `recoger_descargas.py` | recogía descargas del navegador por orden |
| `limpiar_versiones.py` | purga carpetas de trabajo y caché de expandidas |
| `generar_documentacion.py` | genera el `.docx` de `06-Documentacion`. **Describe el estado de V.1**: sigue sirviendo como manual de la plantilla original, no del pipeline actual |

No se borran a propósito: son el registro de cómo se llegó acá, y varios
documentan en su cabecera un error que costó encontrar.

---

## Convenciones que comparten todos

**Rutas.** El repositorio está en una ruta con `ñ` y con espacios. Dos
consecuencias:

- `cv2.imread` devuelve `None` — hay que leer los bytes y usar `cv2.imdecode`.
- `Set-Content -Encoding UTF8` de PowerShell convierte `Diseño` en `DiseÃ±o`.
  Para escribir archivos que contengan la ruta, `io.open(..., encoding='utf-8')`
  desde Python.

**Respaldos.** Todo script que pise una foto o un JSON deja antes una copia:
`03-Fotografias/_V2-0-sin-retoque/`, `03-Fotografias/_generadas-V2-0/`,
`02-Datos/_V2-0/`. Nunca se sobrescribe sin respaldo.

**Verificación del tamaño.** Los que bajan de Firefly comprueban que el archivo
tenga exactamente las dimensiones declaradas. Si no coinciden, el encuadre que
resolvió el solver no aplica y hay que rehacer esa pieza.

**Foto ya expandida.** Cuando existe `03-Fotografias/_generadas/<Carrera>-<post|story>.jpg`,
el generador **borra las claves `expandir_*`** de la pieza y entra con expansión
0. El lienzo ya viene resuelto y el `focal` sigue siendo válido porque las
proporciones son las que se le pidieron a Firefly.
