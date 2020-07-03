#this script should be run using Python 3

import os, sys, stat
import argparse
import subprocess
import numpy as np

sSystem_paths = os.environ['PATH'].split(os.pathsep)
sys.path.extend(sSystem_paths)
from pyes.system import define_global_variables
from pyes.system.define_global_variables import *

sPath_pye3sm = sWorkspace_code +  slash + 'python' + slash + 'e3sm' + slash + 'e3sm_python'
sys.path.append(sPath_pye3sm)
from e3sm.case.e3sm_create_case import e3sm_create_case

sModel = 'h2sc'
sRegion ='global'
      
sFilename_configuration = sWorkspace_configuration + slash + sModel + slash \
               + sRegion + slash + 'h2sc_configuration.txt' 

aHydraulic_anisotropy_exp = np.arange(-3,1.1,0.5)
aHydraulic_anisotropy = np.power(10, aHydraulic_anisotropy_exp)
print(aHydraulic_anisotropy)


#start loop
ncase = len(aHydraulic_anisotropy)
iFlag_debug = 0
iFlag_branch = 0
iFlag_initial = 1
iFlag_spinup = 0
iFlag_continue = 0
iFlag_resubmit = 0
iFlag_short = 0
sDate_spinup = '20200504'
sDate = '20200525'
for iCase in range(1,ncase + 1):
    #call the create case function
    dHydraulic_anisotropy = aHydraulic_anisotropy[iCase-1]
    sHydraulic_anisotropy = "{:0f}".format( dHydraulic_anisotropy)
    
    
    sCase =  sModel + sDate+ "{:03d}".format(iCase)
    sFilename_clm_namelist = sWorkspace_scratch + slash + '04model' + slash + sModel + slash + sRegion + slash \
        + 'cases' + slash + 'user_nl_clm_' + sCase

    sFilename_datm_namelist = sWorkspace_scratch + slash + '04model' + slash + sModel + slash + sRegion + slash \
        + 'cases' + slash + 'user_nl_datm_' + sCase
   

    if (iFlag_initial !=1):
        #normal case,      
        ofs = open(sFilename_clm_namelist, 'w')
        sCommand_out = "fsurdat = " + "'" \
            + '/compyfs/inputdata/lnd/clm2/surfdata_map/surfdata_0.5x0.5_simyr2010_c191025_log10.nc' + "'" + '\n'
        ofs.write(sCommand_out)
        sLine = "use_h2sc = .true." + '\n'
        ofs.write(sLine)
        sLine = "hydraulic_anisotropy = " + sHydraulic_anisotropy + '\n'
        ofs.write(sLine)
        ofs.close()
    else:
        ofs = open(sFilename_clm_namelist, 'w')
        sCommand_out = "fsurdat = " + "'" \
            + '/compyfs/inputdata/lnd/clm2/surfdata_map/surfdata_0.5x0.5_simyr2010_c191025_log10.nc' + "'" + '\n'
        ofs.write(sCommand_out)
        sLine = "use_h2sc = .true." + '\n'
        ofs.write(sLine)
        sLine = "hydraulic_anisotropy = " + sHydraulic_anisotropy + '\n'
        ofs.write(sLine)
        #this is a case that use existing restart file
        #be careful with the filename!!!
        
        sCase_spinup =  sModel + sDate_spinup+ "{:03d}".format(iCase)
        #sCase_spinup = 'h2sc20200409001'

        sLine = "finidat = '/compyfs/liao313/e3sm_scratch/" \
            + sCase_spinup + '/run/' + sCase_spinup +  ".clm2.rh0.1979-01-01-00000.nc'"  + '\n'
        ofs.write(sLine)
        ofs.close()
    

    

    if (iFlag_spinup ==1):        
        #this is a case for spin up
        ofs = open(sFilename_datm_namelist, 'w')
        sLine = 'taxmode = "cycle", "cycle", "cycle"' + '\n'
        ofs.write(sLine)
        ofs.close()
    else:
        #no spin up needed
        pass


    
    #write the clm namelist file
    #e3sm_create_case(sFilename_configuration, iCase, sFilename_clm_namelist)
    
    if (iFlag_spinup ==1):   
        e3sm_create_case(sFilename_configuration,\
                     iFlag_continue_in = iFlag_continue,\
                     iFlag_debug_in = iFlag_debug,\
                     iFlag_resubmit_in = iFlag_resubmit ,\
                     iFlag_short_in = iFlag_short, \
                     iCase_index_in = iCase,  \
                     iYear_end_in=1978,\
                     iYear_start_in=1949,\
                         iYear_data_end_in=1988,\
                     iYear_data_start_in=1979,\
                     sDate_in= sDate,\
                     sFilename_clm_namelist_in = sFilename_clm_namelist,\
                     sFilename_datm_namelist_in= sFilename_datm_namelist )
    else:
        e3sm_create_case(sFilename_configuration,\
                     iFlag_continue_in = iFlag_continue,\
                     iFlag_debug_in = iFlag_debug,\
                     iFlag_resubmit_in = iFlag_resubmit ,\
                     iFlag_short_in = iFlag_short, \
                     iCase_index_in = iCase,  \
                    iYear_end_in=2008,\
                     iYear_start_in=1979,\
                    iYear_data_end_in=2008,\
                     iYear_data_start_in=1979,\
                     sDate_in= sDate,\
                     sFilename_clm_namelist_in = sFilename_clm_namelist)

    




