# scanGUI

Este programa es una interfaz simple para controlar las luces y la cámara del escaner de manos.

## Instalación
Hay que tener instalado Python 3 (a poder ser 3.10 o superior).
Python se puede instalar desde la Windows Store o descargando el instalador de Python desde la web (python.org/downloads/windows). En esta carpeta ya está descargado.

Luego, en Símbolo del sistema hay que ejecutar:
python -m pip install numpy opencv-python pyserial Pillow

## Uso

El programa se abre ejecutando el archivo scanGUI.py. Normalmente basta con hacer doble click en el archivo,
pero si se abre como un archivo de texto hay que "Abrir con" "Python".

Junto a la ventana del programa se abre otra con fondo negro que no hay que cerrar (pues se cerraran ambas).

Al abrir y cerrar el programa se deberian enciender y apagar las luces automáticamente (a menos que se cierre abruptamente).
En el programa hay botones para encender y apagar las luces.

Si las luces no se encienden, la camara no se activa o se activa la webcam en su lugar,
entonces hay que cambiar el archivo de configuración "config.py" abriéndolo con Bloc de Notas.
Hay que probar con otros números (seguramente se haya conectado a otro USB).

Las capturas se pueden hacer con el botón "Capturar" o con la tecla de Enter.

Las capturas se guardan en la carpeta indicada. El nombre estará formado por la serie y captura.
Todo ello se puede modificar a voluntad.

Hay tres modos:

- Nuevo usuario: Guarda la imagen que se ve en pantalla. Las series se llaman TEN_ y un número de 4 cifras.
- Calibración: Al darle a "Capturar" intenta detectar el patrón de calibración de 7x10.
Si lo detecta, se actualizan los parámetros de calibración y se guardan en un archivo .json.
Cuando no lo detecta puede tardar bastante. Las series se llaman CALIB_ y la fecha y hora actual.
Por defecto hay una calibración bastante buena.
- Comprobar calibración: Intenta detectar el patrón de calibración de 36x54. Tarda unos segundos.
Si lo detecta se muestra el error en milímetros obtenido tras aplicar la última calibración.
Aquí el error mide cuanto se desvían las esquinas del patrón de una situación ideal en la que estén equiespaciadas.

Al cambiar el modo se cambia la serie (aumentando le número de 4 cibras o actualizando la fecha y hora)
y se resetea el número de captura.

IMPORTANTE: en lado del portatatil en el que se conectan la cámara y luces no hay que conectar nada más,
la cámara no funcionaría bien. ¯\_(ツ)_/¯
