import numpy as np
import os

from datetime import datetime
from scipy.io import netcdf
import getpass
from netCDF4 import Dataset

from pye3sm.elm.mesh.unstructured.ReadConfigurationFile import ReadConfigurationFile

from pye3sm.elm.mesh.structured.ComputeLatLonAtVertex import ComputeLatLonAtVertex

from pye3sm.elm.mesh.structured.twod.create_customized_elm_surface_file_2d import create_customized_elm_surface_file_2d
from pye3sm.elm.mesh.structured.twod.create_customized_elm_domain_file_2d import create_customized_elm_domain_file_2d
from pye3sm.elm.mesh.unstructured.create_customized_elm_surface_file_1d import create_customized_elm_surface_file_1d
from pye3sm.elm.mesh.unstructured.create_customized_elm_domain_file_1d import create_customized_elm_domain_file_1d

def create_customized_elm_domain( aLon, aLat, aMask_in, dLon, dLat, \
        sFilename_configuration, \
        sFilename_surface_data_in,\
        sFilename_domain_file_in,\
        sFilename_surface_data_out,
        sFilename_domain_file_out):

    aShape = aLon.shape
    iDimension = len(aShape)
    if iDimension ==1:
        iFlag_1d = 1
    else:
        iFlag_1d = 0

    print('1) Reading configuration file')

    cfg = ReadConfigurationFile(sFilename_configuration)

    print('2) Reading latitude/longitude @ cell centroid')
   
   
    print('3) Computing latitude/longitude @ cell vertex')
    aLatV, aLonV = ComputeLatLonAtVertex(iFlag_1d, \
        aLon,aLat, \
         dLon, dLat)


    if iFlag_1d == 1:
        fsurdat    = create_customized_elm_surface_file_1d( aLon, aLat, \
                        sFilename_surface_data_in, \
                        sFilename_surface_data_out, \
                        cfg['set_natural_veg_frac_to_one'])

        print('5) Creating CLM domain')
        fdomain    = create_customized_elm_domain_file_1d( aLon, aLat, \
                        aLonV, aLatV,\
                             sFilename_domain_file_in, \
                       sFilename_domain_file_out)

    
    else:

        print('4) Creating CLM surface dataset')
        fsurdat    = create_customized_elm_surface_file_2d( aLon, aLat,aMask_in, \
                        sFilename_surface_data_in, \
                        sFilename_surface_data_out, \
                        cfg['set_natural_veg_frac_to_one'])

        print('5) Creating CLM domain')
        fdomain    = create_customized_elm_domain_file_2d(aLon, aLat, aMask_in, \
                      aLonV,  aLatV, \
                             sFilename_domain_file_in, \
                       sFilename_domain_file_out)

    return sFilename_surface_data_out


