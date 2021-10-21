#this script should be run using Python 2.7.8 instead of Python 3
#module load python/2.7.8

import os, sys
import argparse
import subprocess
import numpy as np
import multiprocessing

sSystem_paths = os.environ['PATH'].split(os.pathsep)
 

from pyearth.system.define_global_variables import *

 
 
from pye3sm.shared.e3sm import pye3sm
from pye3sm.shared.case import pycase
from pye3sm.elm.general.halfdegree.save.elm_save_variable_halfdegree import elm_save_variable_halfdegree



def h2sc_save_variable_halfdegree(oE3SM_in, oCase_in):

    elm_save_variable_halfdegree(oE3SM_in, oCase_in)


