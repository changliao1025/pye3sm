#the purpose of this script is to prepare a dem dataset for visulization reference
import os , sys
import osr
import numpy as np
from netCDF4 import Dataset #it maybe be replaced by gdal 
#maybe not needed

#import library
sSystem_paths = os.environ['PATH'].split(os.pathsep)
sys.path.extend(sSystem_paths)
#import global variable
from pyes.system.define_global_variables import *  
from pyes.gis.gdal.write.gdal_write_envi_file import gdal_write_envi_file

sPath_pye3sm = sWorkspace_code +  slash + 'python' + slash + 'e3sm' + slash + 'e3sm_python'
sys.path.append(sPath_pye3sm)
from e3sm.shared import oE3SM
from e3sm.shared.e3sm_read_configuration_file import e3sm_read_configuration_file



#prepare the header in
pHeaderParameters = {}    
pHeaderParameters['ncolumn'] = '720'
pHeaderParameters['nrow'] = '360'
pHeaderParameters['ULlon'] = '-180'
pHeaderParameters['ULlat'] = '90'
pHeaderParameters['pixelSize'] = '0.5'
pHeaderParameters['nband'] = '1'
pHeaderParameters['offset'] = '0'
pHeaderParameters['data_type'] = '4'
pHeaderParameters['bsq'] = 'bsq'
pHeaderParameters['byte_order'] = '0'
pHeaderParameters['missing_value'] = '-9999'
def elm_prepare_dem():


    sFilename_old = '/compyfs/inputdata/lnd/clm2/surfdata_map' + slash + 'surfdata_0.5x0.5_simyr2010_c191025.nc'
    pDatasets_in = Dataset(sFilename_old)
    netcdf_format = pDatasets_in.file_format



    for sKey, aValue in pDatasets_in.variables.items():        
        print(aValue.datatype)
        print( aValue.dimensions)
        # we need to take care of rec dimension
        dummy = aValue.dimensions
        if sKey == 'TOPO':
            aDem = aValue[:]
            break
          
         
    #save as envi data file
    aGrid = np.flip(aDem,0)

    pSpatial =osr.SpatialReference()
    pSpatial.ImportFromEPSG(4326)

    sFilename_envi = '/people/liao313/data/h2sc/global/raster/dem/dem.dat'
    gdal_write_envi_file(sFilename_envi, aGrid,\
        float(pHeaderParameters['pixelSize']),\
         float(pHeaderParameters['ULlon']),\
              float(pHeaderParameters['ULlat']),\
                  -9999.0, pSpatial)


    return
if __name__ == '__main__':
    elm_prepare_dem()