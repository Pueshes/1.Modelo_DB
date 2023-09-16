# Procedure para creación de materiales elasticos lineales
# Inputs:
#		$f'c= {kgf/cm2} Resistencia a la compresión 
#		
source Libreria.Unidades.tcl


proc mat_concreto {fc rho} {
	set E [expr 15000*sqrt($fc)]
	set nu 0.2
	set G [expr $E/2.0/[expr 1+$nu]]
	return "$E $G $rho"
}


proc seccion {H B material} {
	source Libreria.Unidades.tcl


	set A [expr $H*$B] 
	set Iz [expr $H*pow($B,3)/12]
	set Iy [expr $B*pow($H,3)/12]
	# set J [expr ($B/2)*pow($H*2,3)*((16/3)-3.36*($H/$B)*(1-pow($H/2,4)/(12*pow($B/2,4))))]
	set J 1.0e10
	# set J 0
	set rho [lindex $material 2]	
	set mass_per_l [expr $A* $rho]
	set E [lindex $material 0]
	set G [lindex $material 1]
	return "$A $E $G $J $Iy $Iz $mass_per_l $rho"

}


