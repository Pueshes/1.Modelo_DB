from libreria_OpenSees.Funciones_texto import *
import subprocess


#############################################################
def extraer_variable(file, Nombre_variable, out_Unidad=False):
    texto_busca = 'set ' + Nombre_variable

    linea = extrer_linea(file, texto_busca)

    if linea.find('expr') >= 0:
        variable = linea.split(' ')
        valor_completo = variable[3].split('*')
        valor = valor_completo[0]

        Unidad = valor_completo[1]
        Unidad = Unidad.strip('$]')

    else:
        variable = linea.split(' ')
        valor = variable[2]
        Unidad = False

    if out_Unidad == True and Unidad:

        return round(float(valor), 2), Unidad

    elif out_Unidad == True:
        print('no existe unidad')
        return round(float(valor), 2)

    else:

        return round(float(valor), 2)


#################################################


###############################################
def cambiar_variable(file, Nombre_variable, valor, unidad='m'):
    if unidad == False:
        N_linea1 = buscar_linea(file, Nombre_variable)
        Linea1 = 'set ' + Nombre_variable + ' ' + str(valor)
        cambiar_linea(file, N_linea1, Linea1)
    else:

        unidad = '*$' + unidad
        N_linea1 = buscar_linea(file, Nombre_variable)
        Linea1 = 'set ' + Nombre_variable + ' [expr ' + str(valor) + unidad + ']'
        cambiar_linea(file, N_linea1, Linea1)


###################################################
def get_period(Hcol, Bcol, Dir_Opensees, file_run, file_Periods, out_periods=1):
    cambiar_variable(file_run, 'Hcol', Hcol)
    cambiar_variable(file_run, 'Bcol', Bcol)

    subprocess.run([Dir_Opensees, file_run], capture_output=True)

    with open(file_Periods) as f:
        periodos = f.readlines()

    # print(f'Periodos= {espPeriodos[0]} y {espPeriodos[1]}', end= '\n')

    t1 = float(periodos[0])
    t2 = float(periodos[1])

    if out_periods == 1:
        return t1
    elif out_periods == 2:
        return t1, t2
    else:
        return False


####################################################
def buscar_optimo(T, Hcol_i, Bcol_i, tolerancia, Dir_Opensees, file_run, file_Periods, incr=0.025,
                  limite_interaciones=100):
    """
    Busca el optimo con un algoritmo simple: Si el periodo es muy bajo
    se aumenta rigidez, y si muy alto se disminuye. Eficiencia depende de las
    dimensiones iniciales

    Parameters
    ----------
    T : float
        Periodo objetivo.
    Hcol_i : float
        Altura de la columna inicial.
    Bcol_i : float
        Base de la columna inicial.
    tolerancia : float
        Tolerancia al error para indicar que se llegó al optimo,
        se expresa en porcentaje.
    Dir_Opensees : str
        Ruta del file del ejecutable del OpenSees.exe.
    file_run : str
        Ruta del file donde se encuentran los paremetros de edifico
        y se corre el modelo.
    file_Periods : str
        Ruta del file donde se encuentran los espPeriodos
        arrojados por el edificio.
    incr : float, optional
        Crecimiento o disminución de las dimensiones de la columna
        . The default is 0.025.
    limite_interaciones : int, optional
        Limite de iteraciones para indicar si el programa converge o no
        . The default is 100.

    Returns
    -------
    None.

    """
    # tolerancia es la diferencia en porcentaje entre el periodo real y el obejtivo
    Hcol = Hcol_i  # 20
    Bcol = Bcol_i  # 20

    contador = 0
    while True:

        cambiar_variable(file_run, 'Hcol', Hcol)
        cambiar_variable(file_run, 'Bcol', Bcol)

        subprocess.run([Dir_Opensees, file_run], capture_output=True)

        with open(file_Periods) as f:
            periodos = f.readlines()

        # print(f'Periodos= {espPeriodos[0]} y {espPeriodos[1]}', end= '\r')

        t1 = float(periodos[0])
        t2 = float(periodos[1])

        porcentaje1 = (t1 - T) / T * 100
        porcentaje2 = (t2 - T) / T * 100

        print(f'Porcentaje de Error:{porcentaje1} con dim: {Hcol}', end='\n')

        if abs(porcentaje1) < tolerancia:
            print('se llegó a las dimensiones optimas', end='\n')
            print('Hcol', Hcol, '\n', end='\n')
            break

        if porcentaje1 > 0 or Hcol < 0:
            # El periodo es muy grande, aumentar rigidez
            Hcol += incr
            Bcol += incr
            Hcol = round(Hcol / incr) * incr
            Bcol = round(Bcol / incr) * incr

        elif porcentaje1 < 0:
            # El periodo es muy bajo, disminuir riquidez
            Hcol -= incr
            Bcol -= incr
            Hcol = round(Hcol / incr) * incr
            Bcol = round(Bcol / incr) * incr

        if contador > limite_interaciones:
            print('se llegó al limite de interaciones', end='\n')
            Hcol = False
            Bcol = False
            break

        contador += 1

    return Hcol, Bcol


def buscar_optimo_bi(T, Hcol_min, Hcol_max, tolerancia, Dir_Opensees, file_run, file_Periods,
                     incr=0.025, limite_interaciones=100, print_int=False, out_tm=True):
    """
    Funcion que buscan las columnas optimas tomando solumnas cuadradas mediante el metodo de biseccion.
    Se requiere una dimension minima y maxima de la columna.

    Parameters
    ----------
    T : float
        Periodo obejetivo al que el edificio debe llegar
    Hcol_min : float
        Dimensión de la columna en metros minma con la que se empezará la iteración.
    Hcol_max : float
        Dimensión de la columna en metros maxima con la que se empezará la iteración.
    tolerancia : float
        Porcentaje minimo de error que se debe decir que es optimo.
    Dir_Opensees : str
        Ruta del file donde se encuentra el ejecutable del OpenSees.
    file_run : str
        Ruta del file donde se encuentra el archivo run con lo parametros del modelo.
    file_Periods : str
        Ruta del file donde se encuentra el archivo de texto donde se guardar los espPeriodos.
    incr : float, optional
        Multiplo al cual se ajusta la dimensión de la columna, es decir si es 0.025 las dimensione sposibles serán 1.025, 1.05, 1.075. The default is 0.025.
    limite_interaciones : int, optional
        Limite de iteraciones para saber si converge. The default is 100.
    print_int : bool, optional
        Indica si quiere que se imprima el error en cada iteracion.
        The default is False.
    Returns
    -------
    Hcol : float, str o bool
        Dimensión final de Hcol, en caso se de retorne err1 quiere decir que los valores no encierran solución. Si rotrna False quiere decir que no
    Bcol : float, str o bool
        Dimension final de Bcol.

    """

    Hcol_a = Hcol_min
    Bcol_a = Hcol_min
    Hcol_b = Hcol_max
    Bcol_b = Hcol_max

    # CALCULAR EL PERIODO MAXIMO Y MINIMO

    ta = get_period(Hcol_a, Bcol_a, Dir_Opensees, file_run, file_Periods)
    tb = get_period(Hcol_b, Bcol_b, Dir_Opensees, file_run, file_Periods)

    fa = T - ta;  # si el ta es menor que T entonces fa positivo
    fb = T - tb;  # si el tb es mayor que T entonces fb negtivo

    if fa * fb >= 0:
        print(f'!!!!!H_min: {Hcol_min} y H_max: {Hcol_max} no encierran la solucion, incremente Hmax', end='\n')
        if out_tm == True:
            return None, None, None
        else:
            return None, None
    # El retorno de err1 indica que no se escogió mal Hcol_max

    contador = 0
    while True:

        if contador > limite_interaciones:
            print('!!!!!Se llegó al limite de iteraciones', '\n')
            Hcol = False
            Bcol = False
            # False como retorno indica que se llegó al limité de iteraciones
            break

        Hcol_m = (Hcol_a + Hcol_b) / 2
        Bcol_m = Hcol_m

        tm = get_period(Hcol_m, Bcol_m, Dir_Opensees, file_run, file_Periods)
        fm = T - tm

        error = abs(fm / T * 100)

        if print_int == True:
            print(f'*Con las dimenisones {Hcol_m} y {Bcol_m} se obtiene un error de {error}', end='\n')

        if error < tolerancia:
            Hcol = round(Hcol_m / incr) * incr
            Bcol = round(Bcol_m / incr) * incr
            print(f'***Se llegó a la dimensiones optimas: {Hcol} , {Bcol}', end='\n')
            print(f'***El periodo mas cercano es {tm} ', end='\n')
            break

        if fa * fm < 0:
            Hcol_b = Hcol_m

            tb = tm
            fb = fm

        else:
            Hcol_a = Hcol_m

            ta = tm
            fa = fm

        contador += 1

    if out_tm == True:
        return Hcol, Bcol, tm
    else:
        return Hcol, Bcol


def set_variable(file_run: str, n_story:int, baysx:int, baysy:int, hz:float,
                 lbx:float, lby:float,
                 hbx:float, hby:float,
                 bbx:float, bby:float,
                 t_max:float,
                 dir_out1=None, dir_out2 = None,
                 hcol=None, bcol=None):
    """

    Args:
        file_run: str, ruta donde se cambiarán las variables
        n_story: int, numero de pisos
        baysx: int, numero de vanos en x
        baysy: int, numero de vanos en y
        hz: float, altura de entrepiso
        lbx: float, longitud de vano en x
        lby: flaat, longitud de vano en y
        hbx: float, altura de la viga en x
        hby: float, altura de la viga en y
        bbx: float, base de la viga en x
        bby: float, base de la viga en y
        t_max: float, array_tiempo que tendra recorder de salida
        dir_out1: str or None, direccion de carpeta nivel 1 donde se guardaran los resultados,
            si es None no se cambia el dir existente en la hoja run.
        dir_out2: str or None, direccion de carpeta nivel 2 donde se guardaran los resultados,
            si es None no se cambia el dir existente en la hoja run.
    Returns:
        retorna solo 0
    """
    cambiar_variable(file_run, 'story', n_story, unidad=False)
    cambiar_variable(file_run, 'baysX', baysx, unidad=False)
    cambiar_variable(file_run, 'baysY', baysy, unidad=False)
    cambiar_variable(file_run, 'Hz', hz)
    cambiar_variable(file_run, 'LbX', lbx)
    cambiar_variable(file_run, 'LbY', lby)
    cambiar_variable(file_run, 'Hbx', hbx)
    cambiar_variable(file_run, 'Hby', hby)
    cambiar_variable(file_run, 'Bbx', bbx)
    cambiar_variable(file_run, 'Bby', bby)
    cambiar_variable(file_run, 'TmaxAnalysis', t_max, unidad = 'seg')

    if dir_out1 is not None:
        cambiar_variable(file_run, 'dir_out1', '"'+ dir_out1 + '"' ,unidad= False)

    if dir_out2 is not None:
        cambiar_variable(file_run, 'dir_out2', '"E'+ str(dir_out2)+ '"' ,unidad= False)

    if hcol is not None and bcol is not None:
        cambiar_variable(file_run, 'Hcol', hcol )
        cambiar_variable(file_run, 'Bcol', bcol )

    return 0
