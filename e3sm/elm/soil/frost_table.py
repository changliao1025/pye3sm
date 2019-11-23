import numpy as np
tfrz=0.0
nlevbed=10
#t_soisno =  np.full(nlevbed, -10.0, dtype=float)
#t_soisno =  np.full(nlevbed, -10.0, dtype=float)
t_soisno =   np.arange(nlevbed) - 5 

t_soisno =   np.arange(nlevbed) * (-1) + 5 

print(t_soisno)
if(t_soisno[0] > tfrz) :
    k_frz=nlevbed
else:
    k_frz=1
         

for k in range (2, nlevbed):
    if (t_soisno[k-1] > tfrz and t_soisno[k] <= tfrz) :
        k_frz=k
        exit
print('finished')



#part 2

e_ice=0.02
imped=10.0**(-e_ice*(0.5*(0.1+0.1)))


qflx_drain_perched = 0.001
dtime = 24*60
jwt = 3
use_vsfm =0 
rsub_top_tot = -  qflx_drain_perched * dtime

h2osoi_liq = np.arange(nlevbed) * 0.1 
eff_porosity = np.arange(nlevbed) * 0.1 

zi = np.arange(nlevbed) * 0.2 

watmin =0.2
zwt = 0.3
for k in range (jwt+1, k_frz):
   dummy = -(h2osoi_liq[k]-watmin)
   rsub_top_layer=max(rsub_top_tot, dummy)
   rsub_top_layer=min(rsub_top_layer,0.0)
   if (use_vsfm==1) :
      rsub_top_layer = 0.0
   
   rsub_top_tot = rsub_top_tot - rsub_top_layer
   h2osoi_liq[k] = h2osoi_liq[k] + rsub_top_layer
   if (rsub_top_tot >= 0.) :
      zwt = zwt - rsub_top_layer / eff_porosity[k]
      exit
   else:
      zwt = zi[k]
               
print('finished')          
            
         