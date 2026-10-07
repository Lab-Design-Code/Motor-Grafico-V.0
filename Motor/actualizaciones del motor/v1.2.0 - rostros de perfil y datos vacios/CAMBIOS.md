# Motor v1.2.0 — rostros de perfil y datos vacíos

**Fecha:** 05-10-2026
**Alcance:** `motor/` (en este repositorio, `Motor/motor/`)
**Archivos tocados:** `motor/rostro.py`, `motor/plantilla.py`, `motor/lote.py`,
`motor/__init__.py` (1.1.0 → 1.2.0)
**Compatibilidad:** total; la consola funciona igual.

## Por qué

Al probar el creador aparecieron tres fallas:

1. **Una foto con la persona de perfil** («Informatica.jpg», un programador
   mirando la pantalla) no se pudo medir. Sin los modelos opcionales
   (mediapipe/YuNet) solo queda Haar, que únicamente reconoce caras de frente.
2. **Una gráfica sin datos** cayó con `ValueError: could not convert string to
   float: ''`, un mensaje que no dice qué falta.
3. Ese error **detuvo el encuadre de todo el lote**, no solo el de esa pieza.

## Qué cambió

| Archivo | Cambio |
|---|---|
| `rostro.py` | Si Haar no encuentra una cara de frente, prueba la cascada **de perfil** sobre la foto y sobre su reflejo (la cascada solo ve caras que miran hacia un lado). |
| `plantilla.py` | `formatear()` rechaza un dato vacío con un mensaje claro: `El dato 'cuota' esta vacio (la plantilla lo pide en "${cuota:miles}")`. |
| `lote.py` | `resolver_encuadres()`: con `progreso` (una interfaz que muestra el avance), una pieza que falla se informa y el lote sigue. Sin `progreso` (consola), el error se ve completo como antes. |

## Verificación

- «Informatica.jpg» ahora se mide: pelo 0,104 · mentón 0,399 · cara x 0,675
  (backend haar, de perfil). La imagen de verificación ubica bien el rostro.
- Se generaron en SVG tres piezas IPG (Psicopedagogía Arauco, Informática Online
  y Enfermería Arauco, post + story) con el motor **antes** y **después**: los 6
  archivos son **idénticos byte a byte**.

## Cómo revertir

Copiar `antes/motor/*.py` sobre `Motor/motor/`.
