import os, sys
import numpy as np
import numpy.ma as ma
import datetime
import glob
from netCDF4 import Dataset #read netcdf
import scipy.ndimage
from pyearth.system.define_global_variables import *
from pyearth.gis.gdal.read.gdal_read_geotiff_file import gdal_read_geotiff_file
from pyearth.gis.gdal.read.gdal_read_envi_file import gdal_read_envi_file_multiple_band
from pyearth.visual.color.create_diverge_rgb_color_hex import create_diverge_rgb_color_hex
from pyearth.toolbox.date.day_in_month import day_in_month
from pyearth.toolbox.data.beta.replace_variable_in_netcdf import replace_variable_in_netcdf


from pye3sm.elm.grid.elm_retrieve_case_dimension_info import elm_retrieve_case_dimension_info
from pye3sm.atm.general.atm_retrieve_forcing_data_info import atm_retrieve_forcing_data_info

missing_value = 1.0E36
def generate_forcing_data_2d(oE3SM_in, oCase_in, sVariable_forcing_in,   \
                                          dData_max_in = None,\
                                          dData_min_in = None,
                                         sUnit_in=None,\
                                          sTitle_in =None):

    sWorkspace_analysis_case = oCase_in.sWorkspace_analysis_case

    

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
    nrow_new = 360
    ncolumn_new = 720
    dResoultion_elm = dResolution_x
    nrow_old = 180
    ncolumn_old = 360

    #get subset

    #subset depends on resolution

    #dimension
    aMask_ul = np.flip(aMask_ll, 0)

    #this forcing is not directly used by elm, so we will only the elm dimension info to extract

    sFolder_origin, sField, aFilename = atm_retrieve_forcing_data_info (oCase_in, sVariable_forcing_in)
    sFolder='/compyfs/liao313/00raw/hybam/HOP_noleap'
    sField='PRECTmms'
    aFilename=''


    dResoultion_forcing_origin =0.5
    dResoultion_forcing =1.0

    #get date 
    iYear_start = oCase_in.iYear_start
    iYear_end = oCase_in.iYear_end

    iYear_start_data = 1950
    iYear_end_data = 2010

    iYear_start_avail = 1979
    iYear_end_avail = 2008

    for iYear in range(iYear_start_data, iYear_end_data + 1, 1):
        iYear_origin = iYear
        sYear_origin =  "{:04d}".format(iYear_origin)
        if iYear < iYear_start_avail:
            #no data available, we need to use the nearest 
            iYear = iYear_start_avail
            pass
        if iYear > iYear_end_avail:
            #no data available, we need to use the nearest 
            iYear = iYear_end_avail
            pass

        sYear =  "{:04d}".format(iYear)

        #get the file by year
        for iMonth in range(1, 12 + 1, 1):
            sMonth =  "{:02d}".format(iMonth)
            sDate = sYear + '-' + sMonth
            sDate_origin = sYear_origin + '-' + sMonth
            dummy = '*'+sDate_origin+'*'
            sRegex_origin = os.path.join( sFolder_origin, dummy )
            dummy = '*'+sDate+'*'
            sRegex = os.path.join( sFolder, dummy )

            dom = day_in_month(iYear, iMonth, iFlag_leap_year_in = 0)
            nts = dom * 8 #3 hour temporal resolution

            for sFilename in glob.glob(sRegex_origin):
                aDatasets = Dataset(sFilename)
                for sKey, aValue in aDatasets.variables.items():
                    if (sKey == 'LONGXY'):                   
                        aLongitude_origin = (aValue[:]).data
                        continue
                    if (sKey == 'LATIXY'):                    
                        aLatitude_origin = (aValue[:]).data
                        continue
                    

                #if np.max(aLongitude_origin) > 180:
                #    aData = np.roll(aData0_origin, int(180/dResoultion_forcing), axis=2)
                sFilename_old = sFilename
                break

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

                #if np.max(aLongitude) > 180:
                #    aData = np.roll(aData0, int(180/dResoultion_forcing), axis=2)
                aData0 = np.flip(aData0, 1)
                aLatitude_origin = np.flip(aLatitude_origin, 0)
         
                aData_out_extract = np.full((nts, nrow_new, ncolumn_new), missing_value, dtype=float)
                

                for iStep in range(nts):
                    dummy0 = aData0[iStep, :,:]
                    dummy = dummy0.reshape(nrow_old, ncolumn_old)
                    aData_out_extract[iStep,:,:] = scipy.ndimage.zoom(dummy, 2, order=0)

                #aData_out_extract =   scipy.ndimage.zoom(aData0, 2, order=0)

                #save to a new location
                aData_out_extract = np.flip(aData_out_extract, 1)

                sFolder_out  = '/compyfs/liao313/00raw/prec'
                sBasename = os.path.basename(sFilename_old)
                sBasename_new = sBasename.replace(sYear, sYear_origin, 1)
                sFilename_new = os.path.join(sFolder_out,sBasename_new )
                
                replace_variable_in_netcdf(sFilename_old, sFilename_new, aData_out_extract, sField)
                
                   

            pass
        pass

    





    return