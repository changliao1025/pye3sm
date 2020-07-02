import numpy as np
begwb= 6651.22253238255
h2ocan_col0= 9.826303776043277E-002
h2osno0=2.513701748718323E-002
h2osfc0=  67.2897931037670 
wa0=4897.61916095636
total_plant_stored_h2o0=0.0000000000000
h2osoi_ice0 =[5.370857719821487E-003,\
                0.0,\
                0.0,\
                0.0,\
                0.0,\
                0.0,\
                0.0,\
                0.0,\
                0.0,\
                0.0]
h2osoi_liq0= [  16.2566793773673,\
                25.4944128658928,\
                33.4145153171282,\
                41.4058719087416,\
                59.0141098130473,\
                90.7089385807551,\
                147.677137050426,\
                243.532836979106,\
                394.815280655951,\
                633.865024861040]

begwb0 = np.sum(h2osoi_ice0) + np.sum(h2osoi_liq0) + h2ocan_col0 + h2osno0 + h2osfc0  + wa0 + total_plant_stored_h2o0

print(begwb0)


endwb=6651.25626653924
h2ocan_col1=9.880533681550320E-002
h2osno1=4.124155723484546E-002
h2osfc1= 67.3068804216576
wa1 = 4897.61916095636
total_plant_stored_h2o1=0.0000000000000
h2osoi_ice1 =[ 2.019545970647362E-002,\
                0.0,\
                0.0,\
                0.0,\
                0.0,\
                0.0,\
                0.0,\
                0.0,\
                0.0,\
                0.0]
h2osoi_liq1= [  16.2418547753807,\
                25.4944128658928,\
                33.4145153171282,\
                41.4058719087416,\
                59.0141098130473,\
                90.7089385807551,\
                147.677137050426,\
                243.532836979106,\
                394.815280655951,\
                633.865024861040]

endwb0 = np.sum(h2osoi_ice1) + np.sum(h2osoi_liq1) + h2ocan_col1 + h2osno1 + h2osfc1  + wa1 + total_plant_stored_h2o1

print(endwb0)

print( h2ocan_col1- h2ocan_col0 )
print( h2osno1- h2osno0 )
print( h2osfc1- h2osfc0 )
print( wa1- wa0 )
print( total_plant_stored_h2o1- total_plant_stored_h2o0 )

print(np.sum(h2osoi_liq0))
print(np.sum(h2osoi_liq1))
print(endwb - begwb)
print(endwb0 - begwb0)


forc_rain_col =  2.697213554039090E-005
forc_snow_col =  8.557993213112620E-006
qflx_floodc = 0.000000000000000E+000
qflx_irrig =  0.000000000000000E+000
qflx_evap_tot =  5.882001259900219E-006
qflx_surf =  1.090692933065112E-005
qflx_h2osfc_surf =0.000000000000000E+000
qflx_qrgwl = 0.000000000000000E+000
qflx_drain = 2.145635562138315E-007
qflx_drain_perched =  0.0
qflx_snwcp_ice = 0.000000000000000E+000
qflx_lateral = 0.000000000000000E+000
dtime = 1800

errh2o = endwb0 - begwb0 \
                 - (forc_rain_col  + forc_snow_col   + qflx_floodc  + qflx_irrig  \
                 - qflx_evap_tot  - qflx_surf   - qflx_h2osfc_surf  \
                 - qflx_qrgwl  - qflx_drain  - qflx_drain_perched  - qflx_snwcp_ice  \
                 - qflx_lateral  ) * dtime
print(errh2o)
print(  (forc_snow_col ) * dtime )
print(  (forc_rain_col + forc_snow_col) * dtime )

print( qflx_drain * dtime )