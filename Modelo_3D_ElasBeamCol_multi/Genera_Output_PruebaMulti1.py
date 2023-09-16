# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 11:46:45 2021

@author: Franklin
"""

from libreria_OpenSees.Funciones_gen_out import filtrar_data_sis, filtrar_data_edi, crear_files_process, \
	remove_files_process, run_OpenSees
# import numpy as np
# np.array([5])
import pandas as pd
import os
from tqdm import tqdm
from time import time, sleep
import multiprocessing

tiempo_i = time()  # Tiempo inicial

time_to_sleep = 10  # Tiempo que dormirá programa para esperar la creación de arch
Numero_procesos = 4  # numero de procesos en parelelo

# ----------DEFINIR FILES---------#

# Ruta de la carpeta donde se guardan las bases de datos
# retrocede la carpeta actual con lo 2 puntos
Path_Data_base = '../Base_datos'

# File donde está el OpenSees
Dir_files = os.getcwd()  # Ruta absula de carpeta actual
Dir_Opensees = os.path.join(Dir_files, 'OpenSees.exe')  # ruta OpenSees.exe

# Nombre de los files originales con parametros que se copiaran con el numero de procesos
run_original = 'Run.tcl'
GM_original = 'Lista_GM.tcl'

# Funcion para crear la lista de archivos para correr
list_file_run, list_file_lista_GM, files_creados = crear_files_process(Numero_procesos, run_original, GM_original)

# Nombre del file donde se guardaran las bases de datos
file_out_DB = 'DB_out_pruebaMultiPtocess1.csv'  # Se guardará en la carpeta de base de datos
# Nombre de la carpeta donde se guardarán las series de array_tiempo
Dir_outs = 'Data_out_pruebaMultiprocess1'
# TODO: REVISAR EL DIRECTORIO DE GUARDADO


# Path de los files de las bases de datos
Path_DB_Sismos = os.path.join(Path_Data_base, 'DB_Sismos.csv')
Path_DB_Edificios = os.path.join(Path_Data_base, 'DB_Edificios.csv')

# ---------------Final Definir Files------------------#


# Importar DataFrames indicando que la columna ID se convierta en el Index
DB_Sismos = pd.read_csv(Path_DB_Sismos, index_col='id')
DB_Edificios = pd.read_csv(Path_DB_Edificios, index_col='id')

# drop columnas que no vaya a necesitar en la ejecución
DB_Sismos.drop(['PATH_DIR_ORG', 'PATH_DIR_PROCES1', 'DT', 'CORTE1', 'CORTE2'],
			   axis=1, inplace=True)

# filtros de ambos DataFrame

# TODO VERIFICAR SI LOS SISMOS SE ESCOGIERON BIEN
Lista_sensores, DB_Sismos = filtrar_data_sis(DB_Sismos, Tipo='lista', filtro=[30, 40])
# Lista_sensores, DB_Sismos = filtrar_data_sis(DB_Sismos, Tipo='aleatorio', filtro=3)

# Si se usa lista se guarda un numero mayor, es decir:
# Lista : [4,5,6] se usaran los GM = [5,6,7]

# TODO VERIFICAR SI LOS EDIFICIOS SE ESCOGIERON BIEN
DB_Edificios = filtrar_data_edi(DB_Edificios, Tipo='lista', filtro=[4, 6])
# DB_Edificios = filtrar_data_edi(DB_Edificios, Tipo='aleatorio', filtro=3)

print('Los Sismos a correr serán', Lista_sensores)
print('Los edificios a correr serán', DB_Edificios.index)

DB_out = pd.DataFrame(columns=(['ID_EDI', 'ID_SISX', 'ID_SISY', 'GM', 'PATH_OUT']))

# Tiempo de detención

sleep(time_to_sleep)
print(f'Se aplico sleep de {time_to_sleep} sec')

# Fin de array_tiempo de detencion


print('Antes de empezar el if de los multiprocesos')

if __name__ == '__main__' and files_creados == 1:

	count_edi = 0  # contador de los edificios para imprimir el la descripcion de tqdm
	total = len(DB_Edificios)  # Total de edificios para desc de tqdm

	procesos = []  # lista donde se guardan los procesos
	n_proces = 0  # contador de procesos

	sema = multiprocessing.Semaphore(Numero_procesos)  # Semaforo que limita el numero de procesos

	for ID_EDI in DB_Edificios.index:
		# for ID_EDI in tqdm(DB_Edificios.index, position=0):
		count_edi += 1

		for GM in tqdm(Lista_sensores, desc='Cargando Sismo de edificio {} --{}/{}'.format(ID_EDI, count_edi, total)):
			# for GM in tqdm(Lista_sensores, position= 1):

			path_out = os.path.join(Dir_outs, 'E' + str(ID_EDI))
			path_out = os.path.join(path_out, str(GM))

			fila_Edificio = DB_Edificios.loc[ID_EDI]
			GM_2_direction = DB_Sismos[DB_Sismos['N_SIS'] == GM]

			ID_SISX = GM_2_direction.index[0]
			ID_SISY = GM_2_direction.index[1]

			DB_out.loc[len(DB_out)] = [ID_EDI, ID_SISX, ID_SISY, GM, path_out]

			sema.acquire()  # hace un lok de lo procesos

			# p = threading.Thread(target= run_OpenSees,
			# args= (n_proces,fila_Edificio, GM_2_direction, GM,ID_EDI,
			# Dir_files, Dir_Opensees,list_file_run,list_file_lista_GM, sema)

			p = multiprocessing.Process(target=run_OpenSees,
										args=(n_proces,
											  fila_Edificio, GM_2_direction,
											  Dir_files, Dir_Opensees, Dir_outs,
											  list_file_run, list_file_lista_GM,
											  sema))

			if n_proces + 1 == len(list_file_run):
				n_proces = 0
			else:
				n_proces += 1

			procesos.append(p)
			p.start()

	for proc in procesos:
		proc.join()

	print('\n Fin de corridas de edificios\n')

	remove_files_process(list_file_run, list_file_lista_GM)

	print('Guardando datos...\n')

	DB_out.to_csv(os.path.join(Path_Data_base, file_out_DB),
				  index_label='id')

	tiempo_f = time()
	print('El array_tiempo que demoró fue:', tiempo_f - tiempo_i, 'Segundos')
