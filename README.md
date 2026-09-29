# Motor Gráfico · Meta IPG 2027

Generador automático de las gráficas de Meta (Instagram y Facebook) para la
Admisión IPG 2027. A partir de un JSON por escuela, una plantilla SVG y una
fotografía por carrera produce el **Post 1080×1080** y el **Story 1080×1920**
de cada carrera y sede.

Hoy son **43 carreras, 83 piezas y 166 gráficas** por versión.

> La documentación completa está en español en [`LEEME.md`](LEEME.md). Este
> archivo sólo resume cómo poner el motor en marcha en otra máquina.

## Cómo empezar

Necesitas una IA que trabaje en tu computador (Claude Code, Cursor o Copilot en
modo agente) y acceso a este repositorio. Para expandir fotos nuevas hace falta
Claude con el conector de Adobe (Firefly); con fotos ya expandidas sirve
cualquiera de ellas.

1. Conecta tu IA a tu cuenta de GitHub.
2. Pégale esto:

   ```text
   Instala el Motor Gráfico desde https://github.com/Lab-Design-Code/Motor-Grafico-V.0 siguiendo su archivo INSTALAR.md.
   ```

3. Cuando te lo pida, entrégale tus plantillas (Post y Story), tu base de datos
   de carreras (presencial u online) y las fotos: selecciona una carpeta propia
   o indícale un banco de imágenes (por ejemplo, Shutterstock) para que te
   recomiende imágenes o las descargue.
4. Pídele las gráficas, por ejemplo: «Genera las gráficas de Enfermería».
5. Revisa las piezas en la carpeta que te indique.

Las instrucciones técnicas que sigue la IA están en [`INSTALAR.md`](INSTALAR.md).

## Qué incluye el repositorio y qué no

La carpeta de trabajo pesa unos 5 GB. Casi todo eso son fotografías
licenciadas y gráficas terminadas, así que **no se versionan**. El
repositorio pesa unos pocos MB.

| Se versiona | No se versiona (ver `.gitignore`) |
|---|---|
| `00-Scripts/`: todo el pipeline en Python | fotografías `.jpg` de `03-Fotografias/` |
| `01-Plantillas/`: plantillas `.svg` de Post y Story | gráficas `.png`/`.svg` de `Gráficas Meta 2027/` |
| `02-Datos/`: JSON de escuelas, encuadres y perfiles | vistas previas `.png` y mapas de zonas seguras |
| `06-Documentacion/`: el manual `.docx` | `node_modules/`, `__pycache__/`, `.zip` |
| Briefs y LEEME de cada carpeta | fuentes `.otf` |
| | la base de datos de admisión (Excel): **la aporta cada institución** |
| La estructura de carpetas, vacía, con `.gitkeep` | |

## Puesta en marcha

```bash
git clone https://github.com/Lab-Design-Code/Motor-Grafico-V.0.git
cd Motor-Grafico-V.0
pip install -r requirements.txt
```

Además necesitas:

| Requisito | Cómo se configura |
|---|---|
| **Python 3.10 o superior** | |
| **Inkscape 1.x** | en el `PATH`, en la ruta estándar de Windows, o en la variable `INKSCAPE` |
| **Montserrat** Black, ExtraBold y Medium | archivos `.otf` **instalados en el sistema**: Inkscape dibuja el texto con las fuentes del sistema (ver [`fuentes/`](fuentes/LEEME.md)) |
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
fuentes/             Montserrat .otf para medir títulos (opcional)
Gráficas Meta 2027/  salida, una carpeta por versión     (vacía en el repo)
Zonas seguras/       mapas de zonas                      (vacía en el repo)
```
