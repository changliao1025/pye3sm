import numpy as np
import os

from datetime import datetime
from scipy.io import netcdf
import getpass
from netCDF4 import Dataset

from pye3sm.mosart.grid.convert_index_between_array import convert_index_between_array

def extract_mosart_by_cellid(iFlag_2d_to_1d, sFilenamae_mosart_in, filename_netcdf_out, aCellID_in):

    aDatasets = Dataset(sFilenamae_mosart_in)

    netcdf_format = aDatasets.file_format
    #output file
    datasets_out = Dataset(filename_netcdf_out, "w", format=netcdf_format)

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
    if iDimension ==1:
        iFlag_1d =1
    else:
        nrow_original = aShape[0]
        ncolumn_original = aShape[1]
        iFlag_1d = 0
    

    if iFlag_1d ==1:
        aID=np.ravel(aID)
        aDnID=np.ravel(aDnID)
        ncell = aID.size
        ncell_extract = len(aCellID_in)
        aIndex=list()
        for i in range(ncell_extract):
            lCellID = aCellID_in[i]
            dummy_index = np.where( aID == lCellID)
            aIndex.append(dummy_index)
        pass

        datasets_out.createDimension('ncell', ncell_extract )
    else:
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
        if iFlag_2d_to_1d ==0:   
            datasets_out.createDimension('lon', ncolumn )
            datasets_out.createDimension('lat', nrow )      
            #now extract variables
            #get     
            
            for sKey, aValue in aDatasets.variables.items():            
                aDimenion_value = aValue.shape 
                if len(aDimenion_value) ==1:
                    outVar = datasets_out.createVariable(sKey, aValue.datatype, aValue.dimensions)
                    aData = (aValue[:]).data
                    iFlag_missing_vale=0
                    for sAttribute in aValue.ncattrs():                
                        if( sAttribute.lower() =='_fillvalue' ):
                            missing_value0 = aValue.getncattr(sAttribute)                    
                            outVar.setncatts( { '_FillValue': missing_value } )                        
                            iFlag_missing_vale = 1
                        else:                                        
                            outVar.setncatts( { sAttribute: aValue.getncattr(sAttribute) } )        
                    if iFlag_missing_vale ==1:
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
                        outVar = datasets_out.createVariable(sKey, aValue.datatype, ('lat','lon'))
                        aData = (aValue[:]).data
                        iFlag_missing_vale=0
                        for sAttribute in aValue.ncattrs():                
                            if( sAttribute.lower() =='_fillvalue' ):
                                missing_value0 = aValue.getncattr(sAttribute)                    
                                outVar.setncatts( { '_FillValue': missing_value } )                        
                                iFlag_missing_vale = 1
                            else:                                        
                                outVar.setncatts( { sAttribute: aValue.getncattr(sAttribute) } )        
                        outVar.setncatts( { '_FillValue': missing_value } )         
                        if iFlag_missing_vale ==1:
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
    
        else:
            #we change 2d to 1d 
            datasets_out.createDimension('gridcell', ncell_extract )
            for sKey, aValue in aDatasets.variables.items():            
                aDimenion_value = aValue.shape 
                if len(aDimenion_value) ==1:
                    #save later     

                    pass
                else:
                    if len(aDimenion_value) == 2:
                        if sKey == 'ID':
                            aData_id = np.full( (nrow, ncolumn), missing_value, dtype= aValue.datatype)
                            kk = 1
                            for ii in range(nrow):
                                for jj in range(ncolumn):
                                    dummy_index = (ii+min_row) * ncolumn_original + jj+min_column
                                    if( dummy_index in  aIndex_1d):
                                        aData_id[ii, jj] = kk
                                        kk = kk + 1
                                    else:
                                        pass

                        else:
                            if sKey == 'dnID':
                                pass
                            else: #others
                                outVar = datasets_out.createVariable(sKey, aValue.datatype, ('gridcell'))
                                aData = (aValue[:]).data
                                iFlag_missing_vale=0
                                for sAttribute in aValue.ncattrs():                
                                    if( sAttribute.lower() =='_fillvalue' ):
                                        missing_value0 = aValue.getncattr(sAttribute)                    
                                        outVar.setncatts( { '_FillValue': missing_value } )                        
                                        iFlag_missing_vale = 1
                                    else:                                        
                                        outVar.setncatts( { sAttribute: aValue.getncattr(sAttribute) } )        
                                outVar.setncatts( { '_FillValue': missing_value } )         
                                if iFlag_missing_vale ==1:
                                    dummy_index = np.where(  aData == missing_value0 ) 
                                    aData[dummy_index] = missing_value              
                                aData0 = np.full( (nrow_original, ncolumn_original), missing_value, dtype= aValue.datatype)     
                                aData0[aIndex_row, aIndex_column] = aData[aIndex_row, aIndex_column]        
                                #extract
                                aData1= aData0[ min_row:max_row+1 , min_column:max_column+1 ]       
                                outVar[:]  = aData1[np.where(aData1 != missing_value)]   

                                if sKey == 'latixy':
                                    aLat_out = aData1[np.where(aData1 != missing_value)] 

                                    pass
                                
                                if sKey == 'longxy':
                                    aLon_out = aData1[np.where(aData1 != missing_value)] 
                                    pass
                    else:
                        #3d array are skiped
                        pass
            
            #now 
            outVar = datasets_out.createVariable('ID', aValue.datatype, ('gridcell'))
            aID2 = aData_id[np.where(aData_id != missing_value)]
            aID2=np.ravel(aID2)
            outVar[:] = aID2

            outVar = datasets_out.createVariable('dnID', aValue.datatype, ('gridcell'))

            aData_dnid = np.full( (nrow, ncolumn), missing_value, dtype= aValue.datatype)

            for ii in range(nrow):
                for jj in range(ncolumn): 
                    dummy_index = (ii+min_row) * ncolumn_original + jj+min_column
                    if( dummy_index in  aIndex_1d):  
                        #find dnid
                        dnid = aDnID[(ii+min_row), jj+min_column ]
                        
                        if dnid == missing_value:
                            aData_dnid[ii,jj] =-1
                            pass
                        else:
                            dummy_index = np.where(aID==dnid)

                            aData_dnid[ii,jj] = aData_id[ dummy_index[0]-min_row, dummy_index[1]-min_column]
                        

                        pass 
            aDnid2  = aData_dnid[np.where(aData_dnid != missing_value)]
            aDnid2[np.where(aDnid2==-1)] = missing_value
            outVar[:]  = np.ravel(aDnid2)

            #lat and lon
            outVar = datasets_out.createVariable('lat', aValue.datatype, ('gridcell'))            
            outVar[:] = aLat_out
            outVar = datasets_out.createVariable('lon', aValue.datatype, ('gridcell'))            
            outVar[:] = aLon_out



    #close the dataset
    datasets_out.close()


    

    
    return