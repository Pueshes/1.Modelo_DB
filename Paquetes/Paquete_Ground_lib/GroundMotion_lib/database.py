import copy
import multiprocessing as multi
import os.path

import joblib
import numpy as np
import pandas as pd
from mapply.mapply import mapply
from tqdm import tqdm

import GroundMotion_lib.edificio as ed
import GroundMotion_lib.importadores as imp


def print_prueba():
    print('SE IMPORTO EL MODULO GroundMotion_lib.database CORRECTAMENTE')


@pd.api.extensions.register_dataframe_accessor('DataBase')
class DataBase:

    def __init__(self, pandas_obj: pd.DataFrame):
        self._obj = pandas_obj

    def _validar_objeto(self, columnas: list, extension: str):
        for name in columnas:
            if name not in self._obj.columns:
                raise ValueError(f'El objeto no se puede usar con {extension}')

    def filtrar_by_index(self, lista_filtro: list or np.ndarray or tuple or pd.Series):

        dataframeFiltrado = self._obj.loc[lista_filtro]
        return dataframeFiltrado

    def save_object(self, path_save, **kwargs):
        joblib.dump(self._obj, path_save, **kwargs)


@pd.api.extensions.register_dataframe_accessor('RegSueDB')
class RegSueDB(DataBase):

    def __init__(self, pandas_obj: pd.DataFrame):
        super().__init__(pandas_obj)
        self._columnasValidacion = ['NOMBRE_SIS', 'N_SIS', 'DIRECCION',
                                    'PATH_DIR_PROCES2', 'DT_PROCES2', 'N_POINTS_PROCES2']
        # self._validar_objeto(self._columnasValidacion, 'RegSueDB')

    @staticmethod
    def _crear_nombre_automatico(fila_of_dataframe, nombre):
        if nombre == 'auto':
            nombreFin = f'{fila_of_dataframe["NOMBRE_SIS"]}'
            nombreFin += f'-{fila_of_dataframe["N_SIS"]}'
            nombreFin += f'-{fila_of_dataframe["DIRECCION"]}'
        else:
            nombreFin = nombre
        return nombreFin

    def import_fila(self, fila_of_dataframe, column_of_path: str,
                    column_of_dt: str, nombre: str = None, path_of_dir: str = ''):
        """
        Importa 1 fila del database, se usa

        Parameters
        ----------
        fila_of_dataframe
        column_of_path
        column_of_dt
        nombre
        path_of_dir

        Returns
        -------

        """

        importador = imp.ImportadorSeries()
        path = fila_of_dataframe[column_of_path]
        path = os.path.join(path_of_dir, path)
        dt = fila_of_dataframe[column_of_dt]

        dataframe_id = fila_of_dataframe.name
        dataframe_info= dict(fila_of_dataframe)

        nombreFin = self._crear_nombre_automatico(fila_of_dataframe, nombre)
        filaImportada = importador.import_t1(path, dt, nombreFin, database_id = dataframe_id,
                                             database_info = dataframe_info)

        return filaImportada

    def import_all_registros(self, column_of_path: str = 'PATH_DIR_PROCES2',
                             column_of_dt: str = 'DT_PROCES2',
                             nombre_columna_importada: str = 'REGISTRO_ACELERACION',
                             path_of_dir: str = ''):

        self._obj[nombre_columna_importada] = self._obj.apply(self.import_fila, axis = 1,
                                                              args = (column_of_path, column_of_dt,
                                                                      'auto', path_of_dir))


@pd.api.extensions.register_dataframe_accessor('EdiDB')
class EdiDB(DataBase):

    def __init__(self, pandas_obj: pd.DataFrame):
        super().__init__(pandas_obj)
        self.nombreColumnaEdificio = None

    @staticmethod
    def crear_edificio_fila(fila_dataframe):
        edificio = ed.Edificio(
                n_pisos = fila_dataframe['#N_Pisos'],
                periodo = fila_dataframe['T'],
                n_vanosx = fila_dataframe['N_VanosX'],
                n_vanosy = fila_dataframe['N_VanosY'],
                h_pisos = fila_dataframe['H_Pisos'],
                l_vanox = fila_dataframe['L_VanoX'],
                l_vanoy = fila_dataframe['L_VanoY'],
                h_vigax = fila_dataframe['H_VigaX'],
                h_vigay = fila_dataframe['H_VigaY'],
                b_vigax = fila_dataframe['B_VigaX'],
                b_vigay = fila_dataframe['B_VigaY'],
                h_colum = fila_dataframe['H_Colum'],
                b_colum = fila_dataframe['B_Colum']
                )

        return edificio

    def crear_all_edificios(self, nombre_columna_edificio: str = 'EDIFICIO'):
        self.nombreColumnaEdificio = nombre_columna_edificio
        self._obj[nombre_columna_edificio] = self._obj.apply(self.crear_edificio_fila, axis = 1)


@pd.api.extensions.register_dataframe_accessor('RegNivDB')
class RegNivDB(DataBase):

    def __init__(self, pandas_obj: pd.DataFrame):
        super().__init__(pandas_obj)
        self._columnasValidacion = ['ID_EDI', 'ID_SISX', 'IS_SISY',
                                    'GM', 'PATH_OUT']

        # self._validar_objeto(self._columnasValidacion, 'RegNivDB')

        self.db_registro_suelo = None
        self.db_edificios = None

        self.nombreColumnaEdificio = None

    # @property
    # def db_registro_suelo(self):
    #     return self._db_registro_suelo
    #
    # @db_registro_suelo.setter
    # def db_registro_suelo(self, valor):
    #     fn.controlerror_isinstance(valor, pd.DataFrame)
    #     self._db_registro_suelo = valor
    #
    # @property
    # def db_edificios(self):
    #     return self._db_edificios
    #
    # @db_edificios.setter
    # def db_edificios(self, valor):
    #     fn.controlerror_isinstance(valor, pd.DataFrame)
    #     self._db_edificios = valor

    @staticmethod
    def _filtrar_edificios_by_id(dataframe_de_filtro: pd.DataFrame,
                                 dataframe_filtrado: pd.DataFrame,
                                 columna_de_filtro: str):
        indicesDeFiltro = dataframe_de_filtro[columna_de_filtro].unique()
        dataframeFiltrado = dataframe_filtrado.DataBase.filtrar_by_index(indicesDeFiltro)
        return dataframeFiltrado

    @staticmethod
    def _filtrar_registro_sismico_by_id(dataframe_de_filtro: pd.DataFrame,
                                        dataframe_filtrado: pd.DataFrame,
                                        columna_de_filtrox: str,
                                        columna_de_filtroy: str):
        indicesDeFiltroX = dataframe_de_filtro[columna_de_filtrox].unique()
        indicesDeFiltroY = dataframe_de_filtro[columna_de_filtroy].unique()

        indicesDeFiltro = np.append(indicesDeFiltroX, indicesDeFiltroY)
        dataframeFiltrado = dataframe_filtrado.DataBase.filtrar_by_index(indicesDeFiltro)

        return dataframeFiltrado

    def _crear_espectros_fila(self, filadf, periodo_array,
                              amortiguamiento: float = 0.05, tipo_metodo: str = 'Newmark1',
                              tipo_espectro: str = 'espectros', lista_guardado = None, sema = None):

        edficio_fila = filadf[self.nombreColumnaEdificio]
        edficio_fila.crear_espectros_niveles(periodo_array,
                                             amortiguamiento,
                                             tipo_metodo,
                                             tipo_espectro)

        if lista_guardado is not None:
            lista_guardado.append(edficio_fila)

            if sema is not None:
                sema.release()

            return
        else:
            return edficio_fila

    def _crear_guardar_espectros_fila(self, filadf, periodo_array,
                                      amortiguamiento: float = 0.05, tipo_metodo: str = 'Newmark1',
                                      tipo_espectro: str = 'espectros', dir_save = '',
                                      sema: multi.Semaphore = None, joblib_compress = 3):

        if not os.path.isdir(dir_save) and dir_save != '':
            os.mkdir(dir_save)

        edficio_fila: ed.Edificio = filadf[self.nombreColumnaEdificio]
        edficio_fila.crear_espectros_niveles(periodo_array,
                                             amortiguamiento,
                                             tipo_metodo,
                                             tipo_espectro)

        nombre_edificio = f'{edficio_fila.database_id:05d}-edi_{filadf["ID_EDI"]}-sis_{filadf["GM"]}.edi'
        path_edficio = os.path.join(dir_save, nombre_edificio)
        joblib.dump(edficio_fila, path_edficio, compress = joblib_compress)

        if sema is not None:
            sema.release()

    def enlazar_basedatos(self, bd_registro_suelo: pd.DataFrame, bd_edificios: pd.DataFrame):
        """
        Agrega bases datos al objeto Pandas para luego ser usado en otras funciones

        Parameters:
        ----------
        bd_registro_suelo: pd.DataFrame
            Base de datos con la infomacion referente a los registros sismicos del suelo
        bd_edificios: pd.Dataframe
            Base de datos con la informacion referente a los edificios a los que se aplica el movimiento sismico
        """
        self.db_registro_suelo = bd_registro_suelo
        self.db_edificios = bd_edificios

    def filtrar_edificios(self):
        """
        Filtra la base de datos de edificios guardados con los id del presente Dataframe en la columna 'ID_EDI'
        el dataframe filtrado se sobreescribe en el atributo db_edificios

        Returns:
        -------
            dataframe_filtrado
        """
        dataFrameFiltrado = self._filtrar_edificios_by_id(self._obj, self.db_edificios, 'ID_EDI')
        self.db_edificios = dataFrameFiltrado

        return dataFrameFiltrado

    def filtrar_registro_sismico(self):
        """
        Filtra la base de datos de edificios guardados con los id del presente Dataframe
        en la columna 'ID_SISX' y 'ID_SISY'
        el dataframe filtrado se sobreescribe en el atributo db_registro_suelo

        Returns:
        -------
            dataframe_filtrado
        """
        dataframeFiltrado = self._filtrar_registro_sismico_by_id(self._obj, self.db_registro_suelo,
                                                                 'ID_SISX', 'ID_SISY')
        self.db_registro_suelo = dataframeFiltrado

        return dataframeFiltrado

    def crear_objetos_db_enlazados(self, path_of_dir = ''):
        """
        Crea los objetos de serietiempo y edificios de la libreria GroundMotion_lib y las guarda en sus respectivos
        base de datos.
        Parameters:
        ----------
        path_of_dir: str
            ruta del directorio donde se guardan los registros sismicos.
        Returns:
        -------
            retorna las bases de datos de edificios y los registros sismicos de suelo
            (db_edificio, db_registro_suelo
        """
        self.db_edificios.EdiDB.crear_all_edificios()
        self.db_registro_suelo.RegSueDB.import_all_registros(path_of_dir = path_of_dir)

        return self.db_edificios, self.db_registro_suelo

    def crear_all_espectros(self, periodo_array: list or tuple or np.ndarray,
                            amortiguamiento: float = 0.05, tipo_metodo: str = 'Newmark1',
                            tipo_espectro: str = 'espectros', progress_bar = False,
                            **progress_kwargs):
        """
        Crea los espectros de los objetos edificio importados en el presente DataFrame.
        Los nuevos objetos quedan guardados en el dataframe.

        Parameters:
        ----------
        periodo_array: list or tuple or np.ndarray
            iterable con los valores de los periodos a calcular
        amortiguamiento: float
            valor de amortiguamiento para el calculo de los espectros
        tipo_metodo: str {Newmark1, Newmark2, PieceWise}
            metodo numerico a usar para el calculo de espectros
        tipo_espectro: str {espectros, pseudo}
            tipo de espectro, si se desea espectros o pseudo espectros
        progress_bar: bool
            si se desea mostrar el progress_bar
        progress_kwargs:
            kwargs usados en el progress_bar

        Returns:
        -------
            retorna el mismo DataFrame actualizado
        """

        tqdm.pandas(disable = not progress_bar, **progress_kwargs)
        self._obj[self.nombreColumnaEdificio] = self._obj.progress_apply(self._crear_espectros_fila,
                                                                         args = (periodo_array, amortiguamiento,
                                                                                 tipo_metodo, tipo_espectro),
                                                                         axis = 1)

        return self._obj

    def crear_guardar_all_espectros(self, periodo_array, amortiguamiento: float = 0.05,
                                    tipo_metodo: str = 'Newmark1', tipo_espectro: str = 'espectros',
                                    progress_bar = False, dir_guardado: str = '', joblib_compress = 3,
                                    **progress_kwargs):
        """
        Crea los espectros de los objetos edificio importados en el presente DataFrame.
        Los nuevos objetos quedan guardados en el dataframe.

        Parameters:
        ----------
        periodo_array: list or tuple or np.ndarray
            iterable con los valores de los periodos a calcular
        amortiguamiento: float
            valor de amortiguamiento para el calculo de los espectros
        tipo_metodo: str {Newmark1, Newmark2, PieceWise}
            metodo numerico a usar para el calculo de espectros
        tipo_espectro: str {espectros, pseudo}
            tipo de espectro, si se desea espectros o pseudo espectros
        progress_bar: bool
            si se desea mostrar el progress_bar
        dir_guardado: str
            nombre del directorio donde se desea guardar los espectros
        progress_kwargs:
            kwargs usados en el progress_bar

        """

        tqdm.pandas(disable = not progress_bar, **progress_kwargs)
        self._obj.progress_apply(self._crear_guardar_espectros_fila,
                                 args = (periodo_array, amortiguamiento, tipo_metodo,
                                         tipo_espectro, dir_guardado, None, joblib_compress), axis = 1)

    # primero probar con un pool
    # probar con el procedimiento normal y devolviendo una lista
    #

    # def crear_all_espectros_multi(self, periodo_array,
    #                               amortiguamiento: float = 0.05, tipo_metodo: str = 'Newmark1',
    #                               tipo_espectro: str = 'espectros', progress_bar = False,
    #                               n_procesos = -1, max_chunks_per_worker = 8, chunk_size = 100):
    #
    #     # multiprocessing_imap(self._crear_espectros_fila, self._obj,
    #     #                      args = (periodo_array, amortiguamiento, tipo_metodo, tipo_espectro),
    #     #                      progressbar = progress_bar, n_workers = n_procesos)
    #
    #     retorno_mapply = mapply(self._obj, self._crear_espectros_fila, axis = 1,
    #                             args = (
    #                                     periodo_array, amortiguamiento, tipo_metodo, tipo_espectro),
    #                             progressbar = progress_bar, n_workers = n_procesos,
    #                             max_chunks_per_worker = max_chunks_per_worker,
    #                             chunk_size = chunk_size)
    #
    #     self._obj[self.nombreColumnaEdificio] = retorno_mapply
    #
    #     return self._obj

    # # POOL
    # def crear_all_espectros_multi(self, periodo_array,
    #                               amortiguamiento: float = 0.05, tipo_metodo: str = 'Newmark1',
    #                               tipo_espectro: str = 'espectros', progress_bar = False,
    #                               n_procesos = 3, chunk_size = 100):
    #
    #     iterable = [(fila_dataframe, periodo_array, amortiguamiento, tipo_metodo, tipo_espectro) for
    #                 index, fila_dataframe in self._obj.iterrows()]
    #
    #     with multi.Pool(n_procesos) as pool_obj:
    #         lista_edificios = pool_obj.starmap(self._crear_espectros_fila, iterable, chunksize = chunk_size)
    #
    #     self._obj[self.nombreColumnaEdificio] = lista_edificios
    #
    #     return self._obj

    # MULTIPROCEES NORMAL, NO SUPERA LA RAM PERO NO USA LOS 20 PROCESOS, SE USARÁ GUARDANDO EL OBJETO DE CADA EDIFICIO
    # noinspection DuplicatedCode
    def crear_all_espectros_multi(self, periodo_array,
                                  amortiguamiento: float = 0.05, tipo_metodo: str = 'Newmark1',
                                  tipo_espectro: str = 'espectros', progress_bar = False,
                                  n_procesos = 3, **progress_kwargs):

        if n_procesos == 0:
            sema = None
        else:
            sema = multi.Semaphore(n_procesos)

        procesos = []
        manager = multi.Manager()
        resultados = manager.list()

        for index in tqdm(range(len(self._obj)), disable = not progress_bar,
                          **progress_kwargs):

            if sema is not None:
                sema.acquire()

            fila = self._obj.iloc[index]
            p = multi.Process(target = self._crear_espectros_fila,
                              args = (fila, periodo_array, amortiguamiento,
                                      tipo_metodo, tipo_espectro, resultados, sema))

            procesos.append(p)
            p.start()

        for proceso in procesos:
            proceso.join()

        self._obj[self.nombreColumnaEdificio] = resultados

        return self._obj

    # noinspection DuplicatedCode
    def crea_guardar_all_espectros_multi(self, periodo_array, amortiguamiento: float = 0.05,
                                         tipo_metodo: str = 'Newmark1', tipo_espectro: str = 'espectros',
                                         progress_bar = False, dir_guardado: str = '',
                                         n_procesos = 3, joblib_compress = 3, **progress_kwargs):

        if n_procesos == 0:
            sema = None
        else:
            sema = multi.Semaphore(n_procesos)

        procesos_list = []

        for index in tqdm(range(len(self._obj)), disable = not progress_bar,
                          **progress_kwargs):

            if sema is not None:
                sema.acquire()

            fila = self._obj.iloc[index]
            p = multi.Process(target = self._crear_guardar_espectros_fila,
                              args = (fila, periodo_array, amortiguamiento,
                                      tipo_metodo, tipo_espectro, dir_guardado, sema, joblib_compress))

            procesos_list.append(p)
            p.start()

        for proceso in procesos_list:
            proceso.join()

    def import_fila(self, fila_of_dataframe: pd.Series, path_of_dir: str = '',
                    colum_edi = 'ID_EDI', colum_sisx = 'ID_SISX', colum_sisy = 'ID_SISY'):
        """
        Crea el objeto edificio para una fila del dataFrame e incorpora los resultados de respuestas sismicas en cada
        piso.

        Parameters:
        ----------
        fila_of_dataframe: pd.Series
            fila del dataframe
        path_of_dir: str
            ruta del directorio donde se encuentran guardadas las respuestas sismicas
        colum_edi: str = 'ID_EDI'
            Nombre de la columna del data frame donde se encuentran los id de la base de datos de edificios
        colum_sisx: str='ID_SISX'
            Nombre de la columna del data frame donde se encuentran los id de los sismos en x de la base de datos de
            registros de suelo
        colum_sisy: str='ID_SISX'
            Nombre de la columna del data frame donde se encuentran los id de los sismos en x de la base de datos de
            registros de suelo

        Returns:
        -------
            retorna el objeto edificio con los datos importados
        """

        filaBDEdificio = self.db_edificios.loc[fila_of_dataframe[colum_edi]]
        filaDBRegistrosX = self.db_registro_suelo.loc[fila_of_dataframe[colum_sisx]]
        filaDBRegistrosY = self.db_registro_suelo.loc[fila_of_dataframe[colum_sisy]]

        idDatadrame = fila_of_dataframe.name

        edificioObjeto: ed.Edificio = copy.deepcopy(filaBDEdificio['EDIFICIO'])

        edificioObjeto.database_id = idDatadrame

        registroSueloX = filaDBRegistrosX['REGISTRO_ACELERACION']
        registroSueloY = filaDBRegistrosY['REGISTRO_ACELERACION']

        edificioObjeto.asignar_aceleraciones_suelo(registroSueloX, registroSueloY)

        pathOfAcelOut = os.path.join(path_of_dir, fila_of_dataframe['PATH_OUT'])
        edificioObjeto.asignar_aceleraciones_niveles(pathOfAcelOut)

        return edificioObjeto

    def import_all(self, nombre_columna_importar = 'EDIFICIO_ACEL_DATA',
                   path_of_dir = '', colum_edi = 'ID_EDI',
                   colum_sisx = 'ID_SISX', colum_sisy = 'ID_SISY'):
        """
        Crea el objeto edificio para todas las filas del dataFrame e incorpora los resultados de respuestas sismicas
        en cadapiso.
        Parameters
        ----------
        nombre_columna_importar: str
            El metodo creará una nueva columnna en el DataFrame, este parametro da nombre a dicha columna
        path_of_dir: str
            ruta del directorio donde se encuentran guardadas las respuestas sismicas
        colum_edi: str = 'ID_EDI'
            Nombre de la columna del data frame donde se encuentran los id de la base de datos de edificios
        colum_sisx: str='ID_SISX'
            Nombre de la columna del data frame donde se encuentran los id de los sismos en x de la base de datos de
            registros de suelo
        colum_sisy: str='ID_SISX'
            Nombre de la columna del data frame donde se encuentran los id de los sismos en x de la base de datos de
            registros de suelo

        Returns
        -------

        """
        self.nombreColumnaEdificio = nombre_columna_importar
        self._obj[nombre_columna_importar] = self._obj.apply(self.import_fila, axis = 1,
                                                             args = (path_of_dir, colum_edi, colum_sisx, colum_sisy))

    def import_all_multi(self, nombre_columna_importar = 'EDIFICIO_ACEL_DATA',
                         path_of_dir = '', colum_edi = 'ID_EDI',
                         colum_sisx = 'ID_SISX', colum_sisy = 'ID_SISY', progress_bar = False,
                         n_procesos = -1, max_chunks_per_worker = 8, chunk_size = 100):
        """
        Igual que import_all, solo que este metodo usa multiprocesos
        Parameters
        ----------
        nombre_columna_importar: str
            El metodo creará una nueva columnna en el DataFrame, este parametro da nombre a dicha columna
        path_of_dir: str
            ruta del directorio donde se encuentran guardadas las respuestas sismicas
        colum_edi: str = 'ID_EDI'
            Nombre de la columna del data frame donde se encuentran los id de la base de datos de edificios
        colum_sisx: str='ID_SISX'
            Nombre de la columna del data frame donde se encuentran los id de los sismos en x de la base de datos de
            registros de suelo
        colum_sisy: str='ID_SISX'
            Nombre de la columna del data frame donde se encuentran los id de los sismos en x de la base de datos de
            registros de suelo
        progress_bar:bool = True
            indica si es que se desea mostras la barra de progreso
        n_procesos: int = -1
            Indica el numero de procesos que se usaran, si es -1 se usara el numero de nucleos de procesador
        max_chunks_per_worker: int = 8
        chunk_size:int = 100

        Returns
        -------

        """
        self.nombreColumnaEdificio = nombre_columna_importar
        retorno_mapply = mapply(self._obj, self.import_fila, axis = 1,
                                args = (path_of_dir, colum_edi, colum_sisx, colum_sisy),
                                progressbar = progress_bar, n_workers = n_procesos,
                                max_chunks_per_worker = max_chunks_per_worker,
                                chunk_size = chunk_size)

        self._obj[self.nombreColumnaEdificio] = retorno_mapply
