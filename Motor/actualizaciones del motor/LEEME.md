# Actualizaciones del motor

Registro de cada cambio al motor (los primeros los pidió la interfaz web, que no está en este repositorio)
(`Motor/motor/`). Una carpeta por versión, con el código **antes** y
**después**, el `cambios.diff` y un `CAMBIOS.md` que explica el porqué y cómo se
verificó que las piezas existentes no cambiaran.

| Versión | Fecha | Qué | Piezas afectadas |
|---|---|---|---|
| [v1.1.0](v1.1.0%20-%20avance%20en%20vivo%20para%20la%20interfaz/CAMBIOS.md) | 05-10-2026 | Avance en vivo (`progreso`), calce exacto de slug, lote que no se detiene ante una pieza fallida | Ninguna: salida idéntica |
| [v1.2.0](v1.2.0%20-%20rostros%20de%20perfil%20y%20datos%20vacios/CAMBIOS.md) | 05-10-2026 | Rostros de perfil (Haar), dato vacío con mensaje claro, el encuadre del lote sigue si falla una pieza. | Ninguna: salida idéntica |
| [v1.3.0](v1.3.0%20-%20expansion%20por%20reflejo%20y%20fotos%20pre-expandidas%20(Firefly)/CAMBIOS.md) | 05-10-2026 | Costura del relleno acotada al 3 % (cara borroneada en fotos chicas), método «reflejo» de Meta V.2 opcional, uso de fotos pre-expandidas con Adobe Firefly. | Ninguna con el método por omisión: salida idéntica |

## Reglas para la próxima actualización

1. Copiar a `antes/` los archivos **antes** de editarlos.
2. Parámetros nuevos siempre **opcionales**: `graficas.py` no debe enterarse.
3. Verificar contra IPG que las piezas salen idénticas (o explicar por qué no).
4. Subir `__version__` en `motor/__init__.py` y agregar la fila a esta tabla.
