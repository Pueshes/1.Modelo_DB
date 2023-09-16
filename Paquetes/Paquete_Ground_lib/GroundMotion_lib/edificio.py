import matplotlib.pyplot as plt
import numpy as np

import GroundMotion_lib.funciones as fn
import GroundMotion_lib.importadores as imp
import GroundMotion_lib.serietiempo as st


# noinspection PyPep8Naming
class Edificio:
    def __init__(self, n_pisos: int, periodo: float, h_pisos: float = None,
                 n_vanosx: int = None, n_vanosy: int = None,
                 l_vanox: float = None, l_vanoy: float = None,
                 h_vigax: float = None, b_vigax: float = None,
                 h_vigay: float = None, b_vigay: float = None,
                 h_colum: float = None, b_colum: float = None, database_id = None, dtype = np.float32):

        # self.type_numpy = dtype

        self.nPisos = int(n_pisos)
        self.periodo = periodo

        self.hPisos = h_pisos

        self.nVanosX = n_vanosx
        self.nVanosY = n_vanosy

        self.lVanosX = l_vanox
        self.lVanosY = l_vanoy

        self.hVigaX = h_vigax
        self.hVigaY = h_vigay

        self.bVigaX = b_vigax
        self.bVigaY = b_vigay

        self.hColum = h_colum
        self.bColum = b_colum

        self.all_propiedades = {
                'nPisos': self.nPisos,
                'nVanosX': self.nVanosX,
                'nVanosY': self.nVanosY,
                'lVanosX': self.lVanosX,
                'lVanosY': self.lVanosY,
                'hVigaX': self.hVigaX,
                'hVigaY': self.hVigaY,
                'bVigaX': self.bVigaX,
                'bVigaY': self.bVigaY,
                'hColum': self.hColum,
                'bColum': self.bColum,
                'periodo': self.periodo
                }

        self.database_id = database_id

        self._crear_niveles()

    def __str__(self):
        return self.all_propiedades.__str__()

    @property
    def nombreSis(self):
        return self.nivelSuelo.nombreSis

    @property
    def PGA_suelo(self):
        return self.nivelSuelo.PGA

    @property
    def nivelesMaxAcel(self):
        lista_maximos = map(lambda nivel: nivel.maxRegacel, self.niveles.values())
        maximo = max(lista_maximos)
        return maximo

    @property
    def nivelesMinAcel(self):
        lista_minimo = map(lambda nivel: nivel.minRegacel, self.niveles.values())
        minimo = min(lista_minimo)
        return minimo

    @property
    def nivelesNPuntosAcel(self):
        niveles = list(self.niveles.values())
        nPuntos = niveles[0].nPuntosRegacel
        return nPuntos

    @property
    def nivelesTiempoAcel(self):
        niveles = list(self.niveles.values())
        tiempoArray = niveles[0].tiempoRegAcel
        return tiempoArray

    @property
    def nivelesMaxEspec(self):
        lista_maximos = map(lambda nivel: nivel.maxEspecAcel, self.niveles.values())
        maximo = max(lista_maximos)
        return maximo

    @property
    def nivelesMinEspec(self):
        lista_maximos = map(lambda nivel: nivel.minEspecAcel, self.niveles.values())
        maximo = max(lista_maximos)
        return maximo

    @property
    def nivelesNPuntosEspec(self):
        niveles = list(self.niveles.values())
        nPuntos = niveles[0].nPuntosEspecAcel
        return nPuntos

    @property
    def nivelesPeriodoEspec(self):
        niveles = list(self.niveles.values())
        periodo = niveles[0].periodosEspec
        return periodo

    @property
    def sueloMaxAcel(self):
        maximo = self.nivelSuelo.maxRegacel
        return maximo

    @property
    def sueloMinAcel(self):
        minimo = self.nivelSuelo.minRegacel
        return minimo

    @property
    def sueloNPuntosAcel(self):
        nPuntos = self.nivelSuelo.nPuntosRegacel
        return nPuntos

    @property
    def sueloTiempoAcel(self):
        tiempoArray = self.nivelSuelo.tiempoRegAcel
        return tiempoArray

    @property
    def sueloMaxEspec(self):
        maximo = self.nivelSuelo.maxEspecAcel
        return maximo

    @property
    def sueloMinEspec(self):
        maximo = self.nivelSuelo.minEspecAcel
        return maximo

    @property
    def sueloNPuntosEspec(self):
        nPuntos = self.nivelSuelo.nPuntosEspecAcel
        return nPuntos

    @property
    def sueloPeriodoEspec(self):
        periodo = self.nivelSuelo.periodosEspec
        return periodo

    @property
    def ediData(self):
        lista = [self.nPisos, self.hPisos, self.nVanosX, self.nVanosY, self.lVanosX, self.lVanosY,
                 self.hVigaX, self.bVigaX, self.hVigaY, self.bVigaY, self.hColum, self.bColum]

        return np.array(lista)

    @property
    def sueloRegacelDict(self) -> dict:
        """
        Obtiene el pametro aceleraciones del objeto edificio.Nivel del suelo.
        El objeto es un diccionario

        Returns:
        -------
            {X:serietiempo.RegistroAceleracion, Y:serietiempo.RegistroAceleracion }
        """
        return self.nivelSuelo.regacelDict

    @property
    def sueloRegacelArray(self) -> np.ndarray:
        """
        Devuelve los objetos serietiempo.RegistroAceleracion perteciente al nivel suelo en cada dirrecion en un array
        array.shape = ( 2 dirreciones)

        Returns:
        -------
                #X                                  #Y
        [serietiempo.RegistroAceleracion, serietiempo.RegistroAceleracion]      #Suelo

        """

        return self.nivelSuelo.regacelArray

    @property
    def sueloEspecAcelArray(self) -> np.ndarray:
        """
        Devuelve los objetos serietiempo.Espectro aceleraicon perteciente al nivel de suelo y dirrecion en un array
        array.shape = ( 2 dirreciones)

        Returns:
        -------
        [serietiempo.Espectro, serietiempo.Espectro], #Nivel suelo
        """
        return self.nivelSuelo.especAcelArray

    @property
    def nivelesRegacelDict(self) -> list:
        """
        Obtiene el pametro aceleraciones del objeto nivel por cada nivel de edificio en forma de lista.
        El objeto es una lista

        Returns:
        -------
        list of dicts:
        \n

        [\t   {X:serietiempo.RegistroAceleracion, Y:serietiempo.RegistroAceleracion}, #Nivel 1\n
        \t    {X:serietiempo.RegistroAceleracion, Y:serietiempo.RegistroAceleracion}, #Nivel 2\n
        \t    {X:serietiempo.RegistroAceleracion, Y:serietiempo.RegistroAceleracion}, #Nivel 3\n
        \t    .                                                                       .\n
        \t    .                                                                       .\n
        \t    .                                                                       .\n
        ]
        """
        niveles = self.niveles.values()
        aceleraciones = list(map(lambda nivel: nivel.regacelDict, niveles))
        return aceleraciones

    @property
    def nivelesRegacelArray(self) -> np.ndarray:
        """
        Devuelve los objetos serietiempo.RegistroAceleracion perteciente para cada nivel y dirrecion en un array
        array.shape = (niveles, 2 dirreciones)

        Returns:
        -------
        [   [serietiempo.RegistroAceleracion, serietiempo.RegistroAceleracion], #Nivel 1
            [serietiempo.RegistroAceleracion, serietiempo.RegistroAceleracion], #Nivel 2
            [serietiempo.RegistroAceleracion, serietiempo.RegistroAceleracion], #Nivel 3
            .                                                                       .
            .                                                                       .
            .                                                                       .
        ]
        """

        niveles = self.niveles.values()
        lista = list(map(lambda nivel: nivel.regacelArray, niveles))
        return np.array(lista)

    @property
    def nivelesEspecAcelArray(self) -> np.ndarray:
        """
        Devuelve los objetos serietiempo.Espectro aceleracion perteciente para cada nivel y dirrecion en un array
        array.shape = (niveles, 2 dirreciones)

        Returns:
        -------
        [   [serietiempo.Espectro, serietiempo.Espectro], #Nivel 1\n
            [serietiempo.Espectro, serietiempo.Espectro], #Nivel 2\n
            [serietiempo.Espectro, serietiempo.Espectro], #Nivel 3\n
            .                                                   .\n
            .                                                   .\n
            .                                                   .\n
        ]
        """
        niveles = self.niveles.values()
        lista = list(map(lambda nivel: nivel.especAcelArray, niveles))
        return np.array(lista)

    @property
    def sueloRegacelData(self):
        """
        Data del suelo en forma de array, no se devuelve ningun objeto
        array.shape= (2 dirreciones, n_puntos)

        Returns:
        -------
        [   [numero de puntos ....],
            [numero de puntos ....]]
        """
        return self.nivelSuelo.regacelData

    @sueloRegacelData.setter
    def sueloRegacelData(self, data):
        self.nivelSuelo.regacelData = data

    @property
    def nivelesRegacelData(self):
        """
        Data de los niveles en forma de array, no se devuelve ningun objeto
        array.shape= (n_niveles,2 dirreciones, n_puntos )

        Returns:
        -------
        [   [numero de puntos ....],[numero de puntos ....] #Nivel 1\n
            [numero de puntos ....],[numero de puntos ....] #Nivel 2\n
            [numero de puntos ....],[numero de puntos ....] #Nivel 3\n
            .
            .
            .

            ]

        """
        niveles = self.niveles.values()
        data = list(map(lambda nivel: nivel.regacelData, niveles))

        return np.array(data, dtype = np.float32)

    @nivelesRegacelData.setter
    def nivelesRegacelData(self, data):

        for indice, nivel in enumerate(self.niveles.values()):
            nivel.regacelData = data[indice]

    @property
    def nivelesEspecAcelData(self):
        """
        Data de los espectro de los niveles en forma de array, no se devuelve ningun objeto
        array.shape= (n_niveles,2 dirreciones, n_puntos )

        Returns:
        -------
        [   [numero de puntos ....],[numero de puntos ....] #Nivel 1\n
            [numero de puntos ....],[numero de puntos ....] #Nivel 2\n
            [numero de puntos ....],[numero de puntos ....] #Nivel 3\n
            .
            .
            .

            ]

        """
        niveles = self.niveles.values()
        data = list(map(lambda nivel: nivel.especAcelData, niveles))

        return np.array(data, dtype = np.float32)

    @nivelesEspecAcelData.setter
    def nivelesEspecAcelData(self, data):

        for indice, nivel in enumerate(self.niveles.values()):
            nivel.especAcelData = data[indice]

    def _crear_niveles(self):
        self.nivelSuelo = Nivel(numero = 0, dtype = np.float32)
        self.niveles = {}

        for piso in range(1, self.nPisos + 1):
            self.niveles[piso] = Nivel(numero = piso, dtype = np.float32)

        return self.nivelSuelo, self.niveles

    def plot_suelo_regacel(self, direccion, *args, x_label: str = '', y_label: str = '',
                           title: str = '', legend: bool = False, show: bool = False,
                           unidad_tiempo = None, unidad_serie = None, subplot_axes: plt.axis = None, **kwargs):

        serie_tiempo_obj: st.RegistroAceleracion = self.sueloRegacelArray[direccion]

        serie_tiempo_obj.plot_xy(*args, x_label = x_label, y_label = y_label, title = title, legend = legend,
                                 show = show, unidad_tiempo = unidad_tiempo, unidad_serie = unidad_serie,
                                 subplot_axes = subplot_axes, **kwargs)

    def plot_1nivel_regacel(self, nivel, direccion, *args, x_label: str = '', y_label: str = '',
                            title: str = '', legend: bool = False, show: bool = False,
                            unidad_tiempo = None, unidad_serie = None, subplot_axes: plt.axis = None, **kwargs):

        serie_tiempo_obj: st.RegistroAceleracion = self.nivelesRegacelArray[nivel, direccion]

        serie_tiempo_obj.plot_xy(*args, x_label = x_label, y_label = y_label, title = title, legend = legend,
                                 show = show, unidad_tiempo = unidad_tiempo, unidad_serie = unidad_serie,
                                 subplot_axes = subplot_axes, **kwargs)

    def plot_1nivel_espec(self, nivel, direccion, *args, x_label: str = '', y_label: str = '',
                          title: str = '', legend: bool = False, show: bool = False,
                          unidad_tiempo = None, unidad_serie = None, subplot_axes: plt.axis = None, **kwargs):

        serie_tiempo_obj: st.RegistroAceleracion = self.nivelesEspecAcelArray[nivel, direccion]

        serie_tiempo_obj.plot_xy(*args, x_label = x_label, y_label = y_label, title = title, legend = legend,
                                 show = show, unidad_tiempo = unidad_tiempo, unidad_serie = unidad_serie,
                                 subplot_axes = subplot_axes, **kwargs)

    def asignar_aceleraciones_niveles(self, path_of_acels_outformat: str,
                                      nombres_direcciones: list = ('X', 'Y')):
        """
        Import y asigna los objetos st.RegistroAceleracion a los niveles, no retorna nada
        Parameters
        ----------
        path_of_acels_outformat: str
            Ruta del directorio donde se guardan los archivos .out del nivel

        nombres_direcciones: list ('X','Y')
            lista con los nombre de las dirreciones que van a tener cada nivel

        Returns
        -------
        None
        """

        importador = imp.ImportadorSeries()

        diccionarioNivelesVsAcel = importador.import_files_por_niveles(path_of_acels_outformat)
        fn.controlerror_igualdad_keys_de_dicts(diccionarioNivelesVsAcel, self.niveles)

        for numeroNivel, objetoNivel in self.niveles.items():
            lista_objeto_regacel_por_piso = diccionarioNivelesVsAcel[numeroNivel]
            aceleracion_por_piso = dict(zip(nombres_direcciones, lista_objeto_regacel_por_piso))

            objetoNivel.regacelDict = aceleracion_por_piso

    def asignar_aceleraciones_suelo(self, serie_tiempo_x, serie_tiempo_y):
        self.nivelSuelo.regacelDict = {'X': serie_tiempo_x, 'Y': serie_tiempo_y}

    def crear_espectros_niveles(self, periodo_array: list or tuple or np.ndarray,
                                amortiguamiento: float = 0.05, tipo_metodo: str = 'Newmark1',
                                tipo_espectro: str = 'espectros'):

        for nivel in self.niveles.values():
            nivel.crear_espectros(periodo_array, amortiguamiento, tipo_metodo, tipo_espectro)

        return self.niveles

    def crear_espectros_suelo(self, periodo_array: list or tuple or np.ndarray,
                              amortiguamiento: float = 0.05, tipo_metodo: str = 'Newmark1',
                              tipo_espectro: str = 'espectros'):

        self.nivelSuelo.crear_espectros(periodo_array, amortiguamiento, tipo_metodo, tipo_espectro)

        return self.nivelSuelo


# noinspection PyPep8Naming
class Nivel:

    def __init__(self, **kwargs):

        # self.type_numpy = kwargs.get('dtype', np.float32)
        self.numero = kwargs.get('numero', None)
        self.regacelDict = kwargs.get('aceleraciones', {})

        self._espectrosDesp: dict = {}
        self._espectrosVel: dict = {}
        self._espectrosAcel: dict = {}

    def __str__(self):
        texto = f'Nivel número {self.numero}, \n'
        texto += f'nDirreciones {self.nDirreciones},\n'
        texto += f'nPuntosRegacel {self.nPuntosRegacel},\n'
        return texto

    @property
    def nombreSis(self):
        aceleracion_nivel = self.regacelArray[0]
        nombre = aceleracion_nivel.database_info['NOMBRE_SIS']
        return nombre

    @property
    def PGA(self):

        pga = 0
        for aceleracion in self.regacelArray:
            pga = max(pga, abs(aceleracion.database_info['PGA']))

        return pga

    @property
    def nDirreciones(self):
        return len(self._regAceleracionDict)

    @property
    def nPuntosRegacel(self):
        nPuntosSerie = self._get_npuntos(self.regacelArray)
        return nPuntosSerie

    @property
    def maxRegacel(self):
        maxSerie = self._get_max(self.regacelArray)
        return maxSerie

    @property
    def minRegacel(self):
        minSerie = self._get_min(self.regacelArray)
        return minSerie

    @property
    def nPuntosEspecDesp(self):
        nPuntosSerie = self._get_npuntos(self.especDespArray)
        return nPuntosSerie

    @property
    def maxEspecDesp(self):
        maxSerie = self._get_max(self.especDespArray)
        return maxSerie

    @property
    def minEspecDesp(self):
        minSerie = self._get_min(self.especDespArray)
        return minSerie

    @property
    def nPuntosEspecVel(self):
        nPuntosSerie = self._get_npuntos(self.especVelArray)
        return nPuntosSerie

    @property
    def maxEspecVel(self):
        maxSerie = self._get_max(self.especVelArray)
        return maxSerie

    @property
    def minEspecVel(self):
        minSerie = self._get_min(self.especVelArray)
        return minSerie

    @property
    def nPuntosEspecAcel(self):
        nPuntosSerie = self._get_npuntos(self.especAcelArray)
        return nPuntosSerie

    @property
    def maxEspecAcel(self):
        maxSerie = self._get_max(self.especAcelArray)
        return maxSerie

    @property
    def minEspecAcel(self):
        minSerie = self._get_min(self.especAcelArray)
        return minSerie

    @property
    def dirreciones(self):
        return self.regacelDict.keys()

    @property
    def regacelDict(self) -> dict:
        """
        Devuelve el atributo aceleraciones, diccionario de la siguiente manera:

        {   direccionName1: serietiempo.RegistroAceleracion,
            direccionName2: serietiempo.RegistroAceleracion,
            direccionName3: serietiempo.RegistroAceleracion,
            }
        """
        return self._regAceleracionDict

    @regacelDict.setter
    def regacelDict(self, diccionario_aceleraciones_niveles: dict):

        # Verificar si el diccionario_aceleraciones_niveles es un diccionario
        fn.controlerror_isinstance(diccionario_aceleraciones_niveles, dict)

        # verificar si cada objeto del diccionario es un registro aceleraicon
        for objetoAceleracion in diccionario_aceleraciones_niveles.values():
            fn.controlerror_isinstance(objetoAceleracion, st.RegistroAceleracion)

        self._regAceleracionDict: dict = diccionario_aceleraciones_niveles

    @property
    def regacelArray(self):
        """
        Devuelve el parametro aceleraciones por cada dirrecion, diccionario de la siguiente manera:

        [   serietiempo.RegistroAceleracion,    #Dirrecion1
            serietiempo.RegistroAceleracion,    #Dirrecion2
            serietiempo.RegistroAceleracion,    #Dirrecion3
            ]
        """
        return np.array(list(self._regAceleracionDict.values()))

    @regacelArray.setter
    def regacelArray(self, valores: np.ndarray):
        """
        Edita los valores de regacel ya existentes, no funciona para asignar
        """

        fn.controlerror_isinstance(valores, np.ndarray)

        fn.controlerror_tamano_lista_igual(valores, len(self._regAceleracionDict),
                                           texto = 'El array de regacel debe tener la misma cantidad de objetos '
                                                   'existente')

        for indice, keyName in enumerate(self._regAceleracionDict):
            self._regAceleracionDict[keyName] = valores[indice]

    @property
    def regacelData(self):
        """
        Devuelve un array con los datos de cada aceleracion guardada en el nivel.
        array.shape = (n_Dirreciones, n_puntos registro)

        [   datos (array),  #Direccion1
            datos (array),  #Direccion2
            datos (array),  #Direccion3
            ]
        """
        lista = list(map(lambda regacelDirrecion: regacelDirrecion.serieArray, self.regacelArray))
        return np.array(lista, dtype = np.float32)

    @regacelData.setter
    def regacelData(self, data_de_registro_aceleracion: np.ndarray or list or tuple):

        # verificar que el valor sea un array
        data_de_registro_aceleracion = fn.controlerror_listtuple_toarray(data_de_registro_aceleracion)
        # Verificar que el temano del array en la primera dimesion sea igual al numero de dirreciones
        fn.controlerror_tamano_lista_igual(data_de_registro_aceleracion, self.nDirreciones)

        # asignar array a cada dirrecion
        for indice, objetoRegAcel in enumerate(self._regAceleracionDict.values()):
            objetoRegAcel.serieArray = data_de_registro_aceleracion[indice]

    @property
    def especDespDict(self):

        return self._espectrosDesp

    @especDespDict.setter
    def especDespDict(self, diccionario_espectros_vs_dirreciones: dict):

        fn.controlerror_isinstance(diccionario_espectros_vs_dirreciones, dict)

        for objetoEspectro in diccionario_espectros_vs_dirreciones.values():
            fn.controlerror_isinstance(objetoEspectro, st.Espectro)

        self._espectrosDesp = diccionario_espectros_vs_dirreciones

    @property
    def especVelDict(self):

        return self._espectrosVel

    @especVelDict.setter
    def especVelDict(self, diccionario_espectros_vs_dirreciones: dict):

        fn.controlerror_isinstance(diccionario_espectros_vs_dirreciones, dict)

        for objetoEspectro in diccionario_espectros_vs_dirreciones.values():
            fn.controlerror_isinstance(objetoEspectro, st.Espectro)

        self._espectrosVel = diccionario_espectros_vs_dirreciones

    @property
    def especAcelDict(self):

        return self._espectrosAcel

    @especAcelDict.setter
    def especAcelDict(self, diccionario_espectros_vs_dirreciones):

        fn.controlerror_isinstance(diccionario_espectros_vs_dirreciones, dict)

        for objetoEspectro in diccionario_espectros_vs_dirreciones.values():
            fn.controlerror_isinstance(objetoEspectro, st.Espectro)

        self._espectrosAcel = diccionario_espectros_vs_dirreciones

    @property
    def especDespArray(self):
        """
        Devuelve los espectros de desplazamiento generador por cada dirrecion

        -------
        [   serietiempo.Espectro desplzamiento,     #Dirrecion1
            serietiempo.Espectro desplzamiento,     #Dirrecion2
            serietiempo.Espectro desplzamiento,     #Dirrecion3
            ]
        """
        return np.array(list(self._espectrosDesp.values()))

    @especDespArray.setter
    def especDespArray(self, array_de_objetos_espectros):
        """
        Edita los valores de especdesp ya existentes, no funciona para asignar
        """

        fn.controlerror_isinstance(array_de_objetos_espectros, np.ndarray)

        fn.controlerror_tamano_lista_igual(array_de_objetos_espectros, len(self._espectrosDesp),
                                           texto = 'El array de especdesp debe tener la misma cantidad de objetos '
                                                   'existente')

        for indice, keyName in enumerate(self._espectrosDesp):
            self._espectrosDesp[keyName] = array_de_objetos_espectros[indice]

    @property
    def especVelArray(self):
        """
        Devuelve los espectros de velocidad generador por cada dirrecion

        -------
        [   serietiempo.Espectro velocidad,     #Dirrecion1
            serietiempo.Espectro velocidad,     #Dirrecion2
            serietiempo.Espectro velocidad,     #Dirrecion3
            ]
        """
        return np.array(list(self._espectrosVel.values()))

    @especVelArray.setter
    def especVelArray(self, array_de_objetos_espectros):
        """
        Edita los valores de especvel ya existentes, no funciona para asignar
        """

        fn.controlerror_isinstance(array_de_objetos_espectros, np.ndarray)

        fn.controlerror_tamano_lista_igual(array_de_objetos_espectros, len(self._espectrosVel),
                                           texto = 'El array de especvel debe tener la misma cantidad de objetos '
                                                   'existente')

        for indice, keyName in enumerate(self._espectrosVel):
            self._espectrosVel[keyName] = array_de_objetos_espectros[indice]

    @property
    def especAcelArray(self):
        """
        Devuelve los espectros de aceleracion generador por cada dirrecion

        -------
        [   serietiempo.Espectro aceleracion,     #Dirrecion1
            serietiempo.Espectro aceleracion,     #Dirrecion2
            serietiempo.Espectro aceleracion,     #Dirrecion3
            ]
        """
        return np.array(list(self._espectrosAcel.values()))

    @especAcelArray.setter
    def especAcelArray(self, array_de_objetos_espectros):
        """
        Edita los valores de especacel ya existentes, no funciona para asignar
        """

        fn.controlerror_isinstance(array_de_objetos_espectros, np.ndarray)

        fn.controlerror_tamano_lista_igual(array_de_objetos_espectros, len(self._espectrosAcel),
                                           texto = 'El array de especacel debe tener la misma cantidad de objetos '
                                                   'existente')

        for indice, keyName in enumerate(self._espectrosAcel):
            self._espectrosAcel[keyName] = array_de_objetos_espectros[indice]

    @property
    def especDespData(self):
        """
        Devuelve un array con los datos de cada espectro guardada en el nivel.
        array.shape = (n_registrosaceleraciones, n_puntos espectro)

        [   datos (array),
            datos (array),
            datos (array),
            .
            .
            .
            ]
        """

        lista = list(map(lambda espectro: espectro.serieArray, self.especDespArray))
        return np.array(lista, dtype = np.float32)

    @especDespData.setter
    def especDespData(self, data_espectro_desplzamiento: np.ndarray):

        # Verificar que el valor sea un array
        data_espectro_desplzamiento = fn.controlerror_listtuple_toarray(data_espectro_desplzamiento)

        # Verificar que el taño del array de la primera dimension sea igual al numero de dirreciones
        fn.controlerror_tamano_lista_igual(data_espectro_desplzamiento, self.nDirreciones)

        # Asignar array a cada dirrecion
        for indice, objetoEspeDesp in enumerate(self._espectrosDesp.values()):
            objetoEspeDesp.serieArray = data_espectro_desplzamiento[indice]

    @property
    def especVelData(self):
        """
        Devuelve un array con los datos de cada espectro guardada en el nivel.
        array.shape = (n_registrosaceleraciones, n_puntos espectro)

        [   datos (array),
            datos (array),
            datos (array),
            .
            .
            .
            ]
        """

        lista = list(map(lambda espectro: espectro.serieArray, self.especVelArray))
        return np.array(lista, dtype = np.float32)

    @especVelData.setter
    def especVelData(self, data_espectro_velocidad: np.ndarray):

        # Verificar que el valor sea un array
        data_espectro_velocidad = fn.controlerror_listtuple_toarray(data_espectro_velocidad)

        # Verificar que el taño del array de la primera dimension sea igual al numero de dirreciones
        fn.controlerror_tamano_lista_igual(data_espectro_velocidad, self.nDirreciones)

        # Asignar array a cada dirrecion
        for indice, objetoEspecVel in enumerate(self._espectrosVel.values()):
            objetoEspecVel.serieArray = data_espectro_velocidad[indice]

    @property
    def especAcelData(self):
        """
        Devuelve un array con los datos de cada espectro guardada en el nivel.
        array.shape = (n_registrosaceleraciones, n_puntos espectro)

        [   datos (array),
            datos (array),
            datos (array),
            .
            .
            .
            ]
        """

        lista = list(map(lambda espectro: espectro.serieArray, self.especAcelArray))
        return np.array(lista, dtype = np.float32)

    @especAcelData.setter
    def especAcelData(self, data_espectro_velocidad: np.ndarray):

        # Verificar que el valor sea un array
        data_espectro_velocidad = fn.controlerror_listtuple_toarray(data_espectro_velocidad)

        # Verificar que el taño del array de la primera dimension sea igual al numero de dirreciones
        fn.controlerror_tamano_lista_igual(data_espectro_velocidad, self.nDirreciones)

        # Asignar array a cada dirrecion
        for indice, objetoEspecVel in enumerate(self._espectrosAcel.values()):
            objetoEspecVel.serieArray = data_espectro_velocidad[indice]

    @property
    def tiempoRegAcel(self):
        return self.regacelArray[0].tiempoArray

    @property
    def periodosEspec(self):
        return self.especAcelArray[0].periodos

    @staticmethod
    def _get_max(objeto_serie):
        maxList = []

        for serieTiempo in objeto_serie:
            maxList.append(serieTiempo.max)

        maxSerie = max(maxList)

        return maxSerie

    @staticmethod
    def _get_min(objeto_serie):
        minList = []

        for serieTiempo in objeto_serie:
            minList.append(serieTiempo.min)

        minSerie = min(minList)

        return minSerie

    @staticmethod
    def _get_npuntos(objeto_serie):
        nPuntosList = []

        for serieTiempo in objeto_serie:
            nPuntosList.append(serieTiempo.nPuntos)

        nPuntosSerie = fn.controlerror_igualvalores_list(nPuntosList)

        return nPuntosSerie

    def plot_dirrecion_regacel(self, dirrecion, *args, x_label: str = '', y_label: str = '',
                               title: str = '', legend: bool = False, show: bool = False,
                               unidad_tiempo = None, unidad_serie = None, subplot_axes: plt.axis = None, **kwargs):
        serie_tiempo_obj:st.RegistroAceleracion = self.regacelArray[dirrecion]

        serie_tiempo_obj.plot_xy(*args, x_label = x_label, y_label = y_label, title = title, legend = legend,
                                 show = show, unidad_tiempo = unidad_tiempo, unidad_serie = unidad_serie,
                                 subplot_axes = subplot_axes, **kwargs)




    def _control_error_exitencia_aceleracion(self):
        if self._regAceleracionDict == {}:
            raise RuntimeError('Aun no se define la aceleracion del nivel')

    def _control_error_exitencia_espectro_desp(self):
        if self._espectrosDesp == {}:
            raise RuntimeError('Aun no se crea ningun espectro de desplzamiento')

    def _control_error_exitencia_espectro_vel(self):
        if self._espectrosVel == {}:
            raise RuntimeError('Aun no se crea ningun espectro de Velocidad')

    def _control_error_exitencia_espectro_acel(self):
        if self._espectrosAcel == {}:
            raise RuntimeError('Aun no se crea ningun espectro de Aceleracion')

    def crear_espectros(self, periodos_array: list or tuple or np.ndarray,
                        amortiguamiento: float = 0.05, tipo_metodo: str = 'Newmark1',
                        tipo_espectro: str = 'espectros'):

        self._control_error_exitencia_aceleracion()

        for direccionName, aceleracion in self._regAceleracionDict.items():
            # name: el nombre que se escoja al definir las aceleraciones, se recomeinda que sean dirreciones
            # se usará dirreicon 'X' & 'Y'
            especDesp, especVel, especAcel = aceleracion.gen_espectros(periodos_array, amortiguamiento,
                                                                       tipo_metodo, tipo_espectro)

            self._espectrosDesp[direccionName] = especDesp
            self._espectrosVel[direccionName] = especVel
            self._espectrosAcel[direccionName] = especAcel

        return self._espectrosDesp, self._espectrosVel, self._espectrosAcel
