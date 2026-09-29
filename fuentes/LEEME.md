# fuentes/

El motor mide y compone los títulos con **Montserrat** Black, ExtraBold y
Medium (`.otf`). Los archivos no se versionan.

Descárgala desde <https://fonts.google.com/specimen/Montserrat> y haz una de
estas tres cosas:

1. Instalarla en el sistema, o
2. copiar `Montserrat-Black.otf`, `Montserrat-ExtraBold.otf` y
   `Montserrat-Medium.otf` en esta carpeta, o
3. apuntar la variable de entorno `IPG_FUENTES` a la carpeta que las contiene.

El motor las busca en ese orden: primero `IPG_FUENTES`, después esta carpeta y
al final las carpetas de fuentes del sistema (Windows, macOS y Linux).
