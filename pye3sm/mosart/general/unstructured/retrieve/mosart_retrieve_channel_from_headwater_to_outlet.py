import numpy as np
import netCDF4 as nc
def mosart_retrieve_channel_from_headwater_to_outlet(sFilename_parameter, lCellID_headwater):
    pFile = nc.Dataset(sFilename_parameter, 'r')
    aFlow_accumulation = pFile.variables['areaTotal2'][:]

    aFlowline_length = pFile.variables['rlen'][:]

    aCellID  = pFile.variables['ID'][:]
    aDnID = pFile.variables['dnID'][:]

    lIndex_headwater = (np.where(aCellID == lCellID_headwater))[0][0]

    #now trace
    aIndex_out = list()
    aLength_out = list()
    aFlow_accumulation_out = list()
    aIndex_out.append(lIndex_headwater)
    aLength_out.append(aFlowline_length[lIndex_headwater])
    aFlow_accumulation_out.append(aFlow_accumulation[lIndex_headwater])
    lIndex_upstream = lIndex_headwater
    iFlag_done = 0
    while iFlag_done == 0:
        lCellID_downslope = aDnID[lIndex_upstream]
        lIndex_downstream = (np.where(aCellID == lCellID_downslope))[0]
        if len(lIndex_downstream) == 0:
            iFlag_done = 1
        else:
            lIndex_downstream = lIndex_downstream[0]
            aIndex_out.append(lIndex_downstream)
            lIndex_upstream = lIndex_downstream

            aLength_out.append(aFlowline_length[lIndex_downstream])
            aFlow_accumulation_out.append(aFlow_accumulation[lIndex_downstream])

    return aIndex_out, aLength_out, aFlow_accumulation_out

