import os 
import numpy as np
from netCDF4 import Dataset #read netcdf
from osgeo import  osr #the default operator
from pyearth.system.define_global_variables import *    
from pye3sm.mosart.mesh.mosart_retrieve_case_dimension_info import mosart_retrieve_case_dimension_info 


def mosart_generate_stream_file_2d(oE3SM_in, oCase_in):
    """
    Generate the stream file for the drof compset

    Args:
        oE3SM_in (pye3sm object): _description_
        oCase_in (pycase object): _description_
    """

    sModel  = oCase_in.sModel
    sRegion = oCase_in.sRegion               
    iYear_start = oCase_in.iYear_start        
    iYear_end = oCase_in.iYear_end          
    iFlag_same_grid = oCase_in.iFlag_same_grid 
    print('The following model is processed: ', sModel)
    
        
    dConversion = oCase_in.dConversion   
    sVariable  = oCase_in.sVariable
    #for the sake of simplicity, all directory will be the same, no matter on mac or cluster
   
    sCase = oCase_in.sCase
    #we only need to change the case number, all variables will be processed one by one
    
    
    sWorkspace_simulation_case_run = oCase_in.sWorkspace_simulation_case_run
    sWorkspace_analysis_case = oCase_in.sWorkspace_analysis_case
    
    if not os.path.exists(sWorkspace_analysis_case):
        os.makedirs(sWorkspace_analysis_case)    

    #new approach
    aLon, aLat , aMask_ll= mosart_retrieve_case_dimension_info(oCase_in)
    #dimension
    aMask_ul = np.flip(aMask_ll, 0)
    nrow = np.array(aMask_ll).shape[0]
    ncolumn = np.array(aMask_ll).shape[1]
    #be careful with the mask 0 or 1 
    aMask_index_ll = np.where(aMask_ll==0)
    aMask_index_ul = np.where(aMask_ul==0)

    #resolution
    dLon_min = np.min(aLon)
    dLon_max = np.max(aLon)
    dLat_min = np.min(aLat)
    dLat_max = np.max(aLat)
    dResolution_x = (dLon_max - dLon_min) / (ncolumn-1)
    dResolution_y = (dLat_max - dLat_min) / (nrow-1)

    print('Prepare the map grid')
   
    longitude = np.arange(dLon_min, dLon_max , dResolution_x)
    latitude = np.arange( dLat_max, dLat_min, -1*dResolution_y)
    grid_x, grid_y = np.meshgrid(longitude, latitude)
   
    
    iFlag_optional = 1 

 
    
    #where should we save the stream file?
    sWorkspace_stream = '/compy/liap313/00raw/drof'
    if not os.path.exists(sWorkspace_stream):
        os.makedirs(sWorkspace_stream)
   
    #how often should be output file is stored, per year is preferred similar to other stream file?
        
    nmonth = (iYear_end - iYear_start +1) * 12
    nday = 365 #no leap year
    
    i=0
    for iYear in range(iYear_start, iYear_end + 1):
        sYear = "{:04d}".format(iYear) #str(iYear).zfill(4)
        sFilename_output = sWorkspace_stream + slash + 'drof_'+ sYear +  sExtension_netcdf
        aGrid_stack= np.full((nday, nrow, ncolumn), -9999.0, dtype= float)
        #should we use the same netcdf format? 
        pFile = Dataset(sFilename_output, 'w', format = 'NETCDF4') 
        pDimension_longitude = pFile.createDimension('lon', ncolumn) 
        pDimension_latitude = pFile.createDimension('lat', nrow) 
        pDimension_time = pFile.createDimension('time', nday) 
        for iMonth in range(iMonth_start, iMonth_end + 1):
            sMonth = str(iMonth).zfill(2)
    
            sDummy = '.mosart.h0.' + sYear + '-' + sMonth + sExtension_netcdf
            sFilename = sWorkspace_simulation_case_run + slash + sCase + sDummy
    
            #read before modification
    
            if os.path.exists(sFilename):
                #print("Yep, I can read that file: " + sFilename)                
                pass
            else:
                print(sFilename + ' is missing')
                print("Nope, the path doesn't reach your file. Go research filepath in python")
                return
    
            aDatasets = Dataset(sFilename)
    
            for sKey, aValue in aDatasets.variables.items():
            
                if (sKey == 'lon'):                   
                    aLongitude = (aValue[:]).data
                    continue
                if (sKey == 'lat'):                    
                    aLatitude = (aValue[:]).data
                    continue
            
            #quality control the longitude data
            dummy_index = np.where(aLongitude > 180)
            aLongitude[dummy_index] = aLongitude[dummy_index] - 360.0
    
            #read the actual data
            sVariable_discharge  = 'RIVER_DISCHARGE_OVER_LAND_LIQ'
            sVariable_discharge  = 'Main_Channel_Water_Depth_LIQ'
            for sKey, aValue in aDatasets.variables.items():
                if sKey.lower() == sVariable_discharge.lower() :
                                   
                    aData_ll = (aValue[:]).data                                    
                    missing_value1 = np.max(aData_ll)  
                    aData_ll = aData_ll.reshape(nrow, ncolumn)                          
                    dummy_index = np.where( aData_ll == missing_value1 ) 
                    aData_ll[dummy_index] = missing_value
                    
                    aData_ll[aMask_index_ll] = missing_value
                    aData_ul = np.flip(aData_ll, 0)   
                    #save output
                    

                    sDummy = sVariable + sYear + sMonth
                    pVar = pFile.createVariable( sDummy , 'f4', ('lat' , 'lon'),fill_value=-9999) 
                    pVar[:] = aData_ll
                    pVar.description = sDummy
                    pVar.unit = 'm' 
                    iFlag_netcdf_first = 0
                    
                    if(iFlag_optional == 1):
                        #stack data
                        aGrid_stack[i, :,: ] =  aData_ul
                        i=i+1
                    break
                else:
                    pass
    
    
    #close netcdf file   
    pFile.close()
 
    
    


    print("finished")



    
