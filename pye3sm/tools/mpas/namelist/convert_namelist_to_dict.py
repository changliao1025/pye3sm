from __future__ import absolute_import, division, print_function, \
    unicode_literals

import six

import re
import os.path

from pye3sm.tools.mpas.shared.containers import ReadOnlyDict
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