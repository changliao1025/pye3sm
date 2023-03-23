import os, sys, stat
from pathlib import Path
import argparse
import subprocess
import numpy as np
import  datetime
from pyearth.system.define_global_variables import *
from pyearth.gis.location.convert_lat_lon_range import convert_180_to_360


from pye3sm.elm.grid.create_elm_surface_data import create_elm_surface_data

from pye3sm.case.e3sm_create_case import e3sm_create_case
from pye3sm.shared.e3sm import pye3sm
from pye3sm.shared.case import pycase
from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_e3sm_configuration_file
from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_case_configuration_file

sModel = 'e3sm'
sRegion ='site'
iCase = 1

dHydraulic_anisotropy = 1.0
#sHydraulic_anisotropy = "{:0f}".format( dHydraulic_anisotropy)
#aHydraulic_anisotropy_exp = np.arange(-3,1.1,0.25)
#aHydraulic_anisotropy = np.power(10, aHydraulic_anisotropy_exp)
#dHydraulic_anisotropy = aHydraulic_anisotropy[iCase-1]
sHydraulic_anisotropy = "{:0f}".format( dHydraulic_anisotropy)


iFlag_default = 1
iFlag_debug = 0 #is this a debug run
iFlag_branch = 0
iFlag_initial = 0 #use restart file as initial
iFlag_spinup = 0 #is this a spinup run
iFlag_short = 0 #do you run it on short queue
iFlag_continue = 0 #is this a continue run
iFlag_resubmit = 0 #is this a resubmit

iFlag_rof =0
iFlag_lnd=1


sDate = '20210807'

sDate_spinup = '20210209'

sWorkspace_scratch = '/compyfs/liao313'

#prepare a ELM namelist based on your input
sWorkspace_region = sWorkspace_scratch + slash + '04model' + slash + sModel + slash + sRegion + slash \
    + 'cases'
if not os.path.exists(sWorkspace_region):
    Path(sWorkspace_region).mkdir(parents=True, exist_ok=True)



sFilename_surface_data_default='/compyfs/inputdata/lnd/clm2/surfdata_map/surfdata_0.5x0.5_simyr2010_c191025.nc'
sFilename_domain_file_default='/compyfs/inputdata/share/domains/domain.lnd.r05_oEC60to30v3.190418.nc'


#'/compyfs/inputdata/lnd/clm2/surfdata_map/surfdata_0.5x0.5_simyr2010_c191025_20210127.nc'

sFilename_configuration = '/people/liao313/workspace/python/pye3sm/pye3sm/elm/grid/elm_sparse_grid.cfg'

#for a single grid case, we can create this file on the fly
sPath = os.path.dirname(os.path.realpath(__file__))

pDate = datetime.datetime.today()
sDate_default = "{:04d}".format(pDate.year) + "{:02d}".format(pDate.month) + "{:02d}".format(pDate.day)

sCase_spinup =  sModel + sDate_spinup + "{:03d}".format(1)

sFilename_initial = '/compyfs/liao313/e3sm_scratch/' \
        + sCase_spinup + '/run/' \
        + sCase_spinup +  '.elm2.rh0.1979-01-01-00000.nc'

dLongitude = -74.86284899999998
dLatitude =  39.16761
#aLon aLat should be used for a list of location

aLon =[-60.2, -66.5,-119,-147.0]
aLat =[-2.6, -11.0,46, 66.0]

ngrid = len(aLon)
for i in range(1):
    iCase = 7
    sCase = sModel + sDate + "{:03d}".format(iCase)

    sFilename_lon_lat_in = sWorkspace_region + sCase +'.txt'
    ofs = open(sFilename_lon_lat_in, 'w')
    
    sGrid =  "{:0d}".format( 1)
    sLine = sGrid + '\n'
    ofs.write(sLine)
    dLatitude = aLat[i]
    dLongitude = convert_180_to_360(aLon[i]) #the customized domain function require 0-360
    sLine = "{:0f}".format( dLatitude) + ' ' + "{:0f}".format( dLongitude) + '\n'
    ofs.write(sLine)
    ofs.close()

    sFilename_elm_namelist = sWorkspace_scratch + slash \
        + '04model'    + slash + sModel + slash + \
            sRegion + slash \
     + 'cases' + slash + 'user_nl_elm_' + sCase

    sFilename_mosart_namelist = sWorkspace_scratch + slash \
                + '04model' + slash + sModel + slash \
                + sRegion + slash \
                + 'cases' + slash + 'user_nl_rtm_' + sCase
    
    sFilename_datm_namelist = sWorkspace_scratch + slash \
        + '04model' + slash + sModel + slash \
        + sRegion + slash \
        + 'cases' + slash + 'user_nl_datm_' + sCase

    sFilename_surface_data_out = sWorkspace_region + '/surfdata_' + sCase + '.nc'
    sFilename_elm_domain_file_out = sWorkspace_region +  '/domain_' + sCase + '.nc'
    create_elm_surface_data( sFilename_configuration, \
                             sFilename_lon_lat_in, \
                                 sFilename_surface_data_default,\
                             sFilename_domain_file_default,\
                             sFilename_surface_data_out,
                             sFilename_elm_domain_file_out)

    #sFilename_surfacedata_out = '/qfs/people/liao313/data/e3sm/amazon/elm/surfdata_amazon_half_c210526.nc'
    #sFilename_elm_domain_out = '/qfs/people/liao313/data/e3sm/amazon/elm/domain_lnd_amazon_half_c210526.nc'
    sFilename_mosart_input = '/qfs/people/liao313/data/e3sm/amazon/mosart/MOSART_amazon_half_c210526.nc'

    if (iFlag_initial !=1):
        #normal case,
        ofs = open(sFilename_elm_namelist, 'w')
        sCommand_out = "fsurdat = " + "'" \
            + sFilename_surface_data_out  + "'" + '\n'
        ofs.write(sCommand_out)
        if (iFlag_default ==1 ):
            pass
        else:
            sLine = "use_h2sc = .true." + '\n'
            ofs.write(sLine)
            sLine = "hydraulic_anisotropy = " + sHydraulic_anisotropy + '\n'
            ofs.write(sLine)
            pass

        ofs.close()

    else:
        ofs = open(sFilename_elm_namelist, 'w')
        sCommand_out = "fsurdat = " + "'" \
            + sFilename_surface_data_out + "'" + '\n'
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

    if iFlag_rof ==1:        
        ofs = open(sFilename_mosart_namelist, 'w')
        #sLine = 'rtmhist_nhtfrq=0' + '\n'
        #ofs.write(sLine)
        sLine = 'frivinp_rtm = ' + "'" + sFilename_mosart_input + "'" + '\n'
        ofs.write(sLine)
        #sLine = 'rtmhist_fincl1= "area"' + '\n'
        #ofs.write(sLine)
        ofs.close()

    if iFlag_spinup ==1:
        #this is a case for spin up
        ofs = open(sFilename_datm_namelist, 'w')
        sLine = 'taxmode = "cycle", "cycle", "cycle"' + '\n'
        ofs.write(sLine)
        ofs.close()
        pass
    else:
        pass

    sFilename_e3sm_configuration = '/qfs/people/liao313/workspace/python/pye3sm/pye3sm/e3sm.xml'
    sFilename_case_configuration = '/qfs/people/liao313/workspace/python/pye3sm/pye3sm/case.xml'
    sCIME_directory ='/qfs/people/liao313/workspace/fortran/e3sm/E3SM/cime/scripts'

    res='ELM_USRDAT'
    res='ELMMOS_USRDAT'
    #res='r05_r05'
    #res = 'ELMMOS_USRDAT'
    compset = 'IELM'
    COMPSET='IELM45'
    
    aParameter_e3sm = pye3sm_read_e3sm_configuration_file(sFilename_e3sm_configuration ,\
                                                          iFlag_debug_in = iFlag_debug, \
                                                          iFlag_branch_in = iFlag_branch,\
                                                          iFlag_continue_in = iFlag_continue,\
                                                          iFlag_resubmit_in = iFlag_resubmit,\
                                                          iFlag_short_in = iFlag_short ,\
                                                          RES_in =res,\
                                                          COMPSET_in = compset ,\
                                                          sCIME_directory_in = sCIME_directory)
    oE3SM = pye3sm(aParameter_e3sm)
    if (iFlag_spinup ==1):
        aParameter_case = pye3sm_read_case_configuration_file(sFilename_case_configuration,\
                                                              iFlag_spinup_in = iFlag_spinup,\
                                                              iYear_start_in = 1969, \
                                                              iYear_end_in = 1978,\
                                                              iYear_data_end_in = 2010, \
                                                              iYear_data_start_in = 1979   ,\
                                                              iCase_index_in = iCase, \
                                                              sDate_in = sDate, \
                                                              sModel_in = sModel,\
                                                              sRegion_in = sRegion,\
                                                              sFilename_atm_domain_in=  sFilename_elm_domain_file_out,\
                                                              sFilename_datm_namelist_in =  sFilename_datm_namelist ,\
                                                              sFilename_lnd_namelist_in =   sFilename_elm_namelist, \
                                                              sFilename_lnd_domain_in=sFilename_elm_domain_file_out, \
                                                                  sFilename_mosart_input_in = sFilename_mosart_input, \
                                                              sWorkspace_scratch_in =   sWorkspace_scratch)
        pass
    else:
        aParameter_case = pye3sm_read_case_configuration_file(sFilename_case_configuration,\
                                                              iFlag_spinup_in = iFlag_spinup,\
                                                                   iFlag_elm_in= iFlag_lnd,\
                                                                  iFlag_rof_in= iFlag_rof,\
                                                              iYear_start_in = 1980, \
                                                              iYear_end_in = 2010,\
                                                              iYear_data_end_in = 2010, \
                                                              iYear_data_start_in = 1979   , \
                                                              iCase_index_in = iCase, \
                                                              sDate_in = sDate, \
                                                              sModel_in = sModel,\
                                                              sRegion_in = sRegion,\
                                                              sFilename_atm_domain_in=  sFilename_elm_domain_file_out,\
                                                              sFilename_datm_namelist_in =  sFilename_datm_namelist ,\
                                                              sFilename_lnd_namelist_in =   sFilename_elm_namelist, \
                                                              sFilename_lnd_domain_in=sFilename_elm_domain_file_out, \
                                                                  sFilename_rof_namelist_in = sFilename_mosart_namelist, \
                                                                  sFilename_mosart_input_in = sFilename_mosart_input, \
                                                              sWorkspace_scratch_in =   sWorkspace_scratch )
        pass
        #print(aParameter_case)

    oCase = pycase(aParameter_case)
    e3sm_create_case(oE3SM, oCase )
