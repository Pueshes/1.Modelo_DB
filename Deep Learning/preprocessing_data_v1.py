import gc
import time

import psutil

import GroundMotion_lib.deeplearning as dl
import GroundMotion_lib.importadores as imp

current_process = psutil.Process()
subprocess_before = set([p.pid for p in current_process.children(recursive = True)])

ti = time.time()
# lista_edificio = imp.importar_edi('Objetos_prueba/edificios_prueba_multi_compress3')
# lista_edificio = imp.importar_edi('Objetos_Guardados/objetos_edificios')
lista_edificio = imp.importar_edi_multi('Objetos_Guardados/objetos_edificios', verbose = 2, n_procesos = 30)
tf = time.time()

print(f'se demoró en importar {tf - ti}seg')


data_edificios = dl.ProcessingObject()
data_edificios.agregar_edificios(lista_edificio)

print('Borrando lista_edificios\n')
del lista_edificio
subprocess_after = set([p.pid for p in current_process.children(recursive = True)])

for subproceso in subprocess_after - subprocess_before:
    print(f'Cerrando subproceso {subproceso}')
    psutil.Process(subproceso).terminate()

print('Aplicando gc.collect\n')
gc.collect(0)
gc.collect(1)
gc.collect(2)

print('aplicando train_test_split\n')
data_edificios.fit_train_test_split(train_size = 0.9, random_state = 5)

data_edificios.fit_all()
data_edificios.processing_all_data_bruta()

data_edificios.save_important('Objetos_Guardados/data5000')
