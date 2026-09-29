# Instrucciones para el asistente de IA

Este archivo es para la IA que instala y opera el motor. La persona sólo te
pidió «instala el Motor Gráfico»: ejecuta tú cada paso, muéstrale el resultado
y resuelve lo que falle antes de seguir. Está pensado para Windows.

## Instalar

1. Comprueba Python 3.10 o superior, Git e Inkscape 1.x. Si falta alguno:
   `winget install Python.Python.3.12 Git.Git Inkscape.Inkscape`, y abre una
   terminal nueva.
2. `git config --global core.longpaths true`. Sin esto el clon falla con
   *Filename too long*.
3. Deja el repositorio en `C:\Motor-Grafico-AG`. Una ruta más profunda supera
   los 260 caracteres de Windows e Inkscape no escribe los PNG.
4. `python -m pip install -r requirements.txt`
5. Descarga `Montserrat-Black.otf`, `Montserrat-ExtraBold.otf` y
   `Montserrat-Medium.otf` de
   <https://github.com/JulietaUla/Montserrat/tree/master/fonts/otf> e
   **instálalas en Windows** para el usuario. Inkscape dibuja el texto con las
   fuentes del sistema; `fuentes/` sólo sirve para medir. Los `.ttf` de Google
   Fonts no los reconoce el motor.
6. Pídele a la persona sus insumos:
   - **Plantillas**: Post 1080×1080 y Story 1080×1920 en `.svg`, a
     `01-Plantillas/`.
   - **Base de datos** de carreras, presencial u online: se traduce a
     `02-Datos/escuela-*.json` con el formato descrito en `LEEME.md`.
   - **Fotografías**, de una de dos formas:
     - **Una carpeta propia**: si trae fotos ya expandidas (`_generadas`),
       cópiala a `03-Fotografias/_generadas/`; si son fotos originales, pásalas
       por el flujo de `LEEME.md` (medir, resolver el encuadre y expandir).
     - **Un banco de imágenes** (por ejemplo Shutterstock): busca candidatas
       según el perfil de la carrera en `02-Datos/perfiles-fotograficos.json`,
       descarta las que no cumplan la regla del 0,30 con
       `00-Scripts/prevalidar_fotos.py` y recomiéndale las mejores con su
       enlace. Descarga sólo con su autorización: cada descarga consume una
       licencia, y la ficha debe decir «Descargas ilimitadas», sin aviso de uso
       editorial. Después sigue el flujo de `LEEME.md`.
7. Prueba: `python 00-Scripts\generar_v3.py escuela-salud.json Enfermeria`.
   Debe imprimir cuatro `ok` y `8 graficas`. Comprueba que los 8 PNG existan en
   `Gráficas Meta 2027\V.3\Escuela de Salud\Enfermeria\` (Inkscape puede fallar
   sin avisar) y muéstrale uno a la persona.

## Generar gráficas

`python 00-Scripts\generar_v3.py <escuela.json> [<carpeta de la carrera> ...]`

Sin carrera genera la escuela completa. La carrera se nombra con su campo
`"carpeta"` del JSON y se rehacen todas sus sedes. Salida en
`Gráficas Meta 2027\V.3\<Escuela>\<Carrera>\<Presencial\Sede | Online>\`.

## Si algo falla

| Síntoma | Causa |
|---|---|
| `Inkscape no escribio …png` | Ruta de más de 260 caracteres, o Inkscape fuera de su carpeta por defecto (variable `INKSCAPE`). |
| Error con `Montserrat-…otf`, o título en otra tipografía | Fuentes `.otf` no instaladas en Windows. |
| Error que menciona un `.jpg` | Falta la foto en `03-Fotografias/_generadas/`. |

El detalle de cada script y del encuadre está en [`LEEME.md`](LEEME.md) y
[`00-Scripts/LEEME.md`](00-Scripts/LEEME.md).
