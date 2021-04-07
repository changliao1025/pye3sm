import os, sys
import argparse
import numpy as np


sSystem_paths = os.environ['PATH'].split(os.pathsep)
 

import pyearth
from pyearth.system.define_global_variables import *

 
 

import pye3sm
from ..shared.e3sm import pye3sm
from ..shared.case import pycase
from ..shared.pye3sm_read_configuration_file import pye3sm_read_e3sm_configuration_file
from ..shared.pye3sm_read_configuration_file import pye3sm_read_case_configuration_file
from pye3sm.elm.general.halfdegree.stats.elm_time_series_analysis_trend_variable_halfdegree_domain import elm_time_series_analysis_trend_variable_halfdegree_domain
def h2sc_calculate_time_series_trend(oE3SM_in, oCase_in):

    elm_time_series_analysis_trend_variable_halfdegree_domain(oE3SM_in, oCase_in)

    return
if __name__ == '__main__':
    iFlag_debug = 1
    if iFlag_debug == 1:
        iIndex_start = 9
        iIndex_end = 9
    else:
        parser = argparse.ArgumentParser()
        parser.add_argument("--iIndex_start", help = "the path",   type = int)
        parser.add_argument("--iIndex_end", help = "the path",   type = int)
        pArgs = parser.parse_args()
        iIndex_start = pArgs.iIndex_start
        iIndex_end = pArgs.iIndex_end

    iFlag_same_grid = 1
    sModel = 'h2sc'
    sRegion = 'global'
    sDate = '20200924'
    sVariable = 'zwt'


    iYear_start = 1979
    iYear_end = 2008


    iCase_index_start = iIndex_start
    iCase_index_end = iIndex_end
    aCase_index = np.arange(iCase_index_start, iCase_index_end + 1, 1)

    #iCase_index = 240
    sFilename_e3sm_configuration = '/qfs/people/liao313/workspace/python/e3sm/pye3sm/pye3sm/shared/e3sm.xml'
    sFilename_case_configuration = '/qfs/people/liao313/workspace/python/e3sm/pye3sm/pye3sm/shared/case.xml'

    aParameter_e3sm = pye3sm_read_e3sm_configuration_file(sFilename_e3sm_configuration)

    oE3SM = pye3sm(aParameter_e3sm)
    for iCase_index in (aCase_index):

        aParameter_case  = pye3sm_read_case_configuration_file(sFilename_case_configuration,\
                                                               iCase_index_in =  iCase_index ,\
                                                               iYear_subset_start_in = 2000, \
                                                               iYear_subset_end_in =2008,\
                                                               iFlag_same_grid_in = iFlag_same_grid, \
                                                               iYear_start_in = iYear_start, \
                                                               iYear_end_in =iYear_end,\
                                                               sDate_in= sDate,\
                                                               sVariable_in = sVariable)

        oCase = pycase(aParameter_case)

        elm_time_series_analysis_trend_variable_halfdegree_domain(oE3SM,  oCase     )

    print('finished')
