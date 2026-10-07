# Motor v1.3.0 — expansión por reflejo y fotos pre-expandidas (Firefly)

**Fecha:** 05-10-2026
**Alcance:** `motor/` (en este repositorio, `Motor/motor/`)
**Archivos tocados:** `motor/foto.py`, `motor/lote.py`, `motor/__init__.py` (1.2.0 → 1.3.0)
**Compatibilidad:** total. Parámetros nuevos opcionales; `graficas.py` no cambia.
**Origen:** lo aprendido en *Meta IPG-2027* (versiones V.2 y V.2-0, ver su `LEEME.md`).

## Por qué

Al proponer fotos de internet apareció una pieza con la cara **borroneada**. La
persona tenía la cabeza cerca del borde superior de una foto chica (1023×684), y
el relleno de bordes del motor (el método V.1, «estirado») difumina una costura
de `max(60 px, 1 %)` × 3. En esa foto eran 180 px, el 26 % del alto, justo
encima de la cara.

En Meta IPG-2027 este relleno ya se había reemplazado dos veces: primero por un
**reflejo de la banda del borde** con rampa de suavizado (V.2) y después por la
**expansión generativa de Adobe Firefly** (V.2-0).

## Qué cambió

| Archivo | Cambio |
|---|---|
| `foto.py` | **Costura acotada:** la tira que se estira y difumina no pasa del 3 % del lado (`_tira`). En fotos de 2000 px o más (todas las de IPG) el valor es el mismo de antes. |
| `foto.py` | **Método «reflejo»** (portado de `capa_fotos_ipg.py` de Meta): refleja el 22 % exterior del borde y le aplica una rampa de suavizado. La foto original queda intacta. Usa la misma aritmética de tamaños (con los `int()`), así que el solver y los encuadres no cambian. Su caché lleva el sufijo `-r`. |
| `foto.py` | `preparar(..., metodo=None)`: `"estirado"` (por omisión) o `"reflejo"`. También se puede elegir con la variable `MG_EXPANSION`. |
| `lote.py` | `construir_pieza` usa la **foto ya expandida por fuera del motor** si la pieza la trae en `expandidas[formato] = {"archivo", "expansiones"}` y esas expansiones son **exactamente** las del encuadre vigente. Así se usan las de Firefly, igual que hace `generar_v3.py` en Meta. Si el encuadre cambió, la ignora y vuelve al relleno propio. |
| `lote.py` | El método de relleno se lee de `proyecto.json` → `"expansion"`. Lo escribe quien arma el proyecto (consola o interfaz). |

## Por qué el estirado sigue por omisión

Se compararon las piezas IPG con reflejo y con estirado. En planos abiertos (el
pasillo de Enfermería) el reflejo repite texturas y se ve más cargado. Meta llegó
a lo mismo: el reflejo duplicaba elementos (en Rehabilitación aparecían dos
sujetos), y por eso V.2-0 pasó a Firefly. Por eso:

- **estirado** queda por omisión: las piezas aprobadas no cambian;
- **reflejo** se puede elegir por campaña;
- **Adobe Firefly** (fotos pre-expandidas, generadas fuera del motor) es la opción de calidad.

## Verificación

- 8 SVG IPG (Enfermería Arauco, Psicopedagogía Arauco, Gestión de Seguridad
  Online e Informática Online; post + story), con expansiones de hasta
  lados 1,9 / arriba 0,24 / abajo 0,5. Motor **antes** y **después**: los 8 son
  **idénticos byte a byte**, y también las 8 fotos expandidas en caché.
- Con `metodo="reflejo"`, la geometría (escala, focal y posición) es idéntica en
  las 8 piezas. Solo cambia la imagen de relleno.
- La pieza de la falla (Marketing Digital, foto de Openverse 1023×684) se
  regeneró y la cara queda nítida.
- Firefly simulado sobre Enfermería (5391×7787, lados 1,9): la copia de trabajo
  (927×1339) se expande a 2687×1926, dentro del máximo de 2688. El compuesto final
  mantiene la proporción del motor (1,39456 vs 1,39476) y el original queda
  nítido en el centro. `_pre_expandida` la usa cuando calza y la ignora cuando el
  encuadre cambió.

## Lo que queda de Meta para una próxima versión

- **Plantilla V.2** (pastilla de modalidad «Estudia | Sede», Montserrat ExtraBold,
  textos por fragmento). La plantilla `ipg-2027` del motor sigue siendo la V.1.
- Solver: regla lateral del Story (el recorte solo puede comerse margen
  generado, holgura de 8 px), barrido fino vectorizado con numpy y tope de
  1000 MP cuando la expansión es de Firefly. Cambian encuadres, así que necesitan
  su propia verificación.

## Cómo revertir

Copiar `antes/motor/*.py` sobre `Motor/motor/`.
