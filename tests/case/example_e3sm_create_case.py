import os, sys, stat
import argparse
import subprocess
import numpy as np
from pyearth.system.define_global_variables import *

from pye3sm.case.e3sm_create_case import e3sm_create_case
from pye3sm.shared.e3sm import pye3sm
from pye3sm.shared.case import pycase
from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_e3sm_configuration_file
from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_case_configuration_file
#import argparse
#parser = argparse.ArgumentParser()
#parser.add_argument("--iCase", help = "the id of the e3sm case", type=int, choices=range(1000))
#args = parser.parse_args()
sModel = 'default'
sRegion ='site'

dHydraulic_anisotropy = 1.0
sHydraulic_anisotropy = "{:0f}".format( dHydraulic_anisotropy)
aHydraulic_anisotropy_exp = np.arange(-3,1.1,0.25)
aHydraulic_anisotropy = np.power(10, aHydraulic_anisotropy_exp)
print(aHydraulic_anisotropy)
iCase = 1
dHydraulic_anisotropy = aHydraulic_anisotropy[iCase-1]
dHydraulic_anisotropy = 1.0
sHydraulic_anisotropy = "{:0f}".format( dHydraulic_anisotropy)
iFlag_default = 1
iFlag_debug = 0 #is this a debug run
iFlag_branch = 0 
iFlag_initial = 0 #use restart file as initial
iFlag_spinup = 1 #is this a spinup run
iFlag_short = 1 #do you run it on short queue
iFlag_continue = 0 #is this a continue run
iFlag_resubmit = 0 #is this a resubmit


sDate = '20210108'
sDate = '20201214'#test default
sDate = '20210127'
sDate = '20210209'
#sDate = '20201215'
#sDate = '20201218'
sDate = '20210504'

#sDate_spinup = '20200412'
sDate_spinup = '20210126'
sDate_spinup = '20210209'
#sDate_spinup = '20201215'


sCase = sModel + sDate + "{:03d}".format(iCase)

sWorkspace_scratch = '/compyfs/liao313'

#prepare a ELM namelist based on your input
sWorkspace_region = sWorkspace_scratch + slash + '04model' + slash + sModel + slash + sRegion + slash \
    + 'cases'
if not os.path.exists(sWorkspace_region):
    os.mkdir(sWorkspace_region)

sFilename_clm_namelist = sWorkspace_scratch + slash + '04model' + slash + sModel + slash + sRegion + slash \
    + 'cases' + slash + 'user_nl_clm_' + sCase


sFilename_domain = '/qfs/people/liao313/workspace/python/pye3sm/pye3sm/elm/grid/singlegrid/surfdata_icom_1x1_sparse_grid_c210504.nc'
sFilename_surface = '/people/liao313/workspace/python/pye3sm/pye3sm/elm/grid/singlegrid/surfdata_icom_1x1_sparse_grid_c210504.nc'
#'/compyfs/inputdata/lnd/clm2/surfdata_map/surfdata_0.5x0.5_simyr2010_c191025_20210127.nc'

sCase_spinup =  sModel + sDate_spinup + "{:03d}".format(1)

sFilename_initial = '/compyfs/liao313/e3sm_scratch/' \
        + sCase_spinup + '/run/' \
        + sCase_spinup +  '.clm2.rh0.1979-01-01-00000.nc'

if (iFlag_initial !=1):
    #normal case,
    ofs = open(sFilename_clm_namelist, 'w')
    sCommand_out = "fsurdat = " + "'" \
        + sFilename_surface  + "'" + '\n'
    ofs.write(sCommand_out)
    if (iFlag_default ==1 ):        
        pass
    else:
        sLine = "use_h2sc = .true." + '\n'
        ofs.write(sLine)
        sLine = "hydraulic_anisotropy = " + sHydraulic_anisotropy + '\n'
        ofs.write(sLine)
    ofs.close()
else:
    ofs = open(sFilename_clm_namelist, 'w')
    sCommand_out = "fsurdat = " + "'" \
        + sFilename_surface + "'" + '\n'
    ofs.write(sCommand_out)
    if (iFlag_default ==1 ):       
        pass
    else:
        sLine = "use_h2sc = .true." + '\n'
        ofs.write(sLine)
        sLine = "hydraulic_anisotropy = " + sHydraulic_anisotropy + '\n'
        ofs.write(sLine)
    
    #this is a case that use existing restart file
    #be careful with the filename!!!
    
    
    sLine = "finidat = " + "'"+ sFilename_initial +"'" + '\n'
    ofs.write(sLine)
    ofs.close()
    #mosart
    #sFilename_rtm_namelist = sWorkspace_scratch + slash \
        #    + '04model' + slash + sModel + slash \
        #    + sRegion + slash \
        #    + 'cases' + slash + 'user_nl_rtm_' + sCase
    #ofs = open(sFilename_rtm_namelist, 'w')
    #sLine = 'rtmhist_nhtfrq=0' + '\n'
    #ofs.write(sLine)
    #sLine = 'rtmhist_fincl1= "area"' + '\n'
    #ofs.write(sLine)
    #ofs.close()
sFilename_datm_namelist = sWorkspace_scratch + slash \
    + '04model' + slash + sModel + slash \
    + sRegion + slash \
    + 'cases' + slash + 'user_nl_datm_' + sCase
if (iFlag_spinup ==1):
    #this is a case for spin up
    ofs = open(sFilename_datm_namelist, 'w')
    sLine = 'taxmode = "cycle", "cycle", "cycle"' + '\n'
    ofs.write(sLine)
    ofs.close()
else:    
    pass

sFilename_e3sm_configuration = '/qfs/people/liao313/workspace/python/e3sm/pye3sm/pye3sm/shared/e3sm.xml'
sFilename_case_configuration = '/qfs/people/liao313/workspace/python/e3sm/pye3sm/pye3sm/shared/case.xml'
sCIME_directory ='/qfs/people/liao313/workspace/fortran/e3sm/E3SM/cime/scripts'
aParameter_e3sm = pye3sm_read_e3sm_configuration_file(sFilename_e3sm_configuration ,\
                                                      iFlag_debug_in = iFlag_debug, \
                                                      iFlag_branch_in = iFlag_branch,\
                                                      iFlag_continue_in = iFlag_continue,\
                                                      iFlag_resubmit_in = iFlag_resubmit,\
                                                      iFlag_short_in = iFlag_short  )
oE3SM = pye3sm(aParameter_e3sm)
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
    #print(aParameter_case)
oCase = pycase(aParameter_case)
e3sm_create_case(oE3SM, oCase )
