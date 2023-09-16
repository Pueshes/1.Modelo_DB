wipe;
wipeAnalysis


source Libreria.Unidades.tcl
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
set story 5
set baysX 5
set baysY 5
set Hz [expr 2.5*$m]
set LbX [expr 3*$m]
set LbY [expr 6*$m]


# STORY QUE PERMITE CAMBIO DE SECCION

set story_cambio 8

#Numero de modos
set num_modos [expr 2]

#file
file mkdir Periodos;
set periodos_file "Periodos/periodos.out"
set dir_out1 "TEMP"
set dir_out2 "E5060"



#--------------------------------------------------------------------
#Set de Materiales
#Input= mat_concreto {fc rho}
#Output= return "$E $G $rho"
set concreto1 [mat_concreto [expr 210*$kgf/$cm2] [expr 2.4*$ton/$m3]]

#---------------------------------------------------------------------
# Secciones de los elementos 
# 3 tipos de elemtos considerados
#Col = Columnas
set Hcol [expr 0.6*$m]
set Bcol [expr 0.6*$m]
#VigaX= viga dirección X
set Hbx [expr 0.3*$m]
set Bbx [expr 0.25*$m]
#VigaY= viga dirección Y
set Hby [expr 0.6*$m]
set Bby [expr 0.3*$m]

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


#Uso de oficinas

set CV [expr 300*$kgf/$m2]
set fcv 0.25
#factor para el porcentaje de carga viva en la masa sismica


#FACTORES DE METODO
set factor_exisl 1; #PARA APLICAR LAS MASAS A LOS ELEMENTOS COMO DISTRIBUIDO
set factor_exisN 0; #PARA APLICAR LAS MASAS A LOS NODOS
set factor_exis_carga 1; #PARA TRANSMITIR LA CARGA DE LA LOSA EN EL ANALISIS ESTATICO


#Parametros de analisis dinamico


# set up ground-motion-analysis parameters
set DtAnalysis	[expr 0.02*$seg];	# time-step Dt for lateral analysis
set TmaxAnalysis [expr 24. *$seg]; #RAE	[expr 24. *$seg];	# maximum duration of ground-motion analysis -- should be 50*$sec

########################################################################################################
##########################################MODELO Y ANALISIS#############################################
########################################################################################################

# Se importa y se crea el modelo
set s1 [clock seconds]
source modelo.elastico.3d1.tcl
set s2 [clock seconds]
set t_modelo [expr $s2-$s1]
puts "tiempo de creacion de modelo"
puts $t_modelo


# Se importan los de datos de los Sismos
set s1 [clock seconds]
source Lista_GM.tcl
set s2 [clock seconds]
set t_datos_sismo [expr $s2-$s1]
puts "tiempo de datos de los sismos"
puts $t_datos_sismo


# Directorio donde se guardarán los archivos
set dataDir "$dir_out1/$dir_out2/$dir_out3"


# Aplicación de la parte estatica
wipeAnalysis;
puts "aplicacion de cargas estaticas \n";

set s1 [clock seconds]
source cargas.estaticas.tcl;
set s2 [clock seconds]
set t_cargas_estatitcas [expr $s2-$s1]
puts "tiempo de aplicacion de cargas estaticas"
puts $t_cargas_estatitcas

puts "termino la parte estatica \n";
wipeAnalysis;


# Guardar los recorder 
puts "Definicion de recorder \n"
source recorder.tcl


# Crear el analisis sismico
set s1 [clock seconds]
source Analisis.Dinamico.tcl;
set s2 [clock seconds]
set t_analsiis_sis [expr $s2-$s1]
puts "tiempo de analisis sismico"
puts $t_analsiis_sis


puts "Analisis completo \n"


