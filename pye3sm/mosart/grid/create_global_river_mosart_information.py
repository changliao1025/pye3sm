import os
import numpy
import numpy as np
from netCDF4 import Dataset
from numpy.lib.shape_base import _put_along_axis_dispatcher
from pyearth.toolbox.reader.text_reader_string import text_reader_string
def create_global_river_mosart_information(sFilename_csv):

    aRiver = text_reader_string(sFilename_csv, iSkipline_in =1, cDelimiter_in=',')
    nriver = len(aRiver)

    sFilename_netcdf= '/compyfs/inputdata/rof/mosart/MOSART_Global_half_20210616.nc'
    print(sFilename_netcdf)
    aDatasets = Dataset(sFilename_netcdf)

    netcdf_format = aDatasets.file_format
    print(netcdf_format)
    print("Print dimensions:")
    print(aDatasets.dimensions.keys())
    print("Print variables:")
    print(aDatasets.variables.keys() )
    #output file

    # Copy variables
    for sKey, aValue in aDatasets.variables.items():
        #print(sKey, aValue)
        print(aValue.datatype)
        print( aValue.dimensions)
        # we need to take care of rec dimension

        # Copy variable attributes
        #outVar.setncatts({k: aValue.getncattr(k) for k in aValue.ncattrs()})
        if sKey == 'ID':
            aID =  (aValue[:]).data
        if sKey == 'dnID':
            aDnID =  (aValue[:]).data

        if sKey == 'fdir':
            aFdir =  (aValue[:]).data
        if sKey == 'latixy':
            aLatitude = (aValue[:]).data
        if sKey == 'longxy':
            aLongitude = (aValue[:]).data
        if sKey == 'areaTotal2':
            aAccu = (aValue[:]).data

    for i in range( nriver ):
        sRiver = aRiver[i][1].strip()
        dDraiange = float(aRiver[i][2].strip())
        dLon = float(aRiver[i][4].strip())
        dLat = float(aRiver[i][5].strip())

        if sRiver.lower() == 'amazon':
            #search mosart parameter 
            dummy_index = np.where( (aLongitude > (dLon-5)) & (aLongitude < (dLon+5)) \
                & (aLatitude > (dLat-5)) & (aLatitude < (dLat+5)) )
            
            if len(dummy_index) > 0:
                dummy_accu = aAccu[dummy_index]
                max_accu = np.max(dummy_accu) 

                print(max_accu/ 1.0E6)
                print(dDraiange)

                dummy_index1 = np.where(dummy_accu == max_accu )
                dummy_index2 = dummy_index1[0]
                dummy_index3 = dummy_index[0][dummy_index2]
                dummy_index4 = dummy_index[1][dummy_index2]
                lID  = aID[ dummy_index3, dummy_index4]
                print(lID)
                print(aAccu[ dummy_index3, dummy_index4])

            pass
        pass
    return


if __name__ == '__main__':
    sFilename_csv = '/qfs/people/liao313/data/e3sm/global/global_river.csv'
    create_global_river_mosart_information(sFilename_csv)