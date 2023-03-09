

import getpass
from datetime import datetime
import numpy as np
import netCDF4 as nc

from pyearth.gis.location.calculate_polygon_area import calculate_polygon_area
def e3sm_create_structured_domain_file(aLon_region, aLat_region, aLonV_region, aLatV_region, 
                                       sFilename_domain_file_out, aArea_in = None):
    """
    Create a structured domain file
    

    Args:
        aLon_region (numpy): 2d array longitude, the index starts from the upper left, different from netcdf lower left
        aLat_region (numpy): 2d array latitude, the index starts from the upper left
        aLonV_region (numpy): vertices coordinates
        aLatV_region (numpy): vertices coordinates
        sFilename_domain_file_out (_type_): _description_
        aArea_in (numpy): the cell area in radians, if not provided, it will be calculated

    Returns:
        _type_: _description_
    """ 

    print('  domain: ' + sFilename_domain_file_out)

    print('  check input upside down!')

    # Check if the file is available   
    
    pDatasets_out = nc.Dataset(sFilename_domain_file_out, 'w',format="NETCDF3_CLASSIC")

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #
    #                           Define dimensions
    #
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    aShape_center= aLon_region.shape 
    aShape_vertex= aLonV_region.shape
    ndim_center = len(aShape_center)
    ndim_vertex = len(aShape_vertex)
    #check simplification setting
   

    if ndim_center==2: #typical 2D. (m*n or m* 1)
        #nrow, ncolumn = aLon_region.shape  
        nrow, ncolumn, nvertex  = aLonV_region.shape
        pass
    else:
        return
       
    dimname = 'nrow'
    pDatasets_out.createDimension(dimname, nrow)
    dimname = 'ncolumn'
    pDatasets_out.createDimension(dimname,ncolumn)    
    dimname = 'nvertex'
    pDatasets_out.createDimension(dimname,nvertex)

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #
    #                           Define variables
    #
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    aDimension_list0=list()    
    aDimension_list0.append('nrow')
    aDimension_list0.append('ncolumn') 
    aDimension_tuple0 = tuple(aDimension_list0)

    aDimension_list1=list()
    aDimension_list1.append('nrow')
    aDimension_list1.append('ncolumn') 
    aDimension_list1.append('nvertex')
    aDimension_tuple1 = tuple(aDimension_list1)

 
    
    aVariable = ['area','frac','mask','xc','xv','yc','yv']
    nVariable = len(aVariable)
    aUnit = ['area','frac','mask','xc','xv','yc','yv']
    aLongName = ['area','frac','mask','xc','xv','yc','yv']
    for i in range(nVariable):
        varname = aVariable[i]
        if varname == 'xv' or varname == 'yv':
            dtype = float
            dims  = aDimension_tuple1
        else:
            if varname == 'mask':
                dtype = 'i4'
            else:
                dtype = float
            dims  = aDimension_tuple0

        pVar = pDatasets_out.createVariable(varname, dtype, dims, fill_value=-9999)
        
        pVar.setncatts( { '_FillValue': -9999 } )
        pVar.setncatts( { 'unit':  aUnit[i] } )
        pVar.setncatts( { 'long name': aLongName[i] } )    

    user_name = getpass.getuser()
    setattr(pDatasets_out,'Created_by',user_name)
    setattr(pDatasets_out,'Created_on',datetime.now().strftime('%c'))

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    for sKey, aValue in pDatasets_out.variables.items():   
        varname = sKey
        if varname == 'xc':
            data = np.flip(aLon_region, 0) #aLon_region
        elif varname == 'yc':
            data = np.flip(aLat_region, 0)
        elif varname == 'xv':
            data = np.flip(aLonV_region, 0)
        elif varname == 'yv':
            data = np.flip(aLatV_region, 0)
        elif varname == 'mask':
            data = np.ones( aShape_center)
        elif varname == 'frac':
            data = np.ones( aShape_center) 
        elif varname == 'area':
            data = np.full( aShape_center, -9999, dtype = float )          
            if aArea_in is None:               
                for i in range(  nrow ):
                    for j in range(ncolumn):
                        aLongitude_in = aLonV_region[i, j,: ].flatten()
                        aLatitude_in = aLatV_region[i, j,:].flatten()
                        data[i, j] = calculate_polygon_area(aLongitude_in, aLatitude_in,  iFlag_radius =1)                
            
            else:
                radius= 6378137.0                      
                dummy_data = np.array(aArea_in ) #m^2
                data  = dummy_data / ( 4*np.pi*(radius**2) )
            data = np.flip(data, 0)
        
        
           
        aValue[:] = data

    pDatasets_out.close()

    return sFilename_domain_file_out
