# scanGUI

Este programa es una interfaz simple para controlar las luces y la cámara del escaner de manos.

## Instalación
Hay que tener instalado Python 3.10.
Python se puede instalar desde la Windows Store o descargando el instalador de Python (64-bits) desde la web (python.org/downloads/windows). En esta carpeta ya está descargado.
Hay que elgir la opción "Añadir Python al PATH" en el instalador.

Luego, en Símbolo del sistema hay que ejecutar:
```
python -m pip install numpy opencv-python pyserial Pillow
```

## Uso

El programa se abre ejecutando el archivo scanGUI.py. Normalmente basta con hacer doble click en el archivo,
pero si se abre como un archivo de texto hay que "Abrir con" "Python".

Junto a la ventana del programa se abre otra con fondo negro que no hay que cerrar (pues se cerraran ambas).

Al abrir y cerrar el programa se deberian encender y apagar las luces automáticamente (a menos que se cierre abruptamente).
En el programa hay botones para encender y apagar las luces.

Si las luces no se encienden, la camara no se activa o se activa la webcam en su lugar,
entonces hay que cambiar el archivo de configuración "config.py" abriéndolo con Bloc de Notas.
Hay que probar con otros números (seguramente se haya conectado a otro USB).

Las capturas se pueden hacer con el botón "Capturar" o con la tecla de Enter.
Si se usan los botones "M1" y "M2" el contenido del campo captura se ignorará y se usará "M1" y "M2" en su lugar.

Las capturas se guardan en la carpeta indicada. El nombre estará formado por la serie y captura.
Todo ello se puede modificar a voluntad.
Cuando se va a guardar una captura con los mismos codigos de serie y captura se añade automaticamente un parentesis con un número.

Hay tres modos:

- Nuevo usuario: Guarda la imagen que se ve en pantalla. Las series se llaman TEN_ y un número de 4 cifras.
- Calibración: Al darle a "Capturar" intenta detectar el patrón de calibración de 7x10.
Si lo detecta, se actualizan los parámetros de calibración y se guardan en un archivo .json.
Cuando no lo detecta puede tardar bastante. Las series se llaman CALIB_ y la fecha y hora actual.
Por defecto hay una calibración bastante buena.
- Comprobar calibración: Intenta detectar el patrón de calibración de 36x54. Tarda unos segundos.
Si lo detecta se muestra el error en milímetros obtenido tras aplicar la última calibración.
Aquí el error mide cuanto se desvían las esquinas del patrón de una situación ideal en la que estén equiespaciadas.

Al cambiar el modo se cambia la serie (aumentando el número de 4 cifras o actualizando la fecha y hora)
y se resetea el número de captura.

### IMPORTANTE
- En lado del portatatil en el que se conectan la cámara y luces no hay que conectar nada más, la cámara no funcionaría bien. ¯\_(ツ)_/¯
- Cuando se usan algunos programas potentes como Chrome la imagen se descuadra totalmente. Este problema es muy llamativo cuando ocurre y basta con cerrar scanGUI y abrir.


## Actualización

Si git (https://git-scm.com/download/win) está instalado, se puede actualizar clicando en la carpeta actual con el botón derecho y seleccionando "Git Bash Here" o "Abrir en Terminal".
A continuación se ejecuta el comando "git pull".

Si no está instalado o da error, se puede descargar el archivo zip desde la web https://lan-git.ibv.org/daruib/scangui/-/archive/main/scangui-main.zip (hay que estar conectado a la red del IBV).
La carpeta actual se puede sustituir por el contenido del zip.
