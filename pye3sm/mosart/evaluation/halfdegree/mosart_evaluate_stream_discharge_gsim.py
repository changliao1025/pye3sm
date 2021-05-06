import os, sys
import numpy as np
import datetime

from pyearth.system.define_global_variables import *
from pyearth.gis.gdal.read.gdal_read_geotiff_file import gdal_read_geotiff_file_multiple_band
from pyearth.toolbox.reader.text_reader_string import text_reader_string
from pyearth.visual.timeseries.plot_time_series_data import plot_time_series_data

from pye3sm.tools.gsim.read_gsim_data import read_gsim_data

#evaluate mosart stream discharge
def mosart_prepare_outlet_coordinates_with_gsim_filenames(sFilename_mosart_gsim_info, iSkipline_in=1):
    """
    extract global outlet indicex for gsim evaluation
    """
    #read the text file
    data_all = text_reader_string(sFilename_mosart_gsim_info, iSkipline_in=1)
    aBasin = data_all[:, 0]
    aFilename_gsim = data_all[:, 1]

    aLon = data_all[:, 2]
    aLon = aLon.astype(np.float)

    aLat =  data_all[:, 3]
    aLat = aLat.astype(np.float)
    
    aID = data_all[:, 4]
    aID = aID.astype(np.long)
    
    

    return aBasin, aLat, aLon, aID, aFilename_gsim

    return

def mosart_evaluate_stream_discharge_gsim(oE3SM_in, \
                                          oCase_in, \
                                              sFilename_mosart_gsim_info):

    """
    evaluate the mosart discharge using the gsim dataset
    """


    #read the time series mosat output at the grid
    sModel = oCase_in.sModel
    sRegion = oCase_in.sRegion
    iFlag_same_grid = oCase_in.iFlag_same_grid
    iYear_start = oCase_in.iYear_start
    iYear_end = oCase_in.iYear_end

    iYear_subset_start = oCase_in.iYear_subset_start
    iYear_subset_end = oCase_in.iYear_subset_end

    sLabel_Y = oCase_in.sLabel_y
    dConversion = oCase_in.dConversion
    sVariable = oCase_in.sVariable
    sCase = oCase_in.sCase
    sWorkspace_simulation_case_run = oCase_in.sWorkspace_simulation_case_run
    sWorkspace_analysis_case = oCase_in.sWorkspace_analysis_case
    sWorkspace_variable_data = sWorkspace_analysis_case + slash + sVariable +  slash + 'tiff'

    nrow = 360
    ncolumn = 720
    #the gsim file to be read
    #read basin mask
    
    dates = list()
    nyear = iYear_end - iYear_start + 1
    for iYear in range(iYear_start, iYear_end + 1):
        for iMonth in range(1,13):
            dSimulation = datetime.datetime(iYear, iMonth, 15)
            dates.append( dSimulation )

    nstress = nyear * nmonth
    #take the subset
    iMonth = 1
    subset_index_start = (iYear_subset_start - iYear_start) * 12 + iMonth-1
    subset_index_end = (iYear_subset_end + 1 - iYear_start) * 12 + iMonth-1
    subset_index = np.arange( subset_index_start,subset_index_end, 1 )


    dates=np.array(dates)
    dates_subset = dates[subset_index]
    nstress_subset= len(dates_subset)

    #read the stack data

    sFilename = sWorkspace_variable_data + slash + sVariable  + sExtension_tiff

    aData_all = gdal_read_geotiff_file_multiple_band(sFilename)
    aVariable_total = aData_all[0]
    aVariable_total_subset = aVariable_total[subset_index,:,:]

    
    sWorkspace_analysis_case_variable = sWorkspace_analysis_case + slash + sVariable
    if not os.path.exists(sWorkspace_analysis_case_variable):
        os.makedirs(sWorkspace_analysis_case_variable)

    sWorkspace_analysis_case_domain = sWorkspace_analysis_case_variable + slash + 'tsplot_domain'
    if not os.path.exists(sWorkspace_analysis_case_domain):
        os.makedirs(sWorkspace_analysis_case_domain)
        pass

    aBasin, aLat, aLon, aID, aFilename_gsim = mosart_prepare_outlet_coordinates_with_gsim_filenames(sFilename_mosart_gsim_info)

    nsite = len(aFilename_gsim)

    sWorkspace_gsim = '/compyfs/liao313/00raw/hydrology/gsim/GSIM_indices/TIMESERIES/monthly'

    for iSite in np.arange(1, nsite+1, 1):
        dLatitude = aLat[iSite-1]
        dLongitude = aLon[iSite-1]
        sFilename_gsim = aFilename_gsim[iSite-1] + '.mon'

        sFilename_gsim =  os.path.join(sWorkspace_gsim, sFilename_gsim) 
        aData = read_gsim_data(sFilename_gsim,iYear_start, iYear_end )


        #the location of the grid


        row_index = int( (90.0-dLatitude)/0.5 )
        column_index =int ((dLongitude + 180.0)/0.5)

        aData_all=[]
        aLabel_legend=[]
        sDomain = aFilename_gsim[iSite-1]
        sLabel_legend = sDomain.title()
        sFilename_out = sWorkspace_analysis_case_domain + slash \
            + sVariable + '_tsplot_' + sDomain +'.png'

        pShape = aVariable_total_subset.shape
        aVariable2 = np.full(nstress_subset, -9999, dtype=float)
        for i in np.arange(0, pShape[0], 1):

            dummy1 = aVariable_total_subset[i,:,:]
            dummy2 = dummy1[ row_index, column_index ]
            #dummy3 =  area[row_index, column_index]
            aVariable2[i] = dummy2 #* dummy3 /1000.0
            pass

        sTitle_in=''
        sLabel_Y=''

        #generate the time series plot using the pyes library
        aDate_all = np.array([dates_subset, dates_subset])
        aData_all = np.array([aVariable2,aData[subset_index] ])
        aLabel_legend=['Modeled river discharge','Observed river discharge']
        plot_time_series_data(aDate_all,
                              aData_all ,\
                              sFilename_out,\
                              iReverse_y_in = 0, \

                              sTitle_in = sTitle_in, \
                              sLabel_y_in= sLabel_Y,\

                              aLabel_legend_in = aLabel_legend, \

                              sLocation_legend_in = 'lower right' ,\
                              aLocation_legend_in = (1.0, 0.0),\

                              iSize_x_in = 12,\
                              iSize_y_in = 5)



    return



