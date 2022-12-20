import numpy as np
def PerformFractionCoverCheck(sVariableName, aData, iFlag_set_natural_veg_frac_to_one):

    if sVariableName == 'PCT_URBAN':
        if iFlag_set_natural_veg_frac_to_one:
            aData = aData * 0
        elif np.max(np.sum(aData,axis=1)) > 0:
            print(' ')
            print('Warning: ' + sVariableName + ' is not 0. for all grids')
            print('         If you wish to create surface dataset')
            print('         with only natural vegetation, set')
            print('         iFlag_set_natural_veg_frac_to_one = 1 in CFG file')
            print(' ')

    elif sVariableName == 'PCT_CROP' or \
         sVariableName == 'PCT_WETLAND' or \
         sVariableName == 'PCT_LAKE' or \
         sVariableName == 'PCT_GLACIER':
        if iFlag_set_natural_veg_frac_to_one:
            aData = aData * 0
        elif np.max(aData) > 0:
            print(' ')
            print('Warning: ' + sVariableName + ' is not 0. for all grids')
            print('         If you wish to create surface dataset')
            print('         with only natural vegetation, set')
            print('         iFlag_set_natural_veg_frac_to_one = 1 in CFG file')
            print(' ')

    elif sVariableName == 'PCT_NATVEG':
        if iFlag_set_natural_veg_frac_to_one:
            aData = aData*0 + 100
        elif np.min(aData) < 100:
            print(' ')
            print('Warning: ' + sVariableName + ' is not 100. for all grids')
            print('         If you wish to create surface dataset')
            print('         with only natural vegetation, set')
            print('         iFlag_set_natural_veg_frac_to_one = 1 in CFG file')
            print(' ')
    
    return aData