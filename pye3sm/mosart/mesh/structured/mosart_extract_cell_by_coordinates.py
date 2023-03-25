import numpy as np
import netCDF4 as nc

def mosart_extract_cell_by_coordinates(sFilenamae_mosart_in, dLon_in, dLat_in , sFilename_mosart_out=None):
    """
    This function is used to extract the elevation information of a single cell from the mosart grid file
    It only supports the 2d case, i.e., the mosart grid file is 2d.

    Args:
        sFilenamae_mosart_in (_type_): _description_
        dLon_in (_type_): _description_
        dLat_in (_type_): _description_

    Returns:
        _type_: _description_
    """
    

    pDatasets_in = nc.Dataset(sFilenamae_mosart_in)

    netcdf_format = pDatasets_in.file_format    

    print(netcdf_format)
    print("Print dimensions:")
    pDimension = pDatasets_in.dimensions.keys()
    print(pDimension)
    print("Print variables:")
    pVariable = pDatasets_in.variables.keys()
    print( pVariable )

    #get     
    for sKey, aValue in pDatasets_in.variables.items():
        if "dnID" == sKey:
            aDnID = (aValue[:]).data            
           
        if "ID" == sKey:
            aID = (aValue[:]).data

        if "longxy" == sKey:
            aLon = (aValue[:]).data      

        if "latixy" == sKey:
            aLat = (aValue[:]).data
        

    #check it is 1d or 2d       
    # 
    aShape = aID.shape
    iDimension = len(aShape)
    if iDimension ==1:
        iFlag_1d =1
    else:
        nrow_original = aShape[0]
        ncolumn_original = aShape[1]
        iFlag_1d = 0
    

    #get the resolution of mosart grid

    dMax_lon = np.max(aLon)
    dMin_lon = np.min(aLon)
    dMax_lat = np.max(aLat)
    dMin_lat = np.min(aLat)


    dResolution_x = (dMax_lon - dMin_lon) / (ncolumn_original-1)
    sResolution_y = (dMax_lat - dMin_lat) / (nrow_original-1)
    
    #find the index of the cell using the coordinates

              
    column_index = int((dLon_in - dMin_lon) / dResolution_x)
    row_index  = int( (90-dLat_in) / sResolution_y)

    nrow = 1
    ncolumn = 1
    missing_value = -9999
    #extract the netcdf if the output file is given
    if sFilename_mosart_out is not None: 
         #output file
        pDatasets_out = nc.Dataset(sFilename_mosart_out, "w", format=netcdf_format)
        if  iDimension == 2:
            #2d case
            
            pDatasets_out.createDimension('lon', ncolumn )
            pDatasets_out.createDimension('lat', nrow )      

            for sKey, aValue in pDatasets_in.variables.items():            
                aDimenion_value = aValue.shape 
                if len(aDimenion_value) ==1:
                    outVar = pDatasets_out.createVariable(sKey, aValue.datatype, aValue.dimensions,fill_value=missing_value )
                    aData = (aValue[:]).data
                    iFlag_missing_value=0
                    for sAttribute in aValue.ncattrs():                
                        if( sAttribute.lower() =='_fillvalue' ):
                            missing_value0 = aValue.getncattr(sAttribute)                    
                            outVar.setncatts( { '_FillValue': missing_value } )                        
                            iFlag_missing_value = 1
                        else:                                        
                            outVar.setncatts( { sAttribute: aValue.getncattr(sAttribute) } )        
                    if iFlag_missing_value ==1:
                        dummy_index = np.where(  aData == missing_value0 ) 
                        aData[dummy_index] = missing_value          
                    if sKey.lower() == 'lat':
                        outVar[:] =  aData[row_index]                       
                    if sKey.lower() == 'lon':
                        outVar[:] = aData[ column_index] 
                    pass
                else:
                    if len(aDimenion_value) == 2:
                        #2d      
                        outVar = pDatasets_out.createVariable(sKey, aValue.datatype, ('lat','lon'),fill_value=missing_value)
                        aData = (aValue[:]).data
                        iFlag_missing_value=0
                        for sAttribute in aValue.ncattrs():                
                            if( sAttribute.lower() =='_fillvalue' ):
                                missing_value0 = aValue.getncattr(sAttribute)                    
                                outVar.setncatts( { '_FillValue': missing_value } )                        
                                iFlag_missing_value = 1
                            else:                                        
                                outVar.setncatts( { sAttribute: aValue.getncattr(sAttribute) } )        
                        outVar.setncatts( { '_FillValue': missing_value } )         
                        

                        #extract
                        outVar[:] =  aData[row_index, column_index]  
                    else:
                        #3d array are skiped
                        pass
                    
                    

        #close the dataset
        pDatasets_out.close()

        pass    

    return 


    

    
    