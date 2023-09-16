# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 11:46:45 2021

@author: Franklin
"""
import joblib
from libreria_OpenSees.Funciones_gen_out import filtrar_data_sis, filtrar_data_edi, crear_files_process, \
	remove_files_process, run_OpenSees
import pandas as pd
import os
import multiprocessing
from tqdm import tqdm
from time import time, sleep, strftime, gmtime
from datetime import date

if __name__ == '__main__':

	tiempo_i = time()  # Tiempo inicial

	time_to_sleep = 20  # Tiempo que dormirá programa para esperar la creación de arch
	Numero_procesos = 60  # numero de procesos en parelelo
	numero_copias_files = Numero_procesos + 20  # numero de copias que se realizaran

	# ----------DEFINIR FILES---------#

	# Ruta de la carpeta donde se guardan las bases de datos
	# retrocede la carpeta actual con lo 2 puntos
	# noinspection DuplicatedCode
	Path_Data_base = '../Base_datos'

	# File donde está el OpenSees
	Dir_files = os.getcwd()  # Ruta absula de carpeta actual
	Dir_Opensees_org = os.path.join(Dir_files, 'OpenSees.exe')  # ruta OpenSees.exe

	# Nombre de los files originales con parametros que se copiaran con el numero de procesos
	run_original = 'Run.tcl'
	GM_original = 'Lista_GM.tcl'

	# Funcion para crear la lista de archivos para correr
	list_file_run, list_file_lista_GM, list_opensees = crear_files_process(numero_copias_files,
																		   run_original, GM_original,
																		   copy_opensees=True,
																		   opensees_file_name=Dir_Opensees_org)

	# Nombre del file donde se guardaran las bases de datos
	file_out_DB = 'DB_out_MultiProcces.csv'  # Se guardará en la carpeta de base de datos
	# Nombre de la carpeta donde se guardarán las series de array_tiempo
	Dir_outs = 'DB_out_MultiProcces'
	# Nombre de la carpeta donde se guardaran
	path_historial = '../Base_datos/Historial'
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

	# TODO: VERIFICAR SI LOS SISMOS SE ESCOGIERON BIEN
	Lista_sensores, DB_Sismos = filtrar_data_sis(DB_Sismos, Tipo='lista', filtro='all')
	# Lista_sensores, DB_Sismos = filtrar_data_sis(DB_Sismos, Tipo='lista', filtro=range(15, 17))

	# Si se usa lista se guarda un numero mayor, es decir:
	# Lista : [4,5,6] se usaran los GM = [5,6,7]

	# TODO: VERIFICAR SI LOS EDIFICIOS SE ESCOGIERON BIEN
	DB_Edificios = filtrar_data_edi(DB_Edificios, Tipo='filtro', filtro=['H_Pisos', 2.5])
	DB_Edificios = DB_Edificios[0::20]
	# DB_Edificios = filtrar_data_edi(DB_Edificios, Tipo='lista', filtro=range(3))

	print('Los Sismos a correr serán', Lista_sensores)
	print('Los edificios a correr serán', DB_Edificios.index)

	# CREACION DE LOS DATAFRAMES NECESARIOS
	DB_out = pd.DataFrame(columns=(['ID_EDI', 'ID_SISX', 'ID_SISY', 'GM', 'PATH_OUT']))

	# Si el archivo existe no crear uno nuevo y apendizar
	apendice = False
	path_file_out_DB = os.path.join(Path_Data_base, file_out_DB)
	if not os.path.isfile(path_file_out_DB):
		previus_db_out = None
		DB_out.to_csv(path_file_out_DB,
					  index_label='id')
		id_db = 0
		# crar un dataframe para el historial
		DB_out_historial = DB_out.copy()
	else:
		previus_db_out = pd.read_csv(path_file_out_DB, index_col='id')
		id_db = max(previus_db_out.index) + 1
		apendice = True
		DB_out_historial = previus_db_out.copy()

	# CREAR NOMBRE Y DICCIONARIO DEL BUCKUP HISTORIAL
	fecha_hoy = date.today()
	hora_hoy = strftime('%H-%M-&S')
	nombre_archivo_historial = f'Genera_Output_Multi1_D{fecha_hoy}_H{hora_hoy}.hst'
	historial = {
		'desc': f'Se corrio el archivo Genera_Output_Multi1_D la fecha: {fecha_hoy} a las {hora_hoy}',
		'numero_sismos': len(Lista_sensores),
		'numero_edificios': len(DB_Edificios.index),
		'lista_sismos': Lista_sensores,
		'lista_edificios': DB_Edificios.index.to_numpy(),
		'numero de procesos': Numero_procesos,
		'DataBase_previa': previus_db_out
	}

	# Tiempo de detención
	sleep(time_to_sleep)
	print(f'Se aplico sleep de {time_to_sleep} sec')
	# Fin de array_tiempo de detencion

	# EMPIEZA MULTIPROCESOS
	print('Antes de empezar el if de los multiprocesos')

	total_sismo = len(Lista_sensores)
	is_break = False

	procesos = []  # lista donde se guardan los procesos
	n_proces = 0  # contador de procesos

	sema = multiprocessing.Semaphore(Numero_procesos)  # Semaforo que limita el numero de procesos

	for n_orden_actual, GM in enumerate(Lista_sensores):

		n_orden_actual += 1

		for id_edi in tqdm(DB_Edificios.index,
						   desc=f'Cargando edificio de sismo {GM} --{n_orden_actual}/{total_sismo}'):

			path_out_for_df = os.path.join(Dir_outs, f'S{GM}', f'E{id_edi}')
			path_out_for_OpenSees = path_out_for_df.replace('\\', '/')

			gm_2_direction = DB_Sismos[DB_Sismos['N_SIS'] == GM]
			fila_edificio = DB_Edificios.loc[id_edi]

			id_sisx = gm_2_direction.index[0]
			id_sisy = gm_2_direction.index[1]

			# GUARDADO DE LAS FILAS DE CADA ITERACION
			fila_db_out = DB_out.copy()
			# guarda una fila de los data frame
			fila_db_out.loc[id_db] = [id_edi, id_sisx, id_sisy, GM,
									  path_out_for_df]
			DB_out_historial.loc[id_db] = [id_edi, id_sisx, id_sisy, GM,
										   path_out_for_df]

			# GUARDAR LA FILA COMO ANEXO EN EL CSV
			fila_db_out.to_csv(path_file_out_DB,
							   index_label='id', mode='a', header=False)
			id_db += 1

			sema.acquire()  # hace un look de los procesos
			Dir_Opensees = list_opensees[n_proces]

			try:
				p = multiprocessing.Process(target=run_OpenSees,
											args=(n_proces,
												  fila_edificio, gm_2_direction,
												  Dir_files, Dir_Opensees, path_out_for_OpenSees,
												  list_file_run, list_file_lista_GM,
												  sema,
												  None, True))
			except:
				print('Ocurrio un error\n')
				print('Eliminando las copias de archivos creadas\n')
				is_break = True
				remove_files_process(list_file_run, list_file_lista_GM)
				break

			# vuelve a usar algun file despues de completar todos
			if n_proces + 1 == numero_copias_files:
				n_proces = 0
			else:
				n_proces += 1

			# pasos finales para los multiprocesos
			procesos.append(p)
			p.start()

		if is_break is True:
			break

	for proc in procesos:
		proc.join()

	print('\n Fin de corridas de edificios\n')
	remove_files_process(list_file_run, list_file_lista_GM, list_opensees)

	tiempo_f = time()
	tiempo_total = tiempo_f - tiempo_i
	tiempor_formato_h_m_s = strftime('%W semanas - (%d-1 dias) - %H:%M:%S ', gmtime(tiempo_total))
	print(f'El array_tiempo que demoro en generar los datos fue {tiempor_formato_h_m_s}')

	print('Guardando historial...\n')
	historial['array_tiempo'] = tiempo_total
	historial['database_generada'] = DB_out_historial

	if not os.path.isdir(path_historial):
		os.mkdir(path_historial)

	joblib.dump(historial,
				os.path.join(path_historial, nombre_archivo_historial),
				compress=3)
