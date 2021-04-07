import os, sys
import argparse
import numpy as np
from netCDF4 import Dataset #it maybe be replaced by gdal 
import datetime
sSystem_paths = os.environ['PATH'].split(os.pathsep)
 

from pyearth.system.define_global_variables import *
from pyearth.gis.gdal.read.gdal_read_geotiff import gdal_read_geotiff

from pyearth.gis.gdal.read.gdal_read_envi_file_multiple_band import gdal_read_envi_file_multiple_band

from pyearth.visual.timeseries.plot_time_series_data import plot_time_series_data


sPath_pye3sm = sWorkspace_code +  slash + 'python' + slash + 'e3sm' + slash + 'e3sm_python'
 
from e3sm.shared import oE3SM
from e3sm.shared.e3sm_read_configuration_file import e3sm_read_configuration_file

def h2sc_evaluate_water_table_depth_sensitivity_to_shape_parameter(sFilename_configuration_in, \
                                               aCase_index,\
                                               aParameter,\
                                               iYear_start_in = None, \
                                               iYear_end_in =None,\
                                               dMin_in = None, \
                                               dMax_in = None, \
                                               dMin_x_in = None, \
                                               dMax_x_in = None, \
                                               dSpace_x_in = None, \
                                               sDate_in = None, \
                                               sLabel_x_in = None, \
                                               sLabel_y_in = None, \
                                               aLabel_legend_in = None, \
                                               sTitle_in=None):

    iCase_index = aCase_index[0]
    e3sm_read_configuration_file(sFilename_configuration_in,\
                                 iCase_index_in = iCase_index, \
                                 iYear_start_in = iYear_start_in,\
                                 iYear_end_in = iYear_end_in,\
                                 sDate_in= sDate_in)

    sModel = oE3SM.sModel
    sRegion = oE3SM.sRegion
    sCase = oE3SM.sCase
    sVariable = oE3SM.sVariable
    #create folder for this variable
    sWorkspace_analysis_variable = oE3SM.sWorkspace_analysis + slash + sVariable.lower()
    if not os.path.exists(sWorkspace_analysis_variable):
        os.makedirs(sWorkspace_analysis_variable)
    #read obs 
    sFilename_mask = sWorkspace_data + slash \
        + 'h2sc' + slash +  sRegion + slash + 'raster' + slash + 'dem' + slash \
        + 'MOSART_Global_half_20180606c.chang_9999.nc'
    #read in mask
    aDatasets = Dataset(sFilename_mask)
    netcdf_format = aDatasets.file_format
    print(netcdf_format)
    print("Print dimensions:")
    print(aDatasets.dimensions.keys())
    print("Print variables:")
    print(aDatasets.variables.keys())
    for sKey, aValue in aDatasets.variables.items():
        if "ele0" == sKey:
            aEle0 = (aValue[:]).data
            break
    aMask = np.where(aEle0 == missing_value)
    aMask1 = np.where(aEle0 != missing_value)


    ncase = len(aCase_index)
    sWorkspace_analysis_grid = sWorkspace_analysis_variable + slash + 'tsplot_sa'
    if not os.path.exists(sWorkspace_analysis_grid):
        os.makedirs(sWorkspace_analysis_grid)
    sFilename_out = sWorkspace_analysis_grid + slash + 'amazon_wtd_sa_' + sPrefix+'.png'
    #we build a multiple ts plot
    #build date
    aDate_sim = list()
    nyear = iYear_end - iYear_start + 1
    for iYear in range(iYear_start, iYear_end + 1):
        for iMonth in range(1,13):
            dSimulation = datetime.datetime(iYear, iMonth, 15)
            aDate_sim.append( dSimulation )
            #do the subset
            #convert date to juliday

    #lJulian_start = gcal2jd(iYear_start, 1, 1)
    iYear_subset_start = 2000
    iYear_subset_end = 2008
    iMonth = 1
    subset_index_start = (iYear_subset_start-iYear_start) * 12 + iMonth-1
    subset_index_end = (iYear_subset_end+1-iYear_start) * 12 + iMonth-1
    subset_index = np.arange( subset_index_start,subset_index_end, 1 )
    aDate_sim = np.array(aDate_sim)
    aDate_sim_subset = aDate_sim[subset_index]
    
    iMonth = 1
    nstress = (iYear_subset_end-iYear_subset_start+1) * 12
    aData_ts = np.full( (ncase, nstress), np.nan, dtype=float)
    dLongitude = -60.2
    dLatitude = -2.6
    lColumn = int((dLongitude - (-180)) / 0.5 )
    lRow = int( (90 - (dLatitude)) / 0.5 )
    for iCase in np.arange(1, ncase+1):
        iCase_index = iCase
        e3sm_read_configuration_file(sFilename_configuration_in,\
                                 iCase_index_in = iCase_index, \
                                 iYear_start_in = iYear_start_in,\
                                 iYear_end_in = iYear_end_in,\
                                 sDate_in = sDate_in)

        #read simulated 
        sWorkspace_analysis_case = oE3SM.sWorkspace_analysis_case
        sVariable = oE3SM.sVariable.lower()
        sWorkspace_analysis_case_variable = sWorkspace_analysis_case + slash + sVariable
        sWorkspace_variable_dat = sWorkspace_analysis_case + slash + sVariable.lower() +    slash + 'dat'
        #read the stack data
    
        sFilename = sWorkspace_variable_dat + slash + sVariable.lower()  + sExtension_envi
    
        aData_all = gdal_read_envi_file_multiple_band(sFilename)
        aVariable_all = aData_all[0]
    
    
    
        aVariable_all1 = aVariable_all[subset_index,lRow,lColumn]
        aData_ts[iCase-1] = aVariable_all1
        
    #plot

    

    aTime_all=[aDate_sim_subset, aDate_sim_subset, aDate_sim_subset]
    aData_all=aData_ts
    plot_time_series_data(aTime_all, aData_all, \
                                  sFilename_out,\
                                  iDPI_in = None,\
                                  iReverse_y_in = 1, \
                                  iSize_x_in = None, \
                                  iSize_y_in = None, \
                                  dMax_y_in =3, \
                                  dMin_y_in = 0, \
                                  dSpace_y_in=1,\
                                  aMarker_in =None,\
                                aColor_in =None,\
                                aLinestyle_in =None,\
                                  sLabel_y_in = None, \
                                  aLabel_legend_in = aLabel_legend_in,\
                                  sTitle_in = None)


    


if __name__ == "__main__":

    iFlag_debug = 1
    if iFlag_debug == 1:
        iIndex_start = 1
        iIndex_end = 7
    else:
        parser = argparse.ArgumentParser()
        parser.add_argument("--iIndex_start", help = "the path",   type = int)
        parser.add_argument("--iIndex_end", help = "the path",   type = int)
        pArgs = parser.parse_args()
        iIndex_start = pArgs.iIndex_start
        iIndex_end = pArgs.iIndex_end

    sModel = 'h2sc'
    sRegion = 'global'
    sDate = '20200421'

    iYear_start = 1980
    iYear_end = 2008



    sVariable = 'zwt'
    sFilename_configuration = sWorkspace_configuration + slash + sModel + slash \
        + sRegion + slash + 'h2sc_configuration_' + sVariable.lower() + sExtension_txt


    sLabel = 'Water table depth (m)'


  

    iCase_index_start = iIndex_start
    iCase_index_end = iIndex_end
    aCase_index = np.arange(iCase_index_start, iCase_index_end + 1, 1)

    #iCase_index = 240
    #for iCase_index in (aCase_index):
    #aCase_index=[5,6, 1]
    #aParameter=[0.25, 0.75, 0.9]
    #sPrefix  = 'K1'
    aCase_index=[2,4, 3]
    aParameter=[0.25, 0.5, 0.75]
    sPrefix  = 'K2'
    #build legend
    
    aLabel_legend=np.full( len(aParameter), '', dtype=object )

    for i in np.arange( len(aParameter) ):
        dummy= sPrefix + ' = ' + '{:0.2f}'.format(aParameter[i])
        aLabel_legend[i]=dummy
    
    h2sc_evaluate_water_table_depth_sensitivity_to_shape_parameter(sFilename_configuration,\
                                                   aCase_index,\
                                                       aParameter,\
                                                   iYear_start_in = iYear_start, \
                                                   iYear_end_in = iYear_end,\
                                                   sDate_in = sDate,\
                                                   aLabel_legend_in = aLabel_legend )

    print('finished')
