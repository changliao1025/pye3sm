#this script should be run using Python 3

import os, sys, stat
import argparse
import subprocess
import numpy as np

sSystem_paths = os.environ['PATH'].split(os.pathsep)
sys.path.extend(sSystem_paths)
from eslib.system import define_global_variables
from eslib.system.define_global_variables import *


sPath_e3sm_python = sWorkspace_code +  slash + 'python' + slash + 'e3sm' + slash + 'e3sm_python'
sys.path.append(sPath_e3sm_python)
from e3sm.case.e3sm_create_case import e3sm_create_case


sModel = 'h2sc'
sRegion ='global'
      
    
sFilename_configuration = sWorkspace_configuration + slash + sModel + slash \
               + sRegion + slash + 'h2sc_configuration.txt' 

aHydraulic_anisotropy = [0.1, 0.5, 1, 5, 10, 20,30, 40, 50, 60, 70, 80, 90, 100,\
     150, 200, 250, 300, 400, 500, 1000, 2000]  

aHydraulic_anisotropy = np.arange(-3,3.1,0.25)
aHydraulic_anisotropy = np.power(10, aHydraulic_anisotropy)
print(aHydraulic_anisotropy)

#start loop
ncase = len(aHydraulic_anisotropy)
iFlag_debug = 0
iFlag_continue = 0
iFlag_resubmit = 1
iFlag_short = 0
sDate = '20200117'
for i in range(20,ncase):
    #call the create case function

    dHydraulic_anisotropy = aHydraulic_anisotropy[i]
    sHydraulic_anisotropy = "{:0f}".format( dHydraulic_anisotropy)
    iCase = i + 1
    
    sCase =  sModel + sDate+ "{:03d}".format(iCase)
    sFilename_clm_namelist = sWorkspace_scratch + slash + '04model' + slash + sModel + slash + sRegion + slash \
        + 'cases' + slash + 'user_nl_clm_' + sCase

    ofs = open(sFilename_clm_namelist, 'w')
    sCommand_out = "fsurdat = " + "'" \
        + '/compyfs/inputdata/lnd/clm2/surfdata_map/surfdata_0.5x0.5_simyr2010_c191025_log10.nc' + "'" + '\n'
    ofs.write(sCommand_out)
    sLine_out = "use_h2sc = .true." + '\n'
    ofs.write(sLine_out)
    sLine_out = "hydraulic_anisotropy = " + sHydraulic_anisotropy + '\n'
    ofs.write(sLine_out)
    ofs.close()
    #write the clm namelist file
    #e3sm_create_case(sFilename_configuration, iCase, sFilename_clm_namelist)
    
    e3sm_create_case(sFilename_configuration,\
                     iFlag_continue_in = iFlag_continue,\
                     iFlag_debug_in = iFlag_debug,\
                     iFlag_resubmit_in = iFlag_resubmit ,\
                     iFlag_short_in = iFlag_short, \
                     iCase_index_in = iCase,  \
                     sDate_in= sDate,\
                     sFilename_clm_namelist_in = sFilename_clm_namelist )




