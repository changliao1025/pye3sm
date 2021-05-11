import numpy as np
import os
import sys

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# - Creates a CLM45 surface dataset and domain netcdf files in an
#   unstrustured grid format for a list sites given by latitude/longitude.
# 
# - The script uses already existing CLM45 surface datasets and create
#   new dataset by finding nearest neighbor for each site.
#
# Originally developed by Gautam Bisht: 
# https://github.com/bishtgautam/matlab-script-for-clm-sparse-grid
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def main():
    cfgfilename= sys.argv[1]
    print('1) Reading configuration file: ' + cfgfilename)
    cfg        = ReadConfigurationFile(cfgfilename)
    print('2) Reading latitude/longitude @ cell centroid')
    lat, lon   = ReadLatLon(cfg['site_latlon_filename'])
    print('3) Computing latitude/longitude @ cell vertex')
    latv, lonv = ComputeLatLonAtVertex(lat, lon, cfg['dlat'], cfg['dlon'])
    print('4) Creating ELM surface dataset')
    fsurdat    = CreateCLMUgridSurfdatForELM(lat, lon,             \
                    cfg['clm_gridded_surfdata_filename'],          \
                    cfg['out_netcdf_dir'], cfg['clm_usrdat_name'], \
                    cfg['set_natural_veg_frac_to_one'])
    print('5) Creating ELM domain')
    fdomain    = CreateCLMUgridDomainForELM(lat, lon,              \
                    latv, lonv, cfg['clm_gridded_domain_filename'],\
                    cfg['out_netcdf_dir'], cfg['clm_usrdat_name'])

def generate_ELM_domain_surface_file(cfgfilename):

    print('1) Reading configuration file: ' + cfgfilename)
    cfg        = ReadConfigurationFile(cfgfilename)
    print('2) Reading latitude/longitude @ cell centroid')
    lat, lon   = ReadLatLon(cfg['site_latlon_filename'])
    print('3) Computing latitude/longitude @ cell vertex')
    latv, lonv = ComputeLatLonAtVertex(lat, lon, cfg['dlat'], cfg['dlon'])
    print('4) Creating ELM surface dataset')
    fsurdat    = CreateCLMUgridSurfdatForELM(lat, lon,             \
                    cfg['clm_gridded_surfdata_filename'],          \
                    cfg['out_netcdf_dir'], cfg['clm_usrdat_name'], \
                    cfg['set_natural_veg_frac_to_one'])
    print('5) Creating ELM domain')
    fdomain    = CreateCLMUgridDomainForELM(lat, lon,              \
                    latv, lonv, cfg['clm_gridded_domain_filename'],\
                    cfg['out_netcdf_dir'], cfg['clm_usrdat_name'])    

def ReadConfigurationFile(fname):
    # Initialization
    cfg = {'site_latlon_filename':'',       \
        'clm_gridded_surfdata_filename':'', \
        'clm_gridded_domain_filename':'',   \
        'clm_usrdat_name':'',               \
        'dlat':[0],                         \
        'dlon':[0],                         \
        'lon_min':[-999],                   \
        'lon_max':[-999],                   \
        'set_natural_veg_frac_to_one': [0], \
        'landuse_timeseries_filename':''}
    
    # Read the file
    with open(fname) as fid:
        line = fid.readline()
        while line:
            if line[0] != '%':
                s = line.split()
                if 'site_latlon_filename' in line.lower():
                    cfg['site_latlon_filename'] = s[1]
                elif 'clm_gridded_surfdata_filename' in line.lower():
                    cfg['clm_gridded_surfdata_filename'] = s[1]
                elif 'clm_gridded_domain_filename' in line.lower():
                    cfg['clm_gridded_domain_filename'] = s[1]
                elif 'clm_usrdat_name' in line.lower():
                    cfg['clm_usrdat_name'] = s[1]
                elif 'dlat' in line.lower():
                    cfg['dlat'] = float(s[1])
                elif 'dlon' in line.lower():
                    cfg['dlon'] = float(s[1])
                elif 'lon_min' in line.lower():
                    cfg['lon_min'] = float(s[1])
                elif 'lon_max' in line.lower():
                    cfg['lon_max'] = float(s[1])
                elif 'set_natural_veg_frac_to_one' in line.lower():
                    cfg['set_natural_veg_frac_to_one'] = float(s[1])
                elif 'landuse_timeseries_filename' in line.lower():
                    cfg['landuse_timeseries_filename'] = s[1]
            line = fid.readline()
    fid.close()

    loc = cfg['site_latlon_filename'].rfind('/')
    if loc > 0:
        cfg['out_netcdf_dir'] = cfg['site_latlon_filename'][:loc]
    else:
        cfg['out_netcdf_dir'] = './'

    return cfg

def ReadLatLon(fname):

    fname = fname.strip()
    tmp_str = fname.split('.')
    if tmp_str[1] == 'txt':
        lat, lon = ReadLatLonFromTxt(fname)
    else:
        raise NameError('Unsupported format to read site level lat/lon')
    return lat, lon
def ReadLatLonFromTxt(fname):

    with open(fname) as fid:
        line = fid.readline()
        cnt   = 0
        while line:
            if cnt == 0:
                num_of_sites = int(line)
                lat  = np.empty((num_of_sites,))
                lon  = np.empty((num_of_sites,))
            else:
                ss = line.split()
                lat[cnt-1] = float(ss[0])
                lon[cnt-1] = float(ss[1])

            line = fid.readline()
            cnt = cnt + 1
    if num_of_sites != cnt - 1:
        raise NameError('Lat Lon size does not matach!')

    fid.close()
    return lat,lon

def ComputeLatLonAtVertex(lat, lon, dlat, dlon):

    npts = len(lat)

    latv = np.empty((npts,4))
    lonv = np.empty((npts,4))

    for i in range(npts):
        lonv[i,:] = [lon[i]-dlon/2, lon[i]+dlon/2, lon[i]+dlon/2, lon[i]-dlon/2]
        latv[i,:] = [lat[i]-dlat/2, lat[i]-dlat/2, lat[i]+dlat/2, lat[i]+dlat/2]
    
    return latv, lonv

def CreateCLMUgridSurfdatForELM(lati_region, long_region, \
    clm_gridded_surfdata_filename, \
    out_netcdf_dir, clm_usrdat_name, \
    set_natural_veg_frac_to_one):

    from datetime import datetime
    from scipy.io import netcdf
    import getpass
    from netCDF4 import Dataset

    fname_out = '%s/surfdata_%s_%s.nc' % \
                (out_netcdf_dir, clm_usrdat_name, datetime.now().strftime('c%-y%m%d'))

    print('  surface_dataset: ' + fname_out)

    if not os.path.exists(clm_gridded_surfdata_filename):
        raise NameError('File not found: ' + clm_gridded_surfdata_filename)
    
    ncid_inq = Dataset(clm_gridded_surfdata_filename, 'r')
    ncid_out = Dataset(fname_out, 'w')

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #
    #                           Define dimensions
    #
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    idim = 1
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
                ncid_out.createDimension('gridcell', len(long_region))
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
    # Find the nearest neighbor index for (long_region,lati_xy) within global
    # dataset
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    # Get Lat/Lon for global 2D grid
    latixy = ncid_inq.variables['LATIXY'][:]
    longxy = ncid_inq.variables['LONGXY'][:]

    # Read in global pft mask 1 = valid, 0 = invalid
    pftmask = ncid_inq.variables['PFTDATA_MASK'][:]
    i = pftmask == 0
    # mark invalid gridcells as [lon, lat] [-9999, -9999]
    latixy[pftmask==0] = -9999
    longxy[pftmask==0] = -9999

    # allcate memory for the index of interpolated coordinates
    if len(long_region.shape) == 2:
        nii, njj = long_region.shape
    elif len(long_region.shape) == 1:
        nii = len(long_region)
        njj = 1

    ii_idx = np.zeros( (nii,njj),dtype=int )
    jj_idx = np.zeros( (nii,njj),dtype=int )
    
    for ii in range(nii):
        for jj in range(njj):
            if lati_region.ndim == 2:
                dist = np.sqrt((latixy - lati_region[ii,jj])**2 + \
                            (longxy - long_region[ii,jj])**2)
            elif lati_region.ndim == 1:
                assert(jj == 0)
                dist = np.sqrt((latixy - lati_region[ii])**2 + \
                            (longxy - long_region[ii])**2)
            #ind = np.unravel_index(np.argmin(dist, axis=None), dist.shape)
            ind = np.where(dist == dist.min())
            if len(ind[0]) > 1:
                if len(lati_region.shape) == 1:
                    msg = '  WARNING: Site with (lat,lon) = (%f,%f) has more than one cells ' % \
                        (lati_region[ii],long_region[ii])
                elif len(lati_region.shape) == 2:
                    msg = '  WARNING: Site with (lat,lon) = (%f,%f) has more than one cells ' % \
                        (lati_region[ii,jj],long_region[ii,jj])
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
            var[varname][:] = lati_region
        elif varname == 'LONGXY':
            var[varname][:] = long_region
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
                    if len(long_region.shape) == 1:
                        nx = len(long_region)
                        ny = 1
                    else:
                        nx, ny = long_region.shape

                    data_2d = np.zeros( (nx,ny) )
                    for ii in range(nx):
                        for jj in range(ny):
                            data_2d[ii,jj] = data[ii_idx[ii,jj],jj_idx[ii,jj]]

                    data_2d_new = data_2d.reshape( (nx*ny,) )
                    data_2d = data_2d_new
                    del data_2d_new

                    data_2d = PerformFractionCoverCheck(varname,data_2d,set_natural_veg_frac_to_one)
                    var[varname][:] = data_2d

                else:
                    var[varname][:] = data
            elif len(ncid_inq.variables[varname].dimensions) == 3:
                if 'lsmlat' in ncid_inq.variables[varname].dimensions and \
                    'lsmlon' in ncid_inq.variables[varname].dimensions:
                    if len(long_region.shape) == 1:
                        nx = len(long_region)
                        ny = 1
                    else:
                        nx, ny = long_region.shape

                    nz = ncid_inq.variables[varname].shape[0]
                    dims = (nz,nx,ny)
                    data_3d = np.zeros( dims )

                    for ii in range(nx):
                        for jj in range(ny):
                            for kk in range(nz):
                                data_3d[kk,ii,jj] = data[kk,ii_idx[ii,jj],jj_idx[ii,jj]]
                    data_3d_new = data_3d.reshape( (nz,nx*ny) )
                    data_3d     = data_3d_new
                    del data_3d_new

                    data_3d = PerformFractionCoverCheck(varname,data_3d,set_natural_veg_frac_to_one)
                    var[varname][:] = data_3d
                
                else:
                    var[varname][:] = data
            
            elif len(ncid_inq.variables[varname].dimensions) == 4:
                if 'lsmlat' in ncid_inq.variables[varname].dimensions and \
                    'lsmlon' in ncid_inq.variables[varname].dimensions:
                    if len(long_region.shape) == 1:
                        nx = len(long_region)
                        ny = 1
                    else:
                        nx, ny = long_region.shape

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

    return fname_out

def PerformFractionCoverCheck(varname, data, set_natural_veg_frac_to_one):

    if varname == 'PCT_URBAN':
        if set_natural_veg_frac_to_one:
            data = data * 0
        elif np.max(np.sum(data,axis=1)) > 0:
            print(' ')
            print('Warning: ' + varname + ' is not 0. for all grids')
            print('         If you wish to create surface dataset')
            print('         with only natural vegetation, set')
            print('         set_natural_veg_frac_to_one = 1 in CFG file')
            print(' ')

    elif varname == 'PCT_CROP' or \
        varname == 'PCT_WETLAND' or \
        varname == 'PCT_LAKE' or \
        varname == 'PCT_GLACIER':
        if set_natural_veg_frac_to_one:
            data = data * 0
        elif np.max(data) > 0:
            print(' ')
            print('Warning: ' + varname + ' is not 0. for all grids')
            print('         If you wish to create surface dataset')
            print('         with only natural vegetation, set')
            print('         set_natural_veg_frac_to_one = 1 in CFG file')
            print(' ')

    elif varname == 'PCT_NATVEG':
        if set_natural_veg_frac_to_one:
            data = data*0 + 100
        elif np.min(data) < 100:
            print(' ')
            print('Warning: ' + varname + ' is not 100. for all grids')
            print('         If you wish to create surface dataset')
            print('         with only natural vegetation, set')
            print('         set_natural_veg_frac_to_one = 1 in CFG file')
            print(' ')
    
    return data

def CreateCLMUgridDomainForELM(lat_region, lon_region, \
    latv_region, lonv_region, clm_gridded_domain_filename, \
    out_netcdf_dir, clm_usrdat_name):

    from datetime import datetime
    from scipy.io import netcdf
    import getpass

    fname_out = '%s/domain_%s_%s.nc' % \
                (out_netcdf_dir, clm_usrdat_name, datetime.now().strftime('c%-y%m%d'))
    print('  domain: ' + fname_out)

    # Check if the file is available
    if not os.path.exists(clm_gridded_domain_filename):
        raise NameError('File not found: ' + clm_gridded_domain_filename)

    ncid_inq = netcdf.netcdf_file(clm_gridded_domain_filename, 'r', \
                                    mmap = False, maskandscale=True, version = 2)
    ncid_out = netcdf.netcdf_file(fname_out, 'w', version = 2)
    
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #
    #                           Define dimensions
    #
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
    ni, nv = lonv_region.shape
    nj = 1

    for dimname in ncid_inq.dimensions:
        if dimname == 'ni':
            ncid_out.createDimension(dimname,ni)
        elif dimname == 'nj':
            ncid_out.createDimension(dimname,nj)
        elif dimname == 'nv':
            ncid_out.createDimension(dimname,nv)

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #
    #                           Define variables
    #
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    var = dict()
    for varname in ncid_inq.variables:
        dtype = ncid_inq.variables[varname].typecode()
        dims  = ncid_inq.variables[varname].dimensions

        var[varname] = ncid_out.createVariable(varname, dtype, dims)
        for attname in ncid_inq.variables[varname]._attributes:
            attvalue = getattr(ncid_inq.variables[varname],attname)
            setattr(var[varname], attname, attvalue)        

    user_name = getpass.getuser()
    setattr(ncid_out,'Created_by',user_name)
    setattr(ncid_out,'Created_on',datetime.now().strftime('%c'))

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #
    #                           Copy variables
    #
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    for varname in ncid_inq.variables:

        if varname == 'xc':
            data = lon_region
        elif varname == 'yc':
            data = lat_region
        elif varname == 'xv':
            data = lonv_region
        elif varname == 'yv':
            data = latv_region
        elif varname == 'mask':
            data = np.ones( (1,len(lon_region)) )
        elif varname == 'frac':
            data = np.ones( (1,len(lon_region)) )
        elif varname == 'area':
            if lonv_region.shape[1] == 3:
                ax = lonv_region[:,0]
                ay = latv_region[:,0]
                bx = lonv_region[:,1]
                by = latv_region[:,1]
                cx = lonv_region[:,2]
                cy = lonv_region[:,2]

                data = 0.5*(ax*(by-cy) + bx*(cy-ay) + cx*(ay-by))
            elif lonv_region.shape[1] == 4:
                data = (lonv_region[:,0] - lonv_region[:,1]) * (latv_region[:,0] - latv_region[:,2])
            else:
                raise NameError('Added area computation')
        
        var[varname][:] = data 


    ncid_inq.close()
    ncid_out.close()

    return fname_out

if __name__ == '__main__':
    main()
