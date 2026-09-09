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

Los proyectos se seleccionaron desde la API pública de GitHub y sus README el
9 de septiembre de 2026. La selección se edita manualmente en la tabla del perfil.
Se respetan los créditos de os_multijob como ediciones y mantenimiento.

Los SVG del rediseño son locales, con animaciones CSS, sin JavaScript ni fuentes
externas. Respetan `prefers-reduced-motion` y conservan una vista estática legible.
Solo los badges de tecnologías dependen de Shields.io.

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
el banner, vuelve al fondo decorativo; `accent_color`, incluido el valor negro 0,
se utiliza como tinte cuando está disponible. Avatar y banner se guardan como PNG
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
externas al mostrarse. Se conserva el aro animado; el avatar es una captura PNG
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
