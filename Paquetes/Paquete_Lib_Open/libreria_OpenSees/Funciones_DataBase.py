# -*- coding: utf-8 -*-
"""
Created on Mon Mar  8 12:12:07 2021

@author: Franklin
"""

import pandas as pd
import numpy as np
import os


###################################################################
def get_TS_Sis(DB, Path_DB = '', tipo = 'DataFrame',
               PATH_DIR_SIS = 'PATH_DIR_PROCES1',
               DeltaT = 'DT',
               N_SIS = 'N_SIS',
               DIRECCION = 'DIRECCION',
               DT_out = True):
    """
    Función aplicable a un data frame de sismos para obtener
    sus series de array_tiempo en forma de array o pd.Series.

    Parameters
    ----------
    DB : DataFrame
        DataFrame con los datos de sismos
    Path_DB : str, optional
        Ruta con la carpeta donde se encuentran las
        bases de datos. The default is ''.
    tipo : str, optional
        Indica el tipo de output, si es DataFrame o Array
        . The default is 'DataFrame'.
    PATH_DIR_SIS : str, optional
        Nombre de la columna del data frame donde se encuentran los GM
        . The default is 'PATH_DIR_PROCES1'.
    DT : str, optional
        Nombre de la columna del data frame que posee los DT de cada GM
        . The default is 'DT'.
    N_SIS : str, optional
        Nombre de la columna del data frame que posee el número de GM
        . The default is 'N_SIS'.
    DIRECCION : str, optional
        Nombre de la columna del data frame que posee la dirrecion de GM
        . The default is 'DIRECCION'.
    DT_out : bool, optional
        Indica si se desea que el output posea una lista con las series
        de array_tiempo
        . The default is 'True'.
    Returns
    -------
    Time_series : array o DataFrame, dependiendo de Tipo
        Traen los registros sismicos desde un file determinado

    """

    Path = os.path.join(Path_DB, DB[PATH_DIR_SIS])
    DT = DB[DeltaT]

    if tipo == 'DataFrame':
        name = '{}- {}'.format(DB[N_SIS], DB[DIRECCION])
        Time_series = pd.read_csv(Path, names = [name])
        if DT_out == True:
            long = len(Time_series)
            Time_series.index = np.arange(long) * DT

    elif tipo == 'Array':
        name = '{}- {}'.format(DB[N_SIS], DB[DIRECCION])
        Time_series = pd.read_csv(Path, names = [name])
        Time_series = Time_series.to_numpy()
        if DT_out == True:
            long = len(Time_series)
            index = np.arange(long) * DT
            Time_series = np.insert(Time_series, 0, index, axis = 1)

    return Time_series


##################################################################
def get_TS_out(DB, Path_DB = '', tipo = 'DataFrame', DT_out = True,
               PATH_OUT = 'PATH_OUT'):
    """
    Obtiene los datos de los Time series de salida guardados en carpetas
    cuyas rutas están guardadas en el DataFrame DB columna PATH_OUT

    Parameters
    ----------
    DB : DataFrame
        Dataframe donde se encuetra la información de los datos de salida.

    Path_DB : str, optional
        Ruta de la carpeta o directorio donde se encuentra las carpetas
        detalladas en el DataFrame
        . The default is ''.

    tipo : str, optional
        Indica el tipo de importacion de los datos de series de array_tiempo
        se pueden tener 23 tipos:
            --> DataFrame: Devuelve el resultado como un DataFrame con
                    nombre del file acompañado de la dirección
            --> Array: Devuelve los datos como un array de 2D
        . The default is 'DataFrame'.

    DT_out : bool, optional
        Indica si el DataFrame debe salir con un index igual al Tiempo
        y si es un array con una columna igual a la array_serie de array_tiempo
        . The default is True.

    PATH_OUT : str , optional
        Nombre de la columna donde se guardan las rutas de los archivos
        . The default is 'PATH_OUT'.


    Returns
    -------
    Time_series : DataFrame o Array
        Data del output de cada edificio con cada sismo.

    """
    # se va a trabajar con DT= 0.02
    Path = os.path.join(Path_DB, DB[PATH_OUT])
    Files_por_piso = os.listdir(Path)

    if tipo == 'DataFrame':

        for count, piso in enumerate(Files_por_piso):

            name, ext = os.path.splitext(piso)
            name_id = name + '_ID'
            name_x = name + '_X'
            name_y = name + '_Y'

            path_piso = os.path.join(Path, piso)

            if DT_out == True:
                Time_serie_piso = pd.read_csv(path_piso, names = [name_id, name_x, name_y], sep = ' ',
                                              index_col = name_id)
            # Time_serie_piso.set_index('ID', inplace=True)
            else:
                Time_serie_piso = pd.read_csv(path_piso, names = [name_id, name_x, name_y], sep = ' ')
                Time_serie_piso.drop(columns = [name_id], inplace = True)

            if count == 0:
                Time_series = Time_serie_piso
            else:
                Time_series = Time_series.merge(Time_serie_piso, left_index = True, right_index = True)
                # si no pongo la variable on, lo junta por index


    elif tipo == 'Array':

        for count, piso in enumerate(Files_por_piso):

            name, ext = os.path.splitext(piso)
            name_id = name + '_ID'
            name_x = name + '_X'
            name_y = name + '_Y'

            name_col = [name_id, name_x, name_y]
            path_piso = os.path.join(Path, piso)

            Time_serie_piso = pd.read_csv(path_piso, names = name_col, sep = ' ')
            index = Time_serie_piso[name_id]
            Time_serie_piso.drop(columns = [name_id], inplace = True)

            if count == 0:

                Time_series = Time_serie_piso
            else:

                Time_series = Time_series.merge(Time_serie_piso, left_index = True, right_index = True)

        Time_series = Time_series.to_numpy()

        if DT_out == True:
            Time_series = np.insert(Time_series, 0, index, axis = 1)

    return Time_series


def get_puntos(Data, posicion = 0):
    """
    Función para obtener los numeros de puntos de un array, util para
    trabajr con DataFrames. aplica un '.shape' al array y se obtiene la
    posicion indicada de la tupla.

    Parameters
    ----------
    Data : Array
        Usualmente datos alojados en un DataFrame.
    posicion : int, optional
        Posición en la tupla que se desea . The default is 0.

    Returns
    -------
    resultado : int
        Shape o numero de puntos de un array.

    """

    Dimensiones = Data.shape
    resultado = Dimensiones[posicion]
    return resultado


def pad_zeros(Array, tipo = 'EJE1', cantidad = (1, 1)):
    """
    Usa la funcion np.pad para llenar de zeros un array.
    Se resumen los argumentos usando el tipo para indicar
    en eje se completará con 0 y con cantidad se indica cuantas filas
    o columnas a cada lado se usan.

    Parameters
    ----------
    Array : Array
        Array a llenar con zeros.
    tipo : srt, optional
        ---> Eje1: Se llenan las filas indicadas en cantidad
        ---> Eje2: Se llenan las columnas indicadas en cantidad
        ---> COMPLETO: Se llenan en ambas direcciones, cantidad debe ser
        una tupla del tamaño igual al array
        . The default is 'EJE1'.
    cantidad : tupla, optional
        tupla donde cada tupla interna indica la cantidad de filas o
        columnas para agregar al inicio o al fin . The default is (1,1).

    Returns
    -------
    a_pad : array
        array llenado con zeros.

    """

    # tipo= EJE1, EJE2, COMPLETO
    tipo = tipo.upper()

    if tipo == 'EJE1':
        # Filas
        a_pad = np.pad(Array, (cantidad, (0, 0)), constant_values = (0))

    elif tipo == 'EJE2':
        # Columnas
        a_pad = np.pad(Array, ((0, 0), cantidad), constant_values = (0))

    elif tipo == 'COMPLETO':

        a_pad = np.pad(Array, cantidad, constant_values = (0))

    return a_pad


def pad_DB(Fila, maximo, Eje = 'EJE2', Col_valores = 'Valores', Col_n_puntos = 'N_COLUMNAS'):
    """
    Funcion para llenar zeros, pero personalisada para usar en un
    DataFrame

    Parameters
    ----------
    Fila : DataFrame
        Fila del DataFrame.
    maximo : int
        Valor maximo a aunmentar un array y llenarlo de zeros.

    Eje : str, optional
        ---> Eje1: Se llenan las filas indicadas en cantidad
        ---> Eje2: Se llenan las columnas indicadas en cantidad
        ---> COMPLETO: Se llenan en ambas direcciones, cantidad debe ser
        una tupla del tamaño igual al array
        . The default is 'EJE2'.

    Col_valores : str, optional
        Nombre de las columnas donde se encuentran los arrays
        . The default is 'Valores'.

    Col_n_puntos : str, optional
        Nombre de las columnas donde se encuentra el numero de puntos actual
        . The default is 'N_COLUMNAS'.

    Returns
    -------
    array
        array con los 0 completos.

    """

    Col_agregar = maximo - Fila[Col_n_puntos]

    if Col_agregar == 0:

        return Fila[Col_valores]

    else:

        Array_pad = pad_zeros(Fila[Col_valores], Eje, (0, Col_agregar))

        return Array_pad

#####################################################
