import os, sys
import argparse
import numpy as np


sSystem_paths = os.environ['PATH'].split(os.pathsep)
sys.path.extend(sSystem_paths)

from eslib.system.define_global_variables import *


sPath_e3sm_python = sWorkspace_code +  slash + 'python' + slash + 'e3sm' + slash + 'e3sm_python'
sys.path.append(sPath_e3sm_python)
from e3sm.elm.general.halfdegree.plot.elm_scatterplot_variables_halfdegree import elm_scatterplot_variables_halfdegree

def h2sc_scatterplot_variables_halfdegree(sFilename_configuration_x, \
    sFilename_configuration_y,\
                                    iCase_index,\
                                    iYear_start_in = None, \
                                    iYear_end_in =None,\
                                         dMin_x_in = None, \
    dMax_x_in = None, \
    dMin_y_in = None, \
    dMax_y_in = None, \
    dSpace_x_in = None, \
    dSpace_y_in = None, \
                                    sDate_in = None,\
                                    sLabel_x_in=None,\
                                        sLabel_y_in=None):
    elm_scatterplot_variables_halfdegree(sFilename_configuration_x,\
        sFilename_configuration_y,\
                                   iCase_index, \
                                   iFlag_same_grid_in = 1,\
                                   iYear_start_in = iYear_start_in,\
                                   iYear_end_in = iYear_end_in,\

                                       dMin_x_in = 0, \
                                         dMax_x_in = dMax_x_in, \
    dMin_y_in = dMin_y_in, \
    dMax_y_in = dMax_y_in, \

    dSpace_x_in = dSpace_x_in, \
    dSpace_y_in = dSpace_y_in, \
                                   sDate_in = sDate_in, \
                                   sLabel_x_in = sLabel_x_in, \
                                       sLabel_y_in= sLabel_y_in)

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
    sDate = '20200421'

    iYear_start = 1980
    iYear_end = 2008

    sVariable = 'sur_slp'
    sFilename_configuration_x = sWorkspace_configuration + slash + sModel + slash \
        + sRegion + slash + 'h2sc_configuration_' + sVariable.lower() + sExtension_txt

    sLabel_x = 'Surface slope (radian)'

    sVariable = 'zwt'
    sFilename_configuration_y = sWorkspace_configuration + slash + sModel + slash \
        + sRegion + slash + 'h2sc_configuration_' + sVariable.lower() + sExtension_txt

    
    sLabel_y = 'Water table depth (m)'




    iCase_index_start = iIndex_start
    iCase_index_end = iIndex_end
    aCase_index = np.arange(iCase_index_start, iCase_index_end + 1, 1)

        #iCase_index = 240       
    for iCase_index in (aCase_index):
        h2sc_scatterplot_variables_halfdegree(sFilename_configuration_x, \
            sFilename_configuration_y,\
                                    iCase_index,\
                                    iYear_start_in = iYear_start, \
                                    iYear_end_in =iYear_end,\
                                        dMin_x_in = 0,\
                                          dMax_x_in = 0.1, \
    dMin_y_in = 0, \
    dMax_y_in = 40, \
    dSpace_x_in = 0.02, \
    dSpace_y_in = 10, \
                                    sDate_in= sDate, \
                                        sLabel_x_in = sLabel_x, \
                                            sLabel_y_in = sLabel_y)

    print('finished')
