import os 
import numpy as np
from netCDF4 import Dataset #read netcdf
from pyearth.system.define_global_variables import *    
from pyearth.toolbox.date.day_in_month import day_in_month
from pyearth.toolbox.date.leap_year import  leap_year
from pye3sm.mosart.mesh.structured.mosart_retrieve_structured_case_dimension_info import mosart_retrieve_structured_case_dimension_info 
import getpass
from datetime import datetime

def mosart_create_stream_file_2d(oCase_in, sWorkspace_stream_in):
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
    aLon, aLat , aMask_ul= mosart_retrieve_structured_case_dimension_info(oCase_in)
    #dimension
    aMask_ll = np.flip(aMask_ul, 0)
    nrow = np.array(aMask_ul).shape[0]
    ncolumn = np.array(aMask_ul).shape[1]
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
   
    #where should we save the stream file?
    #
    
    if not os.path.exists(sWorkspace_stream_in):
        os.makedirs(sWorkspace_stream_in)
   
    i=0
    for iYear in range(iYear_start, iYear_end + 1):
        sYear = "{:04d}".format(iYear) #str(iYear).zfill(4)
        sFilename_output = sWorkspace_stream_in + slash + 'drof_'+ sYear +  sExtension_netcdf

        #if leap_year(iYear):
        #    nday_in_year = 366 #no leap year
        #else:
        nday_in_year = 365 #no leap year

        aGrid_stack= np.full((nday_in_year, nrow, ncolumn), -9999.0, dtype= float)
        #should we use the same netcdf format? 
        pFile = Dataset(sFilename_output, 'w', format = 'NETCDF3_CLASSIC')  #,format="NETCDF3_CLASSIC"
        pDimension_longitude = pFile.createDimension('lon', ncolumn) 
        pDimension_latitude = pFile.createDimension('lat', nrow) 
        pDimension_time = pFile.createDimension('time', nday_in_year) 

        iDay_index = 0
        for iMonth in range(iMonth_start, iMonth_end + 1):
            sMonth = str(iMonth).zfill(2)

            nday_in_month = day_in_month(iYear, iMonth)
            if iMonth==2:
                nday_in_month=28

            for iDay in range(1, nday_in_month +1, 1):
                sDay = str(iDay).zfill(2)
    
                sDummy = '.mosart.h0.' + sYear + '-' + sMonth + '-' + sDay+ '-00000'+ sExtension_netcdf
                sFilename = sWorkspace_simulation_case_run + slash + sCase + sDummy
    
                #read before modification

                if os.path.exists(sFilename):
                    #print("Yep, I can read that file: " + sFilename)                
                    pass
                else:
                    iFlag_found = 0
                    nmax_search = 10

                    for iSearch in range(1, nmax_search, 1):
                        if iFlag_found ==0:
                            search_day = iDay - iSearch;
                            sDay0 = "{:02d}".format(search_day)
                            sDummy_new = '.mosart.h0.' + sYear + '-' + sMonth + '-' + sDay0+ '-00000'+ sExtension_netcdf
                            sFilename_new = sWorkspace_simulation_case_run + slash + sCase + sDummy_new
                            if os.path.exists(sFilename_new):
                                iFlag_found = 1   
                                break                         
                            else:                            
                                search_day = iDay + iSearch;
                                sDay1 = "{:02d}".format(search_day)

                                sDummy_new = '.mosart.h0.' + sYear + '-' + sMonth + '-' + sDay1+ '-00000'+ sExtension_netcdf
                                sFilename_new = sWorkspace_simulation_case_run + slash + sCase + sDummy_new
                                if os.path.exists(sFilename_new):                                  
                                    iFlag_found = 1   
                                    break   
                                else:                                  
                                    continue       

                    print(sFilename + ' is missing, we will use the next available date: ' , sFilename_new)                
                    sFilename = sFilename_new
                    
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
                #sVariable_discharge  = 'RIVER_DISCHARGE_OVER_LAND_LIQ'
                sVariable_discharge  = 'Main_Channel_Water_Depth_LIQ'
                for sKey, aValue in aDatasets.variables.items():
                    if sKey.lower() == sVariable_discharge.lower() :                                       
                        aData_ll = (aValue[:]).data             
                        aData_ll = aData_ll.reshape(nrow, ncolumn)     
                        aData_ll[aMask_index_ll] = missing_value
                        #aData_ul = np.flip(aData_ll, 0)   
                        #save output                        
    
                        aGrid_stack[iDay_index, :, : ] = aData_ll
                        iDay_index = iDay_index + 1
                        break

        sDummy = sVariable 
        pVar = pFile.createVariable( sDummy , 'f4', ('time', 'lat' , 'lon'),fill_value=-9999) 
        pVar[:] = aGrid_stack
        pVar.standard_name = 'river gage height'
        pVar.long_name = 'River gage height'
        pVar.unit = 'm'      


        #add other variable
        sDummy = 'lon'
        pVar = pFile.createVariable( sDummy , 'f4', ( 'lon'),fill_value=-9999) 
        pVar[:] = aLongitude
        pVar.standard_name = 'longitude'
        pVar.long_name = 'longitude'
        pVar.unit = 'degree'   
        pVar.axis = "X" 

        sDummy = 'lat'
        pVar = pFile.createVariable( sDummy , 'f4', ('lat' ),fill_value=-9999) 
        pVar[:] = aLatitude
        pVar.standard_name = 'latitude'
        pVar.long_name = 'latitude'
        pVar.unit = 'degree' 
        pVar.axis = "Y" 

        sDummy = 'time'
        pVar = pFile.createVariable( sDummy , 'f4', ('time'),fill_value=-9999) 
        aTime = np.arange(nday_in_year) # it is also possible to use + 1
        pVar[:] = aTime
        pVar.standard_name = sDummy
        pVar.long_name = sDummy
        pVar.units = 'days since ' +  sYear + '-01-01 00:00:00'
        pVar.calendar = 'standard' 
        pVar.axis = "T" 

        #set global attributes
        pFile.setncattr("Created_by", getpass.getuser())
        pFile.setncattr("Created_on", datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
          
        #close netcdf file   
        pFile.close()
        print(sYear, 'Finished')
 

    print("finished")



    
