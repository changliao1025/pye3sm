import numpy as np
import netCDF4 as nc
def mosart_retrieve_main_channel(sFilename_parameter, dThreshold_in = 0.05):
    #read before modification
    pFile = nc.Dataset(sFilename_parameter, 'r')
    aFlow_accumulation = pFile.variables['areaTotal2'][:]
    #get the max flow accumulation
    dFlow_accumulation_max = np.max(aFlow_accumulation)
    dThreshold_flow_accumulation= dThreshold_in * dFlow_accumulation_max
    nCell = len(aFlow_accumulation)
    aChannel_out = np.zeros(nCell)

    for iIndex in range(nCell):
        if aFlow_accumulation[iIndex] >= dThreshold_flow_accumulation:
            aChannel_out[iIndex] = 1

    return aChannel_out
