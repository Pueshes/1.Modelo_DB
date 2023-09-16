#------------------------------------------------
#Libreria - define sistema de unidades 
#




# Unidades Basicas en [L]=cm,centimetros, [T]=Seg, Segundos, [Fuerza] = kgf, [M]= kgf-s2/cm2  




set cm 1.0
set seg 1.0
set kgf 1.0


set m [expr 100.0*$cm]
set ton [expr 1000.0*$kgf]

set cm2 [expr pow($cm,2)]
set m2 [expr pow($m,2)]
set cm3 [expr $cm2*$cm]
set m3 [expr $m2*$m]
set seg2 [expr pow($seg,2)]

set {kgf/cm2} [expr $kgf/($cm2)]
set {kgf/cm3} [expr $kgf/($cm3)]

set g [expr 9.81 *$m/pow($seg,2)]

set utm [expr $kgf/($g)]

set pi 3.141593

