import os
import numpy
import numpy as np
from netCDF4 import Dataset
from pyearth.toolbox.reader.text_reader_string import text_reader_string
def mosart_create_global_river_information(sFilename_csv, sFilename_out):

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

    ofs = open(sFilename_out, 'w')

    

    # Copy variables
    for sKey, aValue in aDatasets.variables.items():
        #print(sKey, aValue)
        #print(aValue.datatype)
        #print( aValue.dimensions)
        # we need to take care of rec dimension

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
        aRiver[i][1] = sRiver
        dDraiange = float(aRiver[i][2].strip())
        dLon = float(aRiver[i][4].strip())
        dLat = float(aRiver[i][5].strip())

        
        #search mosart parameter 
        dummy_index = np.where( (aLongitude > (dLon-5)) & (aLongitude < (dLon+5)) \
            & (aLatitude > (dLat-5)) & (aLatitude < (dLat+5)) )
        
        if len(dummy_index) > 0:
            dummy_accu = aAccu[dummy_index]
            max_accu = np.max(dummy_accu) 
            
            
            dummy_index1 = np.where(dummy_accu == max_accu )
            dummy_index2 = dummy_index1[0]
            dummy_index3 = dummy_index[0][dummy_index2]
            dummy_index4 = dummy_index[1][dummy_index2]
            lID  = aID[ dummy_index3, dummy_index4]
            print(sRiver, max_accu/1.0E6, dDraiange, int(lID[0]))
            
            #print(aAccu[ dummy_index3, dummy_index4])
            aRiver[i][6] = "{:0d}".format(int(lID[0]))

            sLine = ','.join(aRiver[i] ) + '\n'
            ofs.write(sLine)

        else:
            pass    
        
        

        pass

    ofs.close()
    return

