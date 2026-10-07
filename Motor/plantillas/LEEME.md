# plantillas/ — una carpeta por marca

Cada subcarpeta es **una marca**. El motor no conoce ninguna: la carpeta que
pases por línea de comandos es la marca.

```
plantillas/
  <marca>/
    <formato>.svg      el arte, uno por formato
    plantilla.json     el contrato: qué elemento es cada cosa
    receta.json        opcional, sólo si hubo que estampar ids
```

`<marca>` y `<formato>` son nombres libres. `post` y `story` son sólo los
nombres que usó el primer cliente; `feed`, `vertical`, `banner-4x5` o `mupi`
funcionan igual.

---

## Qué le pides al diseñador

Una cosa, y ahorra un paso entero: **que nombre las capas `m-<algo>` en
Illustrator**. El exportador escribe ese nombre como `id` y la plantilla sale
lista.

Si no, hay que estampar los ids una vez con
`herramientas/preparar_plantilla.py` y una `receta.json`. Funciona, pero es
trabajo que se repite cada vez que el diseñador reexporta.

**Por qué no se puede usar la clase CSS.** Illustrator las renumera en cada
exportación. Un motor que busque `cls-14` se rompe la primera vez que el arte se
vuelve a exportar, y se rompe en silencio: el selector no encuentra nada y la
pieza sale sin ese dato.

---

## Los tres archivos

**`<formato>.svg`** — el arte sin fotos, con la capa de foto marcada. Conviene
que las fotos de stock incrustadas se reemplacen por el marcador de capa: en el
primer cliente eso bajó las plantillas de 14 MB a 0,2 MB.

**`plantilla.json`** — un elemento por dato que cambia, más las zonas seguras.
El esquema completo está en el [README](../README.md#4-plantillajson--el-contrato-de-la-marca).

**`receta.json`** — sólo si hizo falta traducir selectores viejos a ids.

---

## Las zonas seguras no se copian de otra marca

```bash
python graficas.py zonas plantillas/<marca> <formato>
```

Devuelve **medidos del arte** el bloque de logo, la Y del título y la zona de
texto. Esos tres se pegan tal cual.

La **silueta** y el **aire** son decisiones de composición —dónde va la persona,
cuánto respiro bajo el mentón— y hay que revisarlas contra una pieza real.
Dependen de dónde puso el diseñador el logo y el bloque de texto, así que los
valores de una marca no sirven para otra.

Lo mismo vale para el **tamaño máximo de rostro**: es la ventana entre el logo y
el título, y cambia con cada plantilla.
