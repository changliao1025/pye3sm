import math
#dResolution_grid_in =1406 * 1000 #m to mm
dDummy_slope = 5.699999999999999E-003    #ratio. ,not degree or radian
sand = 10
xksat         = 0.0070556 *( 10.**(-0.884+0.0153*sand) )
dSaturate_hydraulic_conductivity_in= 1 * 1.0E-3 #m/s
dSaturate_hydraulic_conductivity_in = 0.107872755330942 

dHeight_below_river_in=42*1000
    
dDummy0 =  1406 * 1000
#head pressure delta H, average  
dDummy1 = dDummy0 * (dDummy_slope)
#cross area A
dDummy2 = dHeight_below_river_in  * 8350000  * 1000
#q = k   A   delta H/ L

#delta h/L
dDummy3 = dDummy1 / dDummy0

dDummy4 =  dSaturate_hydraulic_conductivity_in * dDummy2 * dDummy3 


#drainage area, normalization
dDummy5 = 8350000  * 1406 * 1000000 



dFlow_downslope_out = dDummy4 /  dDummy5 #mm/s 

dFlow_downslope_out = dFlow_downslope_out
#unit?

print(dFlow_downslope_out)


