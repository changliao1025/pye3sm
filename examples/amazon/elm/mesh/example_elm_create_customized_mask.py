import os, sys, stat
from pathlib import Path

import numpy as np
import datetime
from osgeo import gdal, osr 
from shutil import copyfile
from pyearth.system.define_global_variables import *
from pyearth.gis.location.convert_lat_lon_range import convert_180_to_360


from pye3sm.elm.mesh.create_customized_elm_domain import create_customized_elm_domain

from pye3sm.case.e3sm_create_case import e3sm_create_case
from pye3sm.shared.e3sm import pye3sm
from pye3sm.shared.case import pycase
from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_e3sm_configuration_file
from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_case_configuration_file
from pye3sm.mosart.mesh.create_customized_mosart_domain import create_customized_mosart_domain
from pyearth.gis.gdal.write.gdal_write_geotiff_file import gdal_write_geotiff_file

from pye3sm.elm.mesh.elm_extract_grid_latlon_from_mosart import elm_extract_grid_latlon_from_mosart
sModel = 'e3sm'
#sRegion ='site'
sRegion ='amazon'
iCase = 1
iFlag_rof = 1
iFlag_lnd=1
iFlag_elmmosart =1
iFlag_create_mosart_grid = 1
iFlag_create_elm_grid = 1
iFlag_2d_to_1d = 0 
iFlag_create_case = 1 
iFlag_submit_case = 0
sDate = '20211202'
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


#for a single grid case, we can create this file on the fly
sPath = os.path.dirname(os.path.realpath(__file__))
pDate = datetime.datetime.today()
sDate_default = "{:04d}".format(pDate.year) + "{:02d}".format(pDate.month) + "{:02d}".format(pDate.day)
sCase_spinup =  sModel + sDate_spinup + "{:03d}".format(1)


iFlag_default = 0
iFlag_debug = 0 #is this a debug run
iFlag_branch = 0
iFlag_initial = 0 #use restart file as initial
iFlag_spinup = 0 #is this a spinup run
iFlag_short = 1 #do you run it on short queue
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
sFilename_initial = '/compyfs/liao313/e3sm_scratch/' \
        + sCase_spinup + '/run/' \
        + sCase_spinup +  '.elm2.rh0.1979-01-01-00000.nc'
#generate mosart first then use the mosart lat/lon information for elm
sFilename_mosart_netcdf = '/compyfs/inputdata/rof/mosart/MOSART_Global_half_20210616.nc'

#'/compyfs/inputdata/lnd/clm2/surfdata_map/surfdata_0.5x0.5_simyr2010_c191025_20210127.nc'

sFilename_e3sm_configuration = '/qfs/people/liao313/workspace/python/pye3sm/pye3sm/e3sm.xml'
sFilename_case_configuration = '/qfs/people/liao313/workspace/python/pye3sm/pye3sm/case.xml'
sCIME_directory ='/qfs/people/liao313/workspace/fortran/e3sm/E3SM_H2SC/cime/scripts'
sFilename_configuration = '/people/liao313/workspace/python/pye3sm/pye3sm/elm/grid/elm_sparse_grid.cfg'



dHydraulic_anisotropy = 1.0
sHydraulic_anisotropy = "{:0f}".format( dHydraulic_anisotropy)

dFover = 0.6 
sFover = "{:0f}".format( dFover)

sCase_date = sDate + "{:03d}".format(iCase)
sCase = sModel + sDate + "{:03d}".format(iCase)

sWorkspace_region2 = sWorkspace_region1 + slash + sCase
if not os.path.exists(sWorkspace_region2):
    Path(sWorkspace_region2).mkdir(parents=True, exist_ok=True)



lCellID_outlet_in=128418
dResolution = 0.5


if iFlag_create_mosart_grid ==1: 

    sFilename_mosart_netcdf_out = sWorkspace_region2 + slash + 'mosart_'+ sCase_date + '.nc'
    create_customized_mosart_domain(iFlag_2d_to_1d, sFilename_mosart_netcdf,sFilename_mosart_netcdf_out, lCellID_outlet_in)

sFilename_mosart_input = sWorkspace_region2 + slash + 'mosart_' + sCase_date + '.nc'

if not os.path.exists(sFilename_mosart_input):    
    copyfile(sFilename_mosart_netcdf_out, sFilename_mosart_input)


if iFlag_create_elm_grid ==1:
    aLon, aLat, aMask = elm_extract_grid_latlon_from_mosart(sFilename_mosart_netcdf_out)

#resolution
#flip mask
    aMask = np.flip(aMask, 0)
    dLon_min = np.min(aLon)
    dLon_max = np.max(aLon)
    dLat_min = np.min(aLat)
    dLat_max = np.max(aLat)
    #dimension
    nrow = np.array(aMask).shape[0]
    ncolumn = np.array(aMask).shape[1]
    
    dResolution_x = (dLon_max - dLon_min) / (ncolumn-1)
    dResolution_y = (dLat_max - dLat_min) / (nrow-1)

    print('Prepare the map grid')
   
    longitude = np.arange(dLon_min, dLon_max , dResolution_x)
    latitude = np.arange( dLat_max, dLat_min, -1*dResolution_y)
    grid_x, grid_y = np.meshgrid(longitude, latitude)
    #prepare the header in
    pHeaderParameters = {}    
    pHeaderParameters['ncolumn'] = "{:0d}".format(ncolumn)
    pHeaderParameters['nrow'] = "{:0d}".format(nrow)
    pHeaderParameters['ULlon'] = "{:0f}".format(dLon_min-0.5 * dResolution_x)
    pHeaderParameters['ULlat'] = "{:0f}".format(dLat_max+0.5 * dResolution_y)
    pHeaderParameters['pixelSize'] = "{:0f}".format(dResolution_x)
    pHeaderParameters['nband'] = '1'
    pHeaderParameters['offset'] = '0'
    pHeaderParameters['data_type'] = '4'
    pHeaderParameters['bsq'] = 'bsq'
    pHeaderParameters['byte_order'] = '0'
    pHeaderParameters['missing_value'] = '-9999'

    sFilename_tiff = sWorkspace_region2 + slash + 'elm_mask'  + sExtension_tiff
    pSpatial = osr.SpatialReference()
    pSpatial.ImportFromEPSG(4326)
    gdal_write_geotiff_file(sFilename_tiff, aMask,\
        float(pHeaderParameters['pixelSize']),\
         float(pHeaderParameters['ULlon']),\
              float(pHeaderParameters['ULlat']),\
                  -9999.0, pSpatial)