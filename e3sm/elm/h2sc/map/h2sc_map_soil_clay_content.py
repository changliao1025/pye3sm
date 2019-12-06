import os, sys
sSystem_paths = os.environ['PATH'].split(os.pathsep)
sys.path.extend(sSystem_paths)
from eslib.system.define_global_variables import *

sPath_e3sm_python = sWorkspace_code +  slash + 'python' + slash + 'e3sm' + slash + 'e3sm_python'
sys.path.append(sPath_e3sm_python)

from e3sm.shared import e3sm_global
from e3sm.shared.e3sm_read_configuration_file import e3sm_read_configuration_file

def h2sc_map_soil_clay_content(sFilename_configuration_in, iCase_index, iYear_start_in = None, iYear_end_in = None, iFlag_same_grid_in = None):
    #extract information
    e3sm_read_configuration_file(sFilename_configuration_in, iCase_index_in = iCase_index)       
    sModel  = e3sm_global.sModel
    sRegion = e3sm_global.sRegion   
    return
if __name__ == '__main__':

    sModel = 'h2sc'
    sRegion = 'global'
    sFilename_configuration = sWorkspace_configuration + slash + sModel + slash \
               + sRegion + slash + 'h2sc_configuration.txt' 
    print(sFilename_configuration)
    h2sc_map_soil_clay_content(sFilename_configuration)