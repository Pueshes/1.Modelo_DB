import os
from libreria_OpenSees.Funciones_TCL import set_variable, buscar_optimo_bi
from tqdm import tqdm
import pandas as pd
import time
from datetime import date
import joblib

# files importantes
Dir_files = os.getcwd()
Dir_Opensees = os.path.join(Dir_files, 'OpenSees.exe')  # FILE DEL EJECUTABLE
file_run = os.path.join(Dir_files, 'Run_parametros.tcl')  # FILE DEL ARCHIVO CON PARAMETROS
file_Periods = os.path.join(Dir_files, 'Periodos/periodos.out')

# PATH DONDE SE GUARDARÁ LA BASE DE DATOS
file_out = os.path.join('../Base_datos/DB_Edificios.csv')

# tolerancia de 95.105
tolerancia = 100 - 95.105
limite_interaciones = 70

# Distancias entre vanos de 3.0 a 7.0
Distancias_vanos = [3, 4, 5, 6, 7]
# Distancias_vanos = [3, 7]

# cantidad de vanos de 3 a 10
Cantidad_vanos = [3, 4, 5, 6, 8, 10]
# Cantidad_vanos = [3, 4]

# Numero de Pisos de 3 a 25
# Numeros_pisos=[n for n in range(3,25,4)]
Numeros_pisos = [3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 25]
# Numeros_pisos = [10, 20]

# de 2.5 a 3.5
Alturas_piso = [2.5, 3.0]
# Alturas_piso = [2.5]

# Guardar Historial de corrida
fecha_hoy = date.today()
hora_hoy = time.strftime('%H-%M-%S')
historial = {
    'desc': f'Se corrió el archivo Generar_Parametros3.py la fecha: {fecha_hoy} a las {hora_hoy}',
    'Distancias_vanos': Distancias_vanos,
    'Cantidad_vanos': Cantidad_vanos,
    'Numeros_pisos': Numeros_pisos,
    'Alturas_piso': Alturas_piso}
# Al final se guardará con el csv

# Dimension minima para la iteración de bisección
Dimension_min_columna = 0.25

# CALCULO APROXIMADO DEL TIEMPO
Num_iter = (len(Distancias_vanos) * len(Cantidad_vanos)) ** 2 * len(Numeros_pisos) * len(Alturas_piso)
Tiempo = Num_iter * 5
Tiempo_h_m_s = time.strftime('%d dias- %H:%M:%S', time.gmtime(Tiempo))
Continuar = input(f'El array_tiempo que demora {Num_iter} iteraciones será {Tiempo_h_m_s} hrs, desea continuar? (Y/N)')
Continuar = Continuar.upper()
tiempo_inicial = time.time()
############################


# DEFINIR BASE DE DATOS
DB_Edificios = pd.DataFrame(columns=(
    ['#N_Pisos', 'N_VanosX', 'N_VanosY', 'H_Pisos', 'L_VanoX', 'L_VanoY', 'H_VigaX', 'B_VigaX', 'H_BigaY', 'B_VigaY',
     'H_Colum', 'B_Colum', 'T']))

DB_Historial = DB_Edificios.copy()
# GUARDAR BASE DE DATOS PARA LUEGO ANEXAR EN CADA ITERACION

DB_Edificios.to_csv(file_out, index_label='id')
id_db = 0

if Continuar == 'Y':

    for Hz in Alturas_piso:
        for story in Numeros_pisos:

            # Por medio de la formual T=0.028 H^{0.8}
            H_Total = story * Hz * 3.28084
            T = 0.028 * pow(H_Total, 0.8)

            for LbX in Distancias_vanos:
                for LbY in Distancias_vanos:
                    for count_baysX, baysX in enumerate(Cantidad_vanos):
                        for baysY in tqdm(Cantidad_vanos[count_baysX:],
                                          leave=True, postfix='\n',
                                          desc=f'''---->Calculando el modelo de parametros: 
                                -Hz:{Hz}// Pisos:{story}// LbX:{LbX}// LbY:{LbY}// vanX:{baysX} ==>'''):

                            # realizo predimensionamiento de Vigas
                            Hbx = max(LbX / 10, 0.25)
                            Hby = max(LbY / 10, 0.25)
                            Bbx = max(0.5 * Hbx, 0.25)
                            Bby = max(0.5 * Hby, 0.25)

                            set_variable(file_run, story, baysX, baysY, Hz, LbX, LbY, Hbx, Hby, Bbx, Bby)

                            # ########################BISECCION#################################
                            # Valores para metodo de biseccion
                            Hcol_min_bi = Dimension_min_columna
                            Hcol_max_bi = min(LbX, LbY)
                            # Hcol_max_bi = 3.5
                            Hcol, Bcol, t_edi = buscar_optimo_bi(T, Hcol_min_bi, Hcol_max_bi, tolerancia, Dir_Opensees,
                                                                 file_run, file_Periods,
                                                                 limite_interaciones=limite_interaciones,
                                                                 print_int=True)
                            # ########################BISECCION#################################

                            # EN CASO NO SE LLEGUE AL OPTIMO SE REALIZAN LAS SIGUIENTES LINEAS
                            # #######################################
                            if Hcol is False or Hcol is None:
                                print('!!!!!No se puede guardar este edificio porque no tiene solución')
                                continue

                            # CREAR LA FILA PARA GUARDAR BASE DE DATOS
                            Fila_edificio = DB_Edificios.copy()
                            lista_out = (story, baysX, baysY, Hz, LbX, LbY, Hbx, Bbx, Hby, Bby, round(Hcol, 3)
                                         , round(Bcol, 3), t_edi)

                            Fila_edificio.loc[id_db] = lista_out
                            DB_Historial.loc[id_db] = lista_out
                            id_db += 1

                            # GUARDAR LA FILA ANEXANDO EL ARCHIVO CSV
                            Fila_edificio.to_csv(file_out, index_label='id', mode='a', header=False)
    
    
    # LINEAS FINALES 
    
    tiempo_final = time.time()
    tiempo_total = tiempo_final - tiempo_inicial
    tiempo_total_h_m_s = time.strftime('%d dias- %H:%M:%S', time.gmtime(tiempo_total))
    print(f'Todas las iteraciones se demoraron {tiempo_total_h_m_s} horas')
    
    # AGREGAR ULTIMOS DATOS PARA GUARDAR HISTORIAL
    historial['Tiempo'] = tiempo_total
    historial['DataBase_Generada'] = DB_Historial
    
    nombre_archivo = f'Genera_Parametros3_D{fecha_hoy}_H{hora_hoy}.hst'
    
    # GUARGAR EL HISTORIAL
    path_historial = '../Base_datos/Historial'
    
    if not os.path.isdir(path_historial):
        os.mkdir(path_historial)
    
    joblib.dump(historial,
                os.path.join(path_historial,
                             nombre_archivo),
                compress=3)

else:
    print('no se corrió el programa')


