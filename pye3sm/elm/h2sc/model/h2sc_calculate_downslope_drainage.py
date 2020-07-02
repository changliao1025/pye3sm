import math
dResolution_grid_in = 50000  #m
dDummy_slope = 1 * 1.0E-3  #ratio. ,not degree or radian
dSaturate_hydraulic_conductivity_in= 6 * 1.0E-6 #m/s
dHeight_below_river_in= 5.0+ 50
    
dDummy0 =  (dResolution_grid_in * 0.5) 
#head pressure delta H, average  
dDummy1 = dDummy0 * math.tan(dDummy_slope)
#cross area A
dDummy2 = dHeight_below_river_in  * dResolution_grid_in  
#q = k   A   delta H/ L

#delta h/L
dDummy3 = dDummy1 / dDummy0

dDummy4 =  dSaturate_hydraulic_conductivity_in * dDummy2 * dDummy3 


#drainage area, normalization
dDummy5 = dResolution_grid_in * 0.5 * dResolution_grid_in 



dFlow_downslope_out = dDummy4 /  dDummy5 

dFlow_downslope_out = dFlow_downslope_out* 1000

print(dFlow_downslope_out)


