import gc
import math
import os
import time

import psutil

import GroundMotion_lib.deeplearning as dl
import GroundMotion_lib.importadores as imp

DIR_EDIFICIOS = 'Objetos_Guardados/objetos_edificios'
SIZE_PARTICION_EDIFICIOS = 250
N_PROCESOS = 29
processing_obj = dl.ProcessingObject()

cantidad_total = len(os.listdir(DIR_EDIFICIOS))

# Trabajo para vicente
# Importar base de datos Bd_out_12_21 con pandas
# Creas una nueva columna que se llame n_pisos
# importas DB_edificios
# Llenas los datos de DB_Edificios a la columna n_pisos
# for id(1566) in ID_EDI:
#                 DB_Edificos.loc
#     n_pisos= DB_Edificios.iloc[1566,'#N_Pisos']
#     n_pisos=5
#     Bd_out_12_21[fila 1423, N_pisos] = 5

# filtrar base de datos para 3 pisos

# index_total= list(Bd_3 pisos[id])

index_total = list(range(cantidad_total))

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

processing_obj.processing_all_data_bruta()
processing_obj.fit_train_test_split(train_size = 0.9, random_state = 5)
processing_obj.save_important('Objetos_Guardados/data5000')
