#this script should be run using Python 3

import os, sys, stat
import argparse
import subprocess
import numpy as np

from pyearth.system.define_global_variables import *

from ..shared.e3sm import pye3sm
from ..shared.case import pycase
from ..shared.pye3sm_read_configuration_file import pye3sm_read_e3sm_configuration_file
from ..shared.pye3sm_read_configuration_file import pye3sm_read_case_configuration_file
from ..case.e3sm_create_case import e3sm_create_case

sModel = 'h2sc'
sRegion ='global'      

aHydraulic_anisotropy_exp = np.arange(-3,1.1,0.25)
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
#sDate_spinup = '20200504'
sDate_spinup = '20200905'
sDate = '20200906'
sDate = '20210127'
sDate_spinup = '20210126'

sFilename_e3sm_configuration = '/qfs/people/liao313/workspace/python/e3sm/pye3sm/pye3sm/shared/e3sm.xml'
sFilename_case_configuration = '/qfs/people/liao313/workspace/python/e3sm/pye3sm/pye3sm/shared/case.xml'
aParameter_e3sm = pye3sm_read_e3sm_configuration_file(sFilename_e3sm_configuration ,\
                                                          iFlag_debug_in = iFlag_debug, \
                                                          iFlag_branch_in = iFlag_branch,\
                                                          iFlag_continue_in = iFlag_continue,\
                                                          iFlag_resubmit_in = iFlag_resubmit,\
                                                          iFlag_short_in = iFlag_short  )

oE3SM = pye3sm(aParameter_e3sm)

for iCase in range(1,ncase + 1):
    #call the create case function
    dHydraulic_anisotropy = aHydraulic_anisotropy[iCase-1]
    sHydraulic_anisotropy = "{:0f}".format( dHydraulic_anisotropy)
    
    
    sCase =  sModel + sDate+ "{:03d}".format(iCase)
    sFilename_clm_namelist = sWorkspace_scratch + slash + '04model' + slash \
        + sModel + slash + sRegion + slash \
        + 'cases' + slash + 'user_nl_clm_' + sCase

    sFilename_datm_namelist = sWorkspace_scratch + slash + '04model' + slash \
        + sModel + slash + sRegion + slash \
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
        
        sCase_spinup =  sModel + sDate_spinup + "{:03d}".format(iCase)
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


    if (iFlag_spinup ==1):
        aParameter_case = pye3sm_read_case_configuration_file(sFilename_case_configuration,\
            iFlag_spinup_in = iFlag_spinup,\
                                                              iYear_start_in = 1949, \
                                                              iYear_end_in = 1978,\
                                                              iYear_data_end_in = 1988, \
                                                              iYear_data_start_in = 1979   ,\
                                                              iCase_index_in = iCase, \
                                                              sDate_in = sDate, \
                                                              sFilename_clm_namelist_in = sFilename_clm_namelist, \
                                                              sFilename_datm_namelist_in = sFilename_datm_namelist )
        
    else:
        aParameter_case = pye3sm_read_case_configuration_file(sFilename_case_configuration,\
            iFlag_spinup_in = iFlag_spinup,\
                                                              iYear_start_in = 1979, \
                                                              iYear_end_in = 2008,\
                                                              iYear_data_end_in = 2008, \
                                                              iYear_data_start_in = 1979   , \
                                                              iCase_index_in = iCase, \
                                                              sDate_in = sDate, \
                                                              sFilename_clm_namelist_in = sFilename_clm_namelist )
    
    oCase = pycase(aParameter_case)
    e3sm_create_case(oE3SM, oCase )
        

    




