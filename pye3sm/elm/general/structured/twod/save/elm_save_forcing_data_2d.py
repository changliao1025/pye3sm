import os, sys
import numpy as np
import numpy.ma as ma
import datetime
import glob
from netCDF4 import Dataset #read netcdf

from pyearth.system.define_global_variables import *
from pyearth.gis.gdal.read.gdal_read_geotiff_file import gdal_read_geotiff_file
from pyearth.gis.gdal.read.gdal_read_envi_file import gdal_read_envi_file_multiple_band
from pyearth.visual.color.create_diverge_rgb_color_hex import create_diverge_rgb_color_hex
from pyearth.toolbox.date.day_in_month import day_in_month
from pyearth.visual.map.map_raster_data import map_raster_data

from pyearth.toolbox.data.remove_outliers import remove_outliers
from pye3sm.elm.grid.elm_retrieve_case_dimension_info import elm_retrieve_case_dimension_info
from pye3sm.atm.general.atm_retrieve_forcing_data_info import atm_retrieve_forcing_data_info

def elm_save_forcing_data_2d(oE3SM_in, oCase_in, sVariable_forcing_in, iFlag_scientific_notation_colorbar_in =None,   \
                                          dData_max_in = None,\
                                          dData_min_in = None,
                                         sUnit_in=None,\
                                          sTitle_in =None):

    sWorkspace_analysis_case = oCase_in.sWorkspace_analysis_case

    sWorkspace_analysis_case_variable = sWorkspace_analysis_case + slash + sVariable_forcing_in
    if not os.path.exists(sWorkspace_analysis_case_variable):
        os.makedirs(sWorkspace_analysis_case_variable)

    sWorkspace_analysis_case_region = sWorkspace_analysis_case_variable + slash + 'netcdf'
    if not os.path.exists(sWorkspace_analysis_case_region):
        os.makedirs(sWorkspace_analysis_case_region)
        pass

    aLon, aLat , aMask_ll= elm_retrieve_case_dimension_info(oCase_in)
    aLon = np.flip(aLon, 0) 
    aLat = np.flip(aLat, 0) 
    aMask = np.flip(aMask_ll, 0) 
   
    nrow_extract, ncolumn_extract = aLon.shape
    #resolution
    dLon_min = np.min(aLon)
    dLon_max = np.max(aLon)
    dLat_min = np.min(aLat)
    dLat_max = np.max(aLat)
    dResolution_x = (dLon_max - dLon_min) / (ncolumn_extract-1)
    dResolution_y = (dLat_max - dLat_min) / (nrow_extract-1)
    aImage_extent =  [dLon_min- dResolution_x ,dLon_max + dResolution_x, dLat_min -dResolution_x,  dLat_max+dResolution_x]

    dResoultion_elm = dResolution_x

    #get subset

    #subset depends on resolution

    #dimension
    aMask_ul = np.flip(aMask_ll, 0)

    sFolder, sField, aFilename = atm_retrieve_forcing_data_info (oCase_in, sVariable_forcing_in)

    dResoultion_forcing =0.5

    #get date 
    iYear_start = oCase_in.iYear_start
    iYear_end = oCase_in.iYear_end

    for iYear in range(iYear_start, iYear_end + 1, 1):
        sYear =  "{:04d}".format(iYear)
        #get the file by year
        for iMonth in range(1, 12 + 1, 1):
            sMonth =  "{:02d}".format(iMonth)
            sDate = sYear + '-' + sMonth
            dummy = '*'+sDate+'*'
            sRegex = os.path.join( sFolder, dummy )

            sFilename_output = sWorkspace_analysis_case_region + slash + sVariable_forcing_in +  sExtension_netcdf
            #should we use the same netcdf format? 
            pFile = Dataset(sFilename_output, 'w', format = 'NETCDF4') 
            pDimension_longitude = pFile.createDimension('lon', ncolumn_extract) 
            pDimension_latitude = pFile.createDimension('lat', nrow_extract) 

            dom = day_in_month(iYear, iMonth, iFlag_leap_year_in = 0)

            nts = dom * 8 #3 hour temporal resolution
            aGrid_stack= np.full((nts, nrow_extract, ncolumn_extract), -9999.0, dtype= float)
            i=0
            for sFilename in glob.glob(sRegex):
                aDatasets = Dataset(sFilename)
                for sKey, aValue in aDatasets.variables.items():
                    if (sKey == 'LONGXY'):                   
                        aLongitude = (aValue[:]).data
                        continue
                    if (sKey == 'LATIXY'):                    
                        aLatitude = (aValue[:]).data
                        continue
                    if (sKey == sField):                    
                        aData0 = (aValue[:]).data
                        continue

                if np.max(aLongitude) > 180:
                    aData = np.roll(aData0, int(180/dResoultion_forcing), axis=2)

                #aData  = np.reshape( aData, (nts, 360*720) )
                aData  = np.flip( aData, 1 )  
                #now extract
                aData_out_extract = np.full((nts, nrow_extract, ncolumn_extract), -9999, dtype=float)
                for i in range(nrow_extract):
                    for j in range(ncolumn_extract):
                        dLon = aLon[i,j] - 0.5 * dResoultion_elm
                        dLat = aLat[i,j] + 0.5 * dResoultion_elm
                        #locate it
                        iMask = aMask[i,j]
                        if iMask >=1:
                            iIndex = int( (90-(dLat)) / dResoultion_forcing )
                            jIndex = int( (dLon-(-180)) / dResoultion_forcing )
                            
                            aData_out_extract[:,i,j] = aData[:,iIndex, jIndex]
                
                for i in range(nts):
                    sStep ="{:03d}".format(i)
                    aData_out= aData_out_extract[i,:,:]
                    aData_out= np.reshape( aData_out, (nrow_extract,ncolumn_extract) )
                    aData_all = np.array(aData_out)     
                    sFilename_out=sWorkspace_analysis_case_region + slash \
                         + sVariable_forcing_in + '_map_' + sDate + sStep+'.png'            

                    sDummy = sVariable_forcing_in + sYear +  sStep
                    pVar = pFile.createVariable( sDummy , 'f4', ('lat' , 'lon')) 
                    pVar[:] = aData_all
                    pVar.description = sDummy
                    pVar.unit = 'mm/s' 
                    
                    pass    

            pass
        pass

    





    return