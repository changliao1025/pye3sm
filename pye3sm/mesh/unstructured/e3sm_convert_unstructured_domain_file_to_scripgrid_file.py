import os
import getpass
from datetime import datetime
import netCDF4 as nc
import numpy as np

def e3sm_convert_unstructured_domain_file_to_scripgrid_file(sFilename_domain_in, sFilename_script_out):

    if os.path.exists(sFilename_domain_in):
        pass
    else:
        print(sFilename_domain_in)
        return
    
    aDatasets = nc.Dataset(sFilename_domain_in)
    for sKey, aValue in aDatasets.variables.items():      

        if sKey == 'xc':
            grid_center_lon =  (aValue[:]).data 
        if sKey == 'yc':
            grid_center_lat =  (aValue[:]).data 
        if sKey == 'xv':
            grid_corner_lon =  (aValue[:]).data 
        if sKey == 'yv':
            grid_corner_lat =  (aValue[:]).data 
        if sKey == 'mask':
            grid_imask =  (aValue[:]).data
        if sKey == 'area':
            grid_area =  (aValue[:]).data


    ndim_center = len(grid_center_lon.shape)
    ndim_vertex = len(grid_corner_lon.shape)
    
    grid_rank = 1 # mesh is treated as unstructured            
    
    if ndim_vertex == 3:
        nrow,  ncolumn, nvertex = grid_corner_lon.shape
        pass
    else:          
        nrow, nvertex = grid_corner_lon.shape
        ncolumn = 1
    print('be careful with your data dimension')
    pass   

    ncell = nrow * ncolumn
    grid_center_lon.shape=(ncell, 1)
    grid_center_lat.shape=(ncell, 1)
    
    grid_corner_lon.shape=(ncell ,nvertex)
    grid_corner_lat.shape=(ncell, nvertex)

    grid_imask.shape=(ncell, 1)
    grid_area.shape=(ncell, 1)

    for i in range ( ncell):
        for j in range(1, nvertex):
            if grid_corner_lat[i,j] == -9999:                
                grid_corner_lon[i,j] = grid_corner_lon[i, j-1]
                grid_corner_lat[i,j] = grid_corner_lat[i, j-1]
  

    pDatasets_out = nc.Dataset(sFilename_script_out, mode='w', format='NETCDF3_CLASSIC')

    pDatasets_out.createDimension('grid_size', ncell)
    pDatasets_out.createDimension('grid_corners', nvertex)
    pDatasets_out.createDimension('grid_rank', grid_rank)

    aDimension_list1=list()
    aDimension_list1.append('grid_size')
    aDimension_tuple1 = tuple(aDimension_list1)

    aDimension_list2=list()   
    aDimension_list2.append('grid_size')  
    aDimension_list2.append('grid_corners')  
    aDimension_tuple2 = tuple(aDimension_list2)

    aDimension_list3=list()
    aDimension_list3.append('grid_rank')  
    aDimension_tuple3 = tuple(aDimension_list3)    

    pVar = pDatasets_out.createVariable('grid_dims', 'i4', aDimension_tuple3, fill_value=-9999)        

    pVar = pDatasets_out.createVariable('grid_center_lon', float, aDimension_tuple1, fill_value=-9999)
    pVar.setncatts( { 'units': 'degrees' } )

    pVar = pDatasets_out.createVariable('grid_center_lat', float, aDimension_tuple1, fill_value=-9999)
    pVar.setncatts( { 'units': 'degrees' } )

    pVar = pDatasets_out.createVariable('grid_imask', 'i4', aDimension_tuple1, fill_value=-9999)
    pVar.setncatts( { 'units': 'unitless' } )

    pVar = pDatasets_out.createVariable('grid_corner_lon', float, aDimension_tuple2, fill_value=-9999)
    pVar.setncatts( { 'units': 'degrees' } )

    pVar = pDatasets_out.createVariable('grid_corner_lat', float, aDimension_tuple2, fill_value=-9999)
    pVar.setncatts( { 'units': 'degrees' } )

    pVar = pDatasets_out.createVariable('grid_area', float, aDimension_tuple1, fill_value=-9999)
    pVar.setncatts( { 'units': 'radians^2' } )

    for sKey, aValue in pDatasets_out.variables.items():   
        varname = sKey
        if varname == 'grid_dims':
            data = nrow
        elif varname == 'grid_center_lon':
            data = grid_center_lon    
        elif varname == 'grid_center_lat':
            data = grid_center_lat        
        elif varname == 'grid_imask':
            data = grid_imask
        elif varname == 'grid_corner_lon':
            data = grid_corner_lon    
        elif varname == 'grid_corner_lat':
            data = grid_corner_lat        
        elif varname == 'grid_area':
            data = grid_area
            pass
        aValue[:] = data 

    user_name = getpass.getuser()
    setattr(pDatasets_out,'Created_by',user_name)
    setattr(pDatasets_out,'Created_on',datetime.now().strftime('%c'))

    pDatasets_out.close()

if __name__ == '__main__':


    sFilename_domain = '/compyfs/liao313/04model/e3sm/susquehanna/cases_aux/e3sm20230120001/mosart_susquehanna_domain_mpas.nc'
  
    sFilename_out = '/compyfs/liao313/04model/e3sm/susquehanna/cases_aux/e3sm20230120001/mosart_susquehanna_scripgrid_mpas.nc'

    sFilename_domain = '/compyfs/liao313/04model/e3sm/susquehanna/cases_aux/e3sm20230120001/mosart_susquehanna_domain_halfdegree.nc'
  
    sFilename_out = '/compyfs/liao313/04model/e3sm/susquehanna/cases_aux/e3sm20230120001/mosart_susquehanna_scripgrid_halfdegree.nc'
  
    e3sm_convert_unstructured_domain_file_to_scripgrid_file(sFilename_domain,sFilename_out)
