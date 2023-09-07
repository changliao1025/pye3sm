import os
import glob
import shutil
import numpy as np
import netCDF4 as nc
import xml.etree.ElementTree as ET
from pyearth.toolbox.reader.parse_xml_file import parse_xml_file, parse_xml_file_lnd
def elm_extract_data_mode_from_domain_file(sFilename_data_model_origin, 
                                           sFilename_regional_domain, 
                                           sWorkspace_output_region, 
                                           iYear_start_in=None, 
                                           iYear_end_in=None):
    
    if iYear_start_in is None:
        iYear_start = 1980
    else:
        iYear_start = iYear_start_in
    
    if iYear_end_in is None:
        iYear_end = 2010
    else:
        iYear_end = iYear_end_in

    sFilename_domain,aField_domain, sFolder, aField, aFilename = parse_xml_file_lnd(sFilename_data_model_origin)
    #read the data model file to obtain the domain file and the list of data file

    #there are possibly two scenarios: an independent domain file or a domain file for each data file built in the data model file
    #currently, the first data file is used to store the share domain information
    
    if not os.path.exists(sFilename_domain):
        raise NameError('File not found: ' + sFilename_domain)

    #read the domain file
    pDomain = nc.Dataset(sFilename_domain, 'r')
    aLon = pDomain.variables['lon'][:]
    aLat = pDomain.variables['lat'][:]
    
    dLon_min = np.min(aLon)
    dLon_max = np.max(aLon)
    dLat_min = np.min(aLat)
    dLat_max = np.max(aLat)


    #get the dimension of the data
    nrow = len(aLat)
    ncolumn = len(aLon)

    #get resolution
    dResolution_x = 0.05 #(dLon_max-dLon_min) / (ncolumn - 1)
    dResolution_y = 0.05 #(dLat_max-dLat_min) / (nrow - 1)

    
    #the information is likley 2D in the current setting
    #the lon and lat are center instead of corner
    

    #read the data file

    #read the regional domain file
    #an actual domain file will include center and vertex information

    pDomain_region = nc.Dataset(sFilename_regional_domain, 'r')
    aLon_region = pDomain_region.variables['xc'][:]
    aLat_region = pDomain_region.variables['yc'][:]

    dLon_min_region = np.min(aLon_region)
    dLon_max_region = np.max(aLon_region)
    dLat_min_region = np.min(aLat_region)
    dLat_max_region = np.max(aLat_region)

    #check whether the regional is 1d or 2d
    
    iFlag_1d = 1
    
   

    
    #map 1d or 2d to 2d
    if iFlag_1d == 1:
        
        iIndex_start_x = int( (dLon_min_region - dLon_min)/dResolution_x )
        iIndex_end_x = int( (dLon_max_region - dLon_min)/dResolution_x )

        iIndex_start_y = int( (dLat_min_region - dLat_min)/dResolution_y )
        iIndex_end_y = int( (dLat_max_region - dLat_min)/dResolution_y )     

        ncolumn_region = iIndex_end_x-iIndex_start_x + 1
        #int((dLon_max_region-dLon_min_region) /dResolution_x) +1 
        nrow_region = iIndex_end_y-iIndex_start_y + 1
        #int((dLat_max_region - dLat_min_region) /dResolution_y) + 1
 
        pass

    #extract the data based on the regional domain file

    #the output file will also be 2d, following the master file
    nFile = len(aFilename)

    for iYear in range(iYear_start, iYear_end+1):
        sYear = '{:04d}'.format(iYear)
        dummy = '*'+sYear+'*'
        sRegex = os.path.join( sFolder, dummy )

        for sFilename_global in glob.glob(sRegex):       

            #extract filename from the full path
            sFilename = os.path.basename(sFilename_global)

            sFilename_out = sWorkspace_output_region + '/' + sFilename

            if os.path.exists(sFilename_out):
                os.remove(sFilename_out)

            pDatasets_in = nc.Dataset(sFilename_global, 'r')
            pDatasets_out = nc.Dataset(sFilename_out, 'w', format='NETCDF3_CLASSIC')
            for sKey, iValue in pDatasets_in.dimensions.items():
                dummy = len(iValue)
                if sKey == 'lon':
                    pDatasets_out.createDimension(sKey, ncolumn_region)
                else:
                    if sKey == 'lat':
                        pDatasets_out.createDimension(sKey, nrow_region)
                    else:
                        pDatasets_out.createDimension(sKey, dummy )

            #loop through all variables in the file
            #Copy variables
            for sKey, aValue in pDatasets_in.variables.items():        
                # we need to take care of rec dimension
                dummy = aValue.dimensions
                #check whether this dimension include lat and lon
                outVar = pDatasets_out.createVariable(sKey, aValue.datatype, dummy )        
                for sAttribute in aValue.ncattrs():            
                    outVar.setncatts( { sAttribute: aValue.getncattr(sAttribute) } )


                if 'lon' in dummy and 'lat' in dummy:                
                    outVar[:] = aValue[:][:,iIndex_start_y:iIndex_end_y+1, iIndex_start_x:iIndex_end_x+1]
                else:
                    if 'lon' in dummy:
                        outVar[:] = aValue[:][iIndex_start_x:iIndex_end_x+1]
                    else:
                        if 'lat' in dummy:
                            outVar[:] = aValue[:][iIndex_start_y:iIndex_end_y+1]
                        else:
                            outVar[:] = aValue[:]

                # close the output file


            pDatasets_in.close()
            pDatasets_out.close()
            print(sFilename_out, ' is processed!')

    
    #save to a new file in the output folder
    sFilenama_data_model_new = sWorkspace_output_region + '/' + os.path.basename(sFilename_data_model_origin)
    if os.path.exists(sFilenama_data_model_new):
        os.remove(sFilenama_data_model_new)

    #copy the data model file to the output folder
    #shutil.copyfile(sFilename_data_model_origin, sFilenama_data_model_new)
    #update the data model file
    tree = ET.parse(sFilename_data_model_origin)
    root = tree.getroot()

    elems = root.findall('./domainInfo/filePath')
    for elem in elems:
        elem.txt = sWorkspace_output_region

    elems = root.findall('./fieldInfo/filePath')
    for elem in elems:
        elem.txt = sWorkspace_output_region
    
    tree.write(sFilenama_data_model_new)

    print('Finished!')

    return sFilenama_data_model_new