import os
import numpy
import numpy as np
from netCDF4 import Dataset


workspace_data = "/Volumes/mac/01data/h2sc/raster/dem/"
filename_netcdf = "MOSART_Global_half_20180606c.mao.nc"
filename_netcdf_new = "MOSART_Global_half_20180606c.chang0.nc"



filename_netcdf_in = os.path.join(workspace_data, filename_netcdf)
if os.path.exists(filename_netcdf_in):
    print("Yep, I can read that file!")
else:
    print("Nope, the path doesn't reach your file. Go research filepath in python")


filename_netcdf_out = os.path.join(workspace_data, filename_netcdf_new)


print(filename_netcdf_in)
aDatasets = Dataset(filename_netcdf_in)

netcdf_format = aDatasets.file_format
print(netcdf_format)
print("Print dimensions:")
print(aDatasets.dimensions.keys())
print("Print variables:")

print(aDatasets.variables.keys() )


#output file
datasets_out = Dataset(filename_netcdf_out, "w", format=netcdf_format)

#Copy dimensions
for sKey, iValue in aDatasets.dimensions.items():
    #print( sKey, iValue, len(iValue))
    #datasets_out.createDimension(sKey, len(iValue) if not iValue.isunlimited() else None)


    if not iValue.isunlimited():
        datasets_out.createDimension(sKey, len(iValue) )
    else:
        datasets_out.createDimension(sKey, len(iValue) )
        #None

missing_value = 0.0
dummy='nan'
# Copy variables
for sKey, aValue in aDatasets.variables.items():
    #print(sKey, aValue)
    print(aValue.datatype)
    print( aValue.dimensions)
    # we need to take care of rec dimension
    outVar = datasets_out.createVariable(sKey, aValue.datatype, aValue.dimensions)
    
    
    # Copy variable attributes
    #outVar.setncatts({k: aValue.getncattr(k) for k in aValue.ncattrs()})
    

    if "ele" in sKey:
        iFlag_fill=0
        for sAttribute in aValue.ncattrs():
            print(sAttribute)
            if( sAttribute =='_Fillvalue'):
                iFlag_fill = 1
            else:
                outVar.setncatts( { sAttribute: aValue.getncattr(sAttribute) } )
            
        if iFlag_fill ==1:
             pass
        else :
            #create a new attribute
            outVar.setncatts( { '_Fillvalue': missing_value } )
        # cope data??
        #change all fillvalue to missing_value        
        dummy_data =  (aValue[:]).data
        #dummy_data2 = dummy_data.tolist()
        #print( type(dummy_data), dummy_data)
        dummy_index = numpy.where(np.isnan(dummy_data))
        
        #print(dummy_index)
        dummy_data[dummy_index] = missing_value
        #print(dummy_data)
        

        outVar[:] = dummy_data
       
        #print(outVar[:].data[0,0])
       
                
    else:
       
        for sAttribute in aValue.ncattrs():
         
            outVar.setncatts( { sAttribute: aValue.getncattr(sAttribute) } )
        
       # cope data??
        outVar[:] = aValue[:]
# close the output file
datasets_out.close()