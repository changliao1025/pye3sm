#this script should be run using Python 2.7.8 instead of Python 3
#module load python/2.7.8
#maybe I was wrong? 20200305 Chang Liao (chang.liao@pnnl.gov)

import os, sys
import argparse
import numpy as np


sSystem_paths = os.environ['PATH'].split(os.pathsep)
sys.path.extend(sSystem_paths)

from pyes.system.define_global_variables import *

sPath_pye3sm = sWorkspace_code +  slash + 'python' + slash + 'e3sm' + slash + 'e3sm_python'
sys.path.append(sPath_pye3sm)
from e3sm.elm.general.halfdegree.plot.elm_3dtsplot_variable_halfdegree_domain import elm_3dtsplot_variable_halfdegree_domain

def h2sc_3dtsplot_variable_halfdegree_domain(sFilename_configuration, \
                                             iCase_index,\
                                             iYear_start_in = None, \
                                             iYear_end_in =None,\
                                             iYear_subset_start_in = None, \
                                             iYear_subset_end_in = None,\
                                             dMin_x_in = None, \
                                             dMax_x_in = None, \
                                             dMin_z_in = None, \
                                             dMax_z_in = None, \
                                             dSpace_x_in = None, \
                                             dSpace_z_in = None, \
                                             sDate_in = None,\
                                             sLabel_x_in =None, \
                                             sLabel_z_in=None):

    elm_3dtsplot_variable_halfdegree_domain(sFilename_configuration,\
                                            iCase_index, \
                                            iFlag_same_grid_in = 1,\
                                            iYear_start_in = iYear_start_in,\
                                            iYear_end_in = iYear_end_in,\
                                            iYear_subset_start_in = iYear_subset_start_in, \
                                            iYear_subset_end_in =iYear_subset_end_in,\
                                            dMin_z_in = dMin_z_in, \
                                            dMax_z_in = dMax_z_in, \
                                            dSpace_x_in = dSpace_x_in, \
                                            dSpace_z_in = dSpace_z_in, \
                                            sDate_in = sDate_in,\
                                            sLabel_x_in =sLabel_x_in, \
                                            sLabel_z_in=sLabel_z_in)

if __name__ == '__main__':
    iFlag_debug = 1
    if iFlag_debug == 1:
        iIndex_start = 1
        iIndex_end = 1
    else:
        parser = argparse.ArgumentParser()
        parser.add_argument("--iIndex_start", help = "the path",   type = int)
        parser.add_argument("--iIndex_end", help = "the path",   type = int)
        pArgs = parser.parse_args()
        iIndex_start = pArgs.iIndex_start
        iIndex_end = pArgs.iIndex_end

    sModel = 'h2sc'
    sRegion = 'global'
    sDate = '20200413'



    iYear_start = 1980
    iYear_end = 2008
    sVariable='zwt'
    #sVariable = 'drainage'
    #sVariable = 'wt_slp'

    sFilename_configuration = sWorkspace_configuration + slash \
        + sModel + slash \
        + sRegion + slash + 'h2sc_configuration_' + sVariable.lower() + sExtension_txt
    iCase_index_start = iIndex_start
    iCase_index_end = iIndex_end
    aCase_index = np.arange(iCase_index_start, iCase_index_end + 1, 1)

        #iCase_index = 240
    for iCase_index in (aCase_index):
        h2sc_3dtsplot_variable_halfdegree_domain(sFilename_configuration, \
                                                 iCase_index,\
                                                 iYear_start_in = iYear_start, \
                                                 iYear_end_in =iYear_end,\
                                                 iYear_subset_start_in = 1990, \
                                                 iYear_subset_end_in =2008,\

    dMin_z_in = 0, \
                                                 dMax_z_in = 80, \
                                                 dSpace_z_in = 10, \
                                                 sDate_in= sDate, \
                                                 sLabel_x_in = 'Year',\
                                                 sLabel_z_in = 'Water table depth (m)')

    print('finished')
