# Motor v1.1.0 — avance en vivo para la interfaz

**Fecha:** 05-10-2026
**Archivos tocados:** `motor/lote.py`, `motor/__init__.py` (versión 1.0.0 → 1.1.0)
**Compatibilidad:** total. Todos los parámetros nuevos son opcionales y la
línea de comandos (`graficas.py`) funciona igual que antes.

## Por qué

La interfaz web necesita saber **qué pieza se está procesando y cómo salió**
mientras el lote corre. El motor solo lo imprimía en consola, y leer la consola
para armar una barra de avance es frágil.

## Qué cambió

| Función | Parámetro nuevo | Para qué |
|---|---|---|
| `generar()` | `progreso=fn` | Se llama tras cada pieza y formato con `slug`, `formato`, `png`, `hallazgos` del QA, `hechas` y `total` |
| `generar()` | `slugs=[...]` | Calce **exacto** del slug. `--solo` busca texto dentro del slug y "Educacion-Basica" también elegía "Educacion-Basica-y-Parvularia" |
| `generar()` | `continuar=True` | Una pieza que falla (foto corrupta, dato faltante) se informa con `error` y el lote sigue. Solo actúa si hay `progreso` |
| `resolver_encuadres()` | `progreso=fn`, `slugs=[...]` | Un evento por pieza: `ok`, `mensajes` por formato, `medidas` y ruta de la imagen de `verificacion` |
| `filtrar_fotos()` | `progreso=fn` | Un evento por foto con su fila de resultado |

Funciones auxiliares nuevas en `lote.py`: `_elegida()` y `_hallazgos_planos()`.

## Verificación

Se generaron en SVG dos piezas IPG (`Psicopedagogia-Arauco` y
`Educacion-Basica-Online`, post + story) con el motor **antes** y **después**
del cambio: los 4 archivos son **idénticos byte a byte** (md5). El callback
entregó los 4 eventos esperados, sin hallazgos de QA.

## Cómo revertir

Copiar `antes/motor/*.py` sobre `Motor/motor/`. La interfaz web
necesita esta versión: sin ella la generación funciona, pero sin avance en vivo.

## Contenido de esta carpeta

```
antes/motor/      lote.py y __init__.py tal como estaban (v1.0.0)
despues/motor/    lote.py y __init__.py actualizados (v1.1.0)
cambios.diff      diferencia exacta, aplicable con `git apply`
```
