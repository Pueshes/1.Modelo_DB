import gc
import math
import os
import time

import psutil
import joblib

import GroundMotion_lib.deeplearning as dl
import GroundMotion_lib.importadores as imp

DIR_EDIFICIOS = 'Objetos_Guardados/objetos_edificios'

print(DIR_EDIFICIOS)

SIZE_PARTICION_EDIFICIOS = 10
N_PROCESOS = 2
processing_obj = dl.ProcessingObject()

nombre_archivo = "DB_out_3Pisos.csv"

with open(nombre_archivo, "r") as archivo:
    lista_DB = []
    next(archivo, None)
    for linea in archivo:
        # Remover salto de línea
        linea = linea.rstrip()
        # Ahora convertimos la línea a arreglo con split
        separador = ";"
        lista = linea.split(";")
        # Tenemos la lista. En la 0 tenemos el ID
        nombre = int(lista[0])
        lista_DB.append(nombre)

print(lista_DB)

index_total = lista_DB

cantidad_total = len(index_total)

particiones = math.ceil(cantidad_total / SIZE_PARTICION_EDIFICIOS)

current_process = psutil.Process()
subprocess_before = set([p.pid for p in current_process.children(recursive = True)])

for particion in range(particiones):
    print(F'CORRIENDO EL PAQUETE NUMERO {particion}')
    inicio = particion * SIZE_PARTICION_EDIFICIOS
    fin = (particion + 1) * SIZE_PARTICION_EDIFICIOS
    index_edificio = index_total[inicio:fin]
    # index_edificio = index_total[inicio: fin * 15: 20]

    ti = time.time()
    lista_edificio = imp.importar_edi_multi(DIR_EDIFICIOS, index_import = index_edificio,
                                            verbose = 2, n_procesos = N_PROCESOS)
    tf = time.time()

    print(f'se demoró en importar {tf - ti}seg\n')

    processing_obj.agregar_edificios(lista_edificio)

    print('Borrando lista_edificios:')
    del lista_edificio

    print('Aplicando gc.collect\n')
    gc.collect(0)
    gc.collect(1)
    gc.collect(2)

    print('fiteando los datos\n')
    processing_obj.fit_all()
    processing_obj.delete_edificios_list()

subprocess_after = set([p.pid for p in current_process.children(recursive = True)])
for subproceso in subprocess_after - subprocess_before:
    print(f'Cerrando subproceso {subproceso}')
    psutil.Process(subproceso).terminate()

# TODO: falta guardar index total para ser usado despues

ruta_guardado = 'data_3Pisos'

processing_obj.processing_all_data_bruta()
processing_obj.fit_train_test_split(train_size = 0.9, random_state = 5)
processing_obj.save_important(ruta_guardado)
joblib.dump(index_total, ruta_guardado)
