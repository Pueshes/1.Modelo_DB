import copy
import gc
import math
import os

import matplotlib.pyplot as plt

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import joblib
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
import tensorflow.keras as keras

import GroundMotion_lib.edificio as ed
import GroundMotion_lib.funciones as fn
import GroundMotion_lib.importadores as imp
import GroundMotion_lib.serietiempo as st


def plot_historia(historia_obj, limite = None):
    hist_plot = historia_obj.history
    plt.plot(hist_plot['loss'], label = 'loss')
    plt.plot(hist_plot['val_loss'], label = 'val_loss')

    plt.legend()
    plt.xlabel('Epoch')
    plt.ylabel('Error')
    plt.grid(True)
    if limite is not None:
        plt.ylim([0, limite])

    plt.show()


# noinspection PyPep8Naming
class ProcessingObject:
    """
    Objeto con metodos para el procesamiento de una lista de objetos de edificios
    """

    def __init__(self, edificios = None, range_suelo = (0, 1), range_edificio = (0, 1),
                 range_niveles = (0, 1), dtype = np.float64):
        self.type_numpy = dtype

        self.edificios = edificios

        self.edificiosTrain = None
        self.edificiosTest = None

        self.shapeSuelo = None
        self.shapeNiveles = None

        self.scalerSuelo = MinMaxScaler()
        self.scalerEdificio = MinMaxScaler()
        self.scalerNiveles = MinMaxScaler()

        self.rangeSuelo = range_suelo
        self.rangeEdificio = range_edificio
        self.rangeNiveles = range_niveles

        self.data_suelo_bruto = []
        self.data_edificio_bruto = []
        self.data_niveles_bruto = []

        self.data_suelo_process = None
        self.data_edificio_process = None
        self.data_niveles_process = None

        self.train_index = None
        self.test_index = None

        # TODO: HACER QUE SE AGREGUEN OBJETOS EDIFICIO LUEGO EXTRAER LA DATA DE CADA UNO
        #  Y ANEXAR A UN GUARDADO DE DATOS.

        # TIP: SE PUEDE MATENER EL MISMO CODIGO E IR EDITANDO LOS DATA
        # TIP: USAR NP.CONCATENATE PARA JUNTAR LOS DATOS QUE SE AGREGAN EN EL FUTURO

    def save_important(self, path_dir, data = True):

        if not os.path.isdir(path_dir):
            os.mkdir(path_dir)

        joblib.dump(self.shapeSuelo, os.path.join(path_dir, 'shape_suelo.probj'))
        joblib.dump(self.shapeNiveles, os.path.join(path_dir, 'shape_niveles.probj'))

        joblib.dump(self.scalerSuelo, os.path.join(path_dir, 'scaler_suelo.probj'))
        joblib.dump(self.scalerEdificio, os.path.join(path_dir, 'scaler_edificio.probj'))
        joblib.dump(self.scalerNiveles, os.path.join(path_dir, 'scaler_niveles.probj'))

        joblib.dump(self.train_index, os.path.join(path_dir, 'train_index.probj'))
        joblib.dump(self.test_index, os.path.join(path_dir, 'test_index.probj'))

        if data is True:
            joblib.dump(self.data_suelo_process, os.path.join(path_dir, 'data_suelo.probj'))
            joblib.dump(self.data_edificio_process, os.path.join(path_dir, 'data_edificio.probj'))
            joblib.dump(self.data_niveles_process, os.path.join(path_dir, 'data_niveles.probj'))

    def load_important(self, path_dir, data = True):
        self.shapeSuelo = joblib.load(os.path.join(path_dir, 'shape_suelo.probj'))
        self.shapeNiveles = joblib.load(os.path.join(path_dir, 'shape_niveles.probj'))

        self.scalerSuelo = joblib.load(os.path.join(path_dir, 'scaler_suelo.probj'))
        self.scalerEdificio = joblib.load(os.path.join(path_dir, 'scaler_edificio.probj'))
        self.scalerNiveles = joblib.load(os.path.join(path_dir, 'scaler_niveles.probj'))

        self.train_index = joblib.load(os.path.join(path_dir, 'train_index.probj'))
        self.test_index = joblib.load(os.path.join(path_dir, 'test_index.probj'))

        if data is True:
            self.data_suelo_process = joblib.load(os.path.join(path_dir, 'data_suelo.probj'))
            self.data_edificio_process = joblib.load(os.path.join(path_dir, 'data_edificio.probj'))
            self.data_niveles_process = joblib.load(os.path.join(path_dir, 'data_niveles.probj'))

    @property
    def rangeSuelo(self):
        return self.scalerSuelo.feature_range

    @rangeSuelo.setter
    def rangeSuelo(self, range_suelo: tuple):
        self.scalerSuelo.feature_range = range_suelo

    @property
    def rangeEdificio(self):
        return self.scalerEdificio.feature_range

    @rangeEdificio.setter
    def rangeEdificio(self, range_edificio: tuple):
        self.scalerEdificio.feature_range = range_edificio

    @property
    def rangeNiveles(self):
        return self.scalerNiveles.feature_range

    @rangeNiveles.setter
    def rangeNiveles(self, range_niveles: tuple):
        self.scalerNiveles.feature_range = range_niveles

    def get_edi_by_tipo(self, tipo):
        tipo = tipo.upper()

        if tipo == 'TODO':
            return self.edificios
        elif tipo == 'TRAIN':
            return self.edificiosTrain
        elif tipo == 'TEST':
            return self.edificiosTest
        else:
            raise ValueError('Solo se puede usar como tipo {"todo","train", ""test}')

    def _controlerror_existe_edificio(self, texto = 'Aun no se agregan edificios', tipo = 'todo'):
        """
        Controla si es que se han agregado objetos de edificio al atributo adificios, en caso no se haya
        agregado edificios lanza un error con el texto.

        Parameters:
        ----------
        texto: str
            texto que sale como mensaje juto al error de edificios
        Returns
        -------
            None
        """
        tipo = tipo.upper()

        variable_verificar = self.get_edi_by_tipo(tipo)

        if variable_verificar is None:
            raise ValueError(texto)

    def _obtener_tipo_data(self, tipo):
        tipo = tipo.upper()
        self._controlerror_existe_edificio(tipo = tipo)
        data_fit = self.get_edi_by_tipo(tipo)
        return data_fit

    def agregar_edificios(self, edificios: list or tuple or np.ndarray):
        """
        Agrega el argumento edificios al atributo del objeto edificios y calcula cual debe ser los shape para cada
        tipo de datos

        Parameters:
        ----------
        edificios: lilst or tuple or np.ndarray
            debe contener objetos GroundMotion.edificio.Edificio

        Returns:
        -------
            Retorna los edificios guardados en un array
        """
        self.edificios: np.ndarray = fn.controlerror_listtuple_toarray(edificios)

        self.data_suelo_bruto += list(map(lambda edificio: edificio.sueloRegacelData, self.edificios))
        self.data_edificio_bruto += list(map(lambda edificio: edificio.ediData, self.edificios))
        self.data_niveles_bruto += list(map(lambda edificio: edificio.nivelesEspecAcelData, self.edificios))

        self.get_shape_data_suelo()
        self.get_shape_data_niveles()

        return self.edificios

    def get_shape_data_suelo(self, tipo = 'todo'):
        """
        Calcula el shape mas grande de la data de suelos de los edificios que se encuentran en el atributo edificios


        Returns:
        -------
            Devuelve el shape en forma de lista de 2 dimensiones
            [2 direcciones, n Punto Max de suelo]

        """
        tipo_edificio = self._obtener_tipo_data(tipo)

        listNPuntosSuelo = list(map(lambda edificio: edificio.sueloNPuntosAcel, tipo_edificio))
        nPuntosMaxSuelo = max(listNPuntosSuelo)

        if self.shapeSuelo is not None:
            nPuntosMaxSuelo = max(self.shapeSuelo[1], nPuntosMaxSuelo)

        self.shapeSuelo = [2, nPuntosMaxSuelo]
        return self.shapeSuelo

    def get_shape_data_niveles(self, tipo = 'todo'):
        """
        Calcula el shape mas grande de la data de niveles de los edificios que se encuentran en el atributo edificios


        Returns:
        -------
            Devuelve el shape en forma de lista de 3 dimensiones
            [n pisos maximos que tiene, 2dirreciones, n puntos max]

        """
        tipo_edificio = self._obtener_tipo_data(tipo)

        listNPuntosNiveles = list(map(lambda edificio: edificio.nivelesNPuntosEspec, tipo_edificio))
        listNPisos = list(map(lambda edificio: edificio.nPisos, tipo_edificio))

        nPuntosMaxNiveles = max(listNPuntosNiveles)
        NPisosMax = max(listNPisos)

        if self.shapeNiveles is not None:
            nPuntosMaxNiveles = max(self.shapeNiveles[2], nPuntosMaxNiveles)
            NPisosMax = max(self.shapeSuelo[0], NPisosMax)

        self.shapeNiveles = [NPisosMax, 2, nPuntosMaxNiveles]

        return self.shapeNiveles

    def data_for_fit_suelo(self, tipo = 'todo'):
        data_fit = self._obtener_tipo_data(tipo)

        listaDataEdificios = list(map(lambda edificio: edificio.sueloRegacelData.flatten(), data_fit))
        datosConcatenados = np.concatenate(listaDataEdificios)

        try:
            lista_agregar = [self.scalerSuelo.data_max_, self.scalerSuelo.data_min_]
            datosConcatenados = np.append(datosConcatenados, lista_agregar).reshape(-1, 1)
        except AttributeError:
            datosConcatenados = datosConcatenados.reshape(-1, 1)

        return datosConcatenados

    def data_for_fit_edificio(self, tipo = 'todo'):
        data_fit = self._obtener_tipo_data(tipo)

        listaDataEdificios = list(map(lambda edificio: edificio.ediData, data_fit))
        datosConcatenados = np.stack(listaDataEdificios)

        try:
            datosConcatenados = np.vstack((datosConcatenados,
                                           self.scalerEdificio.data_max_, self.scalerEdificio.data_min_))
        except AttributeError:
            datosConcatenados = datosConcatenados

        return datosConcatenados

    def data_for_fit_niveles(self, tipo = 'todo'):
        data_fit = self._obtener_tipo_data(tipo)

        listaDataEdificios = list(map(lambda edificio: edificio.nivelesEspecAcelData.flatten(), data_fit))
        datosConcatenados = np.concatenate(listaDataEdificios)

        try:
            lista_agregar = [self.scalerNiveles.data_max_, self.scalerNiveles.data_min_]
            datosConcatenados = np.append(datosConcatenados, lista_agregar).reshape(-1, 1)
        except AttributeError:
            datosConcatenados = datosConcatenados.reshape(-1, 1)

        return datosConcatenados

    def fit_scaler_suelo(self, tipo = 'todo'):
        datos_to_fit = self.data_for_fit_suelo(tipo = tipo)
        self.scalerSuelo.fit(datos_to_fit)

        return self.scalerSuelo

    def fit_scaler_edificio(self, tipo = 'todo'):
        datos_to_fit = self.data_for_fit_edificio(tipo = tipo)
        self.scalerEdificio.fit(datos_to_fit)

        return self.scalerEdificio

    def fit_scaler_niveles(self, tipo = 'todo'):
        datos_to_fit = self.data_for_fit_niveles(tipo = tipo)
        self.scalerNiveles.fit(datos_to_fit)

        return self.scalerNiveles

    def fit_all(self, tipo = 'todo'):
        self.fit_scaler_suelo(tipo = tipo)
        self.fit_scaler_edificio(tipo = tipo)
        self.fit_scaler_niveles(tipo = tipo)

    def fit_train_test_split(self, test_size = None, train_size = None,
                             random_state = None, shuffle = True, stratify = None):
        """
        Divide el array del atributo edificios en edificios train y edificios test, ambos se guardan en los atributos
        llamados edificiosTrain y edificiosTest

    Parameters:
    ----------

    test_size : float or int, default=None
        If float, should be between 0.0 and 1.0 and represent the proportion
        of the dataset to include in the test split. If int, represents the
        absolute number of test samples. If None, the value is set to the
        complement of the train size. If ``train_size`` is also None, it will
        be set to 0.25.

    train_size : float or int, default=None
        If float, should be between 0.0 and 1.0 and represent the
        proportion of the dataset to include in the train split. If
        int, represents the absolute number of train samples. If None,
        the value is automatically set to the complement of the test size.

    random_state : int, RandomState instance or None, default=None
        Controls the shuffling applied to the data before applying the split.
        Pass an int for reproducible output across multiple function calls.
        See :term:`Glossary <random_state>`.

    shuffle : bool, default=True
        Whether or not to shuffle the data before splitting. If shuffle=False
        then stratify must be None.

    stratify : array-like, default=None
        If not None, data is split in a stratified fashion, using this as
        the class labels.
        Read more in the :ref:`User Guide <stratification>`.

    Returns:
    -------
    (self.edificiosTrain, self.edificiosTest)


    """
        self.train_index, self.test_index = train_test_split(np.arange(len(self.data_suelo_bruto)),
                                                             test_size = test_size,
                                                             train_size = train_size, random_state = random_state,
                                                             shuffle = shuffle, stratify = stratify)

        return self.train_index, self.test_index

    def split_edificios(self, split_train_test = False):

        if split_train_test is True:
            self.fit_train_test_split()

        self.edificiosTrain = self.edificios[self.train_index]
        self.edificiosTest = self.edificios[self.test_index]

        return self.edificiosTrain, self.edificiosTest

    def split_data_suelo(self):
        train_data = self.data_suelo_process[self.train_index]
        test_data = self.data_suelo_process[self.test_index]

        return train_data, test_data

    def split_data_edi(self):
        train_data = self.data_edificio_process[self.train_index]
        test_data = self.data_edificio_process[self.test_index]

        return train_data, test_data

    def split_data_niv(self):
        train_data = self.data_niveles_process[self.train_index]
        test_data = self.data_niveles_process[self.test_index]

        return train_data, test_data

    # fixme: que reciba objeto edificio y tambien datos sueltos por cada edificio
    def processing_suelo(self, data_suelo: ed.Edificio or np.ndarray):
        """
        Procesa los datos del suelo para 1 edificios siguiendo los siguientes pasos
        completa con 0s hasta llegar al shape de suelos maximo encontrados en todos los edificios agregando un -1
        al inicio

        Parameters:
        ----------
        data_suelo: ed.edificios
            objeto edificio con datos de suelo

        Returns:
        -------
            Data de suelo tranformado

        """
        if isinstance(data_suelo, ed.Edificio):
            dataSuelo = data_suelo.sueloRegacelData
        else:
            dataSuelo = data_suelo

        dataSuelo = dataSuelo.astype(self.type_numpy)
        # primero llenar de 0s
        dataSueloCeros = fn.completar_zeros(dataSuelo, self.shapeSuelo)
        # aplanar array para transofrmar
        dataSueloFlatten = dataSueloCeros.flatten().reshape(-1, 1)
        # Escalamos con MaxMinScales
        dataSueloTransform: np.ndarray = self.scalerSuelo.transform(dataSueloFlatten)
        # Volver al tamaño normal
        dataSueloEnrolladoTransform = dataSueloTransform.reshape(self.shapeSuelo)

        return dataSueloEnrolladoTransform

    def inverse_processing_suelo(self, data_suelo: np.ndarray):
        dataSueloFlatten = data_suelo.flatten()
        dataInverseScale: np.ndarray = self.scalerSuelo.inverse_transform(dataSueloFlatten.reshape(-1, 1))
        dataInverseEnrrollado = dataInverseScale.reshape(self.shapeSuelo)

        return dataInverseEnrrollado

    def processing_data_edificio(self, data_edificio: ed.Edificio or np.ndarray):

        if isinstance(data_edificio, ed.Edificio):
            dataEdi = data_edificio.ediData
        else:
            dataEdi = data_edificio

        # Escalamos con MaxMinScaler
        dataEdiTransform: np.ndarray = self.scalerEdificio.transform(dataEdi.reshape(1, -1))

        return dataEdiTransform

    def inverse_processing_data_edificio(self, data_edi: np.ndarray):
        data_edi_inverse = self.scalerEdificio.inverse_transform(data_edi.reshape(1, -1))

        return data_edi_inverse

    def processing_niveles(self, data_niveles: ed.Edificio):

        if isinstance(data_niveles, ed.Edificio):
            dataNiveles = data_niveles.nivelesEspecAcelData
        else:
            dataNiveles = data_niveles

        dataNiveles = dataNiveles.astype(self.type_numpy)

        # primero llenar de 0s
        dataNivelesCeros = fn.completar_zeros(dataNiveles, self.shapeNiveles)
        # aplanar array para transofrmar
        dataNivelesFlatten = dataNivelesCeros.flatten().reshape(-1, 1)
        # Escalamos con MaxMinScales
        dataNivelesTransform: np.ndarray = self.scalerNiveles.transform(dataNivelesFlatten)
        # Volver al tamaño normal
        dataNivelesEnrolladoTransform = dataNivelesTransform.reshape(self.shapeNiveles)

        return dataNivelesEnrolladoTransform

    def inverse_processing_niveles(self, data_niveles: np.ndarray):
        dataNivelesFlatten = data_niveles.flatten()
        dataInverseScale: np.ndarray = self.scalerNiveles.inverse_transform(dataNivelesFlatten.reshape(-1, 1))
        dataInverseEnrrollado = dataInverseScale.reshape(self.shapeNiveles)

        return dataInverseEnrrollado

    def processing_all_data_edificio(self, edificio):
        data_processed_suelo = self.processing_suelo(edificio)
        data_processed_edificio = self.processing_data_edificio(edificio)
        data_processed_niveles = self.processing_niveles(edificio)

        return data_processed_suelo, data_processed_edificio, data_processed_niveles

    def processing_many_edificios(self, edificios_list):
        list_data_processed_suelo = list(map(self.processing_suelo, edificios_list))
        data_processed_suelo = np.stack(list_data_processed_suelo)

        list_data_processed_edificio = list(map(self.processing_data_edificio, edificios_list))
        data_processed_edificio = np.vstack(list_data_processed_edificio)

        list_data_processed_niveles = list(map(self.processing_niveles, edificios_list))
        data_processed_niveles = np.stack(list_data_processed_niveles)

        return data_processed_suelo, data_processed_edificio, data_processed_niveles

    def processing_many_data(self, data_suelo_list, data_edi_list, data_niveles_list):

        list_data_processed_suelo = list(map(self.processing_suelo, data_suelo_list))
        data_processed_suelo = np.stack(list_data_processed_suelo)

        list_data_processed_edificio = list(map(self.processing_data_edificio, data_edi_list))
        data_processed_edificio = np.vstack(list_data_processed_edificio)

        list_data_processed_niveles = list(map(self.processing_niveles, data_niveles_list))
        data_processed_niveles = np.stack(list_data_processed_niveles)

        return data_processed_suelo, data_processed_edificio, data_processed_niveles

    def delete_edificios_list(self):
        del self.edificios
        gc.collect(0)
        gc.collect(1)
        gc.collect(2)

    def processing_all_data_bruta(self, del_edificios_obj = False):

        data_processed_suelo, data_processed_edificio, data_processed_niveles = self.processing_many_data(
                self.data_suelo_bruto, self.data_edificio_bruto, self.data_niveles_bruto
                )

        self.data_suelo_process = data_processed_suelo
        self.data_edificio_process = data_processed_edificio
        self.data_niveles_process = data_processed_niveles

        if del_edificios_obj is True:
            self.delete_edificios_list()

        return data_processed_suelo, data_processed_edificio, data_processed_niveles


class SueloBlock(keras.layers.Layer):
    def __init__(self, output_neurons, conv_layers, final_activation = 'relu',
                 pool_size = 4, pool_type = 'max'):
        super(SueloBlock, self).__init__()

        self.permute = keras.layers.Permute((2, 1))
        self.flatten = keras.layers.Flatten()
        self.out = keras.layers.Dense(output_neurons, activation = final_activation)

        self.conv_layers = conv_layers
        self.list_conv = []

        for layer_data in self.conv_layers:
            self.list_conv.append(keras.layers.Conv1D(layer_data[0],
                                                      layer_data[1],
                                                      activation = 'relu'))

        if pool_type == 'max':
            self.pool = keras.layers.MaxPool1D(pool_size = pool_size)
        elif pool_type == 'avg':
            self.pool = keras.layers.AvgPool1D(pool_size = pool_size)
        else:
            raise ValueError('pool_type: Solo se puede usar max o avg')

    # noinspection PyMethodOverriding,PyUnboundLocalVariable
    def call(self, inputs):

        for i, layer_conv in enumerate(self.list_conv):

            if i == 0:
                previus_layer = inputs
            else:
                previus_layer = pool_layer

            conv_layer = layer_conv(previus_layer)
            pool_layer = self.pool(conv_layer)

        flatten_layer = self.flatten(pool_layer)
        output_layer = self.out(flatten_layer)

        return output_layer


class MultiLayer(keras.layers.Layer):
    def __init__(self, size_layers, final_activation = 'relu'):
        super(MultiLayer, self).__init__()
        self.list_layers = []
        self.nLayers = len(size_layers)

        for i, size_layer in enumerate(size_layers):
            if i == self.nLayers - 1:
                self.list_layers.append(keras.layers.Dense(size_layer,
                                                           activation = final_activation))
            else:
                self.list_layers.append(keras.layers.Dense(size_layer,
                                                           activation = 'relu'))

    # noinspection PyMethodOverriding,PyUnboundLocalVariable
    def call(self, inputs):

        for i, layer in enumerate(self.list_layers):
            if i == 0:
                previus_layer = inputs
            else:
                previus_layer = dense_layer

            dense_layer = layer(previus_layer)

        return dense_layer


def create_edi_predict(modelotf: keras.Model, predict_obj: ProcessingObject, edificio_original):
    """
    Crea un objeto edificio que es copia del objeto pasado como edificio origianl
    Parameters
    ----------
    modelotf: keras.Model
    predict_obj: ProcessingObject
    edificio_original: Edificio

    Returns
    -------
    Retorna el edificio nuevo con los datos de predicción
    """
    suelo_data, edi_data, niveles_data = predict_obj.processing_all_data_edificio(edificio_original)

    nuevo_shape = [1] + list(predict_obj.shapeSuelo)
    suelo_data = suelo_data.reshape(nuevo_shape)

    niveles_predict = modelotf.predict_on_batch([suelo_data, edi_data])
    edificioNuevo: ed.Edificio = copy.deepcopy(edificio_original)
    edificioNuevo.nivelesEspecAcelData = predict_obj.inverse_processing_niveles(niveles_predict)

    return edificioNuevo


class CallbackStopTrain(tf.keras.callbacks.Callback):

    def __init__(self, cantidad_epocas = 5, tipo = 'min'):
        super(CallbackStopTrain, self).__init__()

        self.tipo = tipo
        self.cantidadEpocas = cantidad_epocas
        self.epochStop = 0
        self.weightsModelStop = None

        self.valMinimo = None
        self.valUltimo = None
        self.contadorStop = None

    def comparar_min(self, val_actual):

        if val_actual <= self.valMinimo:
            self.contadorStop = 0
            self.valMinimo = val_actual
            self.weightsModelStop = self.model.get_weights()
        else:
            self.contadorStop += 1

    def comparar_last(self, val_actual):

        if val_actual <= self.valUltimo:
            self.contadorStop = 0
            self.weightsModelStop = self.model.get_weights()
        else:
            self.contadorStop += 1

        self.valUltimo = val_actual

    def on_train_begin(self, logs = None):
        self.valMinimo = 1e6
        self.valUltimo = 1e6
        self.contadorStop = 0

    def on_epoch_end(self, epoch, logs = None):
        valor_actual = logs['val_loss']

        if self.tipo == 'min':
            self.comparar_min(valor_actual)

        elif self.tipo == 'last':
            self.comparar_last(valor_actual)
        else:
            raise ValueError('Solo se permite tipo last o min')

        if self.contadorStop >= self.cantidadEpocas:
            self.epochStop = epoch
            self.model.stop_training = True
            print(f'se supero el limite de {self.cantidadEpocas} en las que aumenta el loss')
            print(f'Se recuperan los pesos de hace {self.cantidadEpocas} epocas')
            self.model.set_weights(self.weightsModelStop)

    def on_train_end(self, logs = None):
        if self.contadorStop == 0:
            print('No se logró la condición, disminuir la cantidad de epocas de condicion o aumentar las epocas')
            print(f'Se detuvo en la epoca {self.epochStop + 1}')


def plot_edi(modelo_tf, predict_obj: ProcessingObject, index_plot, dir_edi, dirrecion,
             original_format = 'b', predict_format = 'r--',
             n_prcesos = 2, factor_fig_size = (5, 7), numero_columnas= 4):
    lista_edificios = imp.importar_edi_multi(dir_edi, index_plot, n_procesos = n_prcesos)

    for edificio in lista_edificios:
        edificioNuevo = create_edi_predict(modelo_tf, predict_obj, edificio)

        n_columns = numero_columnas
        n_rows = math.ceil(edificio.nPisos / n_columns) + 1

        fig = plt.figure(figsize = (n_columns * factor_fig_size[0]+2, n_rows * factor_fig_size[1]+4))

        reg_acel_suelo: st.RegistroAceleracion = edificio.sueloRegacelArray[0]
        info_sismo = reg_acel_suelo.database_info

        titulo = f'''Aceleracion suelo - Sismo: {info_sismo["NOMBRE_SIS"]}
        Sensor: {info_sismo["NOMBRE_SENSOR"]}
        Edificio: {edificio.database_id} - NPisos {edificio.nPisos} '''

        fig.suptitle(titulo)

        reg_acel = plt.subplot(n_rows, 2, 1)
        edificio.plot_suelo_regacel(0, original_format, x_label = 'Tiempo',
                                    y_label = 'Acel', title = 'Aceleracion del suelo dirrecion x',
                                    unidad_serie = 'g', unidad_tiempo = 's', subplot_axes = reg_acel,
                                    )

        reg_acel = plt.subplot(n_rows, 2, 2)
        edificio.plot_suelo_regacel(1, original_format, x_label = 'Tiempo',
                                    y_label = 'Acel', title = 'Aceleracion del suelo dirrecion y',
                                    unidad_serie = 'g', unidad_tiempo = 's', subplot_axes = reg_acel,
                                    )

        for piso in range(edificio.nPisos):
            posicion_imagen = n_columns + piso + 1
            axis1 = plt.subplot(n_rows, n_columns, posicion_imagen)

            edificio.plot_1nivel_espec(piso, dirrecion, original_format, x_label = 'Periodo',
                                       y_label = 'Sa', title = f'Espectro aceleracion piso {piso + 1}',
                                       unidad_serie = 'g', unidad_tiempo = 's', subplot_axes = axis1,
                                       label = 'Original')

            edificioNuevo.plot_1nivel_espec(piso, dirrecion, predict_format, x_label = 'Periodo',
                                            y_label = 'Sa', unidad_serie = 'g', unidad_tiempo = 's',
                                            subplot_axes = axis1,
                                            label = 'Prediccion')

        plt.tight_layout()
        plt.legend()
        plt.show()

# #
# def plot_edi(modelo_tf, predict_obj: ProcessingObject, index_plot, dir_edi, n_prcesos = 2):
#     lista_edificios = imp.importar_edi_multi(dir_edi, index_plot, n_procesos = n_prcesos)
#
#     for edificio in lista_edificios:
#         suelo_data, edi_data, niveles_data = predict_obj.processing_all_data_edificio(edificio)
#
#         nuevo_shape = [1] + list(predict_obj.shapeSuelo)
#         suelo_data = suelo_data.reshape(nuevo_shape)
#
#         niveles_predict = modelo_tf.predict_on_batch([suelo_data, edi_data])
#         print(niveles_predict.shape)
#
#         edificionuevo: ed.Edificio = copy.deepcopy(edificio)
#         edificionuevo.nivelesEspecAcelData = predict_obj.inverse_processing_niveles(niveles_predict)
#
#         edificio.plot_1nivel_espec(25, 0, 'b.', x_label = 'Periodos(s)', y_label = 'Sa(cm/s2)',
#                                    legend = True,
#                                    titulo = f'Espectro de aceleracion edificio {edificio.database_id}, piso {1} en X',
#                                    label = 'Original')
#
#         edificionuevo.plot_1nivel_espec(25, 0, 'r', x_label = 'Periodos(s)', y_label = 'Sa(cm/s2)',
#                                         label = 'Prediccion')
#
#         plt.show()
