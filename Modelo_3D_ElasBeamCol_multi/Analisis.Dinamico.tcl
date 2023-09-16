# --------------------------------------------------------------------------------------------------
# Example 8. Bidirectional Uniform Eartquake Excitation
#                             Silvia Mazzoni & Frank McKenna, 2006
# execute this file after you have built the model, and after you apply gravity
#

# source in procedures
# source ReadSMDfile.tcl;		# procedure for reading GM file and converting it to proper format
source Libreria.Unidades.tcl

# Define DISPLAY -------------------------------------------------------------
# the deformed shape is defined in the build file
# recorder plot $dataDir/DFree.out DisplDOF[lindex $iGMdirection 0] 1200 10 400 400 -columns  1 [expr 1+[lindex $iGMdirection 0]] ; # a window to plot the nodal displacements versus time
# recorder plot $dataDir/DFree.out DisplDOF[lindex $iGMdirection 1] 1200 410 400 400 -columns 1 [expr 1+[lindex $iGMdirection 1]] ; # a window to plot the nodal displacements versus time


# ----------- set up analysis parameters
source Libreria.Analisis.Dinamico.tcl;	# constraintsHandler,DOFnumberer,system-ofequations,convergenceTest,solutionAlgorithm,integrator

# ------------ define & apply damping
# RAYLEIGH damping parameters, Where to put M/K-prop damping, switches (http://opensees.berkeley.edu/OpenSees/manuals/usermanual/1099.htm)
#          D=$alphaM*M + $betaKcurr*Kcurrent + $betaKcomm*KlastCommit + $beatKinit*$Kinitial
set xDamp 0.05;					# damping ratio
set MpropSwitch 1.0;
set KcurrSwitch 0.0;
set KcommSwitch 1.0;
set KinitSwitch 0.0;
set nEigenI 1;		# mode 1
set nEigenJ 3;		# mode 3
set lambdaN [eigen [expr $nEigenJ]];			# eigenvalue analysis for nEigenJ modes
set lambdaI [lindex $lambdaN [expr $nEigenI-1]]; 		# eigenvalue mode i
set lambdaJ [lindex $lambdaN [expr $nEigenJ-1]]; 	# eigenvalue mode j
set omegaI [expr pow($lambdaI,0.5)];
set omegaJ [expr pow($lambdaJ,0.5)];
set alphaM [expr $MpropSwitch*$xDamp*(2*$omegaI*$omegaJ)/($omegaI+$omegaJ)];	# M-prop. damping; D = alphaM*M
set betaKcurr [expr $KcurrSwitch*2.*$xDamp/($omegaI+$omegaJ)];         		# current-K;      +beatKcurr*KCurrent
set betaKcomm [expr $KcommSwitch*2.*$xDamp/($omegaI+$omegaJ)];   		# last-committed K;   +betaKcomm*KlastCommitt
set betaKinit [expr $KinitSwitch*2.*$xDamp/($omegaI+$omegaJ)];         			# initial-K;     +beatKinit*Kini
rayleigh $alphaM $betaKcurr $betaKinit $betaKcomm; 				# RAYLEIGH damping

#  ---------------------------------    perform Dynamic Ground-Motion Analysis
# the following commands are unique to the Uniform Earthquake excitation
# set IDloadTag 400;	# for uniformSupport excitation
# # Uniform EXCITATION: acceleration input

# foreach GMdirection $iGMdirection GMfile $iGMfile GMfact $iGMfact {
# 	incr IDloadTag;
# 	set inFile $GMdir/$GMfile.$extension
# 	set outFile $GMdir/$GMfile.g3;			# set variable holding new filename (PEER files have .at2/dt2 extension)
# 	ReadSMDFile $inFile $outFile dt;			# call procedure to convert the ground-motion file
# 	set GMfatt [expr $g*$GMfact];			# data in input file is in g Unifts -- ACCELERATION TH
# 	set AccelSeries "Series -dt $dt -filePath $outFile -factor  $GMfatt";		# time series information
# 	pattern UniformExcitation  $IDloadTag  $GMdirection -accel  $AccelSeries  ;	# create Unifform excitation
# 	puts $dt
# }

# set IDloadTag 10000
# foreach GMdirection $iGMdirection GMfile $iGMfile GMfact $iGMfact {
# 	incr IDloadTag;
# 	# set inFile $GMdir/$GMfile
# 	set inFile $GMfile
# 	puts "$inFile"
# 	set GMfatt [expr $cm/$seg2*$GMfact];			# data in input file is in cm2/s Unifts -- ACCELERATION TH
# 	set AccelSeries "Series -dt $Deltat -filePath $inFile -factor  $GMfatt";		# time series information
# 	pattern UniformExcitation  $IDloadTag  $GMdirection -accel  $AccelSeries  ;	# create Unifform excitation
# }

set IDloadTag 10000
pattern UniformExcitation $IDloadTag 1 -accel 1
incr IDloadTag 
pattern UniformExcitation $IDloadTag 2 -accel 2



set Nsteps [expr int($TmaxAnalysis/$DtAnalysis)];

## RAE ********************************
## RAE ********************************
constraints Transformation; 
numberer Plain; 
system BandGeneral; 
set TestType RelativeNormDispIncr; 
set Tol 1.0e-3; 
set maxNumIter 30; 
set printFlag 0; 
test $TestType $Tol $maxNumIter  $printFlag; 
algorithm Linear; 
integrator Newmark 0.5 0.25; 
analysis Transient; 
## RAE ********************************
## RAE ********************************


set ok [analyze $Nsteps $DtAnalysis];			# actually perform analysis; returns ok=0 if analysis was successful

if {$ok != 0} {
	# analysis was not successful
	# --------------------------------------------------------------------------------------------------
	# change some analysis parameters to achieve convergence
	# performance is slower inside this loop
	#    Time-controlled analysis
	set ok 0;
	set controlTime [getTime];
	while {$controlTime < $TmaxAnalysis && $ok == 0} {
		set controlTime [getTime]
		set ok [analyze 1 $DtAnalysis]
		if {$ok != 0} {
			puts "Trying Newton with Initial Tangent .."
			test NormDispIncr   $Tol 1000  0
			algorithm Newton -initial
			set ok [analyze 1 $DtAnalysis]
			test $testTypeDynamic $TolDynamic $maxNumIterDynamic  0
			algorithm $algorithmTypeDynamic
		}
		if {$ok != 0} {
			puts "Trying Broyden .."
			algorithm Broyden 8
			set ok [analyze 1 $DtAnalysis]
			algorithm $algorithmTypeDynamic
		}
		if {$ok != 0} {
			puts "Trying NewtonWithLineSearch .."
			algorithm NewtonLineSearch .8
			set ok [analyze 1 $DtAnalysis]
			algorithm $algorithmTypeDynamic
		}
	}
};      # end if ok !0

puts "Ground Motion Done. End Time: [getTime]"
