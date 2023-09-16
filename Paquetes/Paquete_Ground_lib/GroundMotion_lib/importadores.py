import os

import joblib
import numpy as np
import pandas as pd
from tqdm import tqdm

import GroundMotion_lib.funciones as fn
import GroundMotion_lib.serietiempo as st


def importar_edi(dir_edis: str, index_import = None):
    lista_files = os.listdir(dir_edis)
    lista_files = np.array(lista_files)

    if index_import is not None:
        lista_files = lista_files[index_import]

    lista_edi_importados = []

    for edi_path in tqdm(lista_files, desc = f'Importando files de la carpeta {dir_edis}'):
        path = os.path.join(dir_edis, edi_path)
        edificio = joblib.load(path)

        lista_edi_importados.append(edificio)

        # yield edificio
    return lista_edi_importados


def importar_edi_multi(dir_edis: str, index_import = None, n_procesos = 2, verbose = 0, **kwargs):
    lista_files = os.listdir(dir_edis)
    lista_files = np.array(lista_files)

    if index_import is not None:
        lista_files = lista_files[index_import]

    lista_edi_importados = joblib.Parallel(n_jobs = n_procesos, verbose = verbose, **kwargs)(
            joblib.delayed(joblib.load)(os.path.join(dir_edis, edi_path)) for edi_path in lista_files)

    return lista_edi_importados


class ImportadorSeries:
    def __init__(self):
        self.seriesImportadas = list()

    def import_v1(self, file_path: str, delta_t: float, nombre: str = None):
        datos = pd.read_fwf(file_path,
                            names = ['col1', 'col2', 'col3', 'col4', 'col5',
                                     'col6', 'col7', 'col8'])
        datos = datos.to_numpy()
        datos = datos.reshape((-1,))
        datos = datos[np.logical_not((np.isnan(datos)))]

        aceleracion = st.RegistroAceleracion()
        aceleracion.create_by_serie(datos, delta_t, nombre)

        self.seriesImportadas.append(aceleracion)

        return aceleracion

    def import_t1(self, file_path: str, delta_t: float, nombre: str = None, database_id = None, database_info = None):
        nombre_file = list()
        nombre_file.append(os.path.splitext(file_path.split('/')[-1])[0])

        datos = pd.read_csv(file_path, names = nombre_file)
        datos = datos.to_numpy()
        datos = datos.reshape((-1))

        aceleracionSuelo = st.RegistroAceleracion()
        aceleracionSuelo.create_by_serie(datos, delta_t, nombre,
                                         database_id = database_id, database_info = database_info)

        self.seriesImportadas.append(aceleracionSuelo)
        return aceleracionSuelo

    def import_out(self, file_path: str, nombre: str = None):

        colum_names = ('tiempo', 'x', 'y')
        datos = pd.read_csv(file_path, names = colum_names, sep = ' ')

        tiempo = datos['tiempo'].to_numpy()
        serieX = datos['x'].to_numpy()
        serieY = datos['y'].to_numpy()

        respuestaX = st.RegistroAceleracion()
        respuestaY = st.RegistroAceleracion()

        if nombre is None:
            nombre = ''

        respuestaX.create_by_tiempo_serie(serieX, tiempo, nombre + 'X')
        respuestaY.create_by_tiempo_serie(serieY, tiempo, nombre + 'Y')
        self.seriesImportadas.append([respuestaX, respuestaY])

        return respuestaX, respuestaY

    @staticmethod
    def _crear_dict_nivelvspath(lista_de_textos_sin_extension: np.ndarray or list or tuple,
                                lista_paths: list):
        soloNumeros = list(map(lambda text: int(int(text.split('_')[1]) / 1000000), lista_de_textos_sin_extension))
        soloNumeros = np.array(soloNumeros)

        dictNivelesVsPath = {}

        for i, nivel in enumerate(soloNumeros):
            dictNivelesVsPath[nivel] = lista_paths[i]

        return dictNivelesVsPath

    def _crear_dict_nivelvsacel(self, dict_nivelvspath: dict, dir_path = '') -> dict:

        dictNivelesVsAcel = {}
        for piso, path in dict_nivelvspath.items():
            path = os.path.join(dir_path, path)
            nombreSerieTiempo = f'Piso {piso} '
            dictNivelesVsAcel[piso] = self.import_out(path, nombre = nombreSerieTiempo)

        return dictNivelesVsAcel

    def import_files_por_niveles(self, dir_path: str) -> dict:
        """
        Importa los files que se encuentren en el directorio dir_path.
        Lo importan entregando objetos serietiempo.RegistroAceleracion

        Parameters:
        ----------
        dir_path: str
            Directorio donde se encuentran los files en formato ".out" cada file pertenece a un nivel con el nombre
            del nodo de centro de gravedad del nivel.

            Ejemplo:
                <dir_path>
                    <1000000.out>
                    <2000000.out>
                    <3000000.out>
                    .
                    .

        Returns:
        -------

        dict
            Devuelve un diccionario donde cada keyname es el nombre del nivel obtenido de la siguiente forma
                1000000.out -> nivel 1 ( 1000000/1000000)
            y el valor del diccionario pertenece a un objeto serietiempo.RegistroAceleracion con los datso importados

        """
        lista_paths_files_out = os.listdir(dir_path)
        path_CGNivel_ext_format = fn.splitext_desde_listas_de_paths(lista_paths_files_out)

        nivelesVsPath = self._crear_dict_nivelvspath(path_CGNivel_ext_format[:, 0], lista_paths_files_out)
        nivelesVsAcel = self._crear_dict_nivelvsacel(nivelesVsPath, dir_path = dir_path)

        self.seriesImportadas.append(nivelesVsAcel)

        return nivelesVsAcel
