#this script should be run using Python 2.7.8 instead of Python 3
#module load python/2.7.8
#maybe I was wrong? 20200305 Chang Liao (chang.liao@pnnl.gov)

import os, sys
import argparse
import numpy as np


sSystem_paths = os.environ['PATH'].split(os.pathsep)
sys.path.extend(sSystem_paths)

from pyes.system.define_global_variables import *

sPath_pye3sm = sWorkspace_code +  slash + 'python' + slash + 'e3sm' + slash + 'pye3sm'
sys.path.append(sPath_pye3sm)
from pye3sm.shared.e3sm import pye3sm
from pye3sm.shared.case import pycase
from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_e3sm_configuration_file
from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_case_configuration_file
from pye3sm.elm.general.halfdegree.plot.elm_3dtsplot_variable_halfdegree_domain import elm_3dtsplot_variable_halfdegree_domain

def h2sc_3dtsplot_variable_halfdegree_domain(oE3SM_in, \
                                             oCase_in,\
                                           
                                             dMin_x_in = None, \
                                             dMax_x_in = None, \
                                             dMin_z_in = None, \
                                             dMax_z_in = None, \
                                             dSpace_x_in = None, \
                                             dSpace_z_in = None, \
                                             sLabel_x_in =None, \
                                             sLabel_z_in=None):

    elm_3dtsplot_variable_halfdegree_domain(oE3SM_in,\
                                            oCase_in, \
                                            dMin_z_in = dMin_z_in, \
                                            dMax_z_in = dMax_z_in, \
                                            dSpace_x_in = dSpace_x_in, \
                                            dSpace_z_in = dSpace_z_in, \
                                            sLabel_x_in =sLabel_x_in, \
                                            sLabel_z_in=sLabel_z_in)

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
    sVariable='zwt'
    sVariable = 'qdrai'
    #sVariable = 'wt_slp'

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

        dMin_z = -6
        dMax_z = -3
        dSpace_z = 1
        sLabel_z =   'Drainage (log10) (mm/s)'
        h2sc_3dtsplot_variable_halfdegree_domain(oE3SM, \
                                                 oCase,\
                                                 dMin_z_in = dMin_z, \
                                                 dMax_z_in = dMax_z, \
                                                 dSpace_z_in = dSpace_z,\
                                                 sLabel_x_in = 'Year',\
                                                 sLabel_z_in = sLabel_z)

    print('finished')
