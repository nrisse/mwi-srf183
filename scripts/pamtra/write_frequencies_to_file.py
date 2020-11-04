

import numpy as np
import sys
sys.path.append('/home/nrisse/uniHome/WHK/eumetsat/scripts')

from importer import Sensitivity
from mwi_info import mwi
from path_setter import *

"""
Define frequencies used for PAMTRA simulation and write to file

Create frequency array based on where measurements are taken (including actual channel frequencies) and save to
file.

Frequencies from MWI-RX183_Matlab.xlsx are not considered
"""


if __name__ == '__main__':
    
    # read bandpass measurement
    sen_dsb = Sensitivity(path=path_sens, filename='MWI-RX183_DSB_Matlab.xlsx')
    
    freqs_pamtra = sen_dsb.data['frequency [GHz]'].values  # frequencies from dsb file
    freqs_pamtra = np.append(freqs_pamtra, mwi.freq_bw_center.flatten())  # channel frequencies
    freqs_pamtra = np.unique(np.sort(freqs_pamtra))  # sort and remove duplicates
    
    # write frequencies to file
    np.savetxt(path_data + 'frequencies.txt', freqs_pamtra)
    