
#DEFINIR CARGAS ESTATICAS 

#carga distribuida para cada elemento
set s1 [clock seconds]
#
pattern Plain 1 Linear {


	#para recorrer columnas
	for {set iz 1} {$iz<=$story} {incr iz 1} { ; 		#Se crearán las columnas por cada piso, empezando del techo piso1
		
		###### columna ########
		set jzCOL $iz
		######## viga x ##############
		set izVX $iz
		######## viga y ##############
		set izVY $iz


		for {set iy 0} {$iy<=$baysY} {incr iy 1} {
			###### columna ########
			set iyCOL $iy
			######## viga x ##############
			set iyVX $iy

	 		if {$iyVX ==0 || $iyVX==$baysY} {
				set factor_y 0.5
			} else {
				set factor_y 1
			}

			######## viga y ##############
			if {$iy != $baysY } {
				set jyVY [expr $iy+1]
				set CreateVY 1;

			} else {
				set CreateVY 0;
			}


			for {set ix 0} {$ix<=$baysX} {incr ix 1} {
				###### columna ########
				set ixCOL $ix

				set frameTagCOL [expr $TagfrCol+ $jzCOL*$TagfrStory+ $iyCOL*$TagfrBayY+ $ixCOL*$TagfrBayX]

				if {$story<=$story_cambio} {
					eleLoad -ele $frameTagCOL -type -beamUniform 0.0 0.0 -[lindex $columna1 7]
				} else {
					eleLoad -ele $frameTagCOL -type -beamUniform 0.0 0.0 -[lindex $columna2 7]

				}

				# puts "$frameTag"

				######## viga x ##############
				if {$ix != $baysX } {
					set jxVX [expr $ix+1]
					set CreateVX 1;
				} else {
					set CreateVX 0;
				}

				if {$CreateVX == 1 } {
					set frameTagVX [expr $TagfrBeamX+$izVX*$TagfrStory+$iyVX*$TagfrBayY+$jxVX*$TagfrBayX]

					set PVX [expr $Distribuida_VX+ $fx*$Distribuida_losa*$factor_y*$factor_exis_carga]

					eleLoad -ele $frameTagVX -type -beamUniform 0.0 -$PVX
				}

				# puts "$frameTag"

				######## viga y ##############
				set ixVY $ix

				if {$ix ==0 || $ix ==$baysX} {
					set factor_x 0.5
				} else {
					set factor_x 1
				}

				if {$CreateVY == 1 } {
					set PVY [expr $Distribuida_VY+$fy*$Distribuida_losa*$factor_x*$factor_exis_carga]
					
					set frameTagVY [expr $TagfrBeamY+ $izVY*$TagfrStory+ $jyVY*$TagfrBayY+ $ixVY*$TagfrBayX]

					eleLoad -ele $frameTagVY -type -beamUniform 0.0 -$PVY

					# puts "$frameTag"
				}

			}
		}
	}


set s2 [clock seconds]
set t_for_esta [expr $s2-$s1]
puts "tiempo de los for estaticos"
puts $t_for_esta

	# # Para recorrer vigas en X

	# for {set iz 1} {$iz<=$story} {incr iz 1} { ; 		#Se crearán las columnas por cada piso, empezando del techo piso1
	# 	######## viga x ##############
	# 	set izVX iz


	# 	for {set iy 0} {$iy<=$baysY} {incr iy 1} {
	# 		######## viga x ##############
	# 		set iyVX $iy


	#  		if {$iyVX ==0 || $iyVX==$baysY} {
	# 			set factor_y 0.5
	# 		} else {
	# 			set factor_y 1
	# 		}


	# 		for {set ix 0} {$ix< $baysX} {incr ix 1} {
	# 			######## viga x ##############
	# 			if {$ix != $baysX } {
	# 				set jxVX [expr $ix+1]
	# 				set CreateVX 1;
	# 			} else {
	# 				set CreateVX 0;
	# 			}

	# 			if {$CreateVX == 1 } {
	# 				set frameTag [expr $TagfrBeamX+$izVX*$TagfrStory+$iyVX*$TagfrBayY+$jxVX*$TagfrBayX]

	# 				set PVX [expr $Distribuida_VX+ $fx*$Distribuida_losa*$factor_y*$factor_exis_carga]

	# 				eleLoad -ele $frameTag -type -beamUniform 0.0 -$PVX
	# 			}

	# 			# puts "$frameTag"

	# 		}
	# 	}
	# }

	# # Para recorrer vigas en Y

	# for {set iz 1} {$iz<=$story} {incr iz 1} { ; 		#Se crearán las columnas por cada piso, empezando del techo piso1
	# 	######## viga y ##############
	# 	set izVY $iz

	# 	for {set iy 0} {$iy< $baysY} {incr iy 1} {
	# 		######## viga y ##############
	# 		if {$iy != $baysY } {
	# 			set jyVY [expr $iy+1]
	# 			set CreateVY 1;

	# 		} else {
	# 			set CreateVY 0;
	# 		}

			# for {set ix 0} {$ix<=$baysX} {incr ix 1} {
			# 	######## viga y ##############
			# 	set ixVY $ix
			# 	if {$ix ==0 || $ix ==$baysX} {
			# 		set factor_x 0.5
			# 	} else {
			# 		set factor_x 1
			# 	}

	# 			if {$CreateVY == 1 } {
	# 				set PVY [expr $Distribuida_VY+$fy*$Distribuida_losa*$factor_x*$factor_exis_carga]
					
	# 				set frameTag [expr $TagfrBeamY+$izVY*$TagfrStory+$jyVY*$TagfrBayY+$ixVY*$TagfrBayX]

	# 				eleLoad -ele $frameTag -type -beamUniform 0.0 -$PVY

	# 				# puts "$frameTag"
	# 			}
	# 		}
	# 	}
	# }	
}



##########################Analisis###################################
#####################################################################

set s1 [clock seconds]

set Tol 1.0e-8;			# convergence tolerance for test
set NstepGravity 10;  		# apply gravity in 10 steps

#DT=0.1
# ------------------------------------------------- apply gravity load
constraints Lagrange;    #
numberer RCM;			# renumber dof's to minimize band-width (optimization), if you want to
system BandGeneral;		# how to store and solve the system of equations in the analysis
test EnergyIncr $Tol 10 ; 		# determine if convergence has been achieved at the end of an iteration step
algorithm Newton;			# use Newton's solution algorithm: updates tangent stiffness at every iteration

set DGravity [expr 1./$NstepGravity]; 	# first load increment;
integrator LoadControl $DGravity;	# determine the next time step for an analysis
# integrator LoadControl 0.5
analysis Static;			# define type of analysis static or transient
analyze $NstepGravity;		# apply gravity
# ------------------------------------------------- maintain constant gravity loads and reset time to zero
loadConst -time 0.0

set s2 [clock seconds]
set t_analisis_esta [expr $s2-$s1]
puts "tiempo de solo el analisis estatico"
puts $t_analisis_esta
