# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 17:33:25 2021

@author: Franklin
"""

from libreria_OpenSees.Funciones_texto import extraer_fragmentos_linea, remove_todos
from io import open
import numpy as np
import pandas as pd
import os


###################################################################
# funciones
def CambiarPath(Path):
    """
    Cambia los separadores del path, desde \\ a /
    Parameters
    ----------
    Path : STR
        Ruta o Path de algún archivo o directorio

    Returns
    -------
    Path : STR
        Ruta con el separador cambiado.

    """
    Path = Path.replace('\\', '/')
    return Path


#####################################################################3
def int_Arias(Data_cuadrado, dt):
    """
    Calcula la intensidad de arías de un vector que ya está al cuadrado
    Se debe incluir el dt de la data.

    Parameters
    ----------
    Data_cuadrado : array
        Array de aceleraciones del GM elevados al cuadrado

    dt : float
        Delta de array_tiempo entre los puntos,
        o inversa de la frecuencia toma de datos

    Returns
    -------
    integrado : array
        Los valores integrados en forma de array.

    """

    N_points = len(Data_cuadrado)

    integrado = []

    for i in range(N_points):

        if i == 0:
            integrado.append(0)
        else:

            int_acumulado = integrado[i - 1]
            val_1 = Data_cuadrado[i]
            val_0 = Data_cuadrado[i - 1]

            int_actual = 0.5 * (val_1 + val_0) * dt

            int_total = int_acumulado + int_actual

            integrado.append(int_total)

    integrado = np.array(integrado)

    return integrado


####################################################################
def cort_Arias(Data, dt, E1, E2, Data_t = 0,
               ret_cut = True, ret_time = False,
               ret_int = False):
    #####################DATA IN#############################
    # Data : Array con la data del GM
    # dt : Delta de array_tiempo por cada paso
    # E1 : porcentaje con el primer corte del GM
    # E2: porcentaje con el segundo corte del GM
    # Data_t : OPCIONAL, Array con el array_tiempo del GM, del mismo tamaño que Data
    #########################################################

    # Data1_cuadrado= Data1[:,1]**2
    Data1_cuadrado = Data ** 2
    # t = Data1[:, 0]

    if isinstance(Data_t, int):

        long = len(Data)
        t = np.arange(long) * dt

    elif len(Data) == len(Data_t):

        t = Data_t

    ##########################################################
    # Comienza la integración
    intensidad = int_Arias(Data1_cuadrado, dt) * np.pi / (2 * 9.81)
    max_intensidad = max(intensidad)
    porcentaje_int = intensidad / max_intensidad * 100

    for i, tiempo in enumerate(t):

        if i == 0:
            continue

        porcen1 = porcentaje_int[i]
        porcen0 = porcentaje_int[i - 1]

        if E1 == 0:
            tc1 = t[0]

        else:
            # Verifica si el cambio se da entre la posición actual y la anterior, el valor de corte es donde empezara la nueva array_serie de array_tiempo
            if porcen0 < E1 and porcen1 > E1:
                tc1 = t
                corte1 = i

        if porcen0 < E2 and porcen1 > E2:
            tc2 = t
            corte2 = i

    # RETURN
    if ret_cut == True:
        if ret_time == True and ret_int == True:

            return (corte1, corte2), (tc1, tc2), intensidad

        elif ret_time == True:
            return (corte1, corte2), (tc1, tc2)

        elif ret_int == True:
            return (corte1, corte2), intensidad
        else:
            return corte1, corte2

    else:

        if ret_time == True and ret_int == True:

            return (tc1, tc2), intensidad

        elif ret_time == True:
            return tc1, tc2

        elif ret_int == True:
            return intensidad


##################################################################


###############################################################
def read_V2_file(file_in, file_out,
                 Extension, Up_direction = True,
                 write_data_out = True, out_parametros = True):
    Parametros_out = []
    error = 0
    Channels = 0
    seek = 0

    while True:

        Lista_out = []

        Direccion = extraer_fragmentos_linea(file_in, ['CHAN', 'CORRECTED'], 2, remove_espacio = True, seek_o = seek)
        print(Direccion, end = '\r')

        PGA = extraer_fragmentos_linea(file_in, ['PEAK', 'ACCELERATION'], 3, remove_espacio = True, seek_o = seek)
        print(PGA, end = '\r')

        PGV = extraer_fragmentos_linea(file_in, ['PEAK', 'VELOCITY'], 3, remove_espacio = True, seek_o = seek)
        print(PGV, end = '\r')

        PGD = extraer_fragmentos_linea(file_in, ['PEAK', 'DISPLACEMENT'], 3, remove_espacio = True, seek_o = seek)
        print(PGD, end = '\r')

        delta_t, cursor1 = extraer_fragmentos_linea(file_in, ['AT', 'SEC', 'ACCEL DATA'], 1, cursor = True,
                                                    remove_espacio = True, seek_o = seek)
        print(delta_t, end = '\r')

        Lista_out.append(delta_t)
        Lista_out.append(PGA)
        Lista_out.append(PGV)
        Lista_out.append(PGD)
        Lista_out.append(Direccion)

        if Direccion == False or PGA == False:
            if Channels == 0:
                print('error de lectura', end = '\r')
                error = 1
            else:
                print('Se termino de leer el file', end = '\r')

            break


        elif delta_t == False:
            print('error de lectura, no se encontro DT', end = '\r')
            error = 1
            break

        else:
            Channels += 1

        if (Direccion.find('UP') >= 0 or Direccion.find('VERT') >= 0 or Direccion.find('Z') >= 0):
            # si es Falso entonces no queremos convertir esa TS
            if Up_direction == False:
                seek = cursor1

                continue

        file_out_completo = file_out + '_' + Direccion + Extension

        Lista_out.append(file_out_completo)

        with open(file_out_completo, 'w') as f_out:

            if write_data_out == True:
                f_out.write('Direccion= ' + Direccion + '\n')
                f_out.write('PGA= ' + PGA + '\n')
                f_out.write('DT= ' + delta_t + '\n')
                f_out.write('/&\n')

            with open(file_in, 'r') as f_in:
                f_in.seek(cursor1)

                while True:

                    Linea = f_in.readline()

                    Linea = Linea.upper()

                    buscar1 = Linea.find('POINTS OF')
                    buscar2 = Linea.find('DISPL')
                    buscar3 = Linea.find('VELOC')
                    buscar4 = Linea.find('END OF DATA FOR CHANNEL')

                    end_channel = 0

                    if buscar1 >= 0 or buscar2 >= 0 or buscar3 >= 0:
                        print('se terminaron los points', end = '\r')
                        seek = f_in.tell()
                        break

                    if buscar4 >= 0:
                        print('se termino el channel', end = '\r')
                        end_channel += 1
                        seek = f_in.tell()
                        break

                    # print('Nueva_linea',Linea)
                    Linea = Linea.replace('-', ' -')
                    Linea = Linea.replace('\n', '')
                    Linea = Linea.split(' ')
                    Linea = remove_todos(Linea, ' ')
                    Linea = remove_todos(Linea, '')
                    Linea = remove_todos(Linea, '\n')
                    # print(Linea)

                    for punto in Linea:
                        negativo = punto.find('-')

                        if negativo >= 0:
                            punto = ' ' + punto

                        else:
                            punto = '  ' + punto

                        f_out.write(punto + '\n')

        Parametros_out.append(Lista_out)

    if out_parametros == True:
        return error, Parametros_out
    else:
        return error


###############################################################
def read_P2_file(file_in, file_out,
                 Extension, Up_direction = True,
                 write_data_out = True, out_parametros = True):
    Parametros_out = []
    error = 0
    Channels = 0
    seek = 0

    while True:

        Lista_out = []

        Direccion = extraer_fragmentos_linea(file_in, ['COMP', 'CORRECTED'], 1, remove_espacio = True, seek_o = seek)
        print(Direccion, end = '\r')

        PGA = extraer_fragmentos_linea(file_in, ['ACCELERATION', 'PEAK'], 2, remove_espacio = True, seek_o = seek)
        print(PGA, end = '\r')

        PGV = extraer_fragmentos_linea(file_in, ['VELOCITY', 'PEAK'], 2, remove_espacio = True, seek_o = seek)
        print(PGV, end = '\r')

        PGD = extraer_fragmentos_linea(file_in, ['DISPLACEMENT', 'PEAK'], 2, remove_espacio = True, seek_o = seek)
        print(PGD, end = '\r')

        delta_t, cursor1 = extraer_fragmentos_linea(file_in, ['AT', 'SEC', 'ACC DATA'], 1, remove_espacio = True,
                                                    cursor = True, seek_o = seek)
        print(delta_t, end = '\r')

        Lista_out.append(delta_t)
        Lista_out.append(PGA)
        Lista_out.append(PGV)
        Lista_out.append(PGD)
        Lista_out.append(Direccion)

        if Direccion == False or PGA == False:

            if Channels == 0:
                print('error de lectura', end = '\r')
                error = 1
            else:
                print('Se termino de leer el file', end = '\r')
            break


        elif delta_t == False:
            print('error de lectura, no se encontro DT', end = '\r')
            error = 1
            break

        else:
            Channels += 1

        if (Direccion.find('UP') >= 0 or Direccion.find('VERT') >= 0 or Direccion.find('Z') >= 0):
            # si es Falso entonces no queremos convertir esa TS
            if Up_direction == False:
                seek = cursor1
                continue

        file_out_completo = file_out + '_' + Direccion + Extension

        Lista_out.append(file_out_completo)

        with open(file_out_completo, 'w') as f_out:

            if write_data_out == True:
                f_out.write('Direccion= ' + Direccion + '\n')
                f_out.write('PGA= ' + PGA + '\n')
                f_out.write('DT= ' + delta_t + '\n')
                f_out.write('/&\n')

            with open(file_in, 'r') as f_in:
                f_in.seek(cursor1)

                while True:

                    Linea = f_in.readline()

                    Linea = Linea.upper()

                    buscar1 = Linea.find('POINTS OF')
                    buscar2 = Linea.find('DISPL')
                    buscar3 = Linea.find('VELOC')
                    buscar4 = Linea.find('/&')

                    end_channel = 0

                    if buscar1 >= 0 or buscar2 >= 0 or buscar3 >= 0:
                        print('se terminaron los points', end = '\r')
                        seek = f_in.tell()
                        break

                    if buscar4 >= 0:
                        print('se termino el channel', end = '\r')
                        end_channel += 1
                        seek = f_in.tell()
                        break

                    Linea = Linea.replace('-', ' -')
                    Linea = Linea.replace('\n', '')
                    Linea = Linea.split(' ')
                    Linea = remove_todos(Linea, ' ')
                    Linea = remove_todos(Linea, '')
                    Linea = remove_todos(Linea, '\n')

                    for punto in Linea:
                        negativo = punto.find('-')

                        if negativo >= 0:
                            punto = ' ' + punto

                        else:
                            punto = '  ' + punto

                        f_out.write(punto + '\n')

        Parametros_out.append(Lista_out)

    if out_parametros == True:
        return error, Parametros_out
    else:
        return error
