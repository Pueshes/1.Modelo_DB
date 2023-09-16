# FUNCIONES DE EDICICIÓN DE ARCHIVOS
# HECHO POR FRANKLIN PUELLES

from io import open
import os


def buscar_linea(file, elementos, cursor = False):
    # file= File el cual se se buscarÃ¡ la linea que contenga la palabra o las palabras de elemento
    # elementos= texto o lista de textos para buscar la linea con la cual coincida
    # cursor= indica si desea que la funciÃ³n roterne la pocisiÃ³n final del cursor

    lista_elementos = []

    if type(elementos) is str:
        lista_elementos.append(elementos)
    elif type(elementos) is list:
        lista_elementos = lista_elementos + elementos

    with open(file, 'r') as f:

        Numero_lineas = len(f.readlines())
        f.seek(0)
        # print(Numero_lineas)
        i = 0

        while True:
            linea = f.readline()

            elemento_encontrados = 0

            i += 1

            for palabras in lista_elementos:
                buscar = linea.find(palabras)
                if buscar >= 0:
                    # se encontrÃ³ la palabra en la linea
                    elemento_encontrados += 1

            if elemento_encontrados == len(lista_elementos):
                # print('Se encontrÃ³ la linea que coincide con los elementos')
                posicion_cursor = f.tell()
                break
            elif i > Numero_lineas:
                # print('no se encontrÃ³', elemento,'en', file)
                posicion_cursor = False
                break

    if cursor == True and posicion_cursor:
        return i, posicion_cursor
    else:
        return i


def cambiar_linea(file, N_linea, linea):
    with open(file, 'r') as f:
        texto = f.readlines()
    os.remove(file)

    texto[N_linea - 1] = linea + '\n'

    with open(file, 'w') as f:
        f.writelines(texto)


def borrar_linea(file, N_linea):
    with open(file, 'r') as f:
        texto = f.readlines()
    os.remove(file)

    texto.pop(N_linea - 1)

    with open(file, 'w') as f:
        f.writelines(texto)


def remove_todos(Lista, elemento):
    cantidad = Lista.count(elemento)

    for i in range(cantidad):
        Lista.remove(elemento)

    return Lista


def extraer_linea(file, elementos, cursor = False, Mayuscula = True,
                  seek_o = 0, print_linea = False):
    # file= File el cual se se buscarÃ¡ la linea que contenga la palabra o las palabras de elemento
    # elementos= texto o lista de textos para buscar la linea con la cual coincida
    # cursor= indica si desea que la funciÃ³n roterne la pocisiÃ³n final del cursor

    lista_elementos = []

    if type(elementos) is str:
        lista_elementos.append(elementos)

    elif type(elementos) is list:
        lista_elementos = lista_elementos + elementos

    with open(file, 'r') as f:

        Numero_lineas = len(f.readlines())
        f.seek(seek_o)
        # print(Numero_lineas)

        i = 0
        while True:
            linea = f.readline()

            if Mayuscula:
                linea = linea.upper()

            elemento_encontrados = 0

            for palabras in lista_elementos:
                buscar = linea.find(palabras)
                if buscar >= 0:
                    # se encontrÃ³ la palabra en la linea
                    elemento_encontrados += 1

            i += 1

            if elemento_encontrados == len(lista_elementos):
                # print('Se encontrÃ³ la linea que coincide con los elementos')
                posicion_cursor = f.tell()
                break

            elif i > Numero_lineas:
                # print('no se encontrÃ³', elemento,'en', file)
                posicion_cursor = False
                linea = False
                break
    if print_linea == True:
        print(linea)

    if cursor == True:
        return linea, posicion_cursor
    elif cursor == False:
        return linea


def extraer_fragmentos_linea(file, elementos, posiciones_extraccion = 0,
                             posicion_1 = 0, remove_espacio = False,
                             Mayuscula = True, cursor = False, seek_o = 0):
    # file= File el cual se se buscarÃ¡ la linea que contenga la palabra o las palabras de elemento
    # elementos= texto o lista de textos para buscar la linea con la cual coincida
    # posiciones_extraccion= int o lista indicando las posiciones
    # que se extraeran contadas desde la primera palabra
    # Si solo desea la primera palabra se debe poner un 0 solo
    # Posicion_1= posicion inicial desde donde se contaran las extracciones
    # cursor= indica si desea que la funciÃ³n roterne la pocisiÃ³n final del cursor

    # posiciones_extraccion= lista con lo nÃºmeros
    lista_posiciones_extraccion = []

    if type(posiciones_extraccion) is int:
        lista_posiciones_extraccion.append(posiciones_extraccion)
    elif type(posiciones_extraccion) is list:
        lista_posiciones_extraccion = lista_posiciones_extraccion + posiciones_extraccion

    lista_elementos = []

    if type(elementos) is str:
        lista_elementos.append(elementos)
    elif type(elementos) is list:
        lista_elementos = lista_elementos + elementos

    Linea, posicion_cursor = extraer_linea(file, elementos,
                                           cursor = True,
                                           Mayuscula = Mayuscula,
                                           seek_o = seek_o)

    if posicion_cursor != False:

        Linea = Linea.split(' ')
        # comentario
        # si posicion_1=0 entonces la posicion relativa sera la primera de la lista

        if remove_espacio:
            Linea = remove_todos(Linea, '')

        Posicion_inicial_extraccion = Linea.index(lista_elementos[posicion_1])

        if lista_posiciones_extraccion[0] == 0 and len(lista_posiciones_extraccion) == 1:
            extraido = Linea[Posicion_inicial_extraccion]
        else:
            extraido = ''

            for posiciones_de_extraccion in lista_posiciones_extraccion:
                extraido = extraido + Linea[Posicion_inicial_extraccion + posiciones_de_extraccion]

    else:
        extraido = False
        posicion_cursor = False

    if cursor == True:
        return extraido, posicion_cursor
    elif cursor == False:
        return extraido
