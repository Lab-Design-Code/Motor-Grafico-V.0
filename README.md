# Motor Gráfico · Meta IPG 2027

> **© 2026 Ariel Garay Pavez. Todos los derechos reservados · All rights reserved.**
> Software propietario: su uso requiere autorización escrita del autor. Proprietary software: use requires the author's written permission. Ver / See [`LICENSE`](LICENSE).

Generador automático de las gráficas de Meta (Instagram y Facebook). A partir de un JSON, una plantilla SVG y una
fotografía por carrera produce el **Post 1080×1080** y el **Story 1080×1920**.

> La documentación completa está en español en [`LEEME.md`](LEEME.md). Este
> archivo sólo resume cómo poner el motor en marcha en otra máquina.

## Cómo empezar

Necesitas una IA que trabaje en tu computador (Claude Code, OPENCODE o Copilot en
modo agente) y acceso a este repositorio. Para expandir fotos nuevas hace falta
Claude con el conector de Adobe (Firefly)

1. Conecta tu IA a link de GitHub.
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

## Motor genérico (`Motor/`)

La carpeta [`Motor/`](Motor/README.md) trae el **motor genérico**: la misma
lógica de encuadre y QA, pero sin ninguna marca en el código. Cada marca se
declara en `plantillas/<marca>/plantilla.json` y cada lote en un `proyecto.json`.
Versión actual: **1.3.0**:

- **Rostros de perfil:** si no hay cara de frente, la detección prueba de perfil.
- **Datos vacíos:** un dato vacío se informa con un mensaje claro y el lote sigue.
- **Relleno de bordes corregido:** en fotos chicas ya no borronea la cara. El
  reflejo de Meta V.2 queda como opción.
- **Fotos expandidas con Adobe Firefly:** el motor puede usar una foto ya
  expandida con Firefly sin cambiar el encuadre.

Detalle y verificación en
[`Motor/actualizaciones del motor/`](Motor/actualizaciones%20del%20motor/LEEME.md).
La interfaz web local no está incluida.

## Licencia · License

**© 2026 Ariel Garay Pavez. Todos los derechos reservados.**

Este es software propietario; no es de código abierto. Queda prohibido copiar,
modificar, distribuir, sublicenciar, vender o usar con fines comerciales este
repositorio, o cualquier parte de él, sin autorización previa, expresa y por
escrito del autor. Que el repositorio sea visible no concede ninguna licencia.
Los términos completos están en [`LICENSE`](LICENSE).

**© 2026 Ariel Garay Pavez. All rights reserved.**

This is proprietary software; it is not open source. Copying, modifying,
distributing, sublicensing, selling, or making commercial use of this
repository, or any part of it, is prohibited without the author's prior,
express, written permission. The repository's visibility does not grant any
license. The full terms are in [`LICENSE`](LICENSE).
