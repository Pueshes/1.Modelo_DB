def _cambiar_unidad_base(tipo_unidad_dict: dict, unidad_base: str):
    factorDeCambio = tipo_unidad_dict.get(unidad_base)

    for unidad in tipo_unidad_dict:
        # valorAntiguo= tipo_unidad_dict[unidad]
        # tipo_unidad_dict[unidad] = valorAntiguo/factorDeCambio

        tipo_unidad_dict[unidad] /= factorDeCambio

    return tipo_unidad_dict


def _verificar_inclusion_unidad(tipo_unidad, unit):
    return unit in tipo_unidad.keys()


class Unidades:
    def __init__(self, long: str = 'm', tiempo: str = 's', masa: str = 'kg'):
        self._longDefault = long
        self._tiempoDefault = tiempo
        self._masaDefault = masa
        self._listaDeTiposDeUnidad = []

        # Unidades base
        self.longitud = {'cm': 1, 'm': 100, 'km': 1000 * 100}
        self._listaDeTiposDeUnidad.append(self.longitud)

        self.tiempo = {'s': 1, 'min': 60, 'h': 3600}
        self._listaDeTiposDeUnidad.append(self.tiempo)

        self.masa = {'g': 1, 'kg': 1000, 'mg': 1 / 1000}
        self._listaDeTiposDeUnidad.append(self.masa)

        # cambio de unidades base
        _cambiar_unidad_base(self.longitud, self._longDefault)
        _cambiar_unidad_base(self.tiempo, self._tiempoDefault)
        _cambiar_unidad_base(self.masa, self._masaDefault)

        # Unidades derivadas
        self.area = {
            'cm2': self.longitud['cm'] ** 2,
            'm2': self.longitud['m'] ** 2,
            'km2': self.longitud['km'] ** 2
            }
        self._listaDeTiposDeUnidad.append(self.area)

        self.volumen = {
            'cm3': self.longitud['cm'] ** 3,
            'm3': self.longitud['m'] ** 3,
            'km3': self.longitud['km'] ** 3
            }
        self._listaDeTiposDeUnidad.append(self.volumen)

        self.velocidad = {
            'm/s': self.longitud['m'] / self.tiempo['s'],
            'cm/s': self.longitud['cm'] / self.tiempo['s'],
            'km/h': self.longitud['km'] / self.tiempo['h']
            }
        self._listaDeTiposDeUnidad.append(self.velocidad)

        self.aceleracion = {
            'm/s2': self.longitud['m'] / (self.tiempo['s'] ** 2),
            'cm/s2': self.longitud['cm'] / (self.tiempo['s'] ** 2),
            'g': 9.81 * 100 * self.longitud['cm'] / (self.tiempo['s'] ** 2)
            }
        self._listaDeTiposDeUnidad.append(self.aceleracion)

    def _find_unit_type(self, unit: str):

        tipoDeUnidadEncontrado = None

        for tipoDeUnidad in self._listaDeTiposDeUnidad:
            if _verificar_inclusion_unidad(tipoDeUnidad, unit) is True:
                tipoDeUnidadEncontrado = tipoDeUnidad

        if tipoDeUnidadEncontrado is None:
            raise ValueError('La unidad no existe')

        return tipoDeUnidadEncontrado

    @staticmethod
    def _conditional_print( variable_condition, print_message):
        if variable_condition is True:
            print(print_message)

    def assing_unit(self, value: float, unit: str):
        diccionarioDeTipoDeUnidad = self._find_unit_type(unit)
        factorUnidad = diccionarioDeTipoDeUnidad.get(unit)

        valorDeSalida = value * factorUnidad

        return valorDeSalida

    def convertir_unit(self, value: float, unit: str, imprimir = False):
        diccionarioDeTipoDeUnidad = self._find_unit_type(unit)
        factorUnidad = diccionarioDeTipoDeUnidad.get(unit)

        valorDeSalida = value / factorUnidad

        self._conditional_print(imprimir, f'{valorDeSalida} {unit}')

        return valorDeSalida

    def get_default(self):
        salida = {'longitud': self._longDefault,
                  'array_tiempo': self._tiempoDefault,
                  'masa': self._masaDefault}

        return salida

    def print_default(self):
        salida=self.get_default()
        print(salida)
