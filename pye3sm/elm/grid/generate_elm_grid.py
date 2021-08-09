import os
import sys
#we will use datetime and julian package to operate date and time

import numpy as np


from pye3sm.elm.grid import global_variable


from e3sm.elm.grid.global_variable import *

def generate_elm_grid(sFilename_configuration):
    read_configuration_file(sFilename_configuration)


if __name__ == '__main__':
    
    sFilename_configuration = '/Users/liao313/project/e3sm/compset/customized/configuration.txt'
   
    generate_elm_grid(sFilename_configuration)

