import os
import shutil
import time
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import subprocess
from libreria_OpenSees.Funciones_gen_out import filtrar_data_sis, filtrar_data_edi, Define_Edi, \
	Define_Sis
from os import path

# RUTAS DE ARCHIVOS IMPORTANTES
BASE_DATOS = '../Base_datos'
NOMBRE_SISMO = 'DB_Sismos.csv'
NOMBRE_EDIFICIOS = 'DB_Edificios.csv'
DIR_FILES = os.getcwd()
DIR_OPENSEES = path.join(DIR_FILES, 'OpenSees.exe')
DIR_OUT = 'TEMP'
FILE_RUN = 'Run.tcl'
FILE_GM = 'Lista_GM.tcl'

# CARGAR LAS BASES DE DATOS
db_sismos = pd.read_csv(path.join(BASE_DATOS, NOMBRE_SISMO), index_col='id')
db_edificios = pd.read_csv(path.join(BASE_DATOS, NOMBRE_EDIFICIOS), index_col='id')

# FILTRAR LAS BASES DE DATOS COMO EN GENERA OUTPUT
db_edificios = filtrar_data_edi(db_edificios, Tipo='filtro', filtro=('H_Pisos', 2.5))
db_edificios = db_edificios[(db_edificios['#N_Pisos'] >= 7) & (db_edificios['#N_Pisos'] < 25)]
db_edificios = db_edificios[0::20]

# EDIFICIO MÁS PEQUEÑO Y MÁS GRANDE
edi_peque = db_edificios.iloc[0]
edi_grande = db_edificios.iloc[-1]

# CREAR GRAFICA DE BARRAS

db_plot = db_edificios.groupby(['#N_Pisos']).count()
index_plot = np.arange(len(db_plot)) + 0.5
plot1 = plt.bar(index_plot, db_plot['T'], width=0.5)
# plt.xlabel('Numero de pisos de edificio')
plt.ylabel('Numero de edificios')
plt.title(f'Grafico de barras de cantidad de edificios por piso - total:{len(db_edificios)}')
label_sticks = db_plot.index.to_numpy()
label_sticks = label_sticks.astype(int)
# plt.xticks(db_plot.index, label_sticks)
plt.xticks([])

# GRAFICAR UNA TABLA CON LOS DATOS

columnas = label_sticks
filas = ['N_pisos', 'N_edificios', 'Tiempo_min (s)', 'Tiempo_max (s)']
text = list()
text.append(columnas)
text.append(db_plot['T'])  # Cantidad de edificios por pisp
text.append(['-' for _ in range(len(columnas))])
text.append(['-' for _ in range(len(columnas))])
text = np.array(text)

# PLOT DE LA TABLA Y GUARDADO
text[2, 0] = 20.867
text[2, -1] = 111748.816
text[3, 0] = 31.885
text[3, -1] = 108867.1
tabla = plt.table(cellText=text, rowLabels=filas, cellLoc='center')
plt.savefig('N_pisosVS_Edificios.png', bbox_inches='tight')

# SISMO MÁS CORTO Y MÁS LARGO
n_points_min = db_sismos['N_POINTS_PROCES2'].min()
n_points_max = db_sismos['N_POINTS_PROCES2'].max()

n_min, db_sismo_min = filtrar_data_sis(db_sismos, Tipo='filtro',
									   filtro=('N_POINTS_PROCES2', n_points_min))
n_max, db_sismo_max = filtrar_data_sis(db_sismos, Tipo='filtro',
									   filtro=('N_POINTS_PROCES2', n_points_max))

# CORRER EDIFICIO PEQUEÑO CON SISMO CORTOS

ti1 = time.time()
Define_Edi(edi_peque, path.join(DIR_FILES, FILE_RUN, ), DIR_OUT)
Define_Sis(db_sismo_min, int(n_min), FILE_GM,
		   COL_DIR='PATH_DIR_PROCES2', COL_DT='DT_PROCES2')
subprocess.run([DIR_OPENSEES, FILE_RUN], capture_output=True)
tf1 = time.time()
tt_min_peque = tf1 - ti1
print(f'el mas corto demoro {tt_min_peque}')

# CORRER EDIFICIO PEQUEÑO CON SISMO LARGO

ti1 = time.time()
Define_Edi(edi_peque, path.join(DIR_FILES, FILE_RUN, ), DIR_OUT)
Define_Sis(db_sismo_max, int(n_max), FILE_GM,
		   COL_DIR='PATH_DIR_PROCES2', COL_DT='DT_PROCES2')
subprocess.run([DIR_OPENSEES, FILE_RUN], capture_output=True)
tf1 = time.time()
tt_max_peque = tf1 - ti1
print(f'el mas corto demoro {tt_max_peque}')

# CORRER EDIFICIO GRANDE CON SISMO CORTO

ti2 = time.time()
Define_Edi(edi_grande, path.join(DIR_FILES, FILE_RUN, ), DIR_OUT)
Define_Sis(db_sismo_min, int(n_min), FILE_GM,
		   COL_DIR='PATH_DIR_PROCES2', COL_DT='DT_PROCES2')
subprocess.run([DIR_OPENSEES, FILE_RUN], capture_output=True)
tf2 = time.time()
tt_min_gran = tf2 - ti2
print(f'el mas largo demoro {tt_min_gran}')

# # CORRER EDIFICIO GRANDE CON SISMO LARGO

# ti2 = time.time()
# Define_Edi(edi_grande, path.join(DIR_FILES, FILE_RUN, ), DIR_OUT)
# Define_Sis(db_sismo_max, int(n_max), FILE_GM,
# 		   COL_DIR='PATH_DIR_PROCES2', COL_DT='DT_PROCES2')
# subprocess.run([DIR_OPENSEES, FILE_RUN], capture_output=True)
# tf2 = time.time()
# tt_max_gran = tf2 - ti2
# print(f'el mas largo demoro {tt_max_gran}')


# BORRAR LA CARPETA TEMPORAL
# shutil.rmtree(DIR_OUT)

# ULTIMOS DATOS DE LA TABLA
text[2, 0] = tt_min_peque
text[2, -1] = tt_min_gran
text[3, 0] = tt_max_peque
text[3, -1] = 108867.1
tabla = plt.table(cellText=text, rowLabels=filas, cellLoc='center')
plt.savefig('N_pisosVS_Edificios.png', bbox_inches='tight')
