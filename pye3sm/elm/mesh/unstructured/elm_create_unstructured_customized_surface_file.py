import os
import numpy as np
from datetime import datetime
import getpass
import netCDF4 as nc
from pye3sm.elm.mesh.unstructured.PerformFractionCoverCheck import PerformFractionCoverCheck

def elm_create_unstructured_customized_surface_file( aLon_region, aLat_region, 
    sFilename_surface_data_in, 
    sFilename_surface_data_out, 
    set_natural_veg_frac_to_one):

    print('  surface_dataset: ' + sFilename_surface_data_out)

    if not os.path.exists(sFilename_surface_data_in):
        raise NameError('File not found: ' + sFilename_surface_data_in)
    
    ncid_inq = nc.Dataset(sFilename_surface_data_in, 'r')
    ncid_out = nc.Dataset(sFilename_surface_data_out, 'w',format="NETCDF3_CLASSIC")

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #
    #                           Define dimensions
    #
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    idim = 2
    lonlat_found = 0

    # Need to declare first in the list of dimensions for a variabl
    ncid_out.createDimension('time', None)
    for dimname in ncid_inq.dimensions:
        if dimname == 'lsmlat' or dimname == 'lsmlon':
            if dimname == 'lsmlat':
                lat_dimid = idim
            elif dimname == 'lsmlon':
                lon_dimid = idim
            if lonlat_found == 0:
                lonlat_found = 1
                ncid_out.createDimension('gridcell', len(aLon_region))
        elif dimname == 'time':
            #print(ncid_out.dimensions[dimname])
            pass
        else:
            ncid_out.createDimension(dimname, ncid_inq.dimensions[dimname].size)

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #
    #                           Define variables
    #
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    var = dict()
    for varname in ncid_inq.variables:
        dtype = ncid_inq.variables[varname].dtype
        dims  = ncid_inq.variables[varname].dimensions
        if ('lsmlat' in dims) and ('lsmlon' in dims):
            i1 = dims.index('lsmlat')
            i2 = dims.index('lsmlon')
            assert(i1 < i2)
            newdims = []
            for i in range(len(dims)):
                if dims[i] == 'lsmlat':
                    newdims.append('gridcell')
                elif dims[i] == 'lsmlon':
                    pass
                else:
                    newdims.append(dims[i])
            newdims = tuple(newdims)

            var[varname] = ncid_out.createVariable(varname, dtype, newdims)
        else:
            var[varname] = ncid_out.createVariable(varname, dtype, dims)
        for attname in ncid_inq.variables[varname].ncattrs():
            attvalue = ncid_inq.variables[varname].getncattr(attname)
            var[varname].setncattr(attname, attvalue)
        

    user_name = getpass.getuser()
    ncid_out.setncattr('Created_by',user_name)
    ncid_out.setncattr('Created_on',datetime.now().strftime('%c'))

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Find the nearest neighbor index for (aLon_region,lati_xy) within global
    # dataset
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    # Get Lat/Lon for global 2D grid
    latixy = ncid_inq.variables['LATIXY'][:]
    longxy = ncid_inq.variables['LONGXY'][:]

    # Read in global pft mask 1 = valid, 0 = invalid
    pftmask = ncid_inq.variables['PFTDATA_MASK'][:]
    i = pftmask == 0
    # mark invalid gridcells as [aLon, aLat] [-9999, -9999]
    latixy[pftmask==0] = -9999
    longxy[pftmask==0] = -9999

    # allcate memory for the index of interpolated coordinates
    if len(aLon_region.shape) == 2:
        nii, njj = aLon_region.shape
    elif len(aLon_region.shape) == 1:
        nii = len(aLon_region)
        njj = 1

    ii_idx = np.zeros( (nii,njj),dtype=int )
    jj_idx = np.zeros( (nii,njj),dtype=int )
    
    for ii in range(nii):
        for jj in range(njj):
            if aLat_region.ndim == 2:
                dist = np.sqrt((latixy - aLat_region[ii,jj])**2 + \
                            (longxy - aLon_region[ii,jj])**2)
            elif aLat_region.ndim == 1:
                assert(jj == 0)
                dist = np.sqrt((latixy - aLat_region[ii])**2 + \
                            (longxy - aLon_region[ii])**2)
            #ind = np.unravel_index(np.argmin(dist, axis=None), dist.shape)
            ind = np.where(dist == dist.min())
            if len(ind[0]) > 1:
                if len(aLat_region.shape) == 1:
                    msg = '  WARNING: Site with (aLat,aLon) = (%f,%f) has more than one cells ' % \
                        (aLat_region[ii],aLon_region[ii])
                elif len(aLat_region.shape) == 2:
                    msg = '  WARNING: Site with (aLat,aLon) = (%f,%f) has more than one cells ' % \
                        (aLat_region[ii,jj],aLon_region[ii,jj])
                print(msg)
                for kk in range(len(ind[0])):
                    msg = '\t\tPossible grid cells: %f %f' % \
                          (latixy[ind[0][kk],ind[1][kk]], longxy[ind[0][kk],ind[1][kk]])
                    print(msg)
            ii_idx[ii,jj] = ind[0][0]
            jj_idx[ii,jj] = ind[1][0]

    for varname in ncid_inq.variables:

        if ncid_inq.variables[varname].dimensions == ():
            data = ncid_inq.variables[varname][:]
        else:
            data = ncid_inq.variables[varname][:]

        if varname == 'LATIXY':
            var[varname][:] = aLat_region
        elif varname == 'LONGXY':
            var[varname][:] = aLon_region
        else:
            if len(ncid_inq.variables[varname].dimensions) == 0:
                var[varname][:] = data
            elif len(ncid_inq.variables[varname].dimensions) == 1:
                var[varname][:] = data
            elif len(ncid_inq.variables[varname].dimensions) == 2:
                if 'lsmlat' in ncid_inq.variables[varname].dimensions and \
                   'lsmlon' in ncid_inq.variables[varname].dimensions:
                    assert(ncid_inq.variables[varname].dimensions.index('lsmlat') < \
                           ncid_inq.variables[varname].dimensions.index('lsmlon'))
                    if len(aLon_region.shape) == 1:
                        nx = len(aLon_region)
                        ny = 1
                    else:
                        nx, ny = aLon_region.shape

                    data_2d = np.zeros( (nx,ny) )
                    for ii in range(nx):
                        for jj in range(ny):
                            data_2d[ii,jj] = data[ii_idx[ii,jj],jj_idx[ii,jj]]

                    data_2d_new = data_2d.reshape( (nx*ny,) )
                    

                    data_2d = PerformFractionCoverCheck(varname,data_2d_new,set_natural_veg_frac_to_one)
                    var[varname][:] = data_2d

                else:
                    var[varname][:] = data
            elif len(ncid_inq.variables[varname].dimensions) == 3:
                if 'lsmlat' in ncid_inq.variables[varname].dimensions and \
                   'lsmlon' in ncid_inq.variables[varname].dimensions:
                    if len(aLon_region.shape) == 1:
                        nx = len(aLon_region)
                        ny = 1
                    else:
                        nx, ny = aLon_region.shape

                    nz = ncid_inq.variables[varname].shape[0]
                    dims = (nz,nx,ny)
                    data_3d = np.zeros( dims )

                    for ii in range(nx):
                        for jj in range(ny):
                            for kk in range(nz):
                                data_3d[kk,ii,jj] = data[kk,ii_idx[ii,jj],jj_idx[ii,jj]]
                    data_3d_new = data_3d.reshape( (nz,nx*ny) )
                    

                    data_3d = PerformFractionCoverCheck(varname,data_3d_new,set_natural_veg_frac_to_one)
                    var[varname][:] = data_3d
                
                else:
                    var[varname][:] = data
            
            elif len(ncid_inq.variables[varname].dimensions) == 4:
                if 'lsmlat' in ncid_inq.variables[varname].dimensions and \
                   'lsmlon' in ncid_inq.variables[varname].dimensions:
                    if len(aLon_region.shape) == 1:
                        nx = len(aLon_region)
                        ny = 1
                    else:
                        nx, ny = aLon_region.shape

                    nz = ncid_inq.variables[varname].shape[0]
                    na = ncid_inq.variables[varname].shape[1]
                    dims = (nz,na,nx,ny)
                    data_4d = np.zeros( dims )

                    for ii in range(nx):
                        for jj in range(ny):
                            for kk in range(nz):
                                for ll in range(na):
                                    data_4d[kk,ll,ii,jj] = data[kk,ll,ii_idx[ii,jj],jj_idx[ii,jj]]
                    data_4d_new = data_4d.reshape( (nz,na,nx*ny) )
                    data_4d     = data_4d_new
                    del data_4d_new

                    var[varname][:] = data_4d
                
                else:
                    var[varname][:] = data
            else:
                print('error')

    ncid_inq.close()
    ncid_out.close()

    return sFilename_surface_data_out