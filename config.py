# En este archivo se puede elegir la camara a usar, el puerto USB al que conectar las luces,
# la intensidad por defecto de las luces y el directorio en que guardar las imágenes.


# Puede ser 0, 1, 2... según cuantas cámaras haya conectadas al PC
cam = 0

# Puede ser cualquier número. Cambia según el puerto USB al que se conecten las luces. Probablemente es 3, y si no 4.
luz = 3

intensidad = 90  # por ciento

# Carpeta por defecto para guardar las capturas (se puede cambiar cada vez en el programa).
directorio_destino = 'D:/HANDSCANNER_DATA/'

# Balance de blancos objetivo. Es el que se le pide al usuario que ponga.
balance_de_blancos = 5050

# Tamaño del patrón de comprobación.
dimensiones_patron_comprobacion = (49, 31)  # Nuevo (un poco más pequeño para que lo detecte)
# dimensiones_patron_comprobacion = (53, 35)
