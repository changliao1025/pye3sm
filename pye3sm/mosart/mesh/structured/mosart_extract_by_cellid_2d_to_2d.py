import numpy as np
import os

from netCDF4 import Dataset

from pye3sm.mosart.mesh.structured.convert_index_between_array import convert_index_between_array

def mosart_extract_by_cellid_2d_to_2d(sFilename_mosart_in, sFilename_netcdf_out, aCellID_in):

    aDatasets = Dataset(sFilename_mosart_in)

    netcdf_format = aDatasets.file_format
    #output file
    datasets_out = Dataset(sFilename_netcdf_out, "w", format=netcdf_format)

    print(netcdf_format)
    print("Print dimensions:")
    pDimension = aDatasets.dimensions.keys()
    print(pDimension)
    print("Print variables:")
    pVariable = aDatasets.variables.keys()
    print( pVariable )

    #get     
    for sKey, aValue in aDatasets.variables.items():
        if "dnID" == sKey:
            aDnID = (aValue[:]).data            
           
        if "ID" == sKey:
            aID = (aValue[:]).data  

    #check it is 1d or 2d       
    # 
    aShape = aID.shape
    iDimension = len(aShape)
    nrow_original = aShape[0]
    ncolumn_original = aShape[1]
    
     
    if  iDimension==2:

        #2d case
        ncell_extract = len(aCellID_in)
        
        aIndex_row=list()
        aIndex_column=list()
        aIndex_1d=list()
        for i in range(ncell_extract):
            lCellID = aCellID_in[i]        
            dummy_row_index, dummy_column_index  = np.where( aID == lCellID)
            aIndex_row.append(dummy_row_index[0])
            aIndex_column.append(dummy_column_index[0])
            aIndex_1d.append( dummy_row_index[0] * ncolumn_original + dummy_column_index[0] )
        
        min_row = np.min(aIndex_row)
        max_row = np.max(aIndex_row)
        min_column = np.min(aIndex_column)
        max_column = np.max(aIndex_column)
    
        nrow = max_row - min_row + 1
        ncolumn = max_column - min_column + 1
        missing_value = -9999
         
        datasets_out.createDimension('lon', ncolumn )
        datasets_out.createDimension('lat', nrow )      
       
            
        for sKey, aValue in aDatasets.variables.items():            
            aDimenion_value = aValue.shape 
            if len(aDimenion_value) ==1:
                outVar = datasets_out.createVariable(sKey, aValue.datatype, aValue.dimensions,fill_value=missing_value )
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
                    aData0 = np.full( nrow_original, missing_value, dtype= aValue.datatype)
                    aData0[aIndex_row] = aData[aIndex_row]
                    #extract
                    dummy_data =  aData0[ min_row:max_row+1 ] 
                    outVar[:] =  dummy_data                      
                if sKey.lower() == 'lon':
                    aData0 = np.full( ncolumn_original, missing_value, dtype= aValue.datatype)
                    aData0[aIndex_column] = aData[aIndex_column]
                    dummy_data = aData0[min_column:max_column+1 ]      
                    outVar[:] = dummy_data
                pass
            else:
                if len(aDimenion_value) == 2:
                    #id or 2d      
                    outVar = datasets_out.createVariable(sKey, aValue.datatype, ('lat','lon'),fill_value=missing_value)
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
                    if iFlag_missing_value ==1:
                        dummy_index = np.where(  aData == missing_value0 ) 
                        aData[dummy_index] = missing_value              
                    aData0 = np.full( (nrow_original, ncolumn_original), missing_value, dtype= aValue.datatype)     
                    aData0[aIndex_row, aIndex_column] = aData[aIndex_row, aIndex_column]        
                    
                    #extract
                    outVar[:] = aData0[ min_row:max_row+1 , min_column:max_column+1 ]       
                    if sKey == 'latixy':
                        outVar[:] = aData[min_row:max_row+1,min_column:max_column+1 ]
                    if sKey == 'longxy':
                        outVar[:] = aData[min_row:max_row+1,min_column:max_column+1]
                    if sKey == 'ID':
                        aData0 = np.full( (nrow, ncolumn), missing_value, dtype= aValue.datatype)
                        kk = 1
                        for ii in range(nrow):
                            for jj in range(ncolumn):
                                aData0[ii, jj] = kk
                                kk = kk + 1
                        outVar[:] = aData0
                    if sKey == 'dnID':
                        aData0 = np.full( (nrow, ncolumn), missing_value, dtype= aValue.datatype)
                        for ii in range(ncell_extract):
                            lCellID = aCellID_in[ii]
                            dummy_index = np.where( aID == lCellID)
                            dummy_index0 = convert_index_between_array(nrow_original, ncolumn_original, dummy_index, nrow, ncolumn, min_row, min_column)
                            dnID=aDnID[dummy_index]
                            if dnID == -9999:
                            
                                aData0[dummy_index0[0],dummy_index0[1]]= -9999
                            else:
                                dummy_index1 = np.where( aID == dnID)
                                dummy_index2 = convert_index_between_array(nrow_original, ncolumn_original, dummy_index1, nrow, ncolumn, min_row, min_column)
                                kk = (dummy_index2[0]) * ncolumn + dummy_index2[1] + 1
                                #print(dummy_index0, kk)        
                                aData0[dummy_index0[0],dummy_index0[1]]= kk
                        outVar[:] = aData0      
                else:
                    #3d array are skiped
                    pass
    
        

    #close the dataset
    datasets_out.close()

    return