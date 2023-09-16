wipe;
wipeAnalysis


source Libreria.unidades.tcl
source Funciones.tcl


#################################################################################################
########################################PARAMETROS###############################################
#################################################################################################

# nmd= número de dimensiones 2 o 3
# ndf= número de grados de libertad 1 a 6
#inicio ndm
set ndm 3
set ndf 6
#---------------------------------------------------------------------
# Datos de la geometria de la estructura
set story 3
set baysX 5
set baysY 10
set Hz [expr 2.5*$m]
set LbX [expr 5*$m]
set LbY [expr 7*$m]


# STORY QUE PERMITE CAMBIO DE SECCION

set story_cambio 8

#Numero de modos
set num_modos [expr 2]

#file
file mkdir Periodos;
set periodos_file "Periodos/periodos.out"
# set GMdir "D:/OneDrive - UDEP/TESINA/FE model/Base_datos";


set dir_out1 "Data_out_prueba";
set dir_out2 "E300"


#--------------------------------------------------------------------
#Set de Materiales
#Input= mat_concreto {fc rho}
#Output= return "$E $G $rho"
set concreto1 [mat_concreto [expr 210*$kgf/$cm2] [expr 2.4*$ton/$m3]]

#---------------------------------------------------------------------
# Secciones de los elementos 
# 3 tipos de elemtos considerados
#Col = Columnas
set Hcol [expr 0.55*$m]
set Bcol [expr 0.55*$m]
#VigaX= viga dirección X
set Hbx [expr 0.5*$m]
set Bbx [expr 0.25*$m]
#VigaY= viga dirección Y
set Hby [expr 0.7*$m]
set Bby [expr 0.35*$m]

#incremento de sección en columnas

set reduccion_columna [expr 5*$cm]


#Geo transf 1 indica el lado largo de la seccion dirigido al eje global X
#Geo transf 2 indica el lado largo de la seccion dirigido al eje global Y
#Geo transf 3 indica el lado largo de la seccion dirigido al eje global Z

#Geotransf
set DirColumna 2
set DirVigaX 3
set DirVigaY 3

#Set de cargas

#Escoger el espesor de losa
set espesor_losa [expr 15*$cm]
set factor_losa	1; #para aligerados con porcentaje de su peso

# inicio de Diafragma Rigido
# 1000000 2000000 3000000 4000000 5000000 6000000 7000000 8000000 9000000 10000000
# CreaciÃ³n de Columnas
# periods are 1.458658165895277 0.67367106720574
# model build
# [Finished in 5.8s]


#Uso de oficinas

set CV [expr 300*$kgf/$m2]
set fcv 0.25
#factor para el porcentaje de carga viva en la masa sismica


#FACTORES DE METODO
set factor_exisl 1; #PARA APLICAR LAS MASAS A LOS ELEMENTOS COMO DISTRIBUIDO
set factor_exisN 0; #PARA APLICAR LAS MASAS A LOS NODOS
set factor_exis_carga 1; #PARA TRANSMITIR LA CARGA DE LA LOSA EN EL ANALISIS ESTATICO

########################################################################################################
##########################################MODELO Y ANALISIS#############################################
########################################################################################################

# Se importa y se crea el modelo
source modelo.elastico.3d1.tcl

# # Se importan los de datos de los Sismos
# source Lista_GM.tcl

# # Directorio donde se guardarán los archivos
# set dataDir "$dir_out1/$dir_out2/$dir_out3"


# # Aplicación de la parte estatica
# wipeAnalysis;
# puts "aplicacion de cargas estaticas \n";
# source cargas.estaticas.tcl;
# puts "termino la parte estatica \n";
# wipeAnalysis;


# # Guardar los recorder 
# puts "Definicion de recorder \n"
# source recorder.tcl

# # Crear el analisis sismico
# source Analisis.Dinamico.tcl;
# puts "Analisis completo \n"


