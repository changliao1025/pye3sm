import os, sys
import numpy as np
import datetime

from pyearth.system.define_global_variables import *
from pyearth.gis.gdal.read.gdal_read_geotiff_file import gdal_read_geotiff_file_multiple_band
from pyearth.toolbox.reader.text_reader_string import text_reader_string
from pyearth.visual.timeseries.plot_time_series_data import plot_time_series_data
from pye3sm.mosart.mesh.structured.mosart_retrieve_structured_case_dimension_info import mosart_retrieve_case_dimension_info 

from pye3sm.tools.mosart.gsim.read_gsim_data import read_gsim_data
from pye3sm.mosart.general.structured.twod.retrieve.mosart_retrieve_variable_2d import mosart_retrieve_variable_2d
from pye3sm.mosart.general.mosart_prepare_outlet_coordinates_with_gsim_filenames import mosart_prepare_outlet_coordinates_with_gsim_filenames

def mosart_evaluate_stream_discharge_gsim(oE3SM_in,  oCase_in,  sFilename_mosart_gsim_info):
    """
    Evaluate the mosart discharge using the gsim dataset

    Args:
        oE3SM_in (object): the E3SM class object
        oCase_in (object): the Case class object
        sFilename_mosart_gsim_info (str): The filename of the gsim data
    """

    #read the time series mosat output at the grid
    
    iFlag_same_grid = oCase_in.iFlag_same_grid
    iYear_start = oCase_in.iYear_start
    iYear_end = oCase_in.iYear_end

    iYear_subset_start = oCase_in.iYear_subset_start
    iYear_subset_end = oCase_in.iYear_subset_end

    sLabel_Y = oCase_in.sLabel_y
    dConversion = oCase_in.dConversion
    sVariable = oCase_in.sVariable
    
    sWorkspace_analysis_case = oCase_in.sWorkspace_analysis_case
    sWorkspace_variable_data = sWorkspace_analysis_case + slash + sVariable +  slash + 'tiff'

    
     #new approach
    aLon, aLat , aMask_ll= mosart_retrieve_case_dimension_info(oCase_in)
    #dimension
    aMask_ul = np.flip(aMask_ll, 0)
    nrow = np.array(aMask_ll).shape[0]
    ncolumn = np.array(aMask_ll).shape[1]
    aMask_index_ll = np.where(aMask_ll==0)
    aMask_index_ul = np.where(aMask_ul==0)

    #resolution
    dLon_min = np.min(aLon)
    dLon_max = np.max(aLon)
    dLat_min = np.min(aLat)
    dLat_max = np.max(aLat)
    dResolution_x = (dLon_max - dLon_min) / (ncolumn-1)
    dResolution_y = (dLat_max - dLat_min) / (nrow-1)
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
    subset_index1 = np.arange( subset_index_start,subset_index_end, 1 )
    subset_index2 = np.arange( subset_index_start+1,subset_index_end+1, 1 )

    dates=np.array(dates)
    dates_subset1 = dates[subset_index1]
    dates_subset2 = dates[subset_index2]
    nstress_subset= len(dates_subset1)

    sWorkspace_analysis_case_variable = sWorkspace_analysis_case + slash + sVariable
    if not os.path.exists(sWorkspace_analysis_case_variable):
        os.makedirs(sWorkspace_analysis_case_variable)
    sWorkspace_analysis_case_domain = sWorkspace_analysis_case_variable + slash + 'tsplot'
    if not os.path.exists(sWorkspace_analysis_case_domain):
        os.makedirs(sWorkspace_analysis_case_domain)
        pass

    #read the stack data
    iFlag_monthly=1
    if iFlag_monthly ==1:
        aData_ret = mosart_retrieve_variable_2d( oCase_in, iFlag_monthly_in = 1)
        for i in np.arange(nstress_subset):        
            aVariable_total_subset = aData_ret[subset_index1]


            aBasin, aLat, aLon, aID, aFilename_gsim = mosart_prepare_outlet_coordinates_with_gsim_filenames(sFilename_mosart_gsim_info)

            nsite = len(aFilename_gsim)

            sWorkspace_gsim = '/compyfs/liao313/00raw/hydrology/gsim/GSIM_indices/TIMESERIES/monthly'

            for iSite in np.arange(1, nsite+1, 1):
                dLatitude = aLat[iSite-1]
                dLongitude = aLon[iSite-1]

                if dLatitude >=dLat_min and dLatitude<=dLat_max and dLongitude >=dLon_min and dLongitude<=dLon_max:
                    pass
                else:
                    continue
                sFilename_gsim = aFilename_gsim[iSite-1] + '.mon'

                sFilename_gsim = 'BR_0000244.mon'

                sFilename_gsim =  os.path.join(sWorkspace_gsim, sFilename_gsim) 

                print(sFilename_gsim)
                #continue
                aData = read_gsim_data(sFilename_gsim,iYear_start, iYear_end )


                #the location of the grid


                row_index = int( (dLat_max-dLatitude)/0.5 )
                column_index =int ((dLongitude -dLon_min)/0.5)

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
                aDate_all = np.array([dates_subset1, dates_subset1])
                aData_all = np.array([aVariable2,aData[subset_index2] ])
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



