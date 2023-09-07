from __future__ import absolute_import, division, print_function, \
    unicode_literals

import six

import re
import os.path
from pathlib import Path

from pye3sm.tools.namelist.containers import ReadOnlyDict
def convert_namelist_to_dict(fname, readonly=True):
    """
    Converts a namelist file to key-value pairs in dictionary.
    Parameters
    ----------
    fname : str
        The file name of the namelist
    readonly : bool, optional
        Should the resulting dictionary read-only?
    """
    # Authors
    # -------
    # Phillip J Wolfram

    # form dictionary
    nml = dict()

    regex = re.compile(r"^\s*(.*?)\s*=\s*['\"]*(.*?)['\"]*\s*\n")
    with open(fname) as f:
        for line in f:
            match = regex.findall(line)
            if len(match) > 0:
                # assumes that there is only one match per line
                nml[match[0][0].lower()] = match[0][1]
    if readonly:
        nml = ReadOnlyDict(nml)

    return nml
def preprocess_namelist_file(sFilename_in):

    #get folder
    sFolder = os.path.dirname(sFilename_in)      

    #get filename 
    sBasename = Path(sFilename_in).stem
    sFilname_new = sBasename + '_new'
    sFilename_out= os.path.join(sFolder , sFilname_new) 


    ifs=open(sFilename_in, 'r')   
    ofs=open(sFilename_out, 'w') 
    
    sLine=ifs.readline()
    iFlag_connect = 0
    while(sLine):
        sLine = sLine.rstrip()
        if sLine[-1] == ',':
            sLine_new = sLine_new + sLine    
            sLine=ifs.readline()    
            iFlag_connect =1 
            
        else:
            if iFlag_connect ==1:
                sLine_new = sLine_new + '\n'
                ofs.write(sLine_new)
                sLine_new =''
                sLine=ifs.readline()
                iFlag_connect = 0
            else:
                sLine_new = sLine + '\n'
                ofs.write(sLine_new)
                sLine_new =''
                sLine=ifs.readline()
    
    ifs.close()
    ofs.close()
    



    return sFilename_out
def convert_namelist_to_dict2(fname, readonly=True):
    """
    Converts a namelist file to key-value pairs in dictionary.
    Parameters
    ----------
    fname : str
        The file name of the namelist
    readonly : bool, optional
        Should the resulting dictionary read-only?
    """
    # Authors
    # -------
    # Phillip J Wolfram

    # form dictionary
    #preprocess the file first

    fname = preprocess_namelist_file(fname)

    nml = dict()

    regex = re.compile(r"^\s*(.*?)\s*=\s*['\"]*(.*?)['\"]*\s*\n")
    with open(fname) as f:
        for line in f:
            match = regex.findall(line)
            if len(match) > 0:
                # assumes that there is only one match per line
                nml[match[0][0].lower()] = match[0][1]
    if readonly:
        nml = ReadOnlyDict(nml)

    return nml