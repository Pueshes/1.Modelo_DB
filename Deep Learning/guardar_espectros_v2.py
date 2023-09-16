if __name__ == '__main__':
    import os
    import math
    from time import time, sleep

    import GroundMotion_lib.database as db
    import numpy as np
    import pandas as pd

    db.print_prueba()

    NUMERO_PROCESOS = 29
    NUMERO_PROCESOS_IMPORT = 29
    CHUNK_SIZE = 20
    SIZE_PARTICION_DATA_OUT = 200
    PAUSA_POR_PARTICION = 1

    PATH_DATA_BASE = '../Base_datos'
    PATH_GUARDADO = 'Objetos_Guardados'
    PATH_GUARDADO2 = os.path.join(PATH_GUARDADO, 'objetos_edificios')

    PERIODOS = np.linspace(0.05, 2, 40)

    sismos = pd.read_csv(os.path.join(PATH_DATA_BASE, 'DB_Sismos.csv'), index_col = 'id')
    edi = pd.read_csv(os.path.join(PATH_DATA_BASE, 'DB_Edificios.csv'), index_col = 'id')
    # salida_registros = pd.read_csv(os.path.join(PATH_DATA_BASE, 'DBout-21.12-5069.csv'), index_col = 'id')
    salida_registros = pd.read_csv(os.path.join(PATH_DATA_BASE, 'DBout-22.03-11302.csv'), index_col = 'id')
    salida_registros = salida_registros.iloc[5070::].copy(deep=True)

    print('DATOS IMPORTADOS\n')

    particiones = math.ceil(len(salida_registros) / SIZE_PARTICION_DATA_OUT)

    for particion in range(particiones):
        inicio = particion * SIZE_PARTICION_DATA_OUT
        fin = (particion + 1) * SIZE_PARTICION_DATA_OUT
        data_frame_partido = salida_registros.iloc[inicio:fin].copy(deep=True)

        tiempoi = time()

        print(f'Enlazar base de datos de particion {particion}\n')
        data_frame_partido.RegNivDB.enlazar_basedatos(sismos, edi)

        print(f'filtrando datos')
        data_frame_partido.RegNivDB.filtrar_edificios()
        data_frame_partido.RegNivDB.filtrar_registro_sismico()

        data_frame_partido.RegNivDB.crear_objetos_db_enlazados(path_of_dir = PATH_DATA_BASE)

        print('importando datos')
        print(f'usando {NUMERO_PROCESOS} procesos')
        data_frame_partido.RegNivDB.import_all_multi(path_of_dir = PATH_DATA_BASE, progress_bar = True,
                                                     n_procesos = NUMERO_PROCESOS_IMPORT, chunk_size = CHUNK_SIZE)

        tiempof = time()
        print(f'Demoro en importar todos los datos de la particion {particion}: {tiempof - tiempoi} segundos')
        print(f'Empzando con la generación de espectros')

        print(f'pausa de {PAUSA_POR_PARTICION} segundos')
        sleep(PAUSA_POR_PARTICION)

        # MULTIPROCESOS
        tiempoi = time()
        print(f'usando {NUMERO_PROCESOS} procesos')
        descripcion = f'Importando y guardando espectros con multiprocesos-particion:{particion}/{particiones}'
        data_frame_partido.RegNivDB.crea_guardar_all_espectros_multi(PERIODOS, progress_bar = True,
                                                                     dir_guardado = PATH_GUARDADO2,
                                                                     n_procesos = NUMERO_PROCESOS,
                                                                     desc = descripcion,
                                                                     joblib_compress = 3)
        tiempof = time()
        print(f'Demoro en crear con multiprocesos {tiempof - tiempoi} segundos')
