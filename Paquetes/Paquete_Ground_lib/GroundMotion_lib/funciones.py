import collections
import os.path

import numpy as np


def completar_zeros(array_original: np.ndarray, new_shape: tuple):
    nDim = array_original.ndim

    shape_original = array_original.shape
    array_ceros = np.zeros(new_shape)

    if nDim == 2:
        array_ceros[:shape_original[0], :shape_original[1]] = array_original
    elif nDim == 3:
        array_ceros[:shape_original[0], :shape_original[1], :shape_original[2]] = array_original
    else:
        raise ValueError('No funciona para más de 3 dimensiones')

    return array_ceros


def splitext_desde_listas_de_paths(lista: list):
    """
    Funcion que recibe como argumento una lista con textos pertecientes a archivos con exteciones, la funcion devulve
    un array con el nombre del file y la extenesion
    Parameters
    ----------
    lista: list
        lista con textos pertenecientes a nombres de archivos con extensiones

    Returns
    -------

    np.ndarray:
    shape= (n_list, 2)
    [   [nombre file, extension],
        [nombre file, extension],
        .
        .
        .
    ]
    """
    listaSplit = list(map(os.path.splitext, lista))
    listaSplit = np.array(listaSplit)

    return listaSplit


def controlerror_igualdad_keys_de_dicts(*args):
    keys = list(map(lambda diccio: diccio.keys(), args))

    for i in range(len(keys) - 1):
        if collections.Counter(keys[i]) != collections.Counter(keys[i + 1]):
            raise ValueError('Los diccionarios no tiene los mismos keys')


def controlerror_isnone(parametro,
                        texto = 'El parametro aun no esta definido'):
    if parametro is None:
        raise AttributeError(texto)


def controlerror_isinstance(objeto, clase):
    if not isinstance(objeto, clase):
        raise ValueError(f'El objeto {objeto} no pertenece a la clase {clase}')


def controlerror_tamano_lista_igual(lista: list or np.ndarray, tamano,
                                    texto = 'La lista no tiene el tamaño esperado'):
    if len(lista) != tamano:
        raise ValueError(texto)


def controlerror_tamano_lista_diferente(lista: list, tamano,
                                        texto = 'La lista no tiene el tamaño esperado'):
    if len(lista) == tamano:
        raise ValueError(texto)


def controlerror_tamano_lista_mayor(lista: list, tamano,
                                    texto = 'La lista no tiene el tamaño esperado'):
    if len(lista) < tamano:
        raise ValueError(texto)


def controlerror_tamano_lista_menor(lista: list, tamano,
                                    texto = 'La lista no tiene el tamaño esperado'):
    if len(lista) > tamano:
        raise ValueError(texto)


def controlerror_listtuple_toarray(variable_de_control,
                                   texto = 'el elemento del parametro no es correcto ...') -> np.ndarray:
    ##############################################################

    # CONTROL PARA carga_externa
    if isinstance(variable_de_control, list) or isinstance(variable_de_control, tuple):
        # Si la carga es una lista o tupla pasar a array
        variable_retornada = np.array(variable_de_control)
    elif isinstance(variable_de_control, np.ndarray):
        variable_retornada = variable_de_control
    else:
        # si tampoco es un array, entonces hay un error
        raise TypeError(texto)

    return variable_retornada


def controlerror_igualvalores_list(lista: list or np.ndarray or tuple):
    """
    Verifica si todos los valores de la lista son iguales. En caso no serlo lanzará un error, ValueError

    Parameters
    ----------
    lista: list, np.ndarray, tuple
    """
    valoresRepetidosSuprimidos = set(lista)

    if len(valoresRepetidosSuprimidos) != 1:
        raise ValueError('La lista tiene distintos valores')

    resultado = valoresRepetidosSuprimidos.pop()
    return resultado


def controlerror_igualdad_tamanolist(*args):
    """
    Funcion que verifica que todas las listas, arrays, o tuplas pasadas como argumentos tengan el mismo tamaño.
    En caso no sean iguales lanzara un ValueError.

    Parameters
    ----------
    args: list or np.ndarray

    """
    # CONTROL SI SE DESEA QUE TODOS LOS ARRAY SEAN DEL MISMO TAMAÑO
    tamanos = []
    for array in args:
        tamanos.append(len(array))

    tamanosSet = set(tamanos)

    if len(tamanosSet) > 1:
        raise ValueError('Los array no tienen el mismo size')


class MetodosNumericos:

    def __init__(self, carga_externa: np.ndarray or list or tuple, frec_muestreo: float or int,
                 periodo: float = None, razon_amort: float = None,
                 rigidez: float = None, coef_amortiguamiento: float = None,
                 masa: float = -1.0, u0: float = 0.0, u_punto0: float = 0.0, carga_isground_motion = False):

        # Parametros iniciales para los calculos
        self.frecMuestreo = frec_muestreo
        self.periodo = periodo
        self.razonAmort = razon_amort
        self.rigidez = rigidez
        self.coefAmortiguamiento = coef_amortiguamiento
        self.masa = masa

        # Condiciones de contorno
        self.u0 = u0
        self.u_punto0 = u_punto0

        # Respuestas desplazamiento, velocidad y aceleracion
        self.u_out = None
        self.u_punto_out = None
        self.u_dos_puntos_out = None

        # parametros finales para los calculos
        self.parametrosParaCalculo = {}

        # Serie de array_tiempo
        self.cargaExterna = carga_externa
        self.cargaIsGroundMotion = carga_isground_motion
        self.cargaUsada = None

        # Metodos disponibles
        self.metodosDisponibles = {'NEWMARK1': self.newmark1,
                                   'NEWMARK2': self.newmark2,
                                   'PIECEWISE': self.piece_wise_linear}

        # CONTROL CUANDO AL INGRESAR LOS PARAMETROS periodo, razon_amort, rigidez, coef_amortiguamiento
        if self._verificar_entradas_conjuntas_para2(self.periodo, self.razonAmort):
            self._generar_datos_con_periodo_razonamort()
        elif self._verificar_entradas_conjuntas_para2(self.rigidez, self.coefAmortiguamiento):
            self._generar_datos_con_rigidez_coefamort()
        else:
            raise ValueError(
                    'No se ingresó ningun par de datos (periodo, razon_amort) o (rigidez, coef_amortiguamiento)')

        self.cargaExterna = controlerror_listtuple_toarray(self.cargaExterna)
        self._obtener_cargausada()

    @staticmethod
    def _verificar_entradas_conjuntas_para2(variable1, variable2,
                                            texto_error: str = 'Las viriables se deben ingresar en pares...'):
        conValores = True

        if variable1 is None and variable2 is None:
            conValores = False
        elif variable1 is None or variable2 is None:
            raise ValueError(texto_error)

        return conValores

    def _generar_datos_con_rigidez_coefamort(self):

        k = self.rigidez
        coefAmort = self.coefAmortiguamiento

        wn = np.sqrt(k / self.masa)
        razonAmort = coefAmort / (2 * self.masa * wn)
        wd = wn * np.sqrt(1 - razonAmort ** 2)

        self.parametrosParaCalculo['k'] = k
        self.parametrosParaCalculo['wn'] = wn
        self.parametrosParaCalculo['coefAmort'] = coefAmort
        self.parametrosParaCalculo['razonAmort'] = razonAmort
        self.parametrosParaCalculo['wd'] = wd

        return self.parametrosParaCalculo

    def _generar_datos_con_periodo_razonamort(self):

        razonAmort = self.razonAmort
        wn = 2 * np.pi / self.periodo

        wd = wn * np.sqrt(1 - razonAmort ** 2)
        k = wn ** 2 * self.masa
        coefAmort = 2 * razonAmort * self.masa * wn

        self.parametrosParaCalculo['k'] = k
        self.parametrosParaCalculo['wn'] = wn
        self.parametrosParaCalculo['coefAmort'] = coefAmort
        self.parametrosParaCalculo['razonAmort'] = razonAmort
        self.parametrosParaCalculo['wd'] = wd

        return self.parametrosParaCalculo

    def _obtener_cargausada(self):
        # ACCION PARA carga_isground_motion
        if self.cargaIsGroundMotion is True:
            # Si la carga externa es un ground motion de aceleración, se debe multiplicar por la masa
            self.cargaUsada = self.cargaExterna * self.masa
        else:
            self.cargaUsada = self.cargaExterna

    def get_metodos_disp(self):
        return self.metodosDisponibles

    def piece_wise_linear(self):
        ##############################################################

        # OBTENCION DE DATOS
        k = self.parametrosParaCalculo['k']
        wn = self.parametrosParaCalculo['wn']
        wd = self.parametrosParaCalculo['wd']
        chi = self.parametrosParaCalculo['razonAmort']

        # CALCULO DE CONSTANTES INICIALES
        delta_t = 1 / self.frecMuestreo

        A = np.exp(-chi * wn * delta_t)
        A *= chi * np.sin(wd * delta_t) / (1 - chi ** 2) ** 0.5 + np.cos(wd * delta_t)

        B = np.exp(-chi * wn * delta_t)
        B *= np.sin(wd * delta_t) / wd

        C = ((1 - 2 * chi ** 2) / (wd * delta_t) - chi / (1 - chi ** 2) ** 0.5) * np.sin(wd * delta_t)
        C += -(1 + 2 * chi / (wn * delta_t)) * np.cos(wd * delta_t)
        C *= np.exp(-chi * wn * delta_t)
        C += 2 * chi / (wn * delta_t)
        C *= 1 / k

        D = (2 * chi ** 2 - 1) / (wd * delta_t) * np.sin(wd * delta_t)
        D += 2 * chi / (wn * delta_t) * np.cos(wd * delta_t)
        D *= np.exp(-chi * wn * delta_t)
        D += 1 - 2 * chi / (wn * delta_t)
        D *= 1 / k

        A2 = -np.exp(-chi * wn * delta_t)
        A2 *= wn * np.sin(wd * delta_t) / (1 - chi ** 2) ** 0.5

        B2 = np.cos(wd * delta_t) - chi * np.sin(wd * delta_t) / (1 - chi ** 2) ** 0.5
        B2 *= np.exp(-chi * wn * delta_t)

        C2 = (wn / (1 - chi ** 2) ** 0.5 + chi / (delta_t * (1 - chi ** 2) ** 0.5)) * np.sin(wd * delta_t)
        C2 += np.cos(wd * delta_t) / delta_t
        C2 *= np.exp(-chi * wn * delta_t)
        C2 += -1 / delta_t
        C2 *= 1 / k

        D2 = chi * np.sin(wd * delta_t) / (1 - chi ** 2) ** 0.5 + np.cos(wd * delta_t)
        D2 *= -np.exp(-chi * wn * delta_t)
        D2 += 1
        D2 *= 1 / (k * delta_t)

        # VARIABLES PARA LA SALIDA
        n_puntos = len(self.cargaExterna)

        self.u_out = np.zeros(n_puntos)
        self.u_punto_out = np.zeros(n_puntos)
        self.u_dos_puntos_out = np.zeros(n_puntos)

        # CALCULO DE ACELERACIÓN INICAL Y ASIGNAR VALORES INICIALES
        self.u_out[0] = self.u0
        self.u_punto_out[0] = self.u_punto0
        self.u_dos_puntos_out[0] = self.cargaUsada[0] / self.masa - chi * self.u_punto0 - wn ** 2 * self.u0

        # CALCULOS ITERATIVOS
        for i in range(n_puntos - 1):
            self.u_out[i + 1] = A * self.u_out[i] + B * self.u_punto_out[i]
            self.u_out[i + 1] += C * self.cargaUsada[i] + D * self.cargaUsada[i + 1]

            self.u_punto_out[i + 1] = A2 * self.u_out[i] + B2 * self.u_punto_out[i]
            self.u_punto_out[i + 1] += C2 * self.cargaUsada[i] + D2 * self.cargaUsada[i + 1]

            self.u_dos_puntos_out[i + 1] = self.cargaUsada[i + 1] / self.masa - chi * self.u_punto_out[i + 1]
            self.u_dos_puntos_out[i + 1] -= wn ** 2 * self.u_out[i + 1]

        return self.u_out, self.u_punto_out, self.u_dos_puntos_out

    def newmark(self, beta: float = 1 / 4, gamma: float = 1 / 2):
        ######################################################

        # OBTENCION DE DATOS

        k = self.parametrosParaCalculo['k']
        c = self.parametrosParaCalculo['coefAmort']
        # #######################################
        # CALCULOS INICIALES

        u_dos_puntos0 = (self.cargaUsada[0] - c * self.u_punto0 - k * self.u0) / self.masa
        delta_t = 1 / self.frecMuestreo

        coef_a1 = self.masa / (beta * delta_t ** 2) + gamma * c / (beta * delta_t)
        coef_a2 = self.masa / (beta * delta_t) + (gamma / beta - 1) * c
        coef_a3 = (1 / (2 * beta) - 1) * self.masa + delta_t * (gamma / (2 * beta) - 1) * c
        # CAMBIO CON CODIGO RODRIGO
        # coef_a2 = self.masa / (beta * delta_t) + c * gamma / beta
        # coef_a3 = self.masa / (2 * beta) + c * delta_t * (gamma / (2 * beta) - 1)
        coef_k_gorro = k + coef_a1

        # VARIABLES PARA LA SALIDA
        n_puntos = len(self.cargaUsada)

        self.u_out = np.zeros(n_puntos).astype(np.float32)
        self.u_punto_out = np.zeros(n_puntos).astype(np.float32)
        self.u_dos_puntos_out = np.zeros(n_puntos).astype(np.float32)

        # ASIGNAR LOS VALORES INICIALES A LA SALIDA
        self.u_out[0] = self.u0
        self.u_punto_out[0] = self.u_punto0
        self.u_dos_puntos_out[0] = u_dos_puntos0

        # CALCULOS ITERATIVOS

        for i in range(n_puntos - 1):
            coef_p_gorro = self.cargaUsada[i + 1]
            coef_p_gorro += coef_a1 * self.u_out[i]
            coef_p_gorro += coef_a2 * self.u_punto_out[i]
            coef_p_gorro += coef_a3 * self.u_dos_puntos_out[i]

            self.u_out[i + 1] = coef_p_gorro / coef_k_gorro

            self.u_punto_out[i + 1] = gamma * (self.u_out[i + 1] - self.u_out[i]) / (beta * delta_t)
            self.u_punto_out[i + 1] += (1 - gamma / beta) * self.u_punto_out[i]
            self.u_punto_out[i + 1] += delta_t * (1 - gamma / (2 * beta)) * self.u_dos_puntos_out[i]

            self.u_dos_puntos_out[i + 1] = (self.u_out[i + 1] - self.u_out[i]) / (beta * (delta_t ** 2))
            self.u_dos_puntos_out[i + 1] += -self.u_punto_out[i] / (beta * delta_t)
            self.u_dos_puntos_out[i + 1] += -(1 / (2 * beta) - 1) * self.u_dos_puntos_out[i]

        return self.u_out, self.u_punto_out, self.u_dos_puntos_out

        # CAMBIO CON CODIGO RODRIGO
        # CALCULOS ITERATIVOS
        #
        # for i in range(n_puntos - 1):
        #     deltap = self.cargaUsada[i + 1] - self.cargaUsada[i]
        #     # coef_p_gorro += coef_a1 * float(self.u_out[i])
        #     deltap += coef_a2 * self.u_punto_out[i]
        #     deltap += coef_a3 * self.u_dos_puntos_out[i]
        #
        #     delta_u_out = deltap / coef_k_gorro
        #
        #     self.u_out[i + 1] = self.u_out[i] + delta_u_out
        #
        #     delta_u_punto_out = gamma * delta_u_out / (beta * delta_t)
        #     delta_u_punto_out -= gamma / beta * self.u_punto_out[i]
        #     delta_u_punto_out += delta_t * (1.0 - gamma / (2.0 * beta)) * self.u_dos_puntos_out[i]
        #
        #     self.u_punto_out[i + 1] = self.u_punto_out[i] + delta_u_punto_out
        #
        #     delta_u_dos_puntos_out = delta_u_out / (beta * (delta_t ** 2))
        #     delta_u_dos_puntos_out -= self.u_punto_out[i] / (beta * delta_t)
        #     delta_u_dos_puntos_out -= self.u_dos_puntos_out[i] / (2.0 * beta)
        #
        #     self.u_dos_puntos_out[i + 1] = self.u_dos_puntos_out[i] + delta_u_dos_puntos_out

    def newmark1(self):
        retornos = self.newmark(1 / 4)
        return retornos

    def newmark2(self):
        retornos = self.newmark(1 / 6)
        return retornos
