import numpy as np
from netCDF4 import Dataset #read netcdf

from pyearth.system.define_global_variables import *     
from pye3sm.tools.mpas.namelist.convert_namelist_to_dict import convert_namelist_to_dict



def elm_retrieve_surface_data_info(oCase_in, sVariable_in):
    sWorkspace_simulation_case_run = oCase_in.sWorkspace_simulation_case_run
    sFilename_lnd_in = sWorkspace_simulation_case_run + slash + 'lnd_in'

    aParameter_lnd = convert_namelist_to_dict(sFilename_lnd_in)
    sFilename_domain = aParameter_lnd['fsurdat']
    aDatasets = Dataset(sFilename_domain)
    netcdf_format = aDatasets.file_format    
    print(netcdf_format)
    aData_out=None
    for sKey, aValue in aDatasets.variables.items():
        if sVariable_in == sKey:
            aData_out = (aValue[:]).data            
        
        
    return aData_out