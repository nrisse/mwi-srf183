"""
Define frequencies used for PAMTRA simulation and write them to a file.
"""


import numpy as np
import os
from srf_reader import Sensitivity
from mwi_info import mwi
from dotenv import load_dotenv

load_dotenv()


if __name__ == '__main__':
    
    # read bandpass measurement
    sen_dsb = Sensitivity(filename='MWI-RX183_DSB_Matlab.xlsx')
    
    freqs_pamtra = sen_dsb.data.frequency.values*1e-3
    freqs_pamtra = np.append(freqs_pamtra, mwi.freq_bw_center.flatten())
    freqs_pamtra = np.unique(np.sort(freqs_pamtra))
    
    # write frequencies to file
    np.savetxt(os.path.join(
        os.environ['PATH_BRT'],
        'frequencies.txt'), freqs_pamtra)
