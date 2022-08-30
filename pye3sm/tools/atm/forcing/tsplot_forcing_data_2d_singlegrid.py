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

from pyearth.visual.timeseries.plot_time_series_data import plot_time_series_data

from pyearth.toolbox.data.remove_outliers import remove_outliers
from pye3sm.elm.grid.elm_retrieve_case_dimension_info import elm_retrieve_case_dimension_info
from pye3sm.atm.general.atm_retrieve_forcing_data_info import atm_retrieve_forcing_data_info

def tsplot_forcing_data_2d_singlegrid(oE3SM_in, oCase_in, sVariable_forcing_in, iFlag_scientific_notation_colorbar_in =None,   \
                                          dData_max_in = None,\
                                          dData_min_in = None,
                                         sUnit_in=None,\
                                          sTitle_in =None):
    
    dLon = -58.65
    dLat = -10.88

    sWorkspace_analysis_case = oCase_in.sWorkspace_analysis_case

    sWorkspace_analysis_case_variable = sWorkspace_analysis_case + slash + sVariable_forcing_in
    if not os.path.exists(sWorkspace_analysis_case_variable):
        os.makedirs(sWorkspace_analysis_case_variable)

    sWorkspace_analysis_case_region = sWorkspace_analysis_case_variable + slash + 'tsplot'
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

    #sFolder, sField, aFilename = atm_retrieve_forcing_data_info (oCase_in, sVariable_forcing_in)
    sFolder='/compyfs/liao313/00raw/hybam/HOP_noleap'
    sField='PRECTmms'
    aFilename=''
    dResoultion_forcing =1.0
    

    #get date 
    iYear_start = oCase_in.iYear_start
    iYear_end = oCase_in.iYear_end
    dates = list()
    nyear = iYear_end - iYear_start + 1
    for iYear in range(iYear_start, iYear_end + 1):
        for iMonth in range(1,13):
            dSimulation = datetime.datetime(iYear, iMonth, 15)
            dates.append( dSimulation )
    
    dates=np.array(dates)

    nstress = (iYear_end -  iYear_start + 1) * 12
    #now extract
    aData_out_extract = np.full((nstress), 0.0, dtype=float)
    index_date =0 
    for iYear in range(iYear_start, iYear_end + 1, 1):
        sYear =  "{:04d}".format(iYear)
        #get the file by year
        for iMonth in range(1, 12 + 1, 1):
            sMonth =  "{:02d}".format(iMonth)

            
            sDate = sYear + '-' + sMonth
            dummy = '*'+sDate+'*'
            sRegex = os.path.join( sFolder, dummy )

            dom = day_in_month(iYear, iMonth, iFlag_leap_year_in = 0)
            nts = dom * 8 #3 hour temporal resolution
            iIndex = int( (90-(dLat)) / dResoultion_forcing )
            jIndex = int( (dLon-(-180)) / dResoultion_forcing )
            for sFilename in glob.glob(sRegex):
                aDatasets = Dataset(sFilename)
                for sKey, aValue in aDatasets.variables.items():
                    #if (sKey == 'LONGXY'):                   
                    #    aLongitude = (aValue[:]).data
                    #    continue
                    #if (sKey == 'LATIXY'):                    
                    #    aLatitude = (aValue[:]).data
                    #    continue
                    if (sKey == sField):                    
                        aData0 = (aValue[:]).data
                        break

                #if np.max(aLongitude) > 180:
                aData = np.roll(aData0, int(180/dResoultion_forcing), axis=2)                               
                                
                dummy = aData[:,iIndex, jIndex]
                total_prec = np.sum(dummy)
                aData_out_extract[index_date] = total_prec
            
            index_date = index_date + 1   

            pass
        pass

    




    #plot
    sFilename_out = sWorkspace_analysis_case_region + slash \
                + sVariable_forcing_in + '_tsplot' +'.png'

    aDate_all = np.array([dates])
    aData_all = np.array([aData_out_extract])
    aColor = ['red'] 
    iReverse_y_in =0 
    sLabel_y = 'Precipitation (mm/s)'
    aLabel_legend_in=['']
    plot_time_series_data(aDate_all,
                                  aData_all,\
                                  sFilename_out,\
                                  iReverse_y_in = iReverse_y_in, \
                                  #iFlag_log_in = 1,\
                                  ncolumn_in = 1,\
                                  sTitle_in = sTitle_in, \
                                  sLabel_y_in= sLabel_y,\
                                  aLabel_legend_in = aLabel_legend_in, \
                                  aColor_in = aColor,\
                                  aMarker_in = ['+'],\
                                  sLocation_legend_in = 'upper right' ,\
                                  aLocation_legend_in = (1.0, 0.0),\
                                  aLinestyle_in = ['-'],\
                                  iSize_x_in = 12,\
                                  iSize_y_in = 5)
    return