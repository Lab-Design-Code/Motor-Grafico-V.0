# Motor Gráfico · Meta IPG 2027

Generador automático de las gráficas de Meta (Instagram y Facebook) para la
Admisión IPG 2027. A partir de un JSON por escuela, una plantilla SVG y una
fotografía por carrera produce el **Post 1080×1080** y el **Story 1080×1920**
de cada carrera y sede.

Hoy son **43 carreras, 83 piezas y 166 gráficas** por versión.

> La documentación completa está en español en [`LEEME.md`](LEEME.md). Este
> archivo sólo resume cómo poner el motor en marcha en otra máquina.

## Qué incluye el repositorio y qué no

La carpeta de trabajo pesa unos 5 GB. Casi todo eso son fotografías
licenciadas y gráficas terminadas, así que **no se versionan**. El
repositorio pesa unos pocos MB.

| Se versiona | No se versiona (ver `.gitignore`) |
|---|---|
| `00-Scripts/`: todo el pipeline en Python | fotografías `.jpg` de `03-Fotografias/` |
| `01-Plantillas/`: plantillas `.svg` de Post y Story | gráficas `.png`/`.svg` de `Gráficas Meta 2027/` |
| `02-Datos/`: JSON de escuelas, encuadres, perfiles y el Excel de admisión | vistas previas `.png` y mapas de zonas seguras |
| `06-Documentacion/`: el manual `.docx` | `node_modules/`, `__pycache__/`, `.zip` |
| Briefs y LEEME de cada carpeta | fuentes `.otf` |
| La estructura de carpetas, vacía, con `.gitkeep` | |

## Puesta en marcha

```bash
git clone https://github.com/Lab-Design-Code/Motor-Grafico-MT.git
cd Motor-Grafico-MT
pip install -r requirements.txt
```

Además necesitas:

| Requisito | Cómo se configura |
|---|---|
| **Python 3.10 o superior** | |
| **Inkscape 1.x** | en el `PATH`, en la ruta estándar de Windows, o en la variable `INKSCAPE` |
| **Montserrat** Black, ExtraBold y Medium | instalada en el sistema, copiada en [`fuentes/`](fuentes/LEEME.md), o en la variable `IPG_FUENTES` |
| **Fotografías** | una por carrera en `03-Fotografias/<Escuela>/<Carrera>/<Carrera>.jpg` |
| **Conector de Adobe (Firefly)** | sólo para expandir fotografías nuevas |

Los scripts ya no dependen de rutas fijas: toman la raíz del repositorio a
partir de su propia ubicación, así que sirve cualquier carpeta de destino.

### Comprobación

```bash
python 00-Scripts/medir_titulo.py 02-Datos/escuela-salud.json
python 00-Scripts/verificar_docs.py
```

El primero comprueba Inkscape y las fuentes. El segundo, que los enlaces de la
documentación resuelvan.

### Generar las gráficas

Con las fotografías ya instaladas y expandidas en `03-Fotografias/_generadas/`:

```bash
python 00-Scripts/generar_v3.py escuela-salud.json
```

El pipeline completo (instalar foto, medir, resolver el encuadre, expandir con
Firefly y generar) está descrito en [`LEEME.md`](LEEME.md#3-el-pipeline-de-punta-a-punta).
Lo que hace cada script está en [`00-Scripts/LEEME.md`](00-Scripts/LEEME.md).

## Estructura

```
00-Scripts/          el pipeline
01-Plantillas/       Post y Story .svg
02-Datos/            escuela-*.json (fuente de verdad) · encuadres · perfiles
03-Fotografias/      <Escuela>/<Carrera>/<Carrera>.jpg   (vacía en el repo)
  _generadas/        fotos ya expandidas; es lo que consume el generador
06-Documentacion/    manual .docx
fuentes/             Montserrat, si no está instalada en el sistema
Gráficas Meta 2027/  salida, una carpeta por versión     (vacía en el repo)
Zonas seguras/       mapas de zonas                      (vacía en el repo)
```
