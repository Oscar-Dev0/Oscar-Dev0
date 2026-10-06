# Mantenimiento del perfil

La fecha de nacimiento está en `scripts/update_age.py`: 5 de enero de 2004.
El script calcula la edad en `America/Costa_Rica` y modifica únicamente el número
entre los marcadores AGE del README.

Al subir los cambios a la rama predeterminada, el workflow comprueba la edad
diariamente a las 00:23 de Costa Rica y guarda los cambios del perfil. También
permite ejecución manual desde Actions. Los horarios pueden retrasarse.

Actions debe estar habilitado y las reglas de la rama deben permitir el push de
`github-actions[bot]`. No se necesitan tokens personales. GitHub puede desactivar
los workflows programados de repositorios públicos tras 60 días sin actividad;
en ese caso, reactivalo desde Actions.

```sh
python -m unittest discover -s scripts -p 'test_*.py'
python scripts/update_age.py
python scripts/update_discord.py
```

En Windows, si falta la base de zonas horarias, se usa UTC-6 como alternativa
(Costa Rica no aplica horario de verano). No requiere paquetes externos.

La selección se amplió el 6 de octubre de 2026 tras consultar la API pública de
GitHub, los README y los manifiestos de los repositorios. La selección se edita
manualmente en la tabla del perfil. Las fuentes están en `docs/project-review.md`.
Se respetan los créditos de os_multijob como ediciones y mantenimiento, y se
describen las aportaciones a discord_cards sin atribuir autoría exclusiva.

Los SVG del rediseño son locales, con animaciones CSS, sin JavaScript ni fuentes
externas. Respetan `prefers-reduced-motion` y conservan una vista estática legible.
Los lenguajes, las tarjetas y los enlaces también usan SVG locales: la presentación
del README no necesita Shields.io ni otros servicios de imágenes.

## Arte orbital y versiones para móvil

El encabezado combina un núcleo hexagonal de código, anillos en contrarrotación,
marcas de un astrolabio y un prompt ilustrado de Linux. La terminal `stack.yml`
expone las tecnologías de Oscar con un cursor y un barrido de luz decorativo.
No ejecuta comandos ni representa una sesión real. Las secciones usan el mismo
vocabulario visual: iconos de línea, circuitos y superficies negras y azules.
El movimiento se concentra en elementos decorativos; todo el texto permanece fijo.

La paleta base es negro `#020409`, azul noche `#081629`, borde `#1c3553`, azul
eléctrico `#2563eb`, luz `#38a3ff` y blanco `#f4f9ff`. La tipografía usa Segoe UI
para títulos y Consolas/Cascadia Code para fragmentos de código, con alternativas
del sistema. No hay descargas de fuentes.

Los elementos `<picture>` seleccionan versiones compactas hasta 600 px: encabezado,
enlaces, proyectos, terminal, plataformas, áreas, lenguajes, proceso y cierre. Los ocho proyectos
se presentan en una tabla HTML de dos columnas con enlaces y descripciones nativas
debajo de las ilustraciones. Así siguen siendo legibles aunque una imagen no cargue.
Las otras tablas usan Markdown, y los repositorios adicionales están en `<details>`.
El README usa elementos compatibles con GitHub, sin CSS de página ni scripts.
El stack incluye React, SvelteKit, Linux, Docker, Compose y Windows Server junto
a los lenguajes y herramientas anteriores. SvelteKit y Windows Server se incorporan
por la experiencia declarada por Oscar; las tablas de repositorios solo atribuyen
tecnologías comprobadas en sus archivos públicos. No se inventan niveles,
certificaciones, porcentajes de dominio ni servicios desplegados.

Para reconstruir los SVG después de cambiar colores, textos o geometría:

```sh
python scripts/build_profile_art.py
```

El generador valida el XML antes de escribir cada archivo y conserva los bloques
`PROFILE_TITLE`, `AVATAR`, `BANNER`, `NAME` y `USERNAME` del perfil de Discord,
además del APNG original. La sincronización cada diez días sigue editando esos
mismos bloques. Las posiciones del avatar y del nombre se mantienen compatibles
con `scripts/update_discord.py`. Para cambios permanentes en el arte, editá el
generador; una edición manual fuera de los bloques se reemplaza al reconstruir.
El generador no modifica `README.md`, `discord.svg` ni el archivo histórico
`snake.svg`, que no se muestra en el perfil.

La tarjeta `discord-profile.svg` está inspirada en la captura del perfil facilitada
por Oscar: nombre `OscarDev` y usuario `oscar_dev`. Integra su avatar público
y enlaza al ID de Discord que ya figuraba en el README. No consulta presencia,
roles ni insignias: los elementos animados son decorativos.
La bandera `costa-rica.svg` usa las proporciones 1:1:2:1:1 de las cinco franjas.

## Avatar de Discord cada 10 días

La sincronización también actualiza `global_name`, `username` y el título accesible
del SVG. Si no hay nombre visible, usa el usuario. Los nombres se escapan como XML
y el tamaño de letra se ajusta para nombres largos. El enlace usa el ID estable,
por lo que no se rompe al cambiar de usuario.

Cuando `user.banner` contiene un hash, descarga su PNG del CDN oficial y lo coloca
en la cabecera con una capa oscura para mantener el texto legible. Si se elimina
el banner, vuelve al fondo decorativo azul y negro. La paleta elegida por Oscar
prevalece sobre `accent_color` de Discord. Avatar y banner se guardan como PNG
estáticos aunque Discord ofrezca versiones animadas. Las animaciones del SVG se
mantienen. No se infieren Nitro, presencia ni insignias a partir de campos ajenos.

Para actualizar inmediatamente sin esperar el intervalo:

```sh
python scripts/update_discord.py --force
```

La ruta del banner sigue la [referencia oficial del CDN de Discord](https://docs.discord.com/developers/reference#image-formatting).

`scripts/update_discord.py` consulta la [API indicada por Oscar](https://www.vibebot.gg/api/tools/avatar-lookup?id=518251720128856084)
y descarga el PNG de 256 píxeles del CDN de Discord. La imagen queda incrustada
en el SVG como datos base64 para que la tarjeta no necesite cargar imágenes
externas al mostrarse. Se conserva la decoración APNG original; el avatar es una captura PNG
estática aunque el avatar de Discord sea animado.

`assets/discord-avatar.json` registra la fecha local de la última consulta exitosa.
El workflow diario solo llama a la API cuando han pasado al menos 10 días desde
esa fecha, sin reiniciar el intervalo al cambiar de mes. Guarda la nueva fecha
aunque la imagen siga igual. Una ejecución manual también respeta el intervalo.

Si falla la consulta o la validación, se conserva el avatar y la fecha anteriores;
el siguiente workflow diario reintentará. La actualización de edad puede guardarse
igualmente y el workflow señala el error de Discord. No requiere token de Discord.
La programación comienza cuando los archivos están en la rama predeterminada de
GitHub con Actions habilitado; no hay un proceso local ejecutándose en segundo plano.

Referencia: [programación de workflows en GitHub](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule).

## Colores del perfil

Negro (#020409), azul noche (#081629), azul eléctrico (#2563eb) y azul
claro (#38a3ff), con texto blanco y azul pálido. La bandera conserva sus colores
nacionales y las imágenes de Discord sus colores originales. El actualizador
mantiene esta paleta al regenerar la tarjeta.

## Decoración del avatar

La decoración roja de enojo y exclamación procede del [APNG compartido por Oscar](https://img.avatardecoration.com/decorations/angry.png). El original se conserva en `assets/discord-angry.png` (80 fotogramas) y está incrustado sin modificar en el SVG. Reemplaza el aro giratorio anterior, sobre un fondo azul y negro.

Está fuera del bloque AVATAR, por lo que permanece al actualizar la foto, el nombre o el banner. La reproducción depende del soporte APNG del visor. Con `prefers-reduced-motion`, se oculta la decoración animada y se conserva la foto.
