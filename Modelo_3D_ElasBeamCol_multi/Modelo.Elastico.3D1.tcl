

###################################INICIO DE MODELO#######################################
##########################################################################################
##########################################################################################

model BasicBuilder -ndm $ndm -ndf $ndf

#--------------------------------------------------------------------

#Set de Secciones 
#Input= seccion {H B material}; H: Altura o lado largo, B: Base o lado corto
#Output= return "$A $E $G $J $Iy $Iz $mass_per_l $rho"
				# 0  1  2  3  4    5    6 		  7
#Columnas				
set columna1 [seccion [expr $Hcol] [expr $Bcol] $concreto1]
set N_secciones_col 1

if {$story>$story_cambio} {
	set columna2 [seccion [expr $Hcol-$reduccion_columna] [expr $Bcol-$reduccion_columna] $concreto1]
	set N_secciones_col 2
}

# set columna2 [seccion [expr $Hcol2] [expr $Bcol2] $concreto1]
#VigaX
set beamX [seccion [expr $Hbx] [expr $Bbx] $concreto1]
#VigaY
set beamY [seccion [expr $Hby] [expr $Bby] $concreto1]


#--------------------------------------------------------------------
# CREACIÓN DE NODOS
#ix el contador para nodos en el eje X; columna 1 ix=0; +1
#iy el contador para nodos en el eje y; columna 1 iy=0; +100
#iz el contador para nodos en el eje Z; nivel del suelo iz=0; +1000
#
set TagX 1;			#valor de incremento para el tag de los nodos en X
set TagY 100;			#valor de incremento para el tag de los nodos en Y
set TagZ 10000;		#valor de incremento para el tag de los nodos en Z

set recorder_CG ""

set TagCG 100

#Asignacion de Diagrama Rigido

# puts "inicio de nodos"
# puts "EMPIEZA DIAFRAGMA \n"

for {set iz 0} {$iz<= $story} {incr iz 1} {

	if { $iz != 0} {
		set Area [expr $baysX*$LbX*$baysY*$LbY]
		set CGx [expr ($baysX*$LbX)/2];				#Coordenada X de Centro de Gravedad
		set CGy [expr ($baysY*$LbY)/2];				#Coordenada Y de Centro de Gravedad
		set CGz [expr $iz*$Hz];						#Coordenada Z de Centro de Gravedad
		set CGtag [expr $iz*$TagZ*$TagCG];				#Tag Centro de Gravedad		
		node $CGtag $CGx $CGy $CGz

		lappend recorder_CG $CGtag
		fix $CGtag 0 0 1 1 1 0;
	}

	for {set iy 0} {$iy<= $baysY} {incr iy 1} {
		for {set ix 0} {$ix<= $baysX} {incr ix 1} {
			set nodotag [expr $ix*$TagX + $iy*$TagY + $iz*$TagZ]
			set nodox [expr $ix*$LbX]
			set nodoy [expr $iy*$LbY]
			set nodoz [expr $iz*$Hz]
			node $nodotag $nodox $nodoy $nodoz

			# puts "$nodotag $nodox $nodoy $nodoz" ;		#Para mostrar los nodos
			# print node $nodotag
			if { $iz != 0} {
				rigidDiaphragm 3 $CGtag $nodotag
			}



		}
	}
}

puts "Se completaron los nodos"


 
# for {set iz 1} {$iz<= $story} {incr iz 1} {
# 	set Area [expr $baysX*$LbX*$baysY*$LbY]
# 	set CGx [expr ($baysX*$LbX)/2];				#Coordenada X de Centro de Gravedad
# 	set CGy [expr ($baysY*$LbY)/2];				#Coordenada Y de Centro de Gravedad
# 	set CGz [expr $iz*$Hz];						#Coordenada Z de Centro de Gravedad
# 	set CGtag [expr $iz*$TagZ*$TagCG];				#Tag Centro de Gravedad		
# 	node $CGtag $CGx $CGy $CGz
# 
# 	lappend recorder_CG $CGtag
# 	# set masa_piso [expr ($CM+0.25*$CV)*$Area*$utm]
# 	# # set masa_piso [expr $CM*$Area*$utm]
# 	# puts $masa_piso
# 	# mass $CGtag $masa_piso $masa_piso 0.0 0.0 0.0 0.0; #masa en cada de nodo
# 
# 	fix $CGtag 0 0 1 1 1 0; 
# 	for {set iy 0} {$iy<= $baysY} {incr iy 1} {
# 		for {set ix 0} {$ix<= $baysX} {incr ix 1} {
# 			set nodotag [expr $ix*$TagX+ $iy*$TagY+ $iz*$TagZ]
# 			rigidDiaphragm 3 $CGtag $nodotag
# 			# puts "$CGx $CGy $CGz $nodotag $CGtag"
# 			# puts $nodotag
#
# 		}
# 	}
# 
# 	# print node $CGtag
# }

# puts $recorder_CG

#Fix de los nodos de la base

fixZ 0.0 1 1 1 1 1 1

#------------------------------
#cracion de las Grotransf
#Geo transf 1 indica el lado largo dirigido al eje X
#Geo transf 2 indica el lado largo dirigido al eje Y
#Geo transf 3 indica el lado largo dirigido al eje Z

geomTransf Linear 1 1 0 0;
geomTransf Linear 2 0 1 0;
geomTransf Linear 3 0 0 1;

#---------------------------------------------------------------------------
#CREACIÓN DE FRAMES

#UBICACION DEL FRAME

#Indica el incremento en el Tag por cada piso, Elementos de piso 1 empiezan con 100000; del 2, 200000
set TagfrStory 100000; 
#Indica el incremento en el Tag por cada Vano en X
set TagfrBayX 1;
#Indica el incremento en el Tag por cada vanos en Y
set TagfrBayY 100;


#SE DIFERENCIA EL TIPO DE FRAME POR SU UNIDAD DE MILLARES
# Indica el valor de millares para Viga en X 
set TagfrBeamX 10000;
# Indica el valor de millares para Viga en Y		
set TagfrBeamY 20000;
# Indica el valor de millares para Columna 
set TagfrCol 30000;

#MASA Losa aligerada 1 direccion
#
if {$LbX<$LbY} {
	set Lcorto $LbX
	set fx 0
	set fy 1
#FACTORES QUE INDICA A QUE VIGA SE CARGARÁ
} else {
	set Lcorto $LbY
	set fx 1
	set fy 0
}


set rho [lindex $concreto1 2]
set Distribuida_losa_masa [expr ($espesor_losa*$factor_losa*$rho+$fcv*$CV)*$Lcorto]
set Distribuida_losa [expr ($espesor_losa*$factor_losa*$rho+$CV)*$Lcorto]
set Distribuida_VX [lindex $beamX 6]
set Distribuida_VY [lindex $beamY 6]
set Distribuida_COL [lindex $columna1 6]


#-------------------------------------------
#Creación de VigasX -beamX

# puts "Creación de VigasX"

set DirGeomTransfVX $DirVigaX
set DirGeomTransfVY $DirVigaY
set DirGeomTransfCOL $DirColumna


for {set iz 1} {$iz<=$story} {incr iz 1} { ; 	#Con este for se crean los frames de todo el edificio
	
	###### viga x ########
	set izVX $iz
	set jzVX $izVX
	######################
	#
	###### viga Y ########
	set izVY $iz
	set jzVY $izVY
	######################
	#	
	###### columna ########

	set izCOL [expr $iz-1]
	set jzCOL [expr $izCOL+1]	
	######################

	#ITERACIÓN 2


	for {set iy 0} {$iy <= $baysY} {incr iy 1} {

		######## viga x ##############
		set iyVX $iy
		set jyVX $iyVX
		# jyVX

 		if { $iyVX ==0 || $iyVX == $baysY} {
			set factor_y 0.5
		} else {
			set factor_y 1
		}
		##############################
		#
		######## viga y ##############
		if {$iy < $baysY } {
			set iyVY $iy
			set jyVY [expr $iyVY+1]
			set CreateVY 1;

		} else {
			set CreateVY 0;
		}	
		##############################
		#
		######## columna ##############
		set iyCOL $iy
		set jyCOL $iyCOL
		##############################


		##factor_y= factor que indica si toma 2 semipaños o 1 semipaño de losa
		for {set ix 0} {$ix <= $baysX} {incr ix 1} {

			###################### viga x ################################
			if {$ix < $baysX } {
				set ixVX $ix
				set jxVX [expr $ixVX+1]
				set CreateVX 1;

			} else {
				set CreateVX 0;
			}


			if {$CreateVX == 1 } {
				set nodoiVX [expr $ixVX*$TagX+ $iyVX*$TagY+ $izVX*$TagZ]
				set nodojVX [expr $jxVX*$TagX+ $jyVX*$TagY+ $jzVX*$TagZ]
				set frameTagVX [expr $TagfrBeamX+ $izVX*$TagfrStory+ $iyVX*$TagfrBayY+ $jxVX*$TagfrBayX]
				set MasaVX [expr ($Distribuida_VX+ $fx*$Distribuida_losa_masa*$factor_y)*$utm*$factor_exisl]
				# puts $MasaVX
				element elasticBeamColumn $frameTagVX $nodoiVX $nodojVX [lindex $beamX 0] [lindex $beamX 1] [lindex $beamX 2] [lindex $beamX 3] [lindex $beamX 4] [lindex $beamX 5] $DirGeomTransfVX -mass $MasaVX;	
				# element elasticBeamColumn $frameTagVX $nodoiVX $nodojVX [lindex $beamX 0] [lindex $beamX 1] [lindex $beamX 2] [lindex $beamX 3] [lindex $beamX 4] [lindex $beamX 5] $DirGeomTransfVX;
				# puts "$frameTagVX $nodoiVX $nodojVX"
				

			}
			###############################################################
			#
			###################### viga y ################################
			set ixVY $ix
			set jxVY $ixVY

			if {$ixVY ==0 || $ixVY ==$baysX} {
				set factor_x 0.5
			} else {
				set factor_x 1
			}
			##factor_x= factor que indica si toma 2 semipaños o 1 semipaño de losa

			if {$CreateVY == 1 } {

				set nodoiVY [expr $ixVY*$TagX+ $iyVY*$TagY+ $izVY*$TagZ]
				set nodojVY [expr $jxVY*$TagX+ $jyVY*$TagY+ $jzVY*$TagZ]
				set frameTagVY [expr $TagfrBeamY+ $izVY*$TagfrStory+ $jyVY*$TagfrBayY+ $ixVY*$TagfrBayX]
				set MasaVY [expr ($Distribuida_VY+$fy*$Distribuida_losa_masa*$factor_x)*$utm*$factor_exisl]
				# puts $MasaVY
				# element elasticBeamColumn $frameTagVY $nodoiVY $nodojVY [lindex $beamY 0] [lindex $beamY 1] [lindex $beamY 2] [lindex $beamY 3] [lindex $beamY 4] [lindex $beamY 5] $DirGeomTransfVY;
				element elasticBeamColumn $frameTagVY $nodoiVY $nodojVY [lindex $beamY 0] [lindex $beamY 1] [lindex $beamY 2] [lindex $beamY 3] [lindex $beamY 4] [lindex $beamY 5] $DirGeomTransfVY -mass $MasaVY;
			}
				# puts "$frameTagVY $nodoiVY $nodojVY"
			###############################################################
			#
			###################### columna ################################
			set ixCOL $ix
			set jxCOL $ixCOL



			set nodoiCOL [expr $ixCOL*$TagX+ $iyCOL*$TagY+ $izCOL*$TagZ]
			set nodojCOL [expr $jxCOL*$TagX+ $jyCOL*$TagY+ $jzCOL*$TagZ]
			set frameTagCOL [expr $TagfrCol+ $jzCOL*$TagfrStory+ $iyCOL*$TagfrBayY+ $ixCOL*$TagfrBayX]

		
			if {$jzCOL<=$story_cambio} {

				set MCOL [expr $Distribuida_COL*$utm*$factor_exisl]
				#puts $MCOL
				# element elasticBeamColumn $frameTagCOL $nodoiCOL $nodojCOL [lindex $columna1 0] [lindex $columna1 1] [lindex $columna1 2] [lindex $columna1 3] [lindex $columna1 4] [lindex $columna1 5] $DirGeomTransfCOL;
				element elasticBeamColumn $frameTagCOL $nodoiCOL $nodojCOL [lindex $columna1 0] [lindex $columna1 1] [lindex $columna1 2] [lindex $columna1 3] [lindex $columna1 4] [lindex $columna1 5] $DirGeomTransfCOL -mass $MCOL;

				# puts "$frameTagCOL $nodoiCOL $nodojCOL"
			} else {

				set Distribuida_COL [lindex $columna2 6]
				set MCOL [expr $Distribuida_COL*$utm*$factor_exisl]
				#puts $MCOL
				element elasticBeamColumn $frameTagCOL $nodoiCOL $nodojCOL [lindex $columna2 0] [lindex $columna2 1] [lindex $columna2 2] [lindex $columna2 3] [lindex $columna2 4] [lindex $columna2 5] $DirGeomTransfCOL -mass $MCOL;
			}


		# puts "se crearon todos los elementos"
		}

	}
}

puts "Se termino los frames"

#Encontrar los valores propios
set valores_propios [eigen $num_modos]


#Calcular frecuencias y periodos
#---------------------------------------------------
set omega {}
set f {}
set T {}


foreach lam $valores_propios {
	lappend omega [expr sqrt($lam)]
	lappend f [expr sqrt($lam)/(2*$pi)]
	lappend T [expr (2*$pi)/sqrt($lam)]
}

puts "periods are $T"

# write the output file cosisting of periods
#--------------------------------------------
set period $periodos_file
set Periods [open $period "w"]
foreach t $T {
	puts $Periods " $t"
}
close $Periods


puts "model build"




