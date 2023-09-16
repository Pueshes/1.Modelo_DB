
# file delete -force -- $dataDir

file mkdir $dataDir;

# Crear un Time Series

timeSeries Path 1 -dt $Deltat -filePath $iGMfileX;
timeSeries Path 2 -dt $Deltat -filePath $iGMfileY



for {set iz 1} {$iz <= $story} {incr iz 1} {

	# set nodetag [expr $iz*$TagZ* $TagCG]
	# puts $nodetag
	set tag_cg [lindex $recorder_CG [expr $iz-1]]
	set output_name "cg_$tag_cg.out"
	recorder Node -file  $dataDir/$output_name -timeSeries 1 2 -time -node $tag_cg -dof 1 2 accel;

}



