from datetime import datetime

import joblib
import matplotlib.pyplot as plt
import numpy as np

import GroundMotion_lib.funciones as fn
import GroundMotion_lib.unidades as un


class SerieTiempo:

    def __init__(self, longitud = 'cm', tiempo = 's', masa = 'kg',
                 unidades_default_object: un.Unidades = None,
                 tiempo_array = None, serie_array = None,
                 nombre = None, **kwargs):

        self.nombre = nombre

        self.tiempoArray = tiempo_array
        self.serieArray = serie_array

        self.nPuntos = None

        self.max = None
        self.min = None

        if unidades_default_object is None:
            self._unidadesDefault = un.Unidades(long = longitud,
                                                tiempo = tiempo,
                                                masa = masa)
        elif isinstance(unidades_default_object, un.Unidades):
            self._unidadesDefault = unidades_default_object
        else:
            raise ValueError('tipo de parametro incorrecto')

    def __str__(self):
        resultado = f'tiempoArray: {self.tiempoArray.__str__()}'
        resultado += '\n'
        resultado += f'SerieArray: {self.serieArray.__str__()}'

        return resultado

    @property
    def tiempoArray(self):

        fn.controlerror_isnone(self._tiempoArray, 'El atributo Eje x aun no esta definido')
        return self._tiempoArray

    @tiempoArray.setter
    def tiempoArray(self, valor: list or tuple or np.ndarray or None):

        if valor is None:
            self._tiempoArray = None
            return

        valor_corregido = fn.controlerror_listtuple_toarray(valor)
        self._tiempoArray: np.ndarray = valor_corregido.astype(np.float32)
        self.nPuntos = len(self._tiempoArray)

    @property
    def serieArray(self):

        fn.controlerror_isnone(self._serieArray, 'El atributo Eje y aun no esta definido')
        return self._serieArray

    # noinspection PyArgumentList

    @serieArray.setter
    def serieArray(self, valor: list or tuple or np.ndarray or None):

        if valor is None:
            self._serieArray = None
            return

        valor_corregido = fn.controlerror_listtuple_toarray(valor)
        self._serieArray: np.ndarray = valor_corregido.astype(np.float32)
        self.max = self._serieArray.max()
        self.min = self._serieArray.min()
        self.nPuntos = len(self._serieArray)

    @staticmethod
    def _set_plot_parameters(x_label = '', y_label = '', titulo = '',
                             unidad_tiempo = None, unidad_serie = None, legend = False, show = False):
        if x_label != '':
            label = x_label

            if unidad_tiempo is not None:
                label = f'{label} ({unidad_tiempo})'

            plt.xlabel(label)

        if y_label != '':
            label = y_label

            if unidad_serie is not None:
                label = f'{label} ({unidad_serie})'

            plt.ylabel(label)

        if titulo != '':
            plt.title(titulo)

        if legend:
            plt.legend()

        if show:
            plt.show()

    @staticmethod
    def _set_subplot_parameters(subplot_axes: plt.axis, x_label = '', y_label = '', titulo = '',
                                unidad_tiempo = None, unidad_serie = None,
                                legend = False):

        if x_label != '':
            label = x_label

            if unidad_tiempo is not None:
                label = f'{label} ({unidad_tiempo})'

            subplot_axes.set_xlabel(label)

        if y_label != '':
            label = y_label

            if unidad_serie is not None:
                label = f'{label} ({unidad_serie})'

            subplot_axes.set_ylabel(label)

        if titulo != '':
            subplot_axes.set_title(titulo)

        if legend:
            subplot_axes.legend()

    def plot_xy(self, *args, x_label: str = '', y_label: str = '',
                title: str = '', legend: bool = False, show: bool = False,
                unidad_tiempo = None, unidad_serie = None, subplot_axes: plt.axis = None, **kwargs):
        """

        Parameters:
        ----------
        args: *args
            args para matplotlib.pyplot(args)
        x_label: str
            texto que se encontrará en el label del eje X, si es que se agrega unidad_tiempo se anexa al x_label.
            x_label= x_label(unidad_tiempo)
        y_label: str
            texto que se encontrará en el label del eje Y, si es que se agrega unidad_serie se anexa al y_label.
            y_label= y_label(unidad_serie)
        title: str
            titulo de la figura
        legend: bool
            bool que indica si es que se muestra la leyenda aplicando el comando plt.legend()
        show: bool
            bool que indica si es que se muestra la imagen aplicando el comando plt.show()
        unidad_tiempo: str
            Unidad que se usará en el tiempo, se pueden transformar la unidades ingresadas, si es que la serie de tiempo
            esta en una unidad, se puede cambiar a otra que exista en la libreria unidades
        unidad_serie: str
            Unidad que se usará en el tiempo, se pueden transformar la unidades ingresadas, si es que la serie de tiempo
            esta en una unidad, se puede cambiar a otra que exista en la libreria unidades
        kwargs: **kwargs

        Returns:
        -------
            retorna el objeto plot
        """

        tiempoArray = self.transform_unit_tiempo(unidad_tiempo)
        serieArray = self.transform_unit_serie(unidad_serie)

        if subplot_axes is None:

            plot_object = plt.plot(tiempoArray, serieArray, *args, **kwargs)

            self._set_plot_parameters(x_label = x_label, y_label = y_label, titulo = title,
                                      unidad_tiempo = unidad_tiempo, unidad_serie = unidad_serie,
                                      legend = legend, show = show)
        else:
            plot_object = subplot_axes.plot(tiempoArray, serieArray, *args, **kwargs)
            self._set_subplot_parameters(subplot_axes = subplot_axes, x_label = x_label, y_label = y_label,
                                         titulo = title, unidad_tiempo = unidad_tiempo, unidad_serie = unidad_serie,
                                         legend = legend)

        return plot_object

    def transform_unit_tiempo(self, unidad_x):
        if unidad_x is not None:
            tiempoArray = self._unidadesDefault.convertir_unit(self.tiempoArray, unidad_x)

        else:
            tiempoArray = self.tiempoArray

        return tiempoArray

    def transform_unit_serie(self, unidad_y):
        if unidad_y is not None:
            serieArray = self._unidadesDefault.convertir_unit(self.serieArray, unidad_y)

        else:
            serieArray = self.serieArray

        return serieArray

    def save_object(self, path_out, **kwargs):
        joblib.dump(self, path_out, kwargs)
        return path_out


class RegistroAceleracion(SerieTiempo):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.deltaT = kwargs.get('deltaT', None)
        self.frecMuestreo = kwargs.get('frecMuestreo', None)

        # variable de ubicacion si proviene de un DataFrame
        self.database_id = kwargs.get('database_id', None)
        self.nombre_sis = kwargs.get('nombre_sis', None)
        self.database_info = kwargs.get('database_info', None)

        # Variables para espectros
        self.especPeriodos = kwargs.get('frecuencias', None)
        self.especNPuntos = None

        self.especDesp: Espectro or None = None
        self.especVel: Espectro or None = None
        self.especAcel: Espectro or None = None

        # Creados
        self.allEspecGenerados = []
        self.allPseudoEspecGenerados = []

        # variable para los metodos numericos
        self.metodosDisponibles = {}
        self.tiposDeEspectros = {'ESPECTROS': self._calculo_punto_espectro,
                                 'PSEUDO': self._calculo_punto_pseudo}

    # def __str__(self):
    #     super().__str__()

    @property
    def especDespData(self) -> np.ndarray:
        """
        Devuelve el array del ultimo espector de desplazamiento creado
        array.shape = (n_puntos)
        """
        return self.especDesp.espectroData

    @especDespData.setter
    def especDespData(self, valor):
        self.especDesp.espectroData = valor

    @property
    def especVelData(self) -> np.ndarray:
        """
        Devuelve el array del ultimo espector de velocidad creado
        array.shape = (n_puntos)
        """
        return self.especVel.espectroData

    @especVelData.setter
    def especVelData(self, valor):
        self.especVel.espectroData = valor

    @property
    def especAcelData(self):
        """
        Devuelve un array con todos los espectros de aceleracion generados
        array.shape = array.shape = (n_puntos)
        """
        return self.especAcel.espectroData

    @especAcelData.setter
    def especAcelData(self, valor):
        self.especAcel.espectroData = valor

    def _controlerror_nosecrean_espectros(self):
        texto_error = 'Aun no se crea ningun espectro'
        fn.controlerror_tamano_lista_diferente(self.allEspecGenerados, 0, texto_error)

    def _controlerror_nosecrean_pseudo(self):
        texto_error = 'Aun no se crea ningun pseudo espectro'
        fn.controlerror_tamano_lista_diferente(self.allPseudoEspecGenerados, 0, texto_error)

    def _calculo_punto_espectro(self, periodo: float, amortiguamiento: float, tipo_metodo: str):
        """

        Parameters:
        ----------
        periodo: float
            periodo para el calculo del punto de espectro
        amortiguamiento: float
            razon de amortiguamiento para el calculo del punto del espectro
        tipo_metodo: {Newmark1, Newmark2, Piecewise}
            texto con el tipo de metodo numerico a usar para el calulo del espectro

        Returns:
        -------
            tupla: (punto desplazamiento, punto velocidad, punto aceleracion)
        """

        tipo_metodo = tipo_metodo.upper()

        objetoMetodoNumerico = fn.MetodosNumericos(
                carga_externa = self.serieArray,
                frec_muestreo = self.frecMuestreo,
                periodo = periodo,
                razon_amort = amortiguamiento
                )

        self.metodosDisponibles = objetoMetodoNumerico.get_metodos_disp()
        metodoToAply = self.metodosDisponibles[tipo_metodo]

        d, v, a = metodoToAply()

        Sdi = np.abs(d).max()
        Svi = np.abs(v).max()
        Sai = np.abs(a + self.serieArray).max()

        return Sdi, Svi, Sai

    # def _calculo_punto_espectro(self, periodo, amortiguamiento, tipo_metodo,
    #                             queue = None, semaphore = None):
    #
    #     print(f'calculando respuestas para periodo {periodo}')
    #     objetoMetodoNumerico = fn.MetodosNumericos(
    #             carga_externa = self.serieArray,
    #             frec_muestreo = self.frecMuestreo,
    #             periodo = periodo,
    #             razon_amort = amortiguamiento
    #             )
    #
    #     self.metodosDisponibles = objetoMetodoNumerico.get_metodos_disp()
    #     metodoToAply = self.metodosDisponibles[tipo_metodo]
    #
    #     d, v, a = metodoToAply()
    #
    #     Sdi = np.abs(d).max()
    #     Svi = np.abs(v).max()
    #     Sai = np.abs(a + self.serieArray).max()
    #
    #     if queue is not None:
    #         queue.put([Sdi, Svi, Sai])
    #
    #     if semaphore is not None:
    #         semaphore.release()
    #
    #     return Sdi, Svi, Sai

    def _calculo_punto_pseudo(self, periodo, amortiguamiento, tipo_metodo):

        objetoMetodoNumerico = fn.MetodosNumericos(
                carga_externa = self.serieArray,
                frec_muestreo = self.frecMuestreo,
                periodo = periodo,
                razon_amort = amortiguamiento
                )

        self.metodosDisponibles = objetoMetodoNumerico.get_metodos_disp()
        metodoToAply = self.metodosDisponibles[tipo_metodo]

        d, v, a = metodoToAply()

        w = 2 * np.pi / periodo
        Sdi = np.abs(d).max()
        Svi = Sdi * w
        Sai = Sdi * w ** 2

        return Sdi, Svi, Sai

    def _calculo_espectros(self, periodo_array: list or tuple or np.ndarray, amortiguamiento: float,
                           tipo_metodo: str, tipo_espectro: str = 'espectros') -> dict:
        """

        Parameters:
        ----------
        periodo_array: list or tuple or np.ndarrau
            iterable con los valores de los periodos para calcular el espectro
        amortiguamiento: float
            valor de amortiguamiento
        tipo_metodo: {Newmark1, Newmark2, Piecewise}
            texto con el tipo de metodo numerico a usar para el calulo del espectro
        tipo_espectro: str {'espectros', 'pseudo'}
            tipo de espectro a usar, espectro normal o pseudo espectro

        Returns:
        -------
            diccionario con cada tipo de espectro (Sd, Sv, Sa)
        """

        tipo_espectro = tipo_espectro.upper()

        self.especPeriodos = fn.controlerror_listtuple_toarray(periodo_array)
        self.especNPuntos = len(self.especPeriodos)

        amortiguamiento_list = [amortiguamiento for _ in range(self.especNPuntos)]
        tipo_metodo_list = [tipo_metodo for _ in range(self.especNPuntos)]

        funcion_calulo_espectro = self.tiposDeEspectros[tipo_espectro]
        resultados = map(funcion_calulo_espectro, self.especPeriodos, amortiguamiento_list, tipo_metodo_list)

        resultados = np.array(list(resultados), dtype = np.float32)

        Sd = resultados[:, 0]
        Sv = resultados[:, 1]
        Sa = resultados[:, 2]

        salida = self._definir_salida(Sd, Sv, Sa, tipo_espectro)

        return salida

    # INTENTO USANDO QUEUE -- FALLIDO HASTA AHORA
    # def _calculo_espectros_multi(self, periodo_array, amortiguamiento, tipo_metodo,
    #                              n_procesos,
    #                              tipo_espectro: str = 'espectros') -> dict:
    #
    #     self.especPeriodos = fn.controlerror_listtuple_toarray(periodo_array)
    #     self.especNPuntos = len(self.especPeriodos)
    #
    #     # amortiguamiento_list = [amortiguamiento for _ in range(self.especNPuntos)]
    #     # tipo_metodo_list = [tipo_metodo for _ in range(self.especNPuntos)]
    #
    #     # amortiguamiento_array = np.array(amortiguamiento_list)
    #     # tipo_metodo_array = np.array(tipo_metodo_list)
    #     #
    #     # iterable = np.hstack((self.especPeriodos.reshape(-1, 1),
    #     #                       amortiguamiento_array.reshape(-1, 1),
    #     #                       tipo_metodo_array.reshape(-1, 1)))
    #
    #     funcion_calulo_espectro = self.tiposDeEspectros[tipo_espectro]
    #
    #     qu = Queue()
    #     sema = Semaphore(n_procesos)
    #
    #     procesos = []
    #     resultados = []
    #
    #     for periodo in self.especPeriodos:
    #         sema.acquire()
    #         proceso = Process(target = funcion_calulo_espectro,
    #                           args = (periodo, amortiguamiento, tipo_metodo, qu, sema))
    #
    #         procesos.append(proceso)
    #         proceso.start()
    #
    #     for _ in procesos:
    #         resultados.append(qu.get())
    #
    #     for proceso in procesos:
    #         proceso.join()
    #
    #     resultados = np.array(resultados)
    #
    #     Sd = resultados[:, 0]
    #     Sv = resultados[:, 1]
    #     Sa = resultados[:, 2]
    #
    #     salida = self._definir_salida(Sd, Sv, Sa, tipo_espectro)
    #
    #     return salida

    # def _calculo_espectros_multi(self, periodo_array, amortiguamiento, tipo_metodo,
    #                              n_procesos,
    #                              tipo_espectro: str = 'espectros') -> dict:
    #
    #     self.especPeriodos = fn.controlerror_listtuple_toarray(periodo_array)
    #     self.especNPuntos = len(self.especPeriodos)
    #
    #     funcion_calulo_espectro = self.tiposDeEspectros[tipo_espectro]
    #
    #     Sd_array_multi = Array('d', range(self.especNPuntos))
    #     Sv_array_multi = Array('d', range(self.especNPuntos))
    #     Sa_array_multi = Array('d', range(self.especNPuntos))
    #
    #     # sema = Semaphore(n_procesos)
    #     procesos = []
    #
    #     for i, periodo in enumerate(self.especPeriodos):
    #         # sema.acquire()
    #         p = Process(target = funcion_calulo_espectro,
    #                     args = (periodo, amortiguamiento, tipo_metodo,
    #                             Sd_array_multi, Sv_array_multi, Sa_array_multi,
    #                             i))
    #
    #         procesos.append(p)
    #         p.start()
    #
    #     for proceso in procesos:
    #         proceso.join()
    #
    #     Sd = np.array(Sd_array_multi)
    #     Sv = np.array(Sv_array_multi)
    #     Sa = np.array(Sa_array_multi)
    #
    #     salida = self._definir_salida(Sd, Sv, Sa, tipo_espectro)
    #
    #     return salida
    #
    # def _calculo_espectros_multi(self, periodo_array, amortiguamiento, tipo_metodo,
    #                              n_procesos,
    #                              tipo_espectro: str = 'espectros') -> dict:
    #
    #     self.especPeriodos = fn.controlerror_listtuple_toarray(periodo_array)
    #     self.especNPuntos = len(self.especPeriodos)
    #
    #     funcion_calulo_espectro = self.tiposDeEspectros[tipo_espectro]
    #
    #     manager = Manager()
    #
    #     Sd_array_multi = manager.list()
    #     Sv_array_multi = manager.list()
    #     Sa_array_multi = manager.list()
    #
    #     # sema = Semaphore(n_procesos)
    #
    #     procesos = []
    #
    #     for i, periodo in enumerate(self.especPeriodos):
    #         # sema.acquire()
    #         p = Process(target = funcion_calulo_espectro,
    #                     args = (periodo, amortiguamiento, tipo_metodo,
    #                             Sd_array_multi, Sv_array_multi, Sa_array_multi,
    #                             i))
    #
    #         procesos.append(p)
    #         p.start()
    #
    #     for proceso in procesos:
    #         proceso.join()
    #
    #     Sd = np.array(Sd_array_multi)
    #     Sv = np.array(Sv_array_multi)
    #     Sa = np.array(Sa_array_multi)
    #
    #     salida = self._definir_salida(Sd, Sv, Sa, tipo_espectro)
    #
    #     return salida

    @staticmethod
    def _definir_salida(sd, sv, sa, tipo: str = 'espectros'):
        tipo = tipo.upper()

        if tipo == 'ESPECTROS':
            salida = {
                    'Sd': sd,
                    'Sv': sv,
                    'Sa': sa
                    }
        elif tipo == 'PSEUDO':
            salida = {
                    'Sd': sd,
                    'PSv': sv,
                    'PSa': sa
                    }
        else:
            texto = 'El tipo de espectro ingresado es incorrecto, solo se acepta "espectros" y "pseudo"'
            texto = f'{texto} se ingresó {tipo}'
            raise ValueError(texto)

        return salida

    def _guardar_espectro_pseudoespectro(self, espectros_array, tipo_espectro):
        tipo_espectro = tipo_espectro.upper()

        if tipo_espectro == 'ESPECTROS':
            self.allEspecGenerados.append(espectros_array)
        elif tipo_espectro == 'PSEUDO':
            self.allPseudoEspecGenerados.append(espectros_array)
        else:
            texto = 'El tipo de espectro ingresado es incorrecto, solo se acepta "espectros" y "pseudo"'
            texto = f'{texto} se ingresó {tipo_espectro}'
            raise ValueError(texto)

    def create_by_serie(self, serie: list or tuple or np.ndarray,
                        delta_t: float, nombre: str = None,
                        database_id = None, database_info = None, nombre_sis = None):

        self.nombre = nombre
        self.serieArray = serie

        self.tiempoArray = np.arange(self.nPuntos) * delta_t

        self.deltaT = delta_t
        self.frecMuestreo = 1 / self.deltaT

        self.database_id = database_id
        self.database_info = database_info
        self.nombre_sis = nombre_sis

    def create_by_tiempo_serie(self, serie: list or tuple or np.ndarray,
                               time_serie: list or tuple or np.ndarray,
                               nombre: str = None, database_id = None,
                               database_info = None, nombre_sis = None):
        self.nombre = nombre
        self.tiempoArray = time_serie
        self.serieArray = serie

        # CONTROLAR ERRO EN CASO LOS EJES NO TENGAN EL MISMO TAMAÑO
        fn.controlerror_igualdad_tamanolist(self.tiempoArray, self.serieArray)

        self.deltaT = self.tiempoArray[1] - self.tiempoArray[0]
        self.frecMuestreo = 1 / self.deltaT

        self.database_id = database_id
        self.database_info = database_info
        self.nombre_sis = nombre_sis

    def gen_espectros(self, periodo_array: list or tuple or np.ndarray,
                      amortiguamiento: float = 0.05,
                      tipo_metodo: str = 'Newmark1',
                      tipo_espectro: str = 'espectros') -> np.ndarray:
        """

        Parameters:
        ----------
        periodo_array : list or tuple or np.ndarray
            La secuencia de los periodos con los que se generará el espectro
        amortiguamiento : float
            el amortiguamiento para el calculo del espectro
        tipo_metodo : str {'Newmark1', 'Newmark2', 'PieceWise'}
            metodo numerico para el calculo del espectro
        tipo_espectro: str {'espectros', 'pseudo'}
            tipo de espectro a usar, espectro normal o pseudo espectro
        multi:bool
            Indica si desea calcular los espectros por medio de un multiprocees usando el metodo Pool.
            Para usar el multi, se debe ejecutar la funcion dentro de un if __name__ == '__main__':
        n_procesos: int = 3
            El numero de procesos en paralelo a usar
        chunksize: int=1
            Este método corta el iterable en varios fragmentos que envía al grupo de procesos como tareas separadas.
            El tamaño (aproximado) de estos fragmentos se puede especificar configurando chunksize
            en un número entero positivo.

            Para iterables muy largos usar un valor largo de chunksize puede completar el trabajo mucho más rapido.

        Returns:
        -------

        salida : np.ndarray
            objetos serietiempo.Espectro
            [desplzamiento, velocidad, aceleracion]
        """

        # Funcion con la que se calculan espectros, espectro o pseudo espectro

        resultadosEspectros = self._calculo_espectros(periodo_array, amortiguamiento, tipo_metodo, tipo_espectro)

        salida = []

        for espectroName, espectroArray in resultadosEspectros.items():
            espectroObject = Espectro(periodos_array = self.especPeriodos,
                                      espectro_valores = espectroArray,
                                      metodoUsado = tipo_metodo,
                                      tipoEspectro = espectroName,
                                      amort = amortiguamiento)
            salida.append(espectroObject)

        self.especDesp, self.especVel, self.especAcel = salida
        salida = np.array(salida)

        self._guardar_espectro_pseudoespectro(salida, tipo_espectro)

        return salida


class Espectro(SerieTiempo):

    def __init__(self, periodos_array = None, espectro_valores = None, **kwargs):
        super().__init__(**kwargs)

        self.periodos = periodos_array
        self.espectroData = espectro_valores

        self.metodoUsado = kwargs.get('metodoUsado', None)
        self.amortiguamiento = kwargs.get('amort', None)

        self.horaCreacion = datetime.now()

        self.tiposDisponibles = {
                'Sd': 'Espectro de desplazamiento',
                'Sv': 'Espectro de velocidad',
                'Sa': 'Espectro de aceleracion',
                'PSv': 'Pseudo Espectro de velocidad',
                'PSa': 'Pseudo Espectro de aceleracion'
                }

        self.tipoEspectro = kwargs.get('tipoEspectro', None)
        self._extraer_detalle_tipo()

        # Control de errores
        self._control_error_de_tipo()

    def __str__(self):
        resultado = f'Periodos: {self.periodos.__str__()}'
        resultado += '\n'
        resultado += f'Valores Espectro: {self.espectroData.__str__()}'

        return resultado

    @property
    def periodos(self):
        return self.tiempoArray

    @periodos.setter
    def periodos(self, valor):

        if valor is None:
            self.tiempoArray = valor
            self.periodoInicial = None
            self.periodoFinal = None
            return

        self.tiempoArray = valor
        self.periodoInicial = self._tiempoArray[0]
        self.periodoFinal = self._tiempoArray[-1]

    @property
    def espectroData(self):
        return self.serieArray

    @espectroData.setter
    def espectroData(self, valor):
        self.serieArray = valor

    def _extraer_detalle_tipo(self):
        self.tipoDetalle = self.tiposDisponibles.get(self.tipoEspectro)

    def _control_error_de_tipo(self):
        if self.tipoEspectro not in self.tiposDisponibles:
            raise ValueError(f'Solo se puede ingresar los tipos {self.tiposDisponibles.keys()}')
