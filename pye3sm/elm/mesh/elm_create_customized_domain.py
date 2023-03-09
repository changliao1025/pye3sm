
from pye3sm.elm.mesh.structured.ComputeLatLonAtVertex import ComputeLatLonAtVertex
from pye3sm.elm.mesh.unstructured.ReadConfigurationFile import ReadConfigurationFile
from pye3sm.elm.mesh.structured.elm_create_structured_customized_surface_file import elm_create_structured_customized_surface_file
from pye3sm.mesh.structured.e3sm_create_structured_domain_file import e3sm_create_structured_domain_file
from pye3sm.elm.mesh.unstructured.elm_create_unstructured_customized_surface_file import elm_create_unstructured_customized_surface_file
from pye3sm.mesh.unstructured.e3sm_create_unstructured_domain_file_simple import e3sm_create_unstructured_domain_file_simple

def elm_create_customized_domain( aLon, aLat, aMask_in, dLon, dLat, \
        sFilename_configuration, \
        sFilename_surface_data_in,\
        sFilename_domain_file_in,\
        sFilename_surface_data_out,
        sFilename_domain_file_out):

    aShape = aLon.shape
    iDimension = len(aShape)
    if iDimension ==1:
        iFlag_1d = 1
    else:
        iFlag_1d = 0

    print('1) Reading configuration file')

    cfg = ReadConfigurationFile(sFilename_configuration)

    print('2) Reading latitude/longitude @ cell centroid')
   
   
    print('3) Computing latitude/longitude @ cell vertex')
    aLatV, aLonV = ComputeLatLonAtVertex(iFlag_1d, \
        aLon,aLat, \
         dLon, dLat)


    if iFlag_1d == 1:
        fsurdat    = elm_create_unstructured_customized_surface_file( aLon, aLat, \
                        sFilename_surface_data_in, \
                        sFilename_surface_data_out, \
                        cfg['set_natural_veg_frac_to_one'])

        print('5) Creating ELM domain')
        #fdomain    = elm_create_customized_domain_file_1d( aLon, aLat, \
        #                aLonV, aLatV,\
        #                     sFilename_domain_file_in, \
        #               sFilename_domain_file_out)

        e3sm_create_unstructured_domain_file_simple(aLon, aLat, aLonV, aLatV, sFilename_domain_file_out)               

    
    else:

        print('4) Creating ELM surface dataset')
        fsurdat    = elm_create_structured_customized_surface_file( aLon, aLat,aMask_in, \
                        sFilename_surface_data_in, \
                        sFilename_surface_data_out, \
                        cfg['set_natural_veg_frac_to_one'])

        print('5) Creating ELM domain')
        #fdomain    = elm_create_customized_domain_file_2d(aLon, aLat, aMask_in, \
        #              aLonV,  aLatV, \
        #                     sFilename_domain_file_in, \
        #               sFilename_domain_file_out)
        e3sm_create_structured_domain_file(aLon, aLat, aLonV, aLatV, sFilename_domain_file_out)  

    return sFilename_surface_data_out


