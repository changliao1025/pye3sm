import os, sys, stat
from pathlib import Path

import numpy as np
import datetime
from shutil import copyfile

from scipy.stats import qmc


from pyearth.system.define_global_variables import *
from pyearth.gis.location.convert_lat_lon_range import convert_180_to_360


from pye3sm.elm.grid.create_customized_elm_domain import create_customized_elm_domain

from pye3sm.case.e3sm_create_case import e3sm_create_case
from pye3sm.shared.e3sm import pye3sm
from pye3sm.shared.case import pycase
from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_e3sm_configuration_file
from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_case_configuration_file
from pye3sm.mosart.grid.create_customized_mosart_domain import create_customized_mosart_domain
from pye3sm.elm.grid.elm_extract_grid_latlon_from_mosart import elm_extract_grid_latlon_from_mosart

sModel = 'e3sm'
#sRegion ='site'
sRegion ='amazon'
iFlag_rof = 1
iFlag_lnd=1
iFlag_elmmosart =1
iFlag_create_mosart_grid = 1
iFlag_create_elm_grid = 1
iFlag_2d_to_1d = 0 
iFlag_create_case = 1 
iFlag_submit_case = 0
sDate = '20220201'
sDate_spinup = '20210209'

if iFlag_elmmosart == 1:
    res='ELMMOS_USRDAT'
    compset = 'IELM'
else:
    if iFlag_rof ==1:
        pass
    else:    
        res='ELM_USRDAT'      
        compset = 'IELM'

#global setting
iFlag_default = 1
iFlag_debug = 0 #is this a debug run
iFlag_branch = 0
iFlag_initial = 0 #use restart file as initial
iFlag_spinup = 0 #is this a spinup run
iFlag_short = 0 #do you run it on short queue
iFlag_continue = 0 #is this a continue run
iFlag_resubmit = 0 #is this a resubmit
sWorkspace_scratch = '/compyfs/liao313'
#prepare a ELM namelist based on your input
sWorkspace_region = sWorkspace_scratch + slash + '04model' + slash + sModel + slash + sRegion + slash \
    + 'cases'
sWorkspace_region1 = sWorkspace_scratch + slash + '04model' + slash + sModel + slash + sRegion + slash \
    + 'cases_aux'
if not os.path.exists(sWorkspace_region):
    Path(sWorkspace_region).mkdir(parents=True, exist_ok=True)
if not os.path.exists(sWorkspace_region1):
    Path(sWorkspace_region1).mkdir(parents=True, exist_ok=True)
sFilename_surface_data_default='/compyfs/inputdata/lnd/clm2/surfdata_map/surfdata_0.5x0.5_simyr2010_c191025.nc'
sFilename_elm_domain_file_default='/compyfs/inputdata/share/domains/domain.lnd.r05_oEC60to30v3.190418.nc'
#'/compyfs/inputdata/lnd/clm2/surfdata_map/surfdata_0.5x0.5_simyr2010_c191025_20210127.nc'


sFilename_e3sm_configuration = '/qfs/people/liao313/workspace/python/pye3sm/pye3sm/e3sm.xml'
sFilename_case_configuration = '/qfs/people/liao313/workspace/python/pye3sm/pye3sm/case.xml'
sCIME_directory ='/qfs/people/liao313/workspace/fortran/e3sm/E3SM_H2SC/cime/scripts'
sFilename_configuration = '/people/liao313/workspace/python/pye3sm/pye3sm/elm/grid/elm_sparse_grid.cfg'
#for a single grid case, we can create this file on the fly
sPath = os.path.dirname(os.path.realpath(__file__))
pDate = datetime.datetime.today()

sDate_default = "{:04d}".format(pDate.year) + "{:02d}".format(pDate.month) + "{:02d}".format(pDate.day)
sCase_spinup =  sModel + sDate_spinup + "{:03d}".format(1)
sFilename_initial = '/compyfs/liao313/e3sm_scratch/' \
        + sCase_spinup + '/run/' \
        + sCase_spinup +  '.elm2.rh0.1979-01-01-00000.nc'

#generate mosart first then use the mosart lat/lon information for elm
sFilename_mosart_netcdf = '/compyfs/inputdata/rof/mosart/MOSART_Global_half_20210616.nc'

sFilename_user_prec = '/compyfs/liao313/04model/e3sm/amazon/datm.streams.txt.CLMGSWP3v1.Precip'

lCellID_outlet_in=128418
dResolution = 0.5
ncase = 40

sampler = qmc.LatinHypercube(d=2)
sample = sampler.random(n=ncase)

aHydraulic_anisotropy = np.full(ncase,0.0, dtype=float)
aFover=np.full(ncase,0.0, dtype=float)
aHkdepth=np.full(ncase,0.0, dtype=float)
if iFlag_default ==1:
    l_bounds = [0.1, 0.1]
    u_bounds = [5, 5]
    aParameter = qmc.scale(sample, l_bounds, u_bounds)
    aHkdepth=  aParameter[:,0]
    aFover = aParameter[:,1]
else:
    l_bounds = [-3, 0.1]
    u_bounds = [1, 5]


    aParameter = qmc.scale(sample, l_bounds, u_bounds)
    aHydraulic_anisotropy_exp = aParameter[:,0]
    aHydraulic_anisotropy = np.power(10, aHydraulic_anisotropy_exp)
    aFover = aParameter[:,1]




for iCase_index in range(ncase):   
    iCase = iCase_index + 1

    dHydraulic_anisotropy = aHydraulic_anisotropy[iCase_index]
    sHydraulic_anisotropy = "{:0f}".format( dHydraulic_anisotropy)
    
    dFover = aFover[iCase_index]
    sFover = "{:0f}".format( dFover)    

    dHkdepth = aHkdepth[iCase_index]
    sHkdepth = "{:0f}".format( dHkdepth)

    sCase_date = sDate + "{:03d}".format(iCase)
    sCase = sModel + sDate + "{:03d}".format(iCase)

    sWorkspace_region2 = sWorkspace_region1 + slash + sCase
    if not os.path.exists(sWorkspace_region2):
        Path(sWorkspace_region2).mkdir(parents=True, exist_ok=True)
    
    if iFlag_create_mosart_grid ==1: 
        sFilename_mosart_netcdf_out = sWorkspace_region2 + slash + 'mosart_'+ sCase_date + '.nc'
        create_customized_mosart_domain(iFlag_2d_to_1d, sFilename_mosart_netcdf,sFilename_mosart_netcdf_out, lCellID_outlet_in)

    sFilename_mosart_input = sWorkspace_region2 + slash + 'mosart_' + sCase_date + '.nc'
    if not os.path.exists(sFilename_mosart_input):    
        copyfile(sFilename_mosart_netcdf_out, sFilename_mosart_input)    

    if iFlag_create_elm_grid ==1:
        #mask is flipped
        aLon, aLat, aMask = elm_extract_grid_latlon_from_mosart(sFilename_mosart_netcdf_out)
        if iFlag_2d_to_1d == 0:
            lon_min = np.min(aLon)
            lon_max = np.max(aLon)
            lat_min = np.min(aLat)
            lat_max = np.max(aLat)
            nrow = int((lat_max-lat_min) / dResolution + 1)
            ncolumn = int( (lon_max-lon_min) / dResolution + 1 )
            ngrid = ncolumn * nrow
            sFilename_lon_lat_in = sWorkspace_region2 + slash + 'elm_' + sCase_date +'.txt'
            ofs = open(sFilename_lon_lat_in, 'w')
            sGrid =  "{:0d}".format( ngrid )
            sLine = sGrid + '\n'
            ofs.write(sLine)
            aLon = np.full( (nrow, ncolumn), missing_value, dtype=float )
            aLat = np.full( (nrow, ncolumn), missing_value, dtype=float )

            for i in range(nrow):
                for j in range(ncolumn):
                    aLon[i,j] = lon_min + j * dResolution
                    aLat[i,j] = lat_min + i * dResolution
                    sLine = "{:0f}".format( aLat[i,j]) + ' ' + "{:0f}".format( aLon[i,j] ) + '\n'
                    ofs.write(sLine)

            ofs.close()
        else:
            aLon0=np.ravel(aLon)
            aLat0=np.ravel(aLat)
            dummy_index  = np.where( (aLon0 != -9999)&(aLat0 != -9999))
            aLon = aLon0[dummy_index]
            aLat = aLat0[dummy_index]
            ngrid = len(aLon)
            sFilename_lon_lat_in = sWorkspace_region2 + slash + 'elm_' + sCase_date +'.txt'
            ofs = open(sFilename_lon_lat_in, 'w')
            sGrid =  "{:0d}".format( ngrid )
            sLine = sGrid + '\n'
            ofs.write(sLine)
            for i in range(ngrid):
                dLatitude = aLat[i]
                dLongitude = aLon[i]
                #dLongitude = convert_180_to_360(aLon[i]) #the customized domain function require 0-360
                sLine = "{:0f}".format( dLatitude) + ' ' + "{:0f}".format( dLongitude) + '\n'
                ofs.write(sLine)

            ofs.close()

    if iFlag_create_case ==1:    
        sFilename_elm_namelist = sWorkspace_region2 + slash + 'user_nl_elm_' + sCase_date
        sFilename_mosart_namelist = sWorkspace_region2 + slash + 'user_nl_rtm_' + sCase_date
        sFilename_datm_namelist = sWorkspace_region2 + slash + 'user_nl_datm_' + sCase_date
        sFilename_surface_data_out = sWorkspace_region2 + slash + 'elm_surfdata_' + sCase_date + '.nc'
        sFilename_elm_domain_file_out = sWorkspace_region2 + slash +  'elm_domain_' + sCase_date + '.nc'
        create_customized_elm_domain( aLon, aLat, aMask, dResolution, dResolution, \
            sFilename_configuration, \
                                 sFilename_surface_data_default,\
                                 sFilename_elm_domain_file_default,\
                                 sFilename_surface_data_out,
                                 sFilename_elm_domain_file_out)

        if (iFlag_initial !=1):
            #normal case,
            ofs = open(sFilename_elm_namelist, 'w')
            sCommand_out = "fsurdat = " + "'" \
                + sFilename_surface_data_out  + "'" + '\n'
            ofs.write(sCommand_out)
            if (iFlag_default ==1 ):
                sLine = "dHkdepth = " + sHkdepth + '\n'
                ofs.write(sLine)
                sLine = "fover = " + sFover + '\n'
                ofs.write(sLine)
                sLine = 'hist_empty_htapes = .true.' + '\n'
                ofs.write(sLine)
                sLine = "hist_fincl1 = 'QOVER', 'QDRAI', 'QRUNOFF', 'ZWT' "  + '\n'
                ofs.write(sLine)
                pass
            else:
                sLine = "use_h2sc = .true." + '\n'
                ofs.write(sLine)
                sLine = "hydraulic_anisotropy = " + sHydraulic_anisotropy + '\n'
                ofs.write(sLine)
                sLine = "fover = " + sFover + '\n'
                ofs.write(sLine)

                sLine = 'hist_empty_htapes = .true.' + '\n'
                ofs.write(sLine)
                sLine = "hist_fincl1 = 'QOVER', 'QDRAI', 'QRUNOFF', 'ZWT' "  + '\n'
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


#save a copy of parameter as well
sFilename_parameter = sWorkspace_region1 + slash + sDate + '.csv'
np.savetxt(sFilename_parameter, aParameter, delimiter=",")

#write a large sh to run all the 
sFilename_bash = sWorkspace_region1 + slash + 'run_batch'+ sDate +'.sh'
ofs = open(sFilename_bash, 'w')
sLine = '#!/bin/bash' + '\n'
ofs.write(sLine) 
for iCase_index in range(ncase):   
    iCase = iCase_index + 1
    sCase_date = sDate + "{:03d}".format(iCase)
    sCase = sModel + sDate + "{:03d}".format(iCase)
    sWorkspace_region2 = sWorkspace_region1 + slash + sCase
    sLine = 'cd ' + sWorkspace_region2 +  '\n'     
    ofs.write(sLine)
    sLine = './' + sCase + '.sh' +  '\n'
    ofs.write(sLine)
ofs.close()
os.chmod(sFilename_bash, stat.S_IREAD | stat.S_IWRITE | stat.S_IXUSR)
print('Finished')
