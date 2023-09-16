# -*- coding: utf-8 -*-
"""
Created on Thu Feb 11 00:52:55 2021

@author: Franklin
"""

from libreria_OpenSees.Funciones_gen_out import filtrar_data_sis, filtrar_data_edi, Define_Edi, Define_Sis
import pandas as pd
# import numpy as np
import os
import subprocess
from tqdm import tqdm
from time import time

tiempo_i = time()

# retrocede la carpeta actual con lo 2 puntos
Path_Data_base = '../Base_datos'

# File donde está el OpenSees
Dir_files = os.getcwd()
Dir_Opensees = os.path.join(Dir_files, 'OpenSees.exe')

# Files para editar parametros
file_run = os.path.join(Dir_files, 'Run.tcl')
file_lista_GM: str = os.path.join(Dir_files, 'Lista_GM.tcl')

file_out_DB = 'DB_out_p.csv'
Dir_outs = 'Data_out_prueba2'
# ----------------------------------------------------------


# Path de los files de las bases de datos
Path_DB_Sismos = os.path.join(Path_Data_base, 'DB_Sismos.csv')
Path_DB_Edificios = os.path.join(Path_Data_base, 'DB_Edificios.csv')

# Indico que la columna ID se convierta en el Index
DB_Sismos = pd.read_csv(Path_DB_Sismos, index_col='id')
DB_Edificios = pd.read_csv(Path_DB_Edificios, index_col='id')

# drop columnas que no vaya a necesitar en la ejecución
DB_Sismos.drop(['PATH_DIR_ORG', 'PATH_DIR_PROCES1', 'DT', 'CORTE1', 'CORTE2'],
               axis=1, inplace=True)

# filtros de ambos DataFrame
# 168,272
# Lista_sensores, DB_Sismos= filtrar_data_sis(DB_Sismos, Tipo= 'aleatorio', filtro= 2)

Lista_sensores, DB_Sismos = filtrar_data_sis(DB_Sismos, Tipo='lista', filtro=[33])
# Si se usa lista se guarda un numero mayor

DB_Edificios = filtrar_data_edi(DB_Edificios, Tipo='lista', filtro=[2])
############################


DB_out = pd.DataFrame(columns=(['ID_EDI', 'ID_SISX', 'ID_SISY', 'GM', 'PATH_OUT']))

count_edi = 0
total = len(DB_Edificios)

for ID_EDI in DB_Edificios.index:
    # for ID_EDI in tqdm(DB_Edificios.index, position=0):

    if os.path.isdir(Dir_outs) == False:
        os.mkdir(Dir_outs)

    PATH_OUT = os.path.join(Dir_outs, 'E' + str(ID_EDI))

    fila_Edificio = DB_Edificios.loc[ID_EDI]
    Define_Edi(fila_Edificio, file_run, Dir_outs)
    count_edi += 1

    for GM in tqdm(Lista_sensores, desc='Cargando Sismo de edificio {} --{}/{}'.format(ID_EDI, count_edi, total)):
        # for GM in tqdm(Lista_sensores, position= 1):

        PATH_OUT = os.path.join(PATH_OUT, str(GM))
        GM_2_direction = DB_Sismos[DB_Sismos['N_SIS'] == GM]

        Define_Sis(GM_2_direction, GM, file_lista_GM,
                   COL_DIR='PATH_DIR_PROCES2',
                   COL_DT='DT_PROCES2')

        ID_SISX = GM_2_direction['N_SIS'].iloc[0]
        ID_SISY = GM_2_direction['N_SIS'].iloc[1]
        # TODO REVISAR SI LOS ID DE SISMO ESTÁN BIEN
        DB_out.loc[len(DB_out)] = [ID_EDI, ID_SISX, ID_SISY, GM, PATH_OUT]

        var = subprocess.run([Dir_Opensees, file_run], capture_output=True)

print('\n Fin de corridas de edificios\n')
print('Guardando datos...\n')

DB_out.to_csv(os.path.join(Path_Data_base, file_out_DB))

tiempo_f = time()
print('El array_tiempo que demoró fue:', tiempo_f - tiempo_i, 'Segundos')
