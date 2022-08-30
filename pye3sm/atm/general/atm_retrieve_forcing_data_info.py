import numpy as np
from netCDF4 import Dataset #read netcdf
import re
from pyearth.system.define_global_variables import *     
from pye3sm.tools.mpas.namelist.convert_namelist_to_dict import convert_namelist_to_dict2
from pyearth.toolbox.reader.parse_xml_file import parse_xml_file_atm


def atm_retrieve_forcing_data_info(oCase_in, sVariable_in):
    sWorkspace_simulation_case_run = oCase_in.sWorkspace_simulation_case_run
    sFilename_datm_in = sWorkspace_simulation_case_run + slash + 'datm_in'

    aParameter_datm = convert_namelist_to_dict2(sFilename_datm_in)
    aDict = aParameter_datm['streams']
    dummy = aDict.split(",")
    ndata  = len(dummy)
    for i  in range(ndata):
        s = dummy[i]
        if sVariable_in.lower() in s.lower():
            s = s.strip()       
            s = re.sub("[\"\']", "", s)
            dummy = (s.split(" "))[0]
            sFilename = sWorkspace_simulation_case_run + slash + dummy
            
            #parse xml
            sFolder ,sField, aFilename = parse_xml_file_atm(sFilename,'fileNames')
        
    return sFolder, sField, aFilename