import os, sys
import argparse
import numpy as np
from netCDF4 import Dataset #it maybe be replaced by gdal 

sSystem_paths = os.environ['PATH'].split(os.pathsep)
 

from pyearth.system.define_global_variables import *
from pyearth.gis.gdal.read.gdal_read_geotiff_file import gdal_read_geotiff_file, gdal_read_geotiff_file_multiple_band


from pyearth.visual.histogram.histogram_plot import histogram_plot
from pyearth.visual.histogram.histogram_plot_multiple import histogram_plot_multiple



 
 
from ..shared.e3sm import pye3sm
from ..shared.case import pycase
from pye3sm.elm.general.halfdegree.save.elm_save_variable_halfdegree import elm_save_variable_halfdegree
from ..shared.pye3sm_read_configuration_file import pye3sm_read_e3sm_configuration_file
from ..shared.pye3sm_read_configuration_file import pye3sm_read_case_configuration_file

def h2sc_evaluate_water_table_depth_halfdegree(oE3SM_in, \
                                               oCase_in,\
                                               iYear_start_in = None, \
                                               iYear_end_in = None,\
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

   

    sModel = oCase_in.sModel
    sRegion = oCase_in.sRegion
    sCase = oCase_in.sCase
    iYear_start = oCase_in.iYear_start

    iYear_end = oCase_in.iYear_end

    iYear_subset_start = oCase_in.iYear_subset_start

    iYear_subset_end = oCase_in.iYear_subset_end
    #read obs 
    sFilename_mask = oCase_in.sFilename_mask
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


    sFilename_wtd = sWorkspace_data + slash + sModel + slash + sRegion + slash + 'raster' + slash \
    + 'wtd' + slash + 'wtd.tif'

    pWTD = gdal_read_geotiff_file(sFilename_wtd)
    aWTD_obs = pWTD[0]


    #read simulated 
    sWorkspace_analysis_case = oCase_in.sWorkspace_analysis_case
    sVariable = oCase_in.sVariable
    sWorkspace_analysis_case_variable = sWorkspace_analysis_case + slash + sVariable
    sWorkspace_variable_dat = sWorkspace_analysis_case + slash + sVariable.lower() +    slash + 'tiff'
    #read the stack data

    sFilename = sWorkspace_variable_dat + slash + sVariable.lower()  + sExtension_tiff

    aData_all = gdal_read_geotiff_file_multiple_band(sFilename)

    aVariable_all = aData_all[0]
    
   
    iMonth = 1


    #iMonth = 1
    index_start = (iYear_subset_start - iYear_start)* 12 + iMonth - 1
    index_end = (iYear_subset_end + 1 - iYear_start)* 12 + iMonth - 1
    subset_index = np.arange(index_start , index_end , 1 )

    #take average
    aVariable_all1 = aVariable_all[ subset_index,:,:]
    aVariable_all2 = np.mean(  aVariable_all1, axis= 0 )

    #plot kde distribution 

    #now we will remove the high latitudes due to the frozen soil issue.
    nCutoff = 45
    iStart= int(nCutoff/0.5)
    iEnd = 360 - iStart
    aWTD_obs = aWTD_obs[iStart:iEnd,:]

    aMask1 = np.where(aWTD_obs != missing_value)
    aData_a = aWTD_obs[aMask1]
    #sim
    aVariable_all2 = aVariable_all2[iStart:iEnd,:]
    aMask1 = np.where(aVariable_all2 != missing_value )


    aData_b = aVariable_all2[aMask1]
    aMask2 = np.where( (aData_b < 8.8) | (aData_b >8.9) )    
    aData_b = aData_b[aMask2]
    


    sWorkspace_analysis_case_grid = sWorkspace_analysis_case_variable + slash + 'histogram'
    if not os.path.exists(sWorkspace_analysis_case_grid):
        os.makedirs(sWorkspace_analysis_case_grid)
        pass 


    sFilename_out = sWorkspace_analysis_case_grid + slash + sCase + '_wtd_histogram.png'

    #histogram_plot( aData_a,\
    #        sFilename_out, \
    #        iSize_x_in = 12, \
    #        iSize_y_in = 5, \
    #        iDPI_in = 150, \
    #        dMin_in = dMin_in, \
    #        dMax_in = dMax_in, \
    #        dMin_x_in = dMin_x_in, \
    #        dMax_x_in = dMax_x_in, \
    #        dSpace_x_in = dSpace_x_in, \
    #        sLabel_x_in = sLabel_x_in, \
    #        sLabel_y_in = sLabel_y_in, \
    #        sTitle_in = sTitle_in)
    histogram_plot_multiple( aData_a, aData_b,\
            sFilename_out, \
            iSize_x_in = 12, \
            iSize_y_in = 5, \
            iDPI_in = 150, \
            dMin_in = dMin_in, \
            dMax_in = dMax_in, \
            dMin_x_in = dMin_x_in, \
            dMax_x_in = dMax_x_in, \
            dSpace_x_in = dSpace_x_in, \
            
            sLabel_x_in = sLabel_x_in, \
            sLabel_y_in = sLabel_y_in, \
            aLabel_legend_in = aLabel_legend_in, \
            sTitle_in = sTitle_in)
    

    

if __name__ == '__main__':
    iFlag_debug = 1
    if iFlag_debug == 1:
        iIndex_start = 9
        iIndex_end = 9
        pass
    else:
        parser = argparse.ArgumentParser()
        parser.add_argument("--iIndex_start", help = "the path",   type = int)
        parser.add_argument("--iIndex_end", help = "the path",   type = int)
        pArgs = parser.parse_args()
        iIndex_start = pArgs.iIndex_start
        iIndex_end = pArgs.iIndex_end
        pass

    sModel = 'h2sc'
    sRegion = 'global'
    sDate = '20200924'

    iYear_start = 1979
    iYear_end = 2008

    sVariable = 'zwt'  


    sLabel = 'Water table depth (m)'


    aLabel_legend = ['Observed WTD','Simulated WTD' ]

    iCase_index_start = iIndex_start
    iCase_index_end = iIndex_end
    aCase_index = np.arange(iCase_index_start, iCase_index_end + 1, 1)

    sFilename_e3sm_configuration = '/qfs/people/liao313/workspace/python/e3sm/pye3sm/pye3sm/shared/e3sm.xml'
    sFilename_case_configuration = '/qfs/people/liao313/workspace/python/e3sm/pye3sm/pye3sm/shared/case.xml'

    aParameter_e3sm = pye3sm_read_e3sm_configuration_file(sFilename_e3sm_configuration)
    print(aParameter_e3sm)
    oE3SM = pye3sm(aParameter_e3sm)


    for iCase_index in (aCase_index):
        aParameter_case  = pye3sm_read_case_configuration_file(sFilename_case_configuration,\
                                                           iCase_index_in =  iCase_index ,\
                                                           iYear_start_in = iYear_start, \
                                                           iYear_end_in = iYear_end,\
    iYear_subset_start_in = 1990, \
                                                               iYear_subset_end_in =2008,\

                                                           sDate_in= sDate,\
                                                           sVariable_in = sVariable )
    #print(aParameter_case)
        oCase = pycase(aParameter_case)
        h2sc_evaluate_water_table_depth_halfdegree(oE3SM,\
                                                   oCase,\
                                                  
                                                   dMin_in = 0, \
                                                   dMax_in = 60, \
                                                   dMin_x_in = 0, \
                                                   dMax_x_in = 60, \
                                                   dSpace_x_in = 0.5, \
                                                   sDate_in= sDate, \
                                                sLabel_x_in=sLabel,\
                                                #sLabel_y_in='Distribution [%]',\
                                                   #aLabel_legend_in = aLabel_legend,\
                                                   )

    print('finished')
