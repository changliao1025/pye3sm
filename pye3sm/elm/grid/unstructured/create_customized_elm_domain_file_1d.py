import os
import numpy as np
import getpass
from netCDF4 import Dataset
def create_customized_elm_domain_file_1d(lat_region, lon_region, \
    latv_region, lonv_region, sFilename_domain_file_in, \
    sFilename_domain_file_out):

    from datetime import datetime
    from scipy.io import netcdf
    import getpass

    #sFilename_domain_file_out = '%s/domain_%s_%s.nc' % \
    #            (out_netcdf_dir, clm_usrdat_name, datetime.now().strftime('c%-y%m%d'))
    print('  domain: ' + sFilename_domain_file_out)

    # Check if the file is available
    if not os.path.exists(sFilename_domain_file_in):
        raise NameError('File not found: ' + sFilename_domain_file_in)
      
    ncid_inq = netcdf.netcdf_file(sFilename_domain_file_in, 'r', \
                                  mmap = False, maskandscale=True, version = 2)
    #ncid_out = netcdf.netcdf_file(sFilename_domain_file_out, 'w', version = 2)
    ncid_out = Dataset(sFilename_domain_file_out, 'w',format="NETCDF3_CLASSIC")

    
    
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

    return sFilename_domain_file_out