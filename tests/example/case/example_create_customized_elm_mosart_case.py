import os, sys, stat
from pathlib import Path


import numpy as np
import datetime
from shutil import copyfile
from pyearth.system.define_global_variables import *
from pyearth.gis.location.convert_lat_lon_range import convert_180_to_360
from pyearth.toolbox.data.beta.add_variable_to_netcdf import add_multiple_variable_to_netcdf
from pyearth.gis.gdal.read.gdal_read_geotiff_file import gdal_read_geotiff_file
from pye3sm.elm.mesh.create_customized_elm_domain import create_customized_elm_domain

from pye3sm.case.e3sm_create_case import e3sm_create_case
from pye3sm.shared.e3sm import pye3sm
from pye3sm.shared.case import pycase
from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_e3sm_configuration_file
from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_case_configuration_file
from pye3sm.mosart.grid.create_customized_mosart_domain import create_customized_mosart_domain
from pye3sm.mosart.grid.structured.twod.extract_mosart_elevation_profile_for_elm import extract_mosart_elevation_profile_for_elm, extract_mosart_variable_for_elm

from pye3sm.elm.mesh.elm_extract_grid_latlon_from_mosart import elm_extract_grid_latlon_from_mosart
sModel = 'e3sm'
sRegion = 'site'
sRegion = 'sag'
#the lat/lon only used when in single grid case
#1
dLongitude =  -77.8
dLatitude =  -6.35
#2
#dLongitude =  -60
#dLatitude =  -11
sRegion ='amazon'
iCase = 59
iFlag_replace_datm_forcing=0
iFlag_replace_dlnd_forcing=0


iFlag_atm = 0
iFlag_create_atm_grid=0
iFlag_mosart = 1
iFlag_create_mosart_grid = 1
iFlag_elm = 1
iFlag_create_elm_grid = 1

if iFlag_mosart ==1 :
    if iFlag_elm ==1:
        iFlag_elmmosart = 1        
    else:
        iFlag_elmmosart = 0        
else:
    iFlag_elmmosart = 0


iFlag_2d_to_1d = 0 
iFlag_create_case = 1 
iFlag_submit_case = 0

iFlag_default = 0
iFlag_debug = 0 #is this a debug run
iFlag_branch = 0
iFlag_initial = 1 #use restart file as initial
iFlag_elm_spinup = 0 #is this a spinup run
iFlag_short = 0 #do you run it on short queue
iFlag_continue = 0 #is this a continue run
iFlag_resubmit = 0 #is this a resubmit
iFlag_optimal_parameter = 0
sDate = '20220701'
sDate_spinup = '20210209'

if iFlag_elmmosart == 1:
    res='ELMMOS_USRDAT'
    compset = 'IELM'
else:
    if iFlag_mosart == 1:
        if iFlag_elm ==1:
            #impossible, since it would be a coupled case
            pass
        else:
            res='MOS_USRDAT'      
            compset = 'RMOSGPCC'
        pass
    else:    
        res='ELM_USRDAT'      
        compset = 'IELM'


#for a single grid case, we can create this file on the fly
sPath = os.path.dirname(os.path.realpath(__file__))
pDate = datetime.datetime.today()
sDate_default = "{:04d}".format(pDate.year) + "{:02d}".format(pDate.month) + "{:02d}".format(pDate.day)
sCase_spinup =  sModel + sDate_spinup + "{:03d}".format(1)

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


#some pre-defined files     
sFilename_elm_surface_data_default='/compyfs/inputdata/lnd/clm2/surfdata_map/surfdata_0.5x0.5_simyr2010_c191025.nc'
#sFilename_elm_surface_data_default ='/compyfs/inputdata/lnd/clm2/surfdata_map/topounit_based_half_degree_merge_surfdata_0.5x0.5_simyr1850_c211019.20211108_ed20220204.nc'
sFilename_elm_domain_default='/compyfs/inputdata/share/domains/domain.lnd.r05_oEC60to30v3.190418.nc'


sFilename_dlnd_stream = '/qfs/people/liao313/data/e3sm/sag/mosart/dlnd.streams.txt.lnd.gpcc'
#generate mosart first then use the mosart lat/lon information for elm

if iFlag_create_mosart_grid ==1:
    sFilename_mosart_parameter_default = '/compyfs/inputdata/rof/mosart/MOSART_Global_half_20210616.nc'
else:
    sFilename_mosart_parameter_default = '/qfs/people/liao313/data/e3sm/sag/mosart/MOSART_Sag_MPAS_c220804.nc'
    sFilename_mosart_domain_default ='/qfs/people/liao313/data/e3sm/sag/mosart/domain_Sag_MPAS_c220804.nc'
    
sFilename_atm_domain=None

sFilename_etm_domain=None

sFilename_mosart_domain=None
sFilename_mosart_namelist=None

sFilename_initial = '/compyfs/liao313/e3sm_scratch/e3sm20220701050/run/e3sm20220701050.elm.r.1980-01-01-00000.nc'


sFilename_e3sm_configuration = '/qfs/people/liao313/workspace/python/pye3sm/pye3sm/e3sm.xml'
sFilename_case_configuration = '/qfs/people/liao313/workspace/python/pye3sm/pye3sm/case.xml'
if iFlag_default ==1:
    sCIME_directory ='/qfs/people/liao313/workspace/fortran/e3sm/E3SM/cime/scripts'
else:
    sCIME_directory ='/qfs/people/liao313/workspace/fortran/e3sm/E3SM_H2SC/cime/scripts'
sFilename_configuration = '/people/liao313/workspace/python/pye3sm/pye3sm/elm/mesh/elm_sparse_grid.cfg'



dHydraulic_anisotropy = 1.0
sHydraulic_anisotropy = "{:0f}".format( dHydraulic_anisotropy)

dFover = 0.6 
sFover = "{:0f}".format( dFover)

dHkdepth = 2.5
sHkdepth = "{:0f}".format( dHkdepth)

sCase_date = sDate + "{:03d}".format(iCase)
sCase = sModel + sDate + "{:03d}".format(iCase)

sWorkspace_region2 = sWorkspace_region1 + slash + sCase
if not os.path.exists(sWorkspace_region2):
    Path(sWorkspace_region2).mkdir(parents=True, exist_ok=True)

lCellID_outlet_in=128418
dResolution = 0.5

aMask=None
sFilename_mosart_parameter =None

#extract the mosart from a large domain, usually in structured mesh


if iFlag_create_mosart_grid ==1: 

    sFilename_mosart_netcdf_out = sWorkspace_region2 + slash + 'mosart_'+ sCase_date + '.nc'
    create_customized_mosart_domain(iFlag_2d_to_1d, sFilename_mosart_parameter_default,sFilename_mosart_netcdf_out, lCellID_outlet_in)
    
    if iFlag_mosart==1:
        #exact elevation profile from mosart to elm
        aElevation_profile = extract_mosart_elevation_profile_for_elm(sFilename_mosart_netcdf_out)
        #other variable
        aVariable_in=['gxr','rdep','hslp', 'rlen']
        aVariable_mosart = extract_mosart_variable_for_elm(sFilename_mosart_netcdf_out, aVariable_in)

    sFilename_mosart_parameter = sWorkspace_region2 + slash + 'mosart_' + sCase_date + '.nc'
    if not os.path.exists(sFilename_mosart_parameter):    
        copyfile(sFilename_mosart_netcdf_out, sFilename_mosart_parameter)
    else:
        pass

else:
    #pre-defined mosart, usually mpas mesh-based
    sFilename_mosart_parameter = sWorkspace_region2 + slash + 'mosart_'+ sCase_date + '_parameter.nc'
    sFilename_mosart_domain = sWorkspace_region2 + slash + 'mosart_'+ sCase_date + '_domain.nc'

    #overwrite?
    
    if not os.path.exists(sFilename_mosart_parameter):    
        copyfile(sFilename_mosart_parameter_default, sFilename_mosart_parameter)
        
    if not os.path.exists(sFilename_mosart_domain):    
        copyfile(sFilename_mosart_domain_default, sFilename_mosart_domain)
    
    pass
        
if iFlag_create_atm_grid==1:
    pass
else:
    pass

if iFlag_create_elm_grid ==1:
    #have both mosart and elm
    if iFlag_create_mosart_grid ==1:
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
                    sLine = "{:0f}".format( aLon[i,j] ) + ' ' +  "{:0f}".format( aLat[i,j]) + '\n'
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
               
                sLine = "{:0f}".format( dLongitude ) + ' ' +  "{:0f}".format( dLatitude) + '\n'
                ofs.write(sLine)

            ofs.close()
    else:
        #maybe single grid
        
        #aLon aLat should be used for a list of location
        aLon =np.array([dLongitude])
        aLat =np.array([dLatitude])
        sFilename_lon_lat_in = sWorkspace_region2 + slash + 'elm_' + sCase_date +'.txt'
        ofs = open(sFilename_lon_lat_in, 'w')
        ngrid = 1
        sGrid =  "{:0d}".format( ngrid)
        sLine = sGrid + '\n'
        ofs.write(sLine) 
        for i in range(ngrid):
            dLongitude = aLon[i]
            dLatitude = aLat[i]
            
            sLine = "{:0f}".format( dLongitude ) + ' ' +  "{:0f}".format( dLatitude) + '\n'
            ofs.write(sLine)

        ofs.close()


        pass
else:
    sFilename_elm_domain = sFilename_mosart_domain
    pass


    #

if iFlag_create_case ==1:

    if iFlag_elm ==1:
        sFilename_elm_namelist = sWorkspace_region2 + slash + 'user_nl_elm_' + sCase_date
        sFilename_elm_surface_data_out = sWorkspace_region2 + slash + 'elm_surfdata_' + sCase_date + '.nc'
        sFilename_elm_domain_out = sWorkspace_region2 + slash +  'elm_domain_' + sCase_date + '.nc'
        create_customized_elm_domain( aLon, aLat, aMask, dResolution, dResolution, \
                sFilename_configuration, \
                             sFilename_elm_surface_data_default,\
                             sFilename_elm_domain_default,\
                             sFilename_elm_surface_data_out,
                             sFilename_elm_domain_out)
        sFilename_elm_domain = sFilename_elm_domain_out
        if iFlag_create_atm_grid==1:
            pass
        else:
            sFilename_atm_domain = sFilename_elm_domain
            pass
    else:
        #should we use user_nl_dlnd?

        sFilename_elm_domain=sFilename_mosart_domain
        sFilename_elm_namelist = sWorkspace_region2 + slash + 'user_nl_dlnd_' + sCase_date 
        pass

    if iFlag_mosart ==1:
        sFilename_mosart_namelist = sWorkspace_region2 + slash + 'user_nl_rtm_' + sCase_date
    else:
        pass
    
    if iFlag_atm ==1:
        pass
    else:
        sFilename_datm_namelist = sWorkspace_region2 + slash + 'user_nl_datm_' + sCase_date
        pass      

    if iFlag_default ==0:
        #add elevation profile into surface data
        if iFlag_elmmosart == 1:
            sFilename_old=sFilename_elm_surface_data_out
            sFilename_new = sFilename_elm_surface_data_out = sWorkspace_region2 + slash + 'elm_surfdata_' + sCase_date + '_elevation_profile.nc'
            aVariable_all=['ele0', 'ele1','ele2', 'ele3','ele4','ele5','ele6', 'ele7','ele8', 'ele9','ele10']
            aUnit_all= ['m', 'm','m', 'm','m','m','m', 'm','m', 'm','m']
            aDimension= [nrow, ncolumn]
            nElev=11
            aDimension_all= list()
            for i in range(nElev):
                aDimension_all.append( aDimension)
            add_multiple_variable_to_netcdf(sFilename_old, sFilename_new,aElevation_profile, aVariable_all, aUnit_all,  aDimension_all)        
            sFilename_elm_surface_data_out =  sFilename_new

            sFilename_old=sFilename_elm_surface_data_out
            sFilename_new = sFilename_elm_surface_data_out = sWorkspace_region2 + slash + 'elm_surfdata_' + sCase_date + '_mosart.nc'
            aVariable_all = ['gxr','rdep','hslp', 'rlen']
            aUnit_all =['m', 'm-1','unitless','m']
            aDimension_all=[aDimension,aDimension,aDimension, aDimension ]
            add_multiple_variable_to_netcdf(sFilename_old, sFilename_new, aVariable_mosart, aVariable_all, aUnit_all,  aDimension_all)        
            sFilename_elm_surface_data_out =  sFilename_new

            #add ksat from the paper
            sFilename_tiff = '/qfs/people/liao313/data/e3sm/amazon/elm/ksat_new.tif'
            a = gdal_read_geotiff_file(sFilename_tiff)  
            aKsat = data_fover = np.flip(a[0],0)
            sFilename_old = sFilename_elm_surface_data_out
            sFilename_new = sFilename_elm_surface_data_out = sWorkspace_region2 + slash + 'elm_surfdata_' + sCase_date + '_ksat.nc'
            aVariable_ksat = [aKsat]
            aVariable_all = ['ksat']
            aUnit_all = ['mms-1']
            aDimension_all= [aDimension]
            add_multiple_variable_to_netcdf(sFilename_old, sFilename_new, aVariable_ksat, aVariable_all, aUnit_all,  aDimension_all)        
            sFilename_elm_surface_data_out =  sFilename_new
        else:
            pass


    if iFlag_optimal_parameter ==1: #add new parameter into the surface data
        #add k
        sFilename_old = sFilename_elm_surface_data_out
        sFilename_new = sFilename_elm_surface_data_out = sWorkspace_region2 + slash + 'elm_surfdata_' + sCase_date + '_new.nc'
        
        sFilename= '/compyfs/liao313/04model/e3sm/amazon/analysis/gp/kansi.tif'
        a = gdal_read_geotiff_file(sFilename)
        data_ansi0 = np.flip(a[0],0)
        data_ansi = np.power(10, data_ansi0)
       
        #add fover
        sFilename= '/compyfs/liao313/04model/e3sm/amazon/analysis/gp/fover.tif'
        a = gdal_read_geotiff_file(sFilename)
        data_fover = np.flip(a[0],0)
   
        aData_all = [data_ansi,data_fover]
        aDimension_all= [aDimension,aDimension]
        aVailable_all = ['anisotropy','fover']
        aUnit_all=['ms','unitless']
        
        add_multiple_variable_to_netcdf(sFilename_old, sFilename_new,aData_all, aVailable_all, aUnit_all,  aDimension_all)
        sFilename_elm_surface_data_out= sFilename_new

    #prepare namelist
    if iFlag_elm ==1:
        if (iFlag_initial !=1):
            #normal case,
            ofs = open(sFilename_elm_namelist, 'w')
            sCommand_out = "fsurdat = " + "'" \
                + sFilename_elm_surface_data_out  + "'" + '\n'
            ofs.write(sCommand_out)
            sCommand_out = "flndtopo = " + "'" \
                + sFilename_elm_surface_data_out  + "'" + '\n'
            ofs.write(sCommand_out)
            if (iFlag_default ==1 ):
                #sLine = "dHkdepth = " + sHkdepth + '\n'
                #ofs.write(sLine)
                #sLine = "fover = " + sFover + '\n'
                #ofs.write(sLine)
                sLine = 'hist_empty_htapes = .true.' + '\n'
                ofs.write(sLine)
                sLine = "hist_fincl1 = 'QOVER', 'QDRAI', 'QRUNOFF', 'ZWT', 'QCHARGE' "  + '\n'
                ofs.write(sLine)

            else:
                #sLine = "use_var_soil_thick = .true." + '\n'
                #ofs.write(sLine)
                sLine = "use_h2sc = .true." + '\n'
                ofs.write(sLine)
                sLine = "hydraulic_anisotropy = " + sHydraulic_anisotropy + '\n'
                ofs.write(sLine)
                sLine = "fover = " + sFover + '\n'
                ofs.write(sLine)
                sLine = 'hist_empty_htapes = .true.' + '\n'
                ofs.write(sLine)
                #sLine = "hist_fincl1 = 'QOVER', 'QDRAI', 'QRUNOFF', 'ZWT', 'QCHARGE','hk_sat','anisotropy' "  + '\n'
                sLine = "hist_fincl1 = 'QOVER', 'QDRAI', 'QRUNOFF', 'ZWT', 'QCHARGE','hk_sat','anisotropy','sur_elev','sur_slp','wt_slp','gage_height' "  + '\n'

                ofs.write(sLine)
                pass

            ofs.close()

        else:
            ofs = open(sFilename_elm_namelist, 'w')
            sCommand_out = "fsurdat = " + "'" \
                + sFilename_elm_surface_data_out + "'" + '\n'
            ofs.write(sCommand_out)
            sCommand_out = "flndtopo = " + "'" \
                + sFilename_elm_surface_data_out  + "'" + '\n'
            ofs.write(sCommand_out)
            if (iFlag_default ==1 ):
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
                sLine = "hist_fincl1 = 'QOVER', 'QDRAI', 'QRUNOFF', 'ZWT', 'QCHARGE','hk_sat','anisotropy','sur_elev','sur_slp','wt_slp','gage_height', 'RAIN','SNOW','QSOIL', 'QVEGE','QVEGT' "  + '\n'
                ofs.write(sLine)

            #this is a case that use existing restart file
            #be careful with the filename!!!
            sLine = "finidat = " + "'"+ sFilename_initial +"'" + '\n'
            ofs.write(sLine)
            ofs.close()
    else:
        ofs = open(sFilename_elm_namelist, 'w')
        sLine = 'dtlimit=2.0e0' + '\n'
        ofs.write(sLine)
        ofs.close()
        pass
    #mosart

    if iFlag_mosart ==1:        
        ofs = open(sFilename_mosart_namelist, 'w')
        #sLine = 'rtmhist_nhtfrq=0' + '\n'
        #ofs.write(sLine)
        sLine = 'frivinp_rtm = ' + "'" + sFilename_mosart_parameter + "'" + '\n'
        ofs.write(sLine)
        #sLine = 'rtmhist_fincl1= "area"' + '\n'
        #ofs.write(sLine)
        sLine = 'routingmethod = 1'+ '\n'
        ofs.write(sLine)
        sLine = 'inundflag = .false.'+ '\n'
        ofs.write(sLine)
        #opt_elevprof = 1
        ofs.close()

    if iFlag_atm == 1:
        pass
    else:       
        if iFlag_elm_spinup ==1:
            #this is a case for spin up
            ofs = open(sFilename_datm_namelist, 'w')
            sLine = 'taxmode = "cycle", "cycle", "cycle"' + '\n'
            ofs.write(sLine)
            ofs.close()
            pass
        else:
            pass
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
    if (iFlag_elm_spinup ==1):
        aParameter_case = pye3sm_read_case_configuration_file(sFilename_case_configuration,\
                                                             iFlag_atm_in = iFlag_atm,\
                                                              iFlag_elm_spinup_in = iFlag_elm_spinup,\
                                                              iFlag_elm_in= iFlag_elm,\
                                                              iFlag_mosart_in= iFlag_mosart,\
                                                              iYear_start_in = 1890, \
                                                              iYear_end_in = 1919,\
                                                              iYear_data_end_in = 2009, \
                                                              iYear_data_start_in = 1980   ,\
                                                              iCase_index_in = iCase, \
                                                              sDate_in = sDate, \
                                                              sModel_in = sModel,\
                                                              sRegion_in = sRegion,\
                                                              sFilename_atm_domain_in=  sFilename_atm_domain,\
                                                              sFilename_datm_namelist_in =  sFilename_datm_namelist ,\
                                                              sFilename_elm_namelist_in =   sFilename_elm_namelist, \
                                                              sFilename_elm_domain_in=sFilename_elm_domain_out, \
                                                              sFilename_mosart_namelist_in = sFilename_mosart_namelist, \
                                                              sFilename_mosart_parameter_in = sFilename_mosart_parameter, \
                                                              sWorkspace_scratch_in =   sWorkspace_scratch)
        pass
    else:
        iYear_start = 1980
        iYear_end = 2009       
         
        aParameter_case = pye3sm_read_case_configuration_file(sFilename_case_configuration,\
                                                              iFlag_elm_spinup_in = iFlag_elm_spinup,\
                                                              iFlag_atm_in = iFlag_atm,\
                                                              iFlag_elm_in= iFlag_elm,\
                                                              iFlag_mosart_in= iFlag_mosart,\
                                                              iYear_start_in = iYear_start, 
                                                              iYear_end_in = iYear_end,\
                                                              iYear_data_end_in = 2009, \
                                                              iYear_data_start_in = 1980  , \
                                                              iCase_index_in = iCase, \
                                                              sDate_in = sDate, \
                                                              sModel_in = sModel,\
                                                              sRegion_in = sRegion,\
                                                              sFilename_atm_domain_in = sFilename_atm_domain,\
                                                              sFilename_datm_namelist_in = sFilename_datm_namelist ,\
                                                              sFilename_elm_namelist_in = sFilename_elm_namelist, \
                                                              sFilename_elm_domain_in = sFilename_elm_domain, \
                                                              sFilename_mosart_namelist_in = sFilename_mosart_namelist, \
                                                              sFilename_mosart_parameter_in = sFilename_mosart_parameter, \
                                                              sWorkspace_scratch_in =   sWorkspace_scratch )
        pass
        #print(aParameter_case)

    oCase = pycase(aParameter_case)
    e3sm_create_case(oE3SM, oCase, \
    iFlag_replace_datm_forcing=iFlag_replace_datm_forcing,\
    iFlag_replace_dlnd_forcing= iFlag_replace_dlnd_forcing)
