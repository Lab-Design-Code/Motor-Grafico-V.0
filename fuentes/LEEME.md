# fuentes/

El motor mide y compone los títulos con **Montserrat** Black, ExtraBold y
Medium en formato `.otf`. Los archivos no se versionan.

Descárgalas desde el repositorio oficial de la fuente,
<https://github.com/JulietaUla/Montserrat/tree/master/fonts/otf>, e
**instálalas en el sistema**. Es obligatorio: Inkscape dibuja el texto con las
fuentes instaladas, y los `.ttf` que entrega Google Fonts no los reconoce el
motor.

Esta carpeta es opcional. El motor busca los `.otf` para medir los títulos en
este orden: la variable de entorno `IPG_FUENTES`, esta carpeta y las carpetas
de fuentes del sistema (Windows, macOS y Linux).
