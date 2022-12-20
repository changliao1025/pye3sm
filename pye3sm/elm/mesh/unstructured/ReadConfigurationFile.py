    

def ReadConfigurationFile(sFilename_configuration):
    # Initialization
    cfg = {'site_latlon_filename':'', \
           'sFilename_surface_data_in':'', \
           'sFilename_domain_file_in':'', \
           'clm_usrdat_name':'', \
           'dLat':[0], \
           'dLon':[0], \
           'lon_min':[-999], \
           'lon_max':[-999], \
           'set_natural_veg_frac_to_one': [0], \
           'landuse_timeseries_filename':''}
    
    # Read the file
    with open(sFilename_configuration) as fid:
        line = fid.readline()
        while line:
            if line[0] != '%':
                s = line.split()
                if 'site_latlon_filename' in line.lower():
                    cfg['site_latlon_filename'] = s[1]
                elif 'sFilename_surface_data_in' in line.lower():
                    cfg['sFilename_surface_data_in'] = s[1]
                elif 'sFilename_domain_file_in' in line.lower():
                    cfg['sFilename_domain_file_in'] = s[1]
                elif 'clm_usrdat_name' in line.lower():
                    cfg['clm_usrdat_name'] = s[1]
                elif 'dLat' in line.lower():
                    cfg['dLat'] = float(s[1])
                elif 'dLon' in line.lower():
                    cfg['dLon'] = float(s[1])
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
    print(loc)
    if loc > 0:
        cfg['out_netcdf_dir'] = cfg['site_latlon_filename'][:loc]
    else:
        cfg['out_netcdf_dir'] = './'

    return cfg