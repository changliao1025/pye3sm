import os
import numpy as np
import netCDF4 as nc
from pye3sm.mesh.structured.e3sm_create_structured_domain_file import e3sm_create_structured_domain_file
def e3sm_create_structured_envelope_domain_file( sFilename_domain_file_in, sFilename_structured_domain_file_out, 
                                                dResolution_x_in, dResolution_y_in):
    #this function creates a 2D structured domain file based on an unstructured domain file

    #read unstructured domain file
    if os.path.exists(sFilename_domain_file_in):
        pass
    else:
        print(sFilename_domain_file_in)
        return
    
    aDatasets = nc.Dataset(sFilename_domain_file_in)
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


    #get max/min information based on corner instead of center
    grid_corner_lon = grid_corner_lon[np.where(grid_corner_lon != -9999)]
    
    grid_corner_lat = grid_corner_lat[np.where(grid_corner_lat != -9999)]
  

    dLon_min = np.min(grid_corner_lon)
    dLon_max = np.max(grid_corner_lon)
    dLat_min = np.min(grid_corner_lat)
    dLat_max = np.max(grid_corner_lat)

    
    #determine structure boundary 

    #use the global as the 

    #the resolution must be 0.5, 0.25 etc

    #maybe adding a checkpoint here to confirm it


    nrow0 = 180 / dResolution_y_in
    ncolumn0 = 360 / dResolution_x_in

    nleft  = np.floor(  (dLon_min - (-180)) /(dResolution_x_in)  )
    nright = np.ceil(  (dLon_max - (-180)) /(dResolution_x_in)  )

    ntop  = np.floor(  (90 - dLat_max) /(dResolution_x_in)  )
    nbot = np.ceil(  (90 - dLat_min) /(dResolution_x_in)  )

    nrow = int(nbot-ntop)
    ncolumn = int(nright - nleft)

    #setup domain information

    aLon_region = np.full( (nrow, ncolumn), -9999, dtype=float )
    aLat_region= np.full( (nrow, ncolumn), -9999, dtype=float )
    aLonV_region= np.full( (nrow, ncolumn, 4), -9999, dtype=float )
    aLatV_region=np.full( (nrow, ncolumn, 4), -9999, dtype=float )

    for i in range(nrow):
        for j in range(ncolumn):
            aLon_region[i, j] = (-180 + (nleft + j) * dResolution_x_in) + 0.5 * dResolution_x_in
            aLat_region[i, j] = (90 - (ntop + i ) * dResolution_y_in ) + 0.5 * dResolution_y_in

            aLonV_region[i, j, 0] = aLon_region[i, j] - 0.5 * dResolution_x_in
            aLonV_region[i, j, 1] = aLon_region[i, j] - 0.5 * dResolution_x_in
            aLonV_region[i, j, 2] = aLon_region[i, j] + 0.5 * dResolution_x_in
            aLonV_region[i, j, 3] = aLon_region[i, j] + 0.5 * dResolution_x_in

            aLatV_region[i, j, 0] = aLat_region[i, j] - 0.5 * dResolution_y_in
            aLatV_region[i, j, 1] = aLat_region[i, j] + 0.5 * dResolution_y_in
            aLatV_region[i, j, 2] = aLat_region[i, j] + 0.5 * dResolution_y_in
            aLatV_region[i, j, 3] = aLat_region[i, j] - 0.5 * dResolution_y_in
    
    e3sm_create_structured_domain_file(aLon_region, aLat_region, aLonV_region, aLatV_region, sFilename_structured_domain_file_out)







    return

if __name__ == '__main__':

    sFilename_domain_source = '/compyfs/liao313/04model/e3sm/susquehanna/cases_aux/e3sm20230120001/mosart_susquehanna_domain_mpas.nc'  #elm
    sFilename_structured_domain_file_out ='/compyfs/liao313/04model/e3sm/susquehanna/cases_aux/e3sm20230120001/mosart_susquehanna_domain_halfdegree.nc'  #

    e3sm_create_structured_envelope_domain_file(sFilename_domain_source, sFilename_structured_domain_file_out,0.5, 0.5)