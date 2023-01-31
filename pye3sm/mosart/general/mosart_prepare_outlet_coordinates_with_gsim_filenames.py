import numpy as np
from pyearth.toolbox.reader.text_reader_string import text_reader_string

def mosart_prepare_outlet_coordinates_with_gsim_filenames(sFilename_mosart_gsim_info, iSkipline_in=1):
    """
    Extract global outlet indicex for gsim discahrge evaluation

    Args:
        sFilename_mosart_gsim_info (str): The gsim filename
        iSkipline_in (int, optional): how many line to be skipped. Defaults to 1.

    Returns:
        tuple[list, list, list, list, list]: aBasin, aLat, aLon, aID, aFilename_gsim
    """
    #read the text file
    data_all = text_reader_string(sFilename_mosart_gsim_info, iSkipline_in=1)
    aBasin = data_all[:, 0]
    aFilename_gsim = data_all[:, 1]

    aLon = data_all[:, 2]
    aLon = aLon.astype(np.float)

    aLat =  data_all[:, 3]
    aLat = aLat.astype(np.float)
    
    aID = data_all[:, 4]
    aID = aID.astype(np.long)        

    return aBasin, aLat, aLon, aID, aFilename_gsim