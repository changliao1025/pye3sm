import os, sys, stat
import argparse
import subprocess
import numpy as np
sSystem_paths = os.environ['PATH'].split(os.pathsep)
 
from pyearth.system.define_global_variables import *

 
 
from ..shared.e3sm import pye3sm
from ..shared.case import pycase
from ..shared.pye3sm_read_configuration_file import pye3sm_read_e3sm_configuration_file
from ..shared.pye3sm_read_configuration_file import pye3sm_read_case_configuration_file

#evaluate mosart stream discharge
def mosart_evaluate_stream_discharge_gsim(oE3SM_in, oCase_in, lIndex_grid, sFilename_gsim):

    # do we specify the location by lat/lon

    #the gsim file to be read
    #the location of the grid

    #read the time series mosat output at the grid
    #generate the time series plot using the pyearth library

    
    return


if __name__ == '__main__':
    iFlag_debug = 1
    if iFlag_debug == 1:
        iIndex_start = 3
        iIndex_end = 3
    else:
        parser = argparse.ArgumentParser()        
        parser.add_argument("--iIndex_start", help = "the path",   type = int)      
        parser.add_argument("--iIndex_end", help = "the path",   type = int)          
        pArgs = parser.parse_args()       
        iIndex_start = pArgs.iIndex_start
        iIndex_end = pArgs.iIndex_end
    
    sModel = 'h2sc'
    sRegion = 'global'
    
    sDate = '20210209'

    iYear_start = 1979
    iYear_end = 2008

    sVariable = 'zwt'
    sFilename_configuration = sWorkspace_configuration + slash + sModel + slash \
        + sRegion + slash + 'h2sc_configuration_' + sVariable.lower() + sExtension_txt

    iCase_index_start = iIndex_start
    iCase_index_end = iIndex_end
    aCase_index = np.arange(iCase_index_start, iCase_index_end + 1, 1)

        #iCase_index = 240       
    for iCase_index in (aCase_index):
        aParameter_case  = pye3sm_read_case_configuration_file(sFilename_case_configuration,\
                                                               iCase_index_in =  iCase_index ,\
                                                               iFlag_same_grid_in = iFlag_same_grid, \
                                                               iYear_start_in = iYear_start, \
                                                               iYear_end_in = iYear_end,\
                                                               iYear_subset_start_in = iYear_subset_start, \
                                                               iYear_subset_end_in = iYear_subset_end, \
                                                               sDate_in= sDate,\
                                                               sLabel_y_in =  sLabel_y, \
                                                               sVariable_in = sVariable )

        oCase = pycase(aParameter_case)

        dMin_y = -6
        dMax_y = -3
        dSpace_y = 1        

        mosart_evaluate_stream_discharge_gsim(oE3SM, \
                                                 oCase,\
                                                 dMin_y_in = dMin_y, \
                                                 dMax_y_in = dMax_y, \
                                                 dSpace_y_in = dSpace_y)

    print('finished')