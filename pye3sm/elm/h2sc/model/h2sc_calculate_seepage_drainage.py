import numpy as np

dSlope_surface_in = 5.699999999999999E-003
dSaturate_hydraulic_conductivity_in= 0.01
dLength_hillslope = 3000  * 1000 

dWidth_hillslope_in= 50000 * 1000
dLength_seepage = 10 * 1000

dArea_hillslope_in = dWidth_hillslope_in*dLength_hillslope


#head pressure delta H, average  
dDummy1 = dLength_hillslope * dSlope_surface_in
#cross area A
dDummy2 = dLength_seepage  * dWidth_hillslope_in  
#q = k   A   delta H/ L

#delta h/L
dDummy3 = dSlope_surface_in

dDummy4 =  dSaturate_hydraulic_conductivity_in * dDummy2 * dDummy3 


dDummy5 = dArea_hillslope_in
dFlow_downslope_out = dDummy4 /  dDummy5 #mm/s 

dFlow_seepage_out = dSaturate_hydraulic_conductivity_in \
         * dLength_seepage * np.power(dSlope_surface_in,1) * dWidth_hillslope_in / dArea_hillslope_in

print(dFlow_downslope_out)
print(dFlow_seepage_out)