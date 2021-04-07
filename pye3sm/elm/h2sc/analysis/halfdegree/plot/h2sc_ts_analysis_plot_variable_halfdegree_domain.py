#this script should be run using Python 2.7.8 instead of Python 3
#module load python/2.7.8
#maybe I was wrong? 20200305 Chang Liao (chang.liao@pnnl.gov)

import os, sys
import argparse
import numpy as np


sSystem_paths = os.environ['PATH'].split(os.pathsep)
 

from pyearth.system.define_global_variables import *

 
 
from ..shared.e3sm import pye3sm
from ..shared.case import pycase
from ..shared.pye3sm_read_configuration_file import pye3sm_read_e3sm_configuration_file
from ..shared.pye3sm_read_configuration_file import pye3sm_read_case_configuration_file
from pye3sm.elm.general.halfdegree.plot.elm_ts_analysis_plot_variable_halfdegree_domain import elm_ts_analysis_plot_variable_halfdegree_domain

def h2sc_ts_analysis_plot_variable_halfdegree_domain(oE3SM_in, \
                                             oCase_in,\
                                             iFlag_log_in = None,\
                                             dMin_x_in = None, \
                                             dMax_x_in = None, \
                                             dMin_y_in = None, \
                                             dMax_y_in = None, \
                                             dSpace_x_in = None, \
                                             dSpace_y_in = None, \
                                             sLabel_x_in =None, \
                                             sLabel_y_in=None):

    elm_ts_analysis_plot_variable_halfdegree_domain(oE3SM_in,\
                                            oCase_in, \
                                            iFlag_log_in = iFlag_log_in,\
                                            dMin_y_in = dMin_y_in, \
                                            dMax_y_in = dMax_y_in, \
                                            dSpace_x_in = dSpace_x_in, \
                                            dSpace_y_in = dSpace_y_in, \
                                            sLabel_x_in =sLabel_x_in, \
                                            sLabel_y_in=sLabel_y_in)

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

    sModel = 'h2sc'
    sRegion = 'global'
    sDate = '20200924'



    iYear_start = 1979
    iYear_end = 2008
    

    sFilename_e3sm_configuration = '/qfs/people/liao313/workspace/python/e3sm/pye3sm/pye3sm/shared/e3sm.xml'
    sFilename_case_configuration = '/qfs/people/liao313/workspace/python/e3sm/pye3sm/pye3sm/shared/case.xml'

    aParameter_e3sm = pye3sm_read_e3sm_configuration_file(sFilename_e3sm_configuration)
    print(aParameter_e3sm)
    oE3SM = pye3sm(aParameter_e3sm)

    iCase_index_start = iIndex_start
    iCase_index_end = iIndex_end
    aCase_index = np.arange(iCase_index_start, iCase_index_end + 1, 1)


        #iCase_index = 240
    for iCase_index in (aCase_index):
        sVariable = 'zwt'
        #sVariable = 'qdrai'
        sLabel_y = r'Water table depth (m)'
        #sLabel_y = r'Drainage ($mm s^{-1}$)'
        dMin_y = 0
        dMax_y= 40
        dMin_y = 0
        dMax_y= 40
        #dMin_y = -6
        #dMax_y= -3
        dSpace_x = 2
        dSpace_y = 10
        iFlag_log = 0
        aParameter_case  = pye3sm_read_case_configuration_file(sFilename_case_configuration,\
                                                               iCase_index_in =  iCase_index ,\
                                                               iYear_start_in = iYear_start, \
                                                               iYear_end_in = iYear_end,\
                                                               iYear_subset_start_in = 2000, \
                                                               iYear_subset_end_in =2008,\
                                                               sDate_in= sDate,\
                                                               sVariable_in = sVariable )
        #print(aParameter_case)
        oCase  = pycase(aParameter_case)
        h2sc_ts_analysis_plot_variable_halfdegree_domain(oE3SM, \
                                                 oCase,\
                                                 iFlag_log_in = iFlag_log,\
                                                 dMin_y_in = dMin_y, \
                                                 dMax_y_in = dMax_y, \
                                                 dSpace_y_in = dSpace_y, \
                                                 sLabel_x_in = 'Year',\
                                                 sLabel_y_in = sLabel_y)

    print('finished')
