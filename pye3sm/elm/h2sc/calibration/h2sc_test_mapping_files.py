import os
import sys
import numpy as np

from nco import nco 
from pathlib import Path #get the home directory
from osgeo import ogr, osr
from netCDF4 import Dataset #it maybe be replaced by gdal 
import netCDF4 as nc
from scipy.sparse import csr_matrix

#import library
sSystem_paths = os.environ['PATH'].split(os.pathsep)
 
#import global variable
from pyearth.system import define_global_variables
from pyearth.system.define_global_variables import *
from pyearth.gis.envi.envi_write_header import envi_write_header

sVariable = 'wtd'

sWorkspace_data = '/qfs/people/liao313/data'
sModel = 'h2sc'

def h2sc_test_mapping_files():
    sFilename_map1 = '/compyfs/inputdata/lnd/clm2/mappingdata/maps/ne30np4' + slash +   'map_0.5x0.5_nomask_to_ne30np4_nomask_aave_da_c121019.nc'

    sFilename_map2 = '/compyfs/inputdata/lnd/clm2/mappingdata/maps/ne30np4' + slash +   'map_ne30np4_to_0.5x0.5rtm_aave_da_110320.nc'

    #read the first mapping file
    aDatasets1 = Dataset(sFilename_map1)
    netcdf_format = aDatasets1.file_format
    print(netcdf_format)
    print("Print dimensions:")
    print(aDatasets1.dimensions.keys())
    print("Print variables:")
    print(aDatasets1.variables.keys())
    for sKey, aValue in aDatasets1.variables.items():
        if "dst_grid_dims" == sKey:
            dst_grid_dims1 = (aValue[:]).data
            continue
        if "frac_a" == sKey:
            frac_a1 = (aValue[:]).data
            continue
        if "frac_b" == sKey:
            frac_b1 = (aValue[:]).data
            continue
        if "col" == sKey:
            iColumn_index1 = (aValue[:]).data
            continue
        if "row" == sKey:
            iRow_index1 = (aValue[:]).data
            continue
        if "area_a" == sKey:
            area_a1 = (aValue[:]).data
            continue
        if "area_b" == sKey:
            area_b1 = (aValue[:]).data
            continue
        if "S" == sKey:
            c1 = (aValue[:]).data
            continue
    #read the second mapping file
    aDatasets2 = Dataset(sFilename_map2)
    netcdf_format = aDatasets2.file_format
    print(netcdf_format)
    print("Print dimensions:")
    print(aDatasets2.dimensions.keys())
    print("Print variables:")
    print(aDatasets2.variables.keys())
    for sKey, aValue in aDatasets2.variables.items():
        if "dst_grid_dims" == sKey:
            dst_grid_dims = (aValue[:]).data
            continue
        if "frac_a" == sKey:
            frac_a2 = (aValue[:]).data
            continue
        if "frac_b" == sKey:
            frac_b2 = (aValue[:]).data
            continue
        if "col" == sKey:
            iColumn_index2 = (aValue[:]).data
            continue
        if "row" == sKey:
            iRow_index2 = (aValue[:]).data
            continue
        if "area_a" == sKey:
            area_a2 = (aValue[:]).data
            continue
        if "area_b" == sKey:
            area_b2 = (aValue[:]).data
            continue
        if "S" == sKey:
            c2 = (aValue[:]).data
            continue

    #matlab example
    #a1 = double(ncread(mf,'col'));
    #b1 = double(ncread(mf,'row'));
    #c1 = ncread(mf,'S');
    #area_1a = ncread(mf,'area_a'); 
    #area_1b = ncread(mf,'area_b');
    #S1 = sparse(a1,b1,c1);

    nrow = 360
    ncolumn = 720 

    ngrid  = 48602
    ncell  = nrow * ncolumn 

    iRow_index1= iRow_index1.astype(int) - 1
    iColumn_index1= iColumn_index1.astype(int) - 1    
    S1 = csr_matrix((c1, (iRow_index1, iColumn_index1)), shape=( ngrid, ncell))
    S1 = np.transpose(S1)      

    iRow_index2= iRow_index2.astype(int) - 1
    iColumn_index2= iColumn_index2.astype(int) - 1    
    S2 = csr_matrix((c2, (iRow_index2, iColumn_index2)), shape=( ncell, ngrid ))
    S2 = np.transpose(S2)    

    #there are two ways to flatten the 2d data into 1d
    #first one: row major  

    #in = zeros(1,259200)+100; 
    #totalin = sum(in.*area_1a')
    #out = in*S1
    #totalout = sum(out.*area_1b','omitnan')
    #outback = out*S2
    #totaloutback = sum(outback.*area_1a','omitnan')
    
    #test swap first

    dummy0 = np.arange(6)
    print(dummy0)
    dummy1 = dummy0.reshape(2, 3)
    print(dummy1)
    dummy2 = dummy1.swapaxes(0,1)    
    print(dummy2)
    dummy3 = dummy2.reshape(1,6)
    print(dummy3)
    


    #now let's use real data
    data = np.full( (nrow, ncolumn), 1.0, dtype = float)

    data = np.random.rand(nrow, ncolumn)
    data1 = data.reshape(1, ncell)
    data21 = data.swapaxes(0,1)
    data2 = data21.reshape(1, ncell)
   
    dummy1 = data1
    total_in = np.sum(dummy1 * area_a1)
    dummy2 = dummy1 * S1
    total_out = np.sum(dummy2 * area_b1 )   
    print(total_in, total_out)
    #now convert it back    
    total_in = np.sum(dummy2 * area_a2)
    dummy3 = dummy2 * S2
    total_out = np.sum(dummy3 * area_b2 )   
    print(total_in, total_out)

    #second one: column major    
    dummy1 = data2
    print(dummy1.shape)
    total_in = np.sum(dummy1 * area_a1)
    dummy2 = dummy1 * S1
    total_out = np.sum(dummy2 * area_b1 )   
    print(total_in, total_out)
    #now convert it back          
    total_in = np.sum(dummy2 * area_a2)
    dummy3 = dummy2 * S2
    total_out = np.sum(dummy3 * area_b2 )   
    print(total_in, total_out)    
    print('finished')

if __name__ == '__main__':
    h2sc_test_mapping_files()