# Motor Gráfico · Meta IPG 2027

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
