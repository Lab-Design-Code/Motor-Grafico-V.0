# Candidatas V.3 — hojas de contacto

Una hoja por carrera. Cada miniatura va rotulada con su **ID de Shutterstock**:
ese número es lo único que hace falta para pedir la descarga.

**Nada está descargado todavía.** No se licencia ninguna foto hasta que la
nombres por su ID.

## Cómo se armaron

1. **Búsqueda estándar** en Shutterstock (no AI Search), con las keywords de la
   ficha `02-Datos/perfiles-fotograficos.json`, 5 a 7 palabras y siempre con
   `latino` o `latina`. Filtros: Solo imágenes ilimitadas + Fotos + Vertical +
   1 persona. Tres páginas por carrera, 60 candidatas.
2. **Criba técnica** con `00-Scripts/prevalidar_fotos.py` sobre la miniatura
   pública, que es gratis. Detecta el rostro, deduce las medidas y le pregunta
   al solver si existe encuadre para el Post y el Story **con el techo real de
   título de esa carrera**. Lo que no tiene encuadre posible no llega a la hoja.
3. En la hoja quedan sólo las que pasan. Las marcadas `(revisar)` traen más de
   un rostro: hay encuadre, pero hay que elegir sujeto.

De 1.553 candidatas revisadas, 353 pasaron la criba.

## Lo que la criba NO mira

Es un prefiltro de encuadre, no un juicio editorial. **No** comprueba casting,
color de casco, número de protagonistas ni tipo de licencia. Eso se ve en la
hoja. En particular:

- **La licencia editorial no se detecta acá.** Ya pasó una vez: la `2663900595`
  decía «uso editorial únicamente» y habría sido inservible para pauta. Antes de
  descargar hay que abrir la ficha y confirmar que dice «Usa tu plan: Descargas
  ilimitadas», sin aviso amarillo.
- **Medir sobre la miniatura no vale como medición.** Una vez comprada la foto
  hay que volver a medirla con `grilla_fina.py` sobre el archivo real: en
  Podología la miniatura marcaba 0,27 y el archivo 0,35.

## Tres que costaron

| Carrera | Qué pasó |
|---|---|
| Podología | «podiatrist» trae cosmetología, dentistas y primeros planos de pies. Hubo que cruzar «foot care specialist» y «nurse treating patient foot»; aun así quedan sólo 5. |
| Instrumentación Industrial | Con «control panel» salía casi todo sin rostro. Se cambió a «industrial technician orange helmet factory». |
| Procesos Mineros | Los retratos mineros con casco naranjo son escasos y muchos son de faena real sin protagonista. |

## Reparto de cascos en esta tanda

Regla del 24-09-2026: ingenierías **blanco**, técnicos **naranjo**, salvo que la
carrera sólo exista como TNS, que entonces va blanco.

- **Naranjo (5):** Electricidad · Instrumentación Industrial · Operaciones
  Portuarias · Procesos Industriales · Procesos Mineros
- **Blanco (11):** Construcción Civil · Ingeniería Industrial · Prevención de
  Riesgos · Automatización y Control · Mantenimiento Industrial · Minas ·
  Operaciones de Planta Minera · Gestión Logística Portuaria · Comercio
  Exterior · Transporte Marítimo · Maquinaria Naval
