

set dir_out3 316
# dataDir
# Bidirectional Uniform Earthquake ground motion (uniform acceleration input at all support nodes)
set iGMfileX { {Registros_Sismicos_Proces2/Parkfield/316_90.T1} }
set iGMfileY { {Registros_Sismicos_Proces2/Parkfield/316_360.T1} }

set Deltat 0.02


foreach GMfileX $iGMfileX GMfileY $iGMfileY {

	set iGMfile "";

	lappend iGMfile $GMfileX
	lappend iGMfile $GMfileY

}



# set extension "T1"
set iGMdirection "1 2";			# ground-motion direction
set iGMfact "1.0 1.0";			# ground-motion scaling factor
