# -*- coding: utf-8 -*-
"""
Created on Fri Feb 19 12:16:19 2021

@author: Franklin
"""

from libreria_OpenSees.Funciones_texto import cambiar_linea, buscar_linea
from libreria_OpenSees.Funciones_TCL import cambiar_variable, set_variable
from io import open
from random import sample
import numpy as np
import pandas as pd
from pandas.core.frame import DataFrame
import os
import subprocess
import shutil


###############################################################################
# -----------------------------------------------------------------------------#

def run_OpenSees(n_proces: int, fila_Edificio: DataFrame, GM_2_direction: DataFrame,
                 Dir_files: str, Dir_Opensees: str, Dir_outs: str,
                 list_file_run: list, list_file_lista_GM: list, sema,
                 change_dir_level_by_level = True,
                 print_out = True):
    """
    Corre el opensees y cambia los parametros

    Parameters:
    ----------
    n_proces : int
        Numero de procesos que se usará en esta iteracion
    fila_Edificio : DataFrame
        Solo una fila del Dataframe de edificios, el que se usará en esta iteracion
    GM_2_direction : DataFrame
        2 filas de un DataFrame que corresponde a un solo sismo.
    Dir_files : str
        Directorio donde se guardan todos los files a trabajar
    Dir_Opensees : str
        Ruta absoluta o relativa de archivo OpenSees.exe
    Dir_outs : str
        Ruta del directorio donde se guardarán los resultados como primer nivel de carpetas.
        Si change_dir_level_by_level=None entonces será la ruta final de todos los archivos,
        es decir los 3 niveles juntos
    list : list
        lista de todos los nombres de las copias de archivos run
    list_file_lista_GM : list
        lista de todos los nombres de las copias de archivos lista_GM
    sema: object
        Objeto de multiprocess que permite que se detenga el multiproceso si supera la cantidad de procesos
    change_dir_level_by_level: {True, None}, Optional
        Pregunta si deseas cambiar la ruta de los files nivel por nivel. Es decir carpeta de edificio, luego de sismo,
        y finalmente el nombre final del file.
        Si se escoge None entonces la variable Dir_outs debe dar la ruta final del archivo

        Default es True

    print_out : bool Optional
        Si deseas imprimir un mensaje sobre lo que se corrió

    Returns:
    -------

    """
    file_run = list_file_run[n_proces]
    file_run = os.path.join(Dir_files, file_run)

    file_lista_GM = list_file_lista_GM[n_proces]
    file_lista_GM = os.path.join(Dir_files, file_lista_GM)

    GM = GM_2_direction['N_SIS'].iloc[0]
    GM = int(GM)
    n_puntos = GM_2_direction['N_POINTS_PROCES2'].iloc[0]
    dt = GM_2_direction['DT_PROCES2'].iloc[0]
    time_out = (n_puntos - 1) * dt
    ID_EDI = fila_Edificio.name
    ID_EDI = ID_EDI

    Define_Edi(fila_Edificio, file_run, time_out, Dir_outs, dir_out2 = change_dir_level_by_level)
    Define_Sis(GM_2_direction, GM, file_lista_GM,
               COL_DIR = 'PATH_DIR_PROCES2',
               COL_DT = 'DT_PROCES2',
               dir_out3 = change_dir_level_by_level)

    if change_dir_level_by_level is None:
        cambiar_variable(file_run, 'dataDir', f'"{Dir_outs}"', unidad = False)

    var = subprocess.run([Dir_Opensees, file_run], capture_output = True)

    if print_out is True:
        print(f'Se corrio el Sismo {GM} con el edificio {ID_EDI}, con proceso {n_proces}')
    # print(var.stderr)

    sema.release()


# ----------------------------------------------------------------------------#
##############################################################################


###############################################
def crear_files_process(numero_copias_files: int, run_original: str, GM_original: str,
                        print_out = False,
                        copy_opensees = False,
                        opensees_file_name: str = None):
    """
    Crea copias de los files run y GM.

    Parameters:
    ----------
    numero_copias_files : int
    run_original : str
        Nombre del file que corre el programa con los parametros
    GM_original : str
        Nombre del file que guarda los datos del sismo
    print_out : bool, default True
        Indica si desea que se imprima un mensaje de creación o no
    copy_opensees: bool, default False
        Pregunta si se desea copiar el OpenSees Tambien
    opensees_file_name: str, default None
        Si el anterior parametro es verdadero, entonces se necesita el string con el nombre

    Returns:
    -------
    list : list
        lista con los nombres de los file copiados de run
    list_file_lista_GM : list
        lista con los nombres de los files copiados de lista_GM

    Si copy_opensees es Falso entonces el tercer out sera
    ok : {0,1}
        indica si se termino de crear los files, 0 si aún no, 1 si ya lo hizo.
    Si copy_opensees es verdadero
    list_file_opensees: list
        lista con los nombres de los files copiados de Opensees
    """

    ok = 0
    list_file_run = []
    list_file_lista_GM = []

    # Buscar las lineas

    N_linea_source = buscar_linea(run_original, GM_original)

    name_run, ext = os.path.splitext(run_original)
    name_GM, ext = os.path.splitext(GM_original)

    with open(run_original, 'r') as f:
        contenido_run = f.readlines()

    with open(GM_original, 'r') as f:
        contenido_GM = f.readlines()

    for i in range(numero_copias_files):
        name_run_out = name_run + str(i + 1) + ext
        name_GM_out = name_GM + str(i + 1) + ext

        contenido_run[N_linea_source - 1] = 'source ' + name_GM_out

        with open(name_run_out, 'w') as f:
            f.writelines(contenido_run)

        with open(name_GM_out, 'w') as f:
            f.writelines(contenido_GM)

        list_file_run.append(name_run_out)
        list_file_lista_GM.append(name_GM_out)

    if copy_opensees is True:
        list_file_opensees = []
        dir_opensees, opensees_file_name = os.path.split(opensees_file_name)
        opensees, ext = os.path.splitext(opensees_file_name)

        for i in range(numero_copias_files):
            name_opensees_out = opensees + str(i + 1) + ext
            shutil.copyfile(opensees_file_name, name_opensees_out)
            name_list = os.path.join(dir_opensees, name_opensees_out)
            list_file_opensees.append(name_list)

        if print_out == True:
            print('\n Se finalizó el programa que crea los files \n')

        return list_file_run, list_file_lista_GM, list_file_opensees

    else:
        if print_out == True:
            print('\n Se finalizó el programa que crea los files \n')
        ok = 1
        return list_file_run, list_file_lista_GM, ok


###############################################################3


###############################################################
def remove_files_process(*args):
    print('Borrando los archivos para el Process \n')

    for list in args:
        for files in list:
            os.remove(files)


#############################################################################

def filtrar_data_sis(DB_Sismos, filtro = 'all', Tipo = 'lista',
                     comparador = '=='):
    """
    Filtra los datos de sismos de un archivo .csv
    según el criterio de filtro y tipo de filtro

    Parameters:
    ----------
    DB_Sismos : DataFrame
        DataFrame con los datos de los sismos.
    filtro : int or list, optional
        Depende del tipo de filtro que se use:

            - LISTA: Se debe usar una lista [list] con los rangos donde se desea
            tomar el filtro, por ejemplo si se desean los 100 primeros se usa
               filtro = range(100).

            - ALEATORIO: Se debe usar un [int] con la cantidad
            de valores aleatorios.

            - FILTRO: Se debe usar una lista [list] de dos valores
               **[str] con el nombre de la columna filtrar\n
               **[str or int or float] Denpendiendo de los valores de la columna

        . The default is 'all'.

    Tipo : str, optional
        Escoger el tipo de filtracion que se hará:

            - LISTA: Se debe usar una lista [list] con los rangos donde se desea
            tomar el filtro, por ejemplo si se desean los 100 primeros se usa
               filtro = range(100).

            - ALEATORIO: Se debe usar un [int] con la cantidad
            de valores aleatorios.

            - FILTRO: Se debe usar una lista [list] de dos valores
               *[str] con el nombre de la columna filtrar\n
               *[str or int or float] Denpendiendo de los valores de la columna

        . The default is 'lista'.

    comparador: str
        En caso de usa el Tipo = 'FILTRO' indica el comparadaror que se usará
        '=='    :  igualdad
        '>'     :   mayor que
        '>='    :   mayor igual que
        '<'     :   menor que
        '>='    :   mnor igual que

    Returns:
    -------
    Lista_sensores : list
        La lista de los numeros de los sensores que se usará.
    DB_Sismos : DataFrame
        Dataframe de output, filtrado.

    """

    # Tipo es el criterio con el que filtrar:
    # lista se usara una lista o un range
    # aleatorio solo la cantidad de valores deseados
    # filtro una lista de la columna a filtras y que filtrar
    # Filtro all solo arroja una Lista_sensores y no filtra nada.

    Tipo = Tipo.lower()

    if filtro == 'all':

        Lista_sensores = DB_Sismos['N_SIS'].unique()

    elif Tipo == 'lista':
        filtro = np.array(filtro) - 1
        Lista_sensores = DB_Sismos['N_SIS'].unique()
        Lista_sensores = Lista_sensores[filtro]
        DB_Sismos = DB_Sismos[DB_Sismos.N_SIS.isin(Lista_sensores)]

    elif Tipo == 'aleatorio':

        Lista_sensores = DB_Sismos['N_SIS'].unique()
        Lista_sensores = sample(list(Lista_sensores), k = filtro)
        Lista_sensores.sort()
        Lista_sensores = np.array(Lista_sensores)
        DB_Sismos = DB_Sismos[DB_Sismos.N_SIS.isin(Lista_sensores)]

    elif Tipo == 'filtro':

        columna = filtro[0]
        valor = filtro[1]

        if comparador == '==:':
            DB_Sismos = DB_Sismos[DB_Sismos[columna] == valor]
        elif comparador == '>':
            DB_Sismos = DB_Sismos[DB_Sismos[columna] > valor]
        elif comparador == '>=':
            DB_Sismos = DB_Sismos[DB_Sismos[columna] >= valor]
        elif comparador == '<':
            DB_Sismos = DB_Sismos[DB_Sismos[columna] < valor]
        elif comparador == '<=':
            DB_Sismos = DB_Sismos[DB_Sismos[columna] <= valor]

        Lista_sensores = DB_Sismos['N_SIS'].unique()
    else:
        print('Se escogió mal el filtro')

    return Lista_sensores, DB_Sismos


#######################################################################
def filtrar_data_edi(DB_Edificios, filtro, Tipo = 'lista'):
    """
    Filtra los datos de edificios de un archivo .csv
    según el criterio de filtro y tipo de filtro

    Parameters:
    ----------
    DB_Edificios : DataFrame
        DataFrame con los datos de los Edificios.

    filtro : int or list, optional
        Depende del tipo de filtro que se use:

            - lista: Se debe usar una lista [list] con los rangos donde se desea
                tomar el filtro, por ejemplo si se desean los 100 primeros se usa
                filtro = range(100).

            - aleatorio: Se debe usar un [int] con la cantidad
                de valores aleatorios.

            - filtro: Se debe usar una lista [list] de dos valores
               ** [str] con el nombre de la columna filtrar\n
               ** [str or int or float] Denpendiendo de los valores de la columna

        . The default is 'all'.

    Tipo : str, optional
        Escoger el tipo de filtracion que se hará:


            - lista: Se debe usar una lista [list] con los rangos donde se desea
                tomar el filtro, por ejemplo si se desean los 100 primeros se usa
                filtro = range(100).

            - aleatorio: Se debe usar un [int] con la cantidad
                de valores aleatorios.

            - filtro: Se debe usar una lista [list] de dos valores
               ** [str] con el nombre de la columna filtrar\n
               ** [str or int or float] Denpendiendo de los valores de la columna

        . The default is 'lista'.

    Returns:
    -------
    DB_Edificios : DataFrame
        DataFrame filtrado.

    """

    # Tipo es el criterio con el que filtrar:
    # lista se usara una lista o un range
    # aleatorio solo la cantidad de valores deseados
    # filtro una lista de la columna a filtras y que filtrar
    # Filtro all solo arroja una Lista_sensores y no filtra nada.

    Tipo = Tipo.lower()

    if Tipo == 'lista':

        DB_Edificios = DB_Edificios[DB_Edificios.index.isin(filtro)]

    elif Tipo == 'aleatorio':

        maximo = len(DB_Edificios)
        indices_Edi = sample(range(maximo), k = filtro)
        indices_Edi.sort()
        DB_Edificios = DB_Edificios[DB_Edificios.index.isin(indices_Edi)]

    elif Tipo == 'filtro':

        columna = filtro[0]
        valor = filtro[1]

        DB_Edificios = DB_Edificios[DB_Edificios[columna] == valor]
    else:
        print('Se escogió mal el filtro')

    return DB_Edificios


############################################################################


# # Cantidad de datos que necesita de cada DB
# N_Sismos= 1
# N_edificos= 1

# # Indicar si se quieren seguidos o aleatorios
# # Tipos, como 'lista' o como 'aletorio'
# # Tipo= 'aleatorio'
# # Tipo= 'lista'
# # Tipo= 'filtro'

# if Tipo== 'lista':
#     indices_Sis= list(range(N_Sismos))
#     indices_Edi= list(range(N_edificos))

# elif Tipo == 'aleatorio':
#     total_Sis= list(range(len(Lista_sensores)))
#     total_ed= list(range(len(DB_Edificios)))

#     indices_Sis= sample(total_Sis, k=N_Sismos)
#     indices_Edi= sample(total_ed, k=N_edificos)
# indices_Sis.sort()
# indices_Edi.sort()
###########################################################################
#################################################################
# Funciones
def Define_Edi(Fila, file_run, t_max_analisis, dir_outs, dir_out2 = True):
    """
    Define los parametros de los edificios en los scripts tcl.
    En este caso se aplicará a todo el DataFrame fila por fila.

    Parameters:
    ----------
    Fila : DataFramew
        Fila del DataFrame, util para usar el metodo aply().
    file_run : str
        Ruta del file donde se encuentra el archivo que se editará Run.tcl.
    t_max_analisis: float
        Tiempo que tendran los recorders de salida. Ejem: 20seg, 30seg, etc
    dir_outs : str
        Ruta de la carpeta donde se guardarán las salidas
    dir_out2 : {None,True}, optional
        Indica si deseas que se modifique la variable dir_out2 (Esta variable indica el segundo nivel
        de la ruta donde se guardarasn las salidas) si es True entonces se guarda automaticamente con el nombre
        del ID del DataFrame. Ejemplo:

            ID		story		baysX		...\n\r
            ===================================
            5		8			6			...
        La carpeta tomaria el nombre de "5".

        Si usa None, entonces la carpeta se queda con el nombre que tiene la hoja actualmente

        default es True
    Returns:
    -------
    None.

    """
    ID = Fila.name
    story = Fila['#N_Pisos']
    baysX = Fila['N_VanosX']
    baysY = Fila['N_VanosY']
    Hz = Fila['H_Pisos']
    LbX = Fila['L_VanoX']
    LbY = Fila['L_VanoY']
    Hbx = Fila['H_VigaX']
    Bbx = Fila['B_VigaX']
    Hby = Fila['H_VigaY']
    Bby = Fila['B_VigaY']
    Hcol = Fila['H_Colum']
    Bcol = Fila['B_Colum']

    if dir_out2 is not None:
        dir_out2 = ID
    else:
        dir_outs = None

    set_variable(file_run, story, baysX, baysY, Hz, LbX, LbY, Hbx, Hby, Bbx, Bby, t_max_analisis,
                 dir_out1 = dir_outs, dir_out2 = dir_out2, hcol = Hcol, bcol = Bcol)


# cambiar_variable(file_run,'story' , story ,unidad= False )
# cambiar_variable(file_run, 'baysX', baysX ,unidad= False )
# cambiar_variable(file_run, 'baysY', baysY ,unidad= False )
# cambiar_variable(file_run, 'Hz', Hz )
# cambiar_variable(file_run, 'LbX', LbX )
# cambiar_variable(file_run, 'LbY', LbY )
# cambiar_variable(file_run,'Hbx' , Hbx )
# cambiar_variable(file_run, 'Bbx', Bbx )
# cambiar_variable(file_run, 'Hby', Hby )
# cambiar_variable(file_run, 'Bby', Bby )
# cambiar_variable(file_run, 'Hcol', Hcol )
# cambiar_variable(file_run, 'Bcol', Bcol )
# cambiar_variable(file_run, 'dir_out2', '"E'+ str(ID)+ '"' ,unidad= False)

# print(Var_out)
# print('Se definio el edificio ',ID , end='\r')


def Define_Sis(GM_2_direction, GM, file_lista_GM,
               COL_DIR = 'PATH_DIR_PROCES1',
               COL_DT = 'DT',
               dir_out3 = True):
    """
    Define los parametros de los sismos en los scripts tcl.

    Parameters:
    ----------
    GM_2_direction : DataFrame
        Dataframe de solo 2 filas que
        corresponden a las 2 direcciones de un sismo.
    GM : int
        Numero de sismo en el DataFrame general.
    file_lista_GM : str
        Ruta del file .tcl donde se guardan los parametros de sismo.
    COL_DIR : str, optional
        Nombre de la columna donde se encuentra
        el file que se guarda la array_serie de array_tiempo correpondiente. The default is 'PATH_DIR_PROCES1'.
    COL_DT : str, optional
        Nombre de la columna donde se
        encuentra el Delta de array_tiempo. The default is 'DT'.
    dir_out3 : {None,True}, optional
        Indica si deseas que se modifique la variable dir_out3 (Esta variable indica el tercer nivel
        de la ruta donde se guardarasn las salidas) si es True entonces se guarda automaticamente con el nombre
        del GM o N_SIS del DataFrame.
        Si es None se deja como estaba
        default es True
    Returns:
    -------
    None.

    """

    Lista_GMX = 'set iGMfileX {'
    Lista_GMY = 'set iGMfileY {'

    linea_GMX = buscar_linea(file_lista_GM, Lista_GMX)
    linea_GMY = buscar_linea(file_lista_GM, Lista_GMY)

    Lista_GMX += GM_2_direction[COL_DIR].iloc[0]
    Lista_GMY += GM_2_direction[COL_DIR].iloc[1]

    Lista_GMX += '}'
    Lista_GMY += '}'

    Delta = str(GM_2_direction[COL_DT].iloc[0])

    cambiar_linea(file_lista_GM, linea_GMX, Lista_GMX)
    cambiar_linea(file_lista_GM, linea_GMY, Lista_GMY)
    cambiar_variable(file_lista_GM, 'Deltat', Delta, unidad = False)

    if dir_out3 is not None:
        DirOut = str(GM)
        cambiar_variable(file_lista_GM, 'dir_out3', DirOut, unidad = False)

# print('Se definio el sismo ',GM , end='\r')
#################################################################
