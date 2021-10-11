import os
import numpy as np
from netCDF4 import Dataset

from datetime import datetime
from scipy.io import netcdf
import getpass
def create_customized_elm_domain_file_2d(aLon_region,aLat_region,  \
    aLonV_region,aLatV_region,  sFilename_domain_file_in, \
    sFilename_domain_file_out):

    

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

    aShape = aLon_region.shape
    nrow_original = aShape[0]
    ncolumn_original = aShape[1]


    nj,ni, nv = aLonV_region.shape
    

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
            data = aLon_region
        elif varname == 'yc':
            data = aLat_region
        elif varname == 'xv':
            data = aLonV_region
        elif varname == 'yv':
            data = aLatV_region
        elif varname == 'mask':
            data = np.ones( (nj, ni) )
        elif varname == 'frac':
            data = np.ones( (nj, ni) )
        elif varname == 'area':
            if aLonV_region.shape[2] == 3:
                ax = aLonV_region[:,:,0]
                ay = aLatV_region[:,:,0]
                bx = aLonV_region[:,:,1]
                by = aLatV_region[:,:,1]
                cx = aLonV_region[:,:,2]
                cy = aLonV_region[:,:,2]

                data = 0.5*(ax*(by-cy) + bx*(cy-ay) + cx*(ay-by))
            elif aLonV_region.shape[2] == 4:
                data = (aLonV_region[:,:,0] - aLonV_region[:,:,1]) * (aLatV_region[:,:,0] - aLatV_region[:,:,2])
            else:
                raise NameError('Added area computation')
        
        var[varname][:] = data 


    ncid_inq.close()
    ncid_out.close()

    return sFilename_domain_file_out