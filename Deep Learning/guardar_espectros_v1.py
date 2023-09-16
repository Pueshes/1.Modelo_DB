if __name__ == '__main__':
    import os
    from time import time, sleep

    import GroundMotion_lib.database as db
    import numpy as np
    import pandas as pd

    db.print_prueba()

    NUMERO_PROCESOS = 20
    CHUNK_SIZE = 1
    PATH_DATA_BASE = '../Base_datos'
    PATH_GUARDADO = 'Objetos_Guardados/BaseDatosJunto5000_25_02_22.db'

    sismos = pd.read_csv(os.path.join(PATH_DATA_BASE, 'DB_Sismos.csv'), index_col = 'id')
    # sismos = sismos.iloc[1:5]
    # sismos.rgDataBase.import_all_registros(path_of_dir = pathDataBase)
    # print(sismos['REGISTRO_ARRAY'].iloc[0]._tiempoArray.shape)
    # print(sismos['REGISTRO_ARRAY'].iloc[0]._serieArray.shape)
    # print(sismos['REGISTRO_ARRAY'].iloc[0])

    # pathDataBase = '../../Base_datos'
    edi = pd.read_csv(os.path.join(PATH_DATA_BASE, 'DB_Edificios.csv'), index_col = 'id')
    # edi = edi.iloc[1:20]
    # # edi.eDataBase.crear_all_edificios()
    # edi.DataBase.filtrar_by_index([1, 2, 3])

    out = pd.read_csv(os.path.join(PATH_DATA_BASE, 'DBout-21.12-5069.csv'), index_col = 'id')

    # out = out.iloc[0::20]
    # out = out.iloc[200:300]
    # out = out.iloc[10:12]

    print('DATOS IMPORTADOS\n')

    tiempoi = time()

    print('Enlazar base de datos\n')
    out.RegNivDB.enlazar_basedatos(sismos, edi)

    print('filtrando datos')
    out.RegNivDB.filtrar_edificios()
    out.RegNivDB.filtrar_registro_sismico()

    out.RegNivDB.crear_objetos_db_enlazados(path_of_dir = PATH_DATA_BASE)

    print('importando datos')
    # out.RegNivDB.import_all_multi(path_of_dir = PATH_DATA_BASE, progress_bar = True,
    #                               n_procesos = NUMERO_PROCESOS, chunk_size = 2)

    out.RegNivDB.import_all(path_of_dir = PATH_DATA_BASE
                            # , progress_bar = True,
                                  # n_procesos = NUMERO_PROCESOS, chunk_size = 2)
                            )

    PERIODOS = np.concatenate((np.arange(0.05, 1, 0.01), np.arange(1, 3, 0.025)))

    tiempof = time()
    print(f'Demoro en importar todos los datos {tiempof - tiempoi} segundos')
    print(f'Empzando con la generación de espectros')

    print('pausa de 5 segundos')
    sleep(5)

    tiempoi = time()
    out.RegNivDB.crear_all_espectros(PERIODOS, progress_bar = True)
    tiempof = time()
    print(f'Demoro en crear sin multiprocesos{tiempof - tiempoi} segundos')

    # MULTIPROCESOS
    tiempoi = time()
    out.RegNivDB.crear_all_espectros_multi(PERIODOS, progress_bar = True,
                                           n_procesos = NUMERO_PROCESOS, chunk_size = CHUNK_SIZE)
    tiempof = time()
    print(f'Demoro en crear con multiprocesos {tiempof - tiempoi} segundos')
    # out.RegNivDB.save_object(PATH_GUARDADO)

    # edificio1: ed.Edificio = out.iloc[0]['EDIFICIO_ACEL_DATA']
    # nivel1 = edificio1.niveles[1]
    #
    # sys.getsizeof(edificio1)
