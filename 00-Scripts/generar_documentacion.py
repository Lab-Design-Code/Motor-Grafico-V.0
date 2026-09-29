#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera 06-Documentacion/Documentacion_Graficas-Admision-IPG-2027.docx.

La documentacion se genera desde aqui y no se edita a mano, por la misma razon
que las graficas: asi hay una sola version y se puede rehacer.

    python 00-Scripts/generar_documentacion.py
"""
import os, sys, io
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(REPO, "06-Documentacion",
                    "Documentacion_Graficas-Admision-IPG-2027.docx")

AZUL = RGBColor(0x1E, 0x5F, 0xBF)
GRIS = RGBColor(0x55, 0x55, 0x55)
ROJO = RGBColor(0xB0, 0x2A, 0x2A)

d = Document()

s = d.sections[0]
s.page_width, s.page_height = 7772400, 10058400
s.left_margin = s.right_margin = Cm(2.2)
s.top_margin = s.bottom_margin = Cm(2.0)

normal = d.styles["Normal"]
normal.font.name = "Calibri"
normal.font.size = Pt(10.5)
normal.paragraph_format.space_after = Pt(6)
normal.paragraph_format.line_spacing = 1.15

for nombre, tam, color in (("Heading 1", 16, AZUL), ("Heading 2", 12.5, AZUL),
                           ("Heading 3", 11, GRIS)):
    st = d.styles[nombre]
    st.font.name = "Calibri"
    st.font.size = Pt(tam)
    st.font.color.rgb = color
    st.font.bold = True
    st.paragraph_format.space_before = Pt(14 if nombre == "Heading 1" else 10)
    st.paragraph_format.space_after = Pt(5)


def p(texto="", negrita=False, tam=None, color=None):
    par = d.add_paragraph()
    run = par.add_run(texto)
    run.bold = negrita
    if tam:
        run.font.size = Pt(tam)
    if color:
        run.font.color.rgb = color
    return par


def h1(t):
    return d.add_heading(t, level=1)


def h2(t):
    return d.add_heading(t, level=2)


def bullet(texto):
    par = d.add_paragraph(texto, style="List Bullet")
    par.paragraph_format.space_after = Pt(3)
    return par


def code(texto):
    par = d.add_paragraph()
    run = par.add_run(texto)
    run.font.name = "Consolas"
    run.font.size = Pt(9)
    par.paragraph_format.left_indent = Cm(0.6)
    par.paragraph_format.space_after = Pt(2)
    par.paragraph_format.line_spacing = 1.0
    return par


def _borde(celda):
    tcPr = celda._tc.get_or_add_tcPr()
    b = OxmlElement("w:tcBorders")
    for lado in ("top", "left", "bottom", "right"):
        e = OxmlElement("w:" + lado)
        e.set(qn("w:val"), "single")
        e.set(qn("w:sz"), "4")
        e.set(qn("w:color"), "BFBFBF")
        b.append(e)
    tcPr.append(b)


def _sombrear(celda, hexcolor):
    tcPr = celda._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), hexcolor)
    tcPr.append(shd)


def tabla(cabecera, filas, anchos=None):
    t = d.add_table(rows=1, cols=len(cabecera))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = t.rows[0].cells
    for i, c in enumerate(cabecera):
        hdr[i].text = ""
        run = hdr[i].paragraphs[0].add_run(c)
        run.bold = True
        run.font.size = Pt(9)
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        _sombrear(hdr[i], "1E5FBF")
        _borde(hdr[i])
    for fila in filas:
        cells = t.add_row().cells
        for i, v in enumerate(fila):
            cells[i].text = ""
            run = cells[i].paragraphs[0].add_run(str(v))
            run.font.size = Pt(9)
            _borde(cells[i])
    if anchos:
        for fila in t.rows:
            for i, w in enumerate(anchos):
                fila.cells[i].width = Cm(w)
    for fila in t.rows:
        for c in fila.cells:
            for par in c.paragraphs:
                par.paragraph_format.space_after = Pt(2)
                par.paragraph_format.line_spacing = 1.0
    d.add_paragraph().paragraph_format.space_after = Pt(4)
    return t


# ----------------------------------------------------------------- portada
tit = d.add_paragraph()
r = tit.add_run("AUTOMATIZACIÓN GRÁFICAS DE ADMISIÓN IPG 2027")
r.bold = True
r.font.size = Pt(22)
r.font.color.rgb = AZUL
tit.paragraph_format.space_after = Pt(4)

p("Generación estandarizada de Post e Historia por carrera — análisis del "
  "proceso manual y manual de operación del pipeline", tam=12, color=GRIS)
p("Proceso de diseño gráfico (Post-IPG 2027-Plantilla.svg / "
  "Story-IPG 2027-Plantilla.svg) rediseñado en seis módulos de automatización",
  tam=10, color=GRIS)
p()
p("Instituto Profesional IPG  ·  Admisión / Marketing", negrita=True)
p(r"Repositorio: C:\Users\IPG\Documents\Arieh\Diseño&Tenc-2027\IPG-2027\Meta IPG-2027",
  tam=9, color=GRIS)
p("Pipeline en versión 0.8  ·  Estado al 21 de septiembre de 2026  ·  "
  "Campaña completa y cerrada: 4 escuelas, 43 carreras, 83 piezas",
  negrita=True, color=AZUL)
p("Este documento cubre ÚNICAMENTE la campaña de Admisión IPG 2027 y el "
  "pipeline que la produjo. La versión genérica del motor, construida después "
  "para poder reutilizarlo con otras marcas, es un proyecto aparte y tiene su "
  "propia documentación en la carpeta hermana Motor-Graficas (README.md). Los "
  "dos no se mezclan: los scripts de esta carpeta no cambiaron.",
  tam=9, color=GRIS)

# --------------------------------------------------------------- 1. intro
h1("1. Introducción y estado del proyecto")
p("La generación de gráficas de admisión (Post cuadrado 1080×1080 e Historia "
  "vertical 1080×1920, una pieza por carrera + sede) era un proceso de Diseño "
  "Gráfico ejecutado pieza por pieza en Illustrator, repetido para cada "
  "combinación de carrera y sede de la campaña.")
p("Este documento está escrito para que cualquier persona —o cualquier máquina— "
  "pueda reproducir el resultado sin haber participado en las sesiones donde se "
  "construyó el pipeline. La Parte 1 analiza el proceso manual y deja las "
  "reglas por escrito; la Parte 2 es el manual de operación.")

p("La campaña está cerrada", negrita=True, color=AZUL)
tabla(["Escuela", "Carreras", "Piezas", "Archivos", "Estado"],
      [["Salud", "6", "14", "56", "Cerrada y verificada"],
       ["Educación y Desarrollo Social", "6", "23", "92",
        "Cerrada y verificada"],
       ["Gestión, Negocios y Marítima", "13", "19", "76",
        "Cerrada y verificada"],
       ["Ingeniería y Tecnología", "18", "27", "108",
        "Cerrada y verificada"],
       ["Total", "43", "83", "332 (166 PNG + 166 SVG)", "—"]],
      [5.6, 2.0, 1.8, 3.6, 3.6])

p("Cómo leer este documento según para qué se viene", negrita=True)
tabla(["Si lo que quiere es…", "Vaya a"],
      [["Generar una escuela nueva de principio a fin",
        "§5 — el procedimiento completo, comando por comando"],
       ["Elegir fotografías que sirvan",
        "§4.6 — la regla del 0,30, que es la que más cuesta aprender"],
       ["Entender por qué el encuadre es como es",
        "§4.3 y §4.4 — la fórmula y el solver"],
       ["Montar el entorno en otra máquina",
        "§5.0 y §3.9 — dependencias y rutas que hay que cambiar"],
       ["Saber qué hace cada script", "§3.9 — inventario completo"],
       ["Revisar qué se decidió y por qué",
        "§2.3 — las reglas de diseño y negocio"],
       ["No repetir un error conocido", "§6.1 — lo que se aprendió"]],
      [8.2, 8.0])

p("Qué cambió respecto de la versión 0.6", negrita=True)
p("La v0.6 documentaba una sola escuela cerrada. La v0.7 cierra las cuatro y "
  "agrega lo que se aprendió al escalar de 14 a 83 piezas:")
bullet("La regla del 0,30 (RN-28): el rostro no puede ocupar más de ~30 % del "
       "alto de la fotografía. Seis fotos a lo largo del proyecto hubo que "
       "reemplazarlas por esto, y es una condición de selección, no de "
       "calibración.")
bullet("La regla de redondeo quedó resuelta (RN-29): a la decena. Se dedujo "
       "del post de Ingeniería en Minas, que muestra $82.920 para un cálculo "
       "de $82.916,67.")
bullet("Tres scripts nuevos que aparecieron al escalar: asignación automática "
       "de rutas de foto, recogida de descargas en lote y hoja de contacto.")
bullet("Se corrigió un bug del solver que escribía siempre el mismo nombre de "
       "salida y hacía que resolver una escuela pisara los encuadres de otra.")

p("Estado de los módulos", negrita=True)
p("Los Módulos 2 (texto), 4 (fotografía), 5 (renderizado) y 6 (lote) están "
  "construidos y verificados sobre las cuatro escuelas. El Módulo 3 (selección "
  "de fotografía) sigue siendo un procedimiento asistido: la búsqueda está "
  "sistematizada pero el criterio es humano. El Módulo 1 (extracción automática "
  "del Excel) sigue pendiente; el JSON de escuela se arma a mano, una vez por "
  "escuela.")

# --------------------------------------------------- 2. parte 1 (analisis)
h1("2. Parte 1 — Análisis del proceso manual")

h2("2.1 Pasos que ejecutaba Diseño Gráfico (P1–P9)")
tabla(["#", "Proceso", "Naturaleza original", "Estado"],
      [["P1", "Duplicar la plantilla Illustrator para la carrera.",
        "Manual, un archivo por pieza", "Eliminado"],
       ["P2", "Escribir a mano prefijo, nombre de carrera y badges.",
        "Manual, sensible a errores de tipeo", "Automatizado"],
       ["P3", "Ajustar el subrayado y cortar el título a ojo si no cabe.",
        "Manual, a prueba y error", "Automatizado"],
       ["P4", "Calcular y escribir el % de beca y la cuota mensual.",
        "Manual", "Automatizado"],
       ["P5", "Escribir la sede y ajustar la pastilla.",
        "Manual", "Automatizado"],
       ["P6", "Buscar, evaluar y licenciar una fotografía.",
        "Manual, criterio visual sin regla escrita",
        "Semi-automatizado (asistido)"],
       ["P7", "Recortar y posicionar la fotografía evitando logo y texto.",
        "Manual, a prueba y error en Illustrator",
        "Automatizado — resuelto por solver (§4.4)"],
       ["P8", "Exportar cada pieza a PNG.", "Manual", "Automatizado (Inkscape)"],
       ["P9", "Repetir P1–P8 por cada carrera + sede.",
        "Manual, se repite desde cero cada campaña",
        "Automatizado por escuela (Módulo 6)"]],
      [1.0, 5.8, 4.4, 5.0])

h2("2.2 Requerimientos funcionales (RF-01 a RF-30)")
tabla(["Código", "Requerimiento funcional", "Estado"],
      [["RF-01", "Generar el SVG de una carrera a partir de un JSON de datos.",
        "Construido"],
       ["RF-02", "Autoajustar el ancho del subrayado al prefijo.", "Construido"],
       ["RF-03", "Autoajustar el tamaño de fuente y cortar el nombre a dos "
        "líneas balanceadas si no alcanza.", "Construido"],
       ["RF-04", "Quitar y recentrar los badges sobrantes (1 a 3 títulos).",
        "Construido"],
       ["RF-05", "Centrar el monto de la cuota en la pastilla, achicando la "
        "fuente si no cabe.", "Construido"],
       ["RF-06", "Ajustar el ancho de la pastilla de sede al texto real.",
        "Construido"],
       ["RF-07", "Incrustar la fotografía a sangre en el SVG (base64), "
        "reemplazando la plancha gris de la plantilla.", "Construido"],
       ["RF-08", "Reaplicar el degradado inferior para legibilidad del texto.",
        "Construido"],
       ["RF-09", "Aplicar un degradado superior propio para legibilidad del "
        "logo, sin importar el brillo de la foto.", "Construido"],
       ["RF-10", "Punto focal independiente para Post y para Story.",
        "Construido"],
       ["RF-11", "Sobre-escalar la foto más allá del mínimo que cubre el "
        "lienzo, sin perder cobertura.", "Construido"],
       ["RF-12", "Expandir el lienzo de la foto a los lados y hacia arriba.",
        "Construido"],
       ["RF-13", "Usar la misma fotografía en Post y Story de una carrera.",
        "Construido"],
       ["RF-14", "Generar el mapa de zonas seguras superpuesto.",
        "Construido — incluye silueta"],
       ["RF-15", "Ejecutarse por carrera individual sin depender del lote.",
        "Construido"],
       ["RF-16", "Extraer automáticamente los datos desde el Excel.",
        "Pendiente — el JSON se arma por escuela"],
       ["RF-17", "Expandir el lienzo hacia abajo, para subir al sujeto sin "
        "agrandarlo cuando va anclado al borde inferior.", "Construido"],
       ["RF-18", "Resolver el encuadre por búsqueda sobre las restricciones de "
        "zona segura.", "Construido"],
       ["RF-19", "Generar una escuela completa en una sola corrida.",
        "Construido"],
       ["RF-20", "Propagar foto y encuadre a todas las sedes de una carrera.",
        "Construido"],
       ["RF-21", "Purgar versiones anteriores y caché obsoleto.", "Construido"],
       ["RF-22", "Separar la entrega por escuela, carrera, modalidad y sede.",
        "Construido"],
       ["RF-23", "Medir la posición real del título renderizando la pieza sin "
        "foto, en vez de estimarla.", "Construido"],
       ["RF-24", "Leer pelo, mentón y centro de la cabeza sobre una grilla "
        "ampliada en centésimas.", "Construido"],
       ["RF-25", "Emitir el SVG editable junto al PNG cuando se pide.",
        "Construido"],
       ["RF-26", "Regenerar esta documentación desde un script.", "Construido"],
       ["RF-27", "Escribir automáticamente la ruta de foto de cada carrera en "
        "el JSON de escuela.", "Construido — 15-09-2026"],
       ["RF-28", "Recoger varias descargas seguidas y repartirlas por carrera "
        "en orden, sin alternar navegador y consola en cada foto.",
        "Construido — 15-09-2026"],
       ["RF-29", "Montar las piezas de una escuela en una hoja de contacto "
        "para verificarlas de un vistazo.", "Construido — 15-09-2026"],
       ["RF-30", "Derivar el nombre del archivo de encuadres del JSON de "
        "entrada, para que una escuela no pise a otra.",
        "Construido — 15-09-2026, corrección de bug"]],
      [1.8, 10.4, 4.0])

h2("2.3 Reglas de diseño y negocio (RN-01 a RN-31)")
p("Son independientes de la implementación: si el pipeline se reescribe en otro "
  "lenguaje, estas reglas se mantienen.")
tabla(["Código", "Regla", "Estado"],
      [["RN-01", "El <text> de las plantillas se reescribe con un único <tspan "
        "x=\"0\" y=\"0\">: se pierde el kerning de Illustrator, el resultado es "
        "idéntico a la vista.", "Confirmada"],
       ["RN-02", "El font-size de la clase CSS tiene prioridad sobre el "
        "atributo del <text>. Hay que fijarlo con style=\"font-size:Npx\" "
        "inline o el cambio se ignora.", "Confirmada — costó descubrirla"],
       ["RN-03", "Zona de logo — ningún elemento de la foto puede caer en Post "
        "x 20–700 / y 20–185 · Story x 40–720 / y 70–240.",
        "Confirmada — la más estricta"],
       ["RN-04", "Zona de texto — desde Post y≥440 / Story y≥740 la foto puede "
        "quedar cubierta, pero el rostro completo debe quedar sobre esa franja.",
        "Confirmada"],
       ["RN-05", "Banda de rostros — Post y 200–430 · Story y 270–700.",
        "Confirmada"],
       ["RN-06", "Resolución mínima de foto — ancho ≥2160px.", "Confirmada"],
       ["RN-07", "La foto no debe tener fondo plano en la franja detrás del "
        "logo o del texto: debe tener profundidad, nunca fondo de estudio.",
        "Confirmada"],
       ["RN-08", "Fórmula de encuadre (cover con zoom). La dimensión que gana "
        "el max() queda sin holgura.", "Confirmada"],
       ["RN-09", "Límite físico — el alto de la cabeza por la escala final no "
        "puede superar el hueco entre la zona de logo y la de texto.",
        "Confirmada"],
       ["RN-10", "Expansión de lienzo — se estira y difumina una tira del "
        "borde, nunca se genera contenido con IA. Orden fijo lados → arriba → "
        "abajo, y cada fracción sobre el tamaño en ese punto de la cadena.",
        "Confirmada"],
       ["RN-11", "El punto focal y el zoom son independientes por formato.",
        "Confirmada"],
       ["RN-12", "Criterio de selección — retrato individual cintura-arriba, "
        "ambiente de la carrera desenfocado detrás, sin brazos levantados del "
        "lado izquierdo, mirando a cámara.", "Confirmada"],
       ["RN-13", "Las fotos se descargan en la resolución máxima licenciada.",
        "Confirmada"],
       ["RN-14", "Una gráfica por carrera + sede, agrupando los niveles de una "
        "misma disciplina en hasta 3 badges bajo el prefijo del nivel superior "
        "— Técnico, Profesional y Plan Continuidad conviven en la misma pieza.",
        "Confirmada — ejercitada en Gestión e Ingeniería"],
       ["RN-15", "Tipo de título derivado del nombre: «PLAN CONTINUIDAD» → Plan "
        "Continuidad · «TÉCNICO DE NIVEL SUPERIOR» o «TÉCNICO EN» → Título "
        "Técnico · el resto → Título Profesional.", "Confirmada"],
       ["RN-16", "Cuando hay más de una jornada o más de un nivel con cuotas "
        "distintas se usa la más baja, porque la plantilla dice «Cuotas desde».",
        "Aplicada en las 4 escuelas — pendiente de confirmación formal"],
       ["RN-17", "Calibración del Post anclado abajo — expandir_abajo sube al "
        "sujeto sin agrandarlo; si la cabeza invade la zona de logo se compensa "
        "con más expandir_lados.", "Confirmada"],
       ["RN-18", "Zona de silueta — el sujeto va dentro de Post x 600–960 / y "
        "210–1080 · Story x 445–1015 / y 305–1920. Está corrida a la derecha "
        "para dejar libre el margen izquierdo.", "Confirmada"],
       ["RN-19", "Título de dos líneas — sube el bloque completo una interlínea "
        "(~73px Post, ~85px Story) y el techo del mentón baja otro tanto.",
        "Confirmada"],
       ["RN-20", "expandir_lados es lo único que da recorrido horizontal. Sin "
        "ancho sobrante el clamp deja la cabeza contra el borde izquierdo.",
        "Confirmada"],
       ["RN-21", "Una foto por carrera, compartida por todas sus sedes.",
        "Decidida por el usuario"],
       ["RN-22", "Sujeto único — cuando la foto trae más de una persona se "
        "elige una. El punto medio parte a la otra contra el borde.",
        "Confirmada"],
       ["RN-23", "El entregable es el PNG; el SVG se emite junto a él con "
        "--con-svg. Windows oculta las extensiones, así que el par se ve como "
        "dos archivos del mismo nombre.", "Confirmada"],
       ["RN-24", "La entrega se separa por escuela, carrera, modalidad y sede. "
        "Presencial y Online son campañas distintas.", "Confirmada"],
       ["RN-25", "Las medidas del rostro se leen sobre una grilla ampliada en "
        "centésimas, nunca se estiman sobre una miniatura. Un error de 0,05 del "
        "alto son ~50px en el lienzo.", "Confirmada"],
       ["RN-26", "Aire mínimo entre mentón y título: 70px en Post y 90px en "
        "Story; 50 y 70 cuando el título va a dos líneas.", "Confirmada"],
       ["RN-27", "Tope de 180 megapíxeles para la foto expandida.",
        "Confirmada"],
       ["RN-28", "El rostro no puede ocupar más de ~30 % del alto de la "
        "fotografía. En el Post la ventana vertical entre la zona de logo y el "
        "título es de 190px sobre 1080, así que un primer plano no tiene "
        "solución a ninguna combinación de expansiones.",
        "Confirmada — 15-09-2026, seis fotos reemplazadas"],
       ["RN-29", "Redondeo de la cuota mensual: a la decena. $82.916,67 → "
        "$82.920 y $70.833,33 → $70.830.",
        "Resuelta — deducida del post de Ingeniería en Minas"],
       ["RN-30", "Las filas del Excel con código «NUEVA» o «NUEVA EN SEDE» no "
        "traen prefijo de sede: se asignan por el bloque de sede donde están en "
        "la hoja.", "Confirmada — 15-09-2026"],
       ["RN-31", "Cuando el nombre de la carrera no admite el prefijo de la "
        "plantilla («Ingeniería en», «Técnico de Nivel Superior en») se usa "
        "«Carrera Profesional de». Afecta a Psicopedagogía, Contador Auditor, "
        "Administración Pública, Construcción Civil e Ingeniería Industrial.",
        "Aplicada — pendiente de confirmación"]],
      [1.8, 10.4, 4.0])

h2("2.4 Riesgos: estado actual")
tabla(["Riesgo", "Estado"],
      [["Desborde de texto fuera del lienzo.",
        "Eliminado — auto-fit con métricas reales de fuente."],
       ["La fotografía tapa el logo o el título.",
        "Eliminado — el solver no devuelve un encuadre que viole las zonas; si "
        "no hay solución, lo dice."],
       ["El texto queda pegado al mentón aunque el encuadre «cumpla».",
        "Eliminado — RN-25 (medir, no estimar) y RN-26 (aire suficiente)."],
       ["Elegir una fotografía que después no tiene encuadre posible.",
        "Mitigado — RN-28 da el criterio al elegir. El solver lo detecta, pero "
        "para entonces la descarga ya se gastó."],
       ["Fondo plano detrás del logo o del texto.",
        "Mitigado — RN-07 como criterio de selección, sin verificación "
        "automática."],
       ["Dependencia de una sola persona.",
        "Eliminado para texto, encuadre y render. Sigue en la selección de "
        "fotografía (P6)."],
       ["SVG de 15–30 MB acumulándose en la carpeta de entrega.",
        "Controlado — el SVG sólo se emite con --con-svg (RN-23)."],
       ["Foto expandida tan grande que Pillow la rechaza.",
        "Eliminado — tope de 180 MP en el solver (RN-27)."],
       ["Resolver una escuela pisa los encuadres de otra.",
        "Eliminado — el nombre de salida se deriva del de entrada (RF-30)."],
       ["Inkscape devuelve exit code 0 sin escribir el PNG.",
        "Eliminado — se invoca por lista de argumentos desde Python."]],
      [7.6, 8.6])

# ------------------------------------------------------- 3. parte 2 pipeline
h1("3. Parte 2 — El pipeline")
p("Seis módulos independientes, encadenados en el orden en que se ejecutan.")

h2("3.1 Alcance: los seis módulos")
tabla(["Módulo", "Reemplaza", "Entrega", "Estado"],
      [["M1 — Datos (Excel → JSON)", "P1",
        "Un JSON por escuela con todas sus carreras y sedes",
        "Pendiente — se arma a mano"],
       ["M2 — Generador de texto", "P1–P5",
        "SVG con el texto puesto y autoajustado", "Construido"],
       ["M3 — Selección de fotografía", "P6",
        "Una fotografía por carrera en máxima resolución",
        "Semi-automatizado"],
       ["M4 — Capa de fotografía", "P7",
        "SVG con la foto incrustada, expandida y encuadrada", "Construido"],
       ["M5 — Renderizado a PNG", "P8", "PNG listo para publicar", "Construido"],
       ["M6 — Orquestación de lote", "P9",
        "Una escuela completa, ordenada por carrera, modalidad y sede",
        "Construido"]],
      [4.2, 2.4, 5.6, 4.0])

h2("3.2 Módulo 1 — Datos (Excel → JSON de escuela)")
p("Pendiente como script. El JSON se arma leyendo las hojas «OA Presencial» y "
  "«OA Online 27» de «Documento Admisión 2027 (1).xlsx».")
p("Tres cosas que hay que saber para construirlo", negrita=True)
bullet("La sede sale del prefijo del código de carrera: AR Arauco, CC "
       "Concepción, LU La Unión, PG Panguipulli. La modalidad sale de la sede: "
       "la única virtual es «Sede Online».")
bullet("Las filas con código «NUEVA» o «NUEVA EN SEDE» no traen prefijo. Hay "
       "que asignarlas por el bloque de sede donde están en la hoja, que se "
       "reconoce por las filas de encabezado repetidas (RN-30).")
bullet("Los niveles de una misma disciplina se agrupan en una pieza con badges "
       "(RN-14), y la cuota que se muestra es la más baja de las agrupadas "
       "(RN-16).")

h2("3.3 Módulo 2 — Generador de texto")
code(r"00-Scripts\generar_graficas_ipg.py")
bullet("Prefijo y subrayado: reemplaza el texto y recalcula el ancho del "
       "subrayado con métricas reales de la fuente (RN-01, RN-02).")
bullet("Nombre: si no entra en el ancho máximo (1011px Post / 968px Story) "
       "achica la fuente hasta el 82%; si aún no entra, corta en dos líneas "
       "balanceadas y sube el bloque una interlínea (RN-19).")
bullet("Badges: centra el texto en cada pastilla y elimina las sobrantes.")
bullet("Beca y cuota: formatea con separador de miles y centra en la pastilla.")
bullet("Sede: reemplaza el texto y ajusta el ancho de la pastilla.")

h2("3.4 Módulo 3 — Selección y descarga de fotografía")
p("No hay script: es un procedimiento asistido, en §5.2. Es el único paso del "
  "pipeline donde el criterio sigue siendo humano.")
p("Revisar sin gastar descargas", negrita=True)
p("Las miniaturas con marca de agua («…-260nw-<id>.jpg») son públicas. Se bajan "
  "varias, se montan en una hoja de contacto y se elige sobre ella. En las "
  "cuatro escuelas se revisaron unas 150 candidatas y se descargaron 43.")
p("Filtros de URL que funcionan", negrita=True)
p("image_type=photo · orientation=horizontal · mreleased=true · age=20s (un "
  "solo valor: la lista separada por comas descarta todo) · ethnicity=hispanic, "
  "que es el metadato propio de Shutterstock para perfil latinoamericano.")
p("Descarga", negrita=True)
p("El botón «Descargar» funciona con plan activo. Brave deja el archivo como "
  ".tmp sin renombrarlo aunque esté completo: hay que recogerlo buscando el "
  "JPEG más reciente y validándolo al abrirlo, no por la extensión.")

h2("3.5 Módulo 4 — Capa de fotografía y expansión de lienzo")
code(r"00-Scripts\capa_fotos_ipg.py")
bullet("Si el JSON pide expansión, genera la foto expandida aplicando lados → "
       "arriba → abajo y la cachea en 03-Fotografias\\_expandidas\\.")
bullet("Calcula escala y desplazamiento con la fórmula cover + zoom + foco.")
bullet("Reemplaza el grupo de fotos de la plantilla por la foto incrustada.")
bullet("Elimina la plancha gris que tapa la capa de fotos.")
bullet("Reaplica el degradado inferior y agrega uno superior propio.")
bullet("Dibuja el mapa de zonas seguras, incluida la silueta, para verificar.")

h2("3.6 Módulo 5 — Renderizado a PNG")
p("Inkscape 1.4.4 en línea de comandos, invocado desde Python por lista de "
  "argumentos — nunca por shell. La ruta del repositorio tiene espacios, «&» y "
  "«ñ»: pasada por shell sin entrecomillar, Inkscape interpreta cada fragmento "
  "como un archivo distinto, aborta y devuelve 0 igual, sin escribir el PNG.")

h2("3.7 Módulo 6 — Orquestación de lote")
code(r"00-Scripts\lote_graficas_ipg.py")
bullet("Importa el generador de texto y la capa de fotografía en memoria, sin "
       "archivos intermedios entre módulos.")
bullet("Escribe el SVG en temporal, lo rasteriza y lo borra, salvo que se pida "
       "--con-svg (RN-23).")
bullet("Ordena la salida por carrera, modalidad y sede (RN-24).")

h2("3.8 Antes y después")
tabla(["Aspecto", "Proceso manual", "Proceso automatizado"],
      [["Nombre, badges, beca, cuota, sede", "Tipeo manual por pieza",
        "Generado desde el JSON de escuela"],
       ["Ajuste de tamaño de título", "A ojo, prueba y error",
        "Automático, con métricas reales de fuente"],
       ["Selección de fotografía", "Búsqueda manual sin criterio escrito",
        "Búsqueda asistida con hoja de contacto y criterio documentado"],
       ["Medición del rostro", "No se medía",
        "Grilla en centésimas sobre recorte ampliado (RN-25)"],
       ["Encuadre de la fotografía", "Recorte y posicionamiento a mano",
        "Resuelto por solver sobre tres restricciones"],
       ["Verificación de zonas seguras", "Visual, sin referencia",
        "Mapa de zonas superpuesto, incluida la silueta"],
       ["Verificación de la escuela", "Abrir los PNG uno por uno",
        "Hoja de contacto con una pieza por carrera"],
       ["Exportación a PNG", "Manual desde Illustrator",
        "Automática vía Inkscape, con verificación de archivo"],
       ["Repetición por escuela", "Se repite todo a mano",
        "Una corrida por escuela"],
       ["Documentación", "Se escribía a mano y quedaba desfasada",
        "Se regenera desde generar_documentacion.py"]],
      [4.6, 5.4, 6.2])

h2("3.9 Inventario de scripts")
tabla(["Script", "Qué hace", "Cuándo se corre"],
      [["generar_graficas_ipg.py", "Módulo 2: el texto de una pieza.",
        "Lo llama el lote; rara vez directo"],
       ["capa_fotos_ipg.py",
        "Módulo 4: expansión, encuadre, degradados y mapa de zonas.",
        "Lo llama el lote"],
       ["grilla_fina.py",
        "Dibuja centésimas sobre un recorte ampliado, para leer pelo, mentón y "
        "centro de la cabeza.", "Una vez por foto nueva (§5.3)"],
       ["medir_titulo.py",
        "Renderiza cada pieza sin foto y mide en qué Y empieza el título.",
        "Una vez por escuela (§5.3)"],
       ["solver_encuadre.py",
        "Resuelve expansiones y punto focal contra las zonas seguras.",
        "Cada vez que cambian las medidas"],
       ["aplicar_encuadres.py",
        "Vuelca los encuadres resueltos al JSON de escuela.",
        "Después del solver"],
       ["asignar_fotos.py",
        "Escribe la ruta de foto de cada carrera en el JSON.",
        "Después de descargar las fotos"],
       ["propagar_fotos.py",
        "Copia foto y encuadre a todas las sedes de cada carrera.",
        "Después de asignar fotos"],
       ["recoger_descargas.py",
        "Recoge varias descargas y las reparte por carrera en orden.",
        "Después de una tanda de descargas"],
       ["lote_graficas_ipg.py",
        "Módulo 6: genera la escuela completa.", "El comando principal"],
       ["hoja_contacto.py",
        "Monta las piezas de una escuela en una sola hoja.",
        "Para verificar (§5.6)"],
       ["limpiar_versiones.py",
        "Purga carpetas de trabajo y caché obsoleto.", "Al cerrar una escuela"],
       ["generar_documentacion.py", "Regenera este documento.",
        "Cuando cambia el pipeline"]],
      [4.4, 7.4, 4.4])

# ------------------------------------------------- 4. datos y encuadre
h1("4. Esquema de datos y encuadre")

h2("4.1 Los cuatro archivos por escuela")
tabla(["Archivo", "Qué contiene", "Quién lo escribe"],
      [["02-Datos\\escuela-<x>.json",
        "Todas las carreras y sedes: textos, beca, cuota, foto y encuadre. Es "
        "la única fuente de verdad del lote.",
        "A mano desde el Excel, más lo que inyectan los scripts"],
       ["02-Datos\\medidas-<x>.json",
        "Tres medidas por foto y el Y del título en cada formato.",
        "A mano con grilla_fina.py; el título lo escribe medir_titulo.py"],
       ["02-Datos\\titulos-<x>.json",
        "Y donde empieza el título de cada carrera, por formato.",
        "medir_titulo.py"],
       ["02-Datos\\encuadres-<x>.json",
        "Expansiones y punto focal resueltos por carrera.",
        "solver_encuadre.py; no se edita a mano"]],
      [4.6, 7.0, 4.6])
p("Las cuatro escuelas del proyecto usan los sufijos salud, educacion, gestion "
  "e ingenieria.", tam=9.5, color=GRIS)

h2("4.2 El JSON de escuela — campo por campo")
code('{')
code('  "escuela": "Escuela de Salud",')
code('  "carreras": [')
code('    {')
code('      "carpeta": "Enfermeria",')
code('      "slug": "Enfermeria-Panguipulli",')
code('      "prefijo": "Técnico de Nivel Superior en",')
code('      "nombre": "ENFERMERÍA",')
code('      "badges": ["Título Técnico"],')
code('      "beca": 40,')
code('      "cuota": 115000,')
code('      "sede": "Sede Panguipulli",')
code('      "foto": "Escuela de Salud/Enfermeria/Enfermeria.jpg",')
code('      "expandir_lados_post": 1.9,')
code('      "expandir_arriba_post": 0.22,')
code('      "expandir_abajo_post": 0.18,')
code('      "focal_post": [0.4655, 1, 0.7222, 1],')
code('      "focal_story": [0.4467, 0, 0.6759, 0]')
code('    }')
code('  ]')
code('}')
p()
tabla(["Campo", "Obligatorio", "Descripción"],
      [["escuela", "Sí", "Nombre de la carpeta de escuela en la entrega."],
       ["carpeta", "Sí", "Carpeta de la carrera. Agrupa sus sedes y es la clave "
        "con que se propagan foto y encuadre."],
       ["slug", "Sí", "Identificador de archivo, sin espacios ni tildes."],
       ["prefijo", "Sí", "Define el ancho del subrayado. Puede variar entre "
        "sedes de la misma carrera si cambia el nivel que se dicta."],
       ["nombre", "Sí", "Nombre en mayúsculas, con tildes. Se autoajusta a una "
        "o dos líneas."],
       ["badges", "Sí", "1 a 3 textos de tipo de título."],
       ["beca", "Sí", "Porcentaje: 40 presencial, 50 online."],
       ["cuota", "Sí", "Monto mensual sin puntos ni signo, redondeado a la "
        "decena (RN-29)."],
       ["sede", "Sí", "De aquí salen la modalidad y la carpeta de destino."],
       ["foto", "Si hay foto",
        "Ruta relativa dentro de 03-Fotografias. La escribe asignar_fotos.py."],
       ["focal_post / focal_story", "No",
        "[fx, fy, fx_destino, fy_destino]. Lo escribe el solver."],
       ["expandir_lados / _arriba / _abajo (_post, _story)", "No",
        "Fracciones de expansión. Las escribe el solver."],
       ["_codigo, _notas, _supuestos_a_confirmar", "No",
        "Campos con guion bajo: documentación interna, el pipeline los ignora."]],
      [4.8, 2.2, 9.2])

h2("4.3 Fórmula de encuadre (cover con zoom y foco)")
p("Dada una foto de nw×nh px y un lienzo de cw×ch px:")
code("escala = max(cw / nw, ch / nh) × zoom")
code("sw, sh = nw × escala, nh × escala")
code("tx = cw × fx_destino − sw × fx")
code("ty = ch × fy_destino − sh × fy")
code("tx = min(0, max(cw − sw, tx))    ← recorte, nunca deja huecos")
code("ty = min(0, max(ch − sh, ty))")
p()
p("fx y fy son la fracción del punto de la FOTO que se usa como referencia; "
  "fx_destino y fy_destino, la fracción del LIENZO donde debe caer ese punto.")
p("Consecuencia práctica: si fx es el centro horizontal de la cabeza, entonces "
  "fx_destino es directamente la posición de la cabeza en el lienzo dividida "
  "por su ancho. Eso permite apuntar a la silueta sin tanteo.")
p("Los dos clamps son la razón de RN-20: para llevar la cabeza a la silueta hay "
  "que correr la foto a la derecha, y eso exige ancho sobrante. Si no sobra, el "
  "clamp deja tx en 0 y la cabeza se queda contra el borde.")

h2("4.4 El solver de encuadre")
code(r"00-Scripts\solver_encuadre.py")
p("Recorre las combinaciones de expansión, replica la aritmética exacta de "
  "capa_fotos_ipg.py —incluidos los int() de cada expansión, que redondean "
  "hacia abajo y corren el resultado varios píxeles— y se queda con la que "
  "cumple las restricciones:")
tabla(["Restricción", "Post 1080×1080", "Story 1080×1920"],
      [["Tope del pelo o del casco, bajo la zona de logo", "y ≥ 205", "y ≥ 300"],
       ["Mentón, con aire suficiente bajo el título (RN-26)",
        "título − 70", "título − 90"],
       ["Ídem cuando el título va a dos líneas", "título − 50", "título − 70"],
       ["Cabeza dentro de la silueta (RN-18)", "x 600–960", "x 445–1015"],
       ["Tamaño de la foto expandida (RN-27)", "≤ 180 MP", "≤ 180 MP"]],
      [7.2, 4.4, 4.6])
p("El orden de preferencia es explícito y no trivial: primero centra la cabeza "
  "en la silueta, y sólo entre los encuadres centrados maximiza la escala. "
  "Maximizar la escala a secas admite soluciones donde la cara apenas entra por "
  "el borde izquierdo de la caja, válidas pero descentradas.")
p("Si no hay solución, el solver lo dice en vez de entregar un encuadre que "
  "viole una zona. Eso convierte a RN-03 y RN-04 en garantías y no en "
  "recomendaciones — y es lo que detecta las fotografías que no sirven.")

h2("4.5 El techo del mentón se mide, no se estima")
code(r"00-Scripts\medir_titulo.py")
p("El techo depende del largo del nombre: si no cabe en una línea, el generador "
  "parte el título y sube el bloque una interlínea calculada sobre el cuerpo ya "
  "autoajustado, que también varía.")
p("El script renderiza cada pieza SIN foto —el fondo es la plancha gris #606060 "
  "de la plantilla, así que el texto blanco se separa sin ambigüedad— y busca "
  "el primer píxel del título. En la práctica sólo da dos valores por formato:")
tabla(["Caso", "Título en Post", "Título en Story"],
      [["Nombre que entra en una línea", "y 465", "y 763"],
       ["Nombre que se parte en dos líneas", "y 391", "y 678 – 692"]],
      [8.0, 4.0, 4.2])

h2("4.6 La regla del 0,30 — el criterio al elegir la fotografía")
p("Es la regla que más cuesta aprender y la que más descargas cuesta ignorar.",
  negrita=True, color=ROJO)
p("En el Post la ventana vertical útil va del borde inferior de la zona de "
  "logo (205) al techo del mentón (395 con título de una línea): 190 px sobre "
  "un lienzo de 1080. Como la foto se escala para cubrir el lienzo, el rostro "
  "ocupa en el lienzo la misma fracción del alto que ocupaba en la foto, "
  "dividida por la expansión vertical que se aplique.")
code("expansión necesaria  ≥  fracción_del_rostro × 1080 / 190")
p("Con un rostro al 20 % del alto basta una expansión de 1,14. Al 30 % hace "
  "falta 1,71. Al 40 % hace falta 2,27 — la foto tendría que más que duplicar "
  "su alto en relleno difuminado, y en general el tope de 180 MP o la "
  "restricción del pelo lo impiden antes.")
p("En la práctica: si el rostro pasa de ~30 % del alto, la foto no sirve. Es un "
  "primer plano, y además viola RN-12, que pide plano de medio cuerpo.")
p("Costó seis fotografías a lo largo del proyecto", negrita=True)
tabla(["Foto", "Escuela", "Por qué falló"],
      [["Educación Parvularia (la del piloto)", "Educación",
        "Rostro al 28,5 % de una foto vertical: sin solución en Post"],
       ["Dos fotos de puerto", "Gestión",
        "Rostro al 57 % del alto — primeros planos"],
       ["Construcción Civil, Gestión de Seguridad, Programación, IA",
        "Ingeniería", "Rostro entre 33 % y 50 %: cuatro SIN SOLUCIÓN"]],
      [6.0, 3.4, 6.8])

h2("4.7 Las medidas del rostro también se miden")
code(r"00-Scripts\grilla_fina.py")
p("Dibuja centésimas del alto sobre un recorte ampliado de la zona del rostro. "
  "Ahí se leen los tres puntos que necesita el solver: tope del pelo —o del "
  "casco, cuando lo hay, porque es lo que no puede entrar en la zona de logo—, "
  "mentón y centro horizontal de la cabeza.")
p("No sirve estimarlos sobre una miniatura: las seis fotos de Salud se midieron "
  "primero sobre miniaturas de 560px y las seis quedaron mal (RN-25). "
  "Enfermería es el caso extremo: tenía anotado mentón 0,13 cuando el real es "
  "0,30 — unos 1.300px de diferencia sobre una foto de 7.787px de alto.")

# ------------------------------------------------------- 5. procedimiento
h1("5. Procedimiento — generar una escuela completa")

h2("5.0 Entorno (una sola vez por máquina)")
bullet("Python 3.12 con fonttools, Pillow, openpyxl y python-docx.")
bullet("Inkscape 1.4.4 o superior.")
bullet("Fuentes Montserrat Black y Medium instaladas.")
bullet("Sesión iniciada en una cuenta Shutterstock con plan activo.")
p("Rutas que hay que cambiar al mover de máquina", negrita=True, color=ROJO)
tabla(["Archivo", "Qué tiene fija", "Valor actual"],
      [["generar_graficas_ipg.py", "Rutas de las fuentes Montserrat",
        "C:\\Users\\IPG\\AppData\\Local\\Microsoft\\Windows\\Fonts\\"],
       ["lote_graficas_ipg.py", "Ruta de Inkscape",
        "C:\\Program Files\\Inkscape\\bin\\inkscape.exe"],
       ["medir_titulo.py", "Ruta de Inkscape", "ídem"]],
      [4.6, 5.0, 6.6])
p("Los demás scripts resuelven sus rutas a partir de su propia ubicación, así "
  "que basta mover la carpeta completa.", tam=9.5, color=GRIS)

h2("5.1 Armar el JSON de escuela")
p("Leer las hojas «OA Presencial» y «OA Online 27» del Excel y escribir "
  "02-Datos\\escuela-<x>.json con una entrada por carrera + sede. Aplicar "
  "RN-14, RN-15, RN-16, RN-29, RN-30 y RN-31. Anotar en "
  "«_supuestos_a_confirmar» todo nombre de marketing que se haya reescrito.")

h2("5.2 Conseguir una fotografía por carrera")
bullet("Buscar en Shutterstock con términos de la carrera más «retrato» y pose "
       "cintura-arriba, con los filtros de §3.4.")
bullet("Extraer del listado los identificadores y las URL de miniatura, bajar "
       "las miniaturas y montarlas en una hoja de contacto. Elegir sobre esa "
       "hoja, no abriendo fichas una por una.")
bullet("Verificar contra RN-06, RN-07, RN-12, RN-22 y sobre todo RN-28 —la "
       "regla del 0,30— antes de descargar.")
bullet("Descargar todas seguidas y recogerlas después en orden:")
code(r'python 00-Scripts\recoger_descargas.py "<Escuela>" Carrera1 Carrera2 ...')

h2("5.3 Medir")
p("Este es el paso donde se juega el resultado. Las dos mediciones son "
  "independientes y ambas son obligatorias.")
code(r'python 00-Scripts\grilla_fina.py "<Escuela>" <Carrera> salida.jpg 0.0 0.55')
p("Abrir la imagen resultante y leer pelo, mentón y centro horizontal de la "
  "cabeza. Anotarlos en 02-Datos\\medidas-<x>.json.")
code(r"python 00-Scripts\medir_titulo.py 02-Datos\escuela-<x>.json")
p("Escribe 02-Datos\\titulos-<x>.json. Copiar titulo_post y titulo_story a "
  "medidas-<x>.json.")

h2("5.4 Resolver y aplicar")
code(r"python 00-Scripts\solver_encuadre.py 02-Datos\medidas-<x>.json")
code(r"python 00-Scripts\aplicar_encuadres.py 02-Datos\escuela-<x>.json 02-Datos\encuadres-<x>.json")
code(r"python 00-Scripts\asignar_fotos.py 02-Datos\escuela-<x>.json")
code(r"python 00-Scripts\propagar_fotos.py 02-Datos\escuela-<x>.json")
p("Si el solver devuelve SIN SOLUCIÓN para alguna carrera, la fotografía no "
  "sirve: hay que reemplazarla (§4.6), no forzar los parámetros.")

h2("5.5 Generar")
code(r"python 00-Scripts\lote_graficas_ipg.py 02-Datos\escuela-<x>.json")
p("Agregar --con-svg si se quiere el editable junto a cada PNG.")

h2("5.6 Verificar")
code(r'python 00-Scripts\hoja_contacto.py "<Escuela>" Post salida.jpg')
p("Confirmar sobre la hoja que ningún elemento de la foto entra en la zona de "
  "logo, que el rostro cae en la banda y dentro de la silueta, que hay aire "
  "visible entre el mentón y el título, y que el fondo detrás del logo y del "
  "texto no es plano.")
p("Si algo falla, corregir la medida en medidas-<x>.json y volver a §5.4. No "
  "editar los parámetros de encuadre a mano: se pierde la trazabilidad entre la "
  "medida y el resultado, y la próxima corrida del solver los pisa.")

h2("5.7 Limpiar")
code(r"python 00-Scripts\limpiar_versiones.py 02-Datos\escuela-<x>.json --borrar")
p("Sin --borrar sólo informa qué eliminaría.")

h2("5.8 Estructura de la entrega")
code("Gráficas Meta 2027/")
code("  <Escuela>/")
code("    <Carrera>/")
code("      Presencial/")
code("        <Sede>/")
code("          Post-IPG_2027-<Carrera>-<Sede>.png    1080×1080")
code("          Story-IPG_2027-<Carrera>-<Sede>.png   1080×1920")
code("      Online/")
code("          Post-IPG_2027-<Carrera>-Online.png")
code("          Story-IPG_2027-<Carrera>-Online.png")
p()
p("Online no abre un nivel de sede porque sólo tiene una. Las sedes no son "
  "versiones: cambia la pastilla y a veces la cuota.")

# ------------------------------------------------------------- 6. resumen
h1("6. Resumen del estado")
bullet("9 procesos (P1–P9): todos automatizados salvo P6, que es asistido.")
bullet("30 requerimientos funcionales: 29 construidos, 1 pendiente (RF-16).")
bullet("31 reglas de diseño y negocio: todas confirmadas salvo RN-16 y RN-31, "
       "aplicadas pero pendientes de confirmación formal.")
bullet("6 módulos: M1 pendiente · M3 semi-automatizado · M2, M4, M5 y M6 "
       "construidos y verificados sobre las cuatro escuelas.")
bullet("4 escuelas cerradas: 43 carreras, 83 piezas, 332 archivos.")
bullet("Entrega respaldada y verificada el 21-09-2026: copia completa en "
       r"C:\Users\IPG\Documents\Arieh\_Respaldos\IPG-2027_2026-09-21, con los "
       "1.169 archivos comprobados uno a uno por hash (hashes.md5 permite "
       "repetir la comprobación).")
bullet("Los scripts de esta carpeta quedaron congelados tal como produjeron la "
       "campaña. Las mejoras posteriores se hicieron en un proyecto aparte "
       "(§6.2) para no alterar lo que ya está aprobado.")

h2("6.1 Lo que se aprendió — errores que no conviene repetir")
p("La fotografía se elige con una regla, no con el ojo.", negrita=True)
p("La regla del 0,30 (§4.6) es la lección más cara del proyecto: seis fotos "
  "descargadas y descartadas porque el rostro era demasiado grande. El solver "
  "las detecta, pero para entonces la licencia ya se consumió. Hay que aplicar "
  "el criterio sobre la miniatura, antes de descargar.")
p("Medir es más barato que tantear, pero sólo si se mide bien.", negrita=True)
p("El segundo error más caro no fue de código: fue estimar las medidas del "
  "rostro sobre miniaturas. El solver funcionaba, las reglas estaban bien y el "
  "resultado igual salía con el texto sobre el mentón, porque la entrada estaba "
  "corrida. Las seis fotos de Salud hubo que remedirlas.")
p("La silueta era la restricción que faltaba.", negrita=True)
p("Las primeras piezas se generaron con el sujeto centrado y se veían mal sin "
  "que fuera evidente por qué: cumplían las tres zonas documentadas. La cuarta "
  "—la silueta, corrida a la derecha— es la que deja el margen izquierdo limpio "
  "para el logo y el título.")
p("Cumplir la regla no es lo mismo que verse bien.", negrita=True)
p("30px de aire cumplían RN-04 y se leían como texto pegado a la cara. El "
  "número que importa no es el que evita la colisión, sino el que deja el "
  "rostro visiblemente despejado.")
p("Un nombre de salida fijo es una bomba de tiempo.", negrita=True)
p("El solver escribía siempre «encuadres-salud.json». Al resolver la segunda "
  "escuela pisó los encuadres de la primera. No llegó a ninguna gráfica porque "
  "se detectó al revisar, pero es el tipo de error que sólo aparece cuando el "
  "proyecto escala.")

h2("6.2 Continuidad: el motor genérico es otro proyecto")
p("Entre el 15 y el 21 de septiembre de 2026 se construyó una versión genérica "
  "de este pipeline, capaz de trabajar con cualquier marca en vez de estar atada "
  "a las plantillas de IPG. Vive en la carpeta hermana Motor-Graficas y tiene "
  "documentación propia.")
p("La separación es deliberada", negrita=True)
p("Este proyecto es una campaña terminada; el otro es una herramienta en "
  "evolución. Mezclarlos haría que cualquier cambio en la herramienta pusiera en "
  "duda una entrega ya aprobada. Los scripts de 00-Scripts no se tocaron: siguen "
  "produciendo exactamente lo que está en «Gráficas Meta 2027».")
p("Qué relación tienen", negrita=True)
tabla(["Aspecto", "Este proyecto (campaña)", "Motor genérico (aparte)"],
      [["Alcance", "Admisión IPG 2027, cuatro escuelas",
        "Cualquier marca con plantilla y planilla"],
       ["Estado", "Cerrado y respaldado", "En desarrollo"],
       ["Plantillas", "Post y Story de IPG, localizadas por clase de Illustrator",
        "Las mismas, convertidas a identificadores estables"],
       ["Datos", "Cuatro JSON de escuela", "Un JSON de proyecto por campaña"],
       ["Si hay que rehacer la campaña 2027",
        "Usar este pipeline, como documenta §5",
        "También sirve: reproduce estas piezas casi píxel a píxel"]],
      [3.4, 5.7, 5.7])
p("La equivalencia se verificó: el motor genérico regeneró las 166 piezas y se "
  "compararon una a una contra las de esta entrega. 90 salieron bit-idénticas y "
  "en el resto la diferencia máxima de color fue de 16 sobre 255 —imperceptible, "
  "propia del antialiasing al reescribir el texto—. El detalle de esa "
  "verificación está en la documentación de ese proyecto, no aquí.",
  tam=9, color=GRIS)

# ------------------------------------------------------- 7. preguntas
h1("7. Preguntas abiertas")
tabla(["Pregunta", "Estado"],
      [["¿Una foto por carrera o una por escuela?",
        "Resuelta — una por carrera, compartida por sus sedes (RN-21)."],
       ["Vencimiento del plan Shutterstock.",
        "Resuelta — plan ilimitado más 350 descargas mensuales, vigente hasta "
        "octubre de 2026. La campaña completa consumió unas 30 del cupo "
        "mensual; el resto entró por el ilimitado."],
       ["¿Regla de redondeo de la cuota mensual?",
        "Resuelta — a la decena (RN-29), deducida del post de Ingeniería en "
        "Minas."],
       ["¿Una gráfica por carrera + sede aunque haya jornadas o niveles con "
        "cuotas distintas?",
        "Parcialmente abierta — RN-16 aplicada en las cuatro escuelas, "
        "pendiente de confirmación como regla general."],
       ["¿Prefijo para las carreras que no admiten «Ingeniería en» ni «Técnico "
        "de Nivel Superior en»?",
        "Abierta — se usó «Carrera Profesional de» (RN-31) en cinco carreras. "
        "Necesita visto bueno de Marketing."],
       ["¿Listado oficial de nombres de marketing, con tildes?",
        "Abierta — el Excel trae la mayoría sin acentos. Cada escuela lleva sus "
        "reescrituras anotadas en «_supuestos_a_confirmar»."],
       ["¿Acortar los nombres que no caben en una línea?",
        "Abierta — el título de dos líneas obliga a achicar al sujeto. Afecta a "
        "ocho piezas del proyecto."],
       ["Calidad de algunas fotografías.",
        "Abierta — Podología es la más floja: el banco no tiene un retrato "
        "individual decente y lo disponible lee como «salud genérica»."]],
      [6.4, 9.8])

# ------------------------------------------------------- 8. estado y backlog
h1("8. Fases y mejora continua")

h2("8.1 Fases")
tabla(["Fase", "Estado", "Cierre"],
      [["Traspaso de contexto y organización del repositorio", "Completada",
        "11–12-09-2026"],
       ["Entorno técnico", "Completada", "11-09-2026"],
       ["Módulo 2 (texto)", "Completada", "11-09-2026"],
       ["Módulo 4 (foto): descarga y fórmula de encuadre", "Completada",
        "12–14-09-2026"],
       ["Piloto en 2 carreras reales", "Completada", "14-09-2026"],
       ["Módulo 6: orquestación de lote por escuela", "Completada",
        "15-09-2026"],
       ["Solver de encuadre y zona de silueta", "Completada", "15-09-2026"],
       ["Medición de título y de rostro; reencuadre completo", "Completada",
        "15-09-2026"],
       ["Escuela de Salud — 6 carreras, 14 piezas", "Completada", "15-09-2026"],
       ["Escuela de Educación y Desarrollo Social — 6 carreras, 23 piezas",
        "Completada", "15-09-2026"],
       ["Escuela de Gestión, Negocios y Marítima — 13 carreras, 19 piezas",
        "Completada", "15-09-2026"],
       ["Escuela de Ingeniería y Tecnología — 18 carreras, 27 piezas",
        "Completada", "15-09-2026"],
       ["Campaña completa: 166 gráficas entregadas", "Completada",
        "15-09-2026"],
       ["Respaldo íntegro verificado por hash (1.169 archivos)", "Completada",
        "21-09-2026"],
       ["Módulo 1: extracción automática del Excel", "No iniciado", "—"],
       ["Revisión final de Marketing antes de publicar", "Pendiente", "—"]],
      [8.4, 4.0, 3.8])
p("Las dos fases pendientes son las únicas que quedan abiertas en ESTE "
  "proyecto. Todo lo demás que aparece como mejora se ejecutó en el motor "
  "genérico, que es otro repositorio (§6.2).", tam=9, color=GRIS)

h2("8.2 Backlog de mejora continua")
tabla(["Prioridad", "Tema", "Depende de"],
      [["Alta", "Confirmar los supuestos de nombres y prefijos anotados en cada "
        "JSON antes de publicar.", "Marketing"],
       ["Alta", "Confirmar RN-16 (cuota más baja entre niveles agrupados) como "
        "regla general.", "Decisión del usuario"],
       ["Media", "Construir el Módulo 1 (Excel → JSON de escuela).",
        "Esquema de columnas final del Excel"],
       ["Baja", "Reemplazar la foto de Podología si hay producción propia.",
        "Presupuesto"],
       ["Baja", "Registrar el código de carrera además del slug, para evitar "
        "colisiones entre carreras homónimas.", "—"],
       ["Resuelta", "SVG acumulándose en la carpeta de entrega (RN-23).", "—"],
       ["Resuelta", "Exit code poco fiable de Inkscape.", "—"],
       ["Resuelta", "Foto expandida rechazada por Pillow (RN-27).", "—"],
       ["Resuelta", "El solver pisaba los encuadres de otra escuela (RF-30).",
        "—"],
       ["Resuelta\naparte",
        "Automatizar la medición del rostro con detección facial. Era el único "
        "paso manual del encuadre y el que más errores produjo.",
        "Motor genérico"],
       ["Resuelta\naparte",
        "Aplicar la regla del 0,30 automáticamente antes de descargar, para no "
        "gastar licencias en fotos inservibles.", "Motor genérico"]],
      [2.4, 10.0, 3.8])
p("«Resuelta aparte» significa que la mejora existe en el motor genérico "
  "(§6.2) y NO en los scripts de esta carpeta, que quedaron congelados. Si se "
  "vuelve a producir una campaña con este pipeline, esos dos pasos siguen "
  "siendo manuales aquí.", tam=9, color=GRIS)

# ------------------------------------------------------------- 9. roles
h1("9. Roles")
tabla(["Quién", "Qué hace"],
      [["Usuario (Luis Rivera)",
        "Define y aprueba criterios de diseño y encuadre, gestiona la cuenta "
        "Shutterstock, decide las reglas de negocio pendientes y da el visto "
        "bueno final de cada pieza."],
       ["Sesión Claude Code",
        "Mantiene los scripts, ejecuta el pipeline, busca y descarga "
        "fotografías, mide y resuelve los encuadres, renderiza, verifica cada "
        "pieza y regenera esta documentación."],
       ["Diseño Gráfico / Marketing",
        "Dueño original de las plantillas Illustrator; confirma los nombres de "
        "marketing y revisa antes de publicar."]],
      [4.6, 11.6])

p()
p("Documento generado por 00-Scripts/generar_documentacion.py a partir de las "
  "conversaciones del 11 al 15 de septiembre de 2026 · Mantenido por Luis "
  "Rivera · luis.rivera@ipg.cl · Última actualización: 15 de septiembre de 2026 "
  "· Pipeline en versión 0.7", tam=8.5, color=GRIS)

d.save(DEST)
print("guardado:", DEST)
