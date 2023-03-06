

import getpass
from datetime import datetime
import numpy as np
import netCDF4 as nc

from pyearth.gis.location.calculate_polygon_area import calculate_polygon_area
def e3sm_create_structured_domain_file(aLon_region, aLat_region, aLonV_region, aLatV_region, 
                                       sFilename_domain_file_out, aArea_in = None):
    """
    Create a domain file

    Args:
        aLon_region (numpy): _description_
        aLat_region (numpy): _description_
        aLonV_region (numpy): _description_
        aLatV_region (numpy): _description_
        sFilename_domain_file_out (_type_): _description_
        aArea_in (numpy): _description_

    Returns:
        _type_: _description_
    """ 

    print('  domain: ' + sFilename_domain_file_out)

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
    #
    #                           Copy variables
    #
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    for sKey, aValue in pDatasets_out.variables.items():   
        varname = sKey
        if varname == 'xc':
            data = aLon_region
        elif varname == 'yc':
            data = aLat_region
        elif varname == 'xv':
            data = aLonV_region
        elif varname == 'yv':
            data = aLatV_region
        elif varname == 'mask':
            data = np.ones( aShape_center)
        elif varname == 'frac':
            data = np.ones( aShape_center) 
        elif varname == 'area':
            data = np.full( aShape_center, -9999, dtype = float )          
            if aArea_in is None:               
                for j in range(  nrow ):
                    for i in range(ncolumn):
                        aLongitude_in = aLonV_region[j, i,: ].flatten()
                        aLatitude_in = aLatV_region[j, i,:].flatten()
                        data[j, i] = calculate_polygon_area(aLongitude_in, aLatitude_in,  iFlag_radius =1)                
            
            else:
                radius= 6378137.0                      
                dummy_data = np.array(aArea_in ) #m^2
                data  = dummy_data / ( 4*np.pi*(radius**2) )
        
        
           
        aValue[:] = data 

    pDatasets_out.close()

    return sFilename_domain_file_out
