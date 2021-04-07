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

from pye3sm.elm.general.halfdegree.plot.elm_tsplot_variable_halfdegree_domain import elm_tsplot_variable_halfdegree_domain

from ..shared.pye3sm_read_configuration_file import pye3sm_read_e3sm_configuration_file
from ..shared.pye3sm_read_configuration_file import pye3sm_read_case_configuration_file

def h2sc_tsplot_variable_halfdegree_domain(oE3SM_in, \
    oCase_in, \
                                           dMax_y_in = None,\
                                           dMin_y_in= None ,\
                                               dSpace_y_in = None ):

    elm_tsplot_variable_halfdegree_domain(oE3SM_in, \
        oCase_in, \
                                          dMax_y_in = dMax_y_in,\
                                          dMin_y_in = dMin_y_in,\
                                              dSpace_y_in = dSpace_y_in)

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

    iFlag_same_grid = 1

    sDate = '20200924'
    sDate = '20201214'
    sDate = '20210108'


    iYear_start = 1979
    iYear_end = 2008
    iYear_subset_start = 2000
    iYear_subset_end = 2008

    sVariable = 'qdrai'
    #sVariable = 'wt_slp'
    sVariable='zwt'
    sVariable='gage_height'
    #sVariable = 'RAIN'
    #sVariable = 'SNOW'
    #sVariable = 'QSOIL'
    #sVariable = 'QVEGE'
    #sVariable = 'QVEGT'
    #sVariable = 'QDRAI'
    #sVariable = 'QOVER'
    
    sLabel_y = r'Water table slope'
    #sLabel_y = r'Rain (mm/s)'
    sLabel_y = r'Water table depth (m)'
    #sLabel_y = r'Soil evaporation (mm/s)'
    #sLabel_y = r'Vegetation evaporation (mm/s)'
    #sLabel_y = r'Vegetation transpiration (mm/s)'

    #sLabel_y = r'Overland runoff (mm/s)'
    #sLabel_y =   r'Drainage ($mm \times s^{-1}$)'
    sLabel_y = r'Gage height (m)'
    iCase_index_start = iIndex_start
    iCase_index_end = iIndex_end
    aCase_index = np.arange(iCase_index_start, iCase_index_end + 1, 1)

    
    sFilename_e3sm_configuration = '/qfs/people/liao313/workspace/python/e3sm/pye3sm/pye3sm/shared/e3sm.xml'
    sFilename_case_configuration = '/qfs/people/liao313/workspace/python/e3sm/pye3sm/pye3sm/shared/case.xml'

    aParameter_e3sm = pye3sm_read_e3sm_configuration_file(sFilename_e3sm_configuration)

    oE3SM = pye3sm(aParameter_e3sm)
    for iCase_index in (aCase_index):
     
        dConversion = 1.0
        aParameter_case  = pye3sm_read_case_configuration_file(sFilename_case_configuration,\
                                                               iCase_index_in =  iCase_index ,\
                                                               iFlag_same_grid_in = iFlag_same_grid, \
                                                               iYear_start_in = iYear_start, \
                                                               iYear_end_in = iYear_end,\
                                                               iYear_subset_start_in = iYear_subset_start, \
                                                               iYear_subset_end_in = iYear_subset_end, \
                                                                   dConversion_in = dConversion,\
                                                               sDate_in= sDate,\
                                                               sLabel_y_in =  sLabel_y, \
                                                               sVariable_in = sVariable )

        oCase = pycase(aParameter_case)

        dMin_y = 0
        dMax_y = 10
        dSpace_y = 5        

        h2sc_tsplot_variable_halfdegree_domain(oE3SM, \
                                                 oCase,\
                                                 dMin_y_in = dMin_y, \
                                                 dMax_y_in = dMax_y, \
                                                 dSpace_y_in = dSpace_y)

    print('finished')
