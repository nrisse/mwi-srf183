"""
Compare defined frequency grid and frequency grid from measurement files
"""


import numpy as np
import matplotlib.pyplot as plt
import os
from srf_reader import Sensitivity
from mwi_info import mwi
from dotenv import load_dotenv

load_dotenv()


if __name__ == '__main__':
    
    # read measurement
    sen_dsb = Sensitivity(filename=Sensitivity.files[0])
    sen = Sensitivity(filename=Sensitivity.files[1])
    
    # read pamtra frequencies
    freqs_pamtra = np.loadtxt(os.path.join(
        os.environ['PATH_BRT'], 'frequencies.txt'))
    
    # plot frequencies
    plt.figure(figsize=(6, 2))
    
    plt.plot(freqs_pamtra, [1]*len(freqs_pamtra), 'xk', label='pamtra frequencies', alpha=0.6, markeredgecolor=None)
    plt.plot(sen_dsb.data.frequency*1e-3, 
             [1]*len(sen_dsb.data.frequency), '.r',
             label='MWI-RX183_DSB_Matlab.xlsx', alpha=0.6, markeredgecolor=None)
    plt.plot(sen.data.frequency*1e-3, [1]*len(sen.data.frequency), '.b',
             label='MWI-RX183_Matlab.xlsx', alpha=0.6, markeredgecolor=None)
    
    for f in mwi.freq_bw_center.flatten():
        plt.axvline(f, color='k')
    
    plt.axvline(x=183.31, color='gray')
    plt.axvline(x=183.312, color='lightgray')
    plt.legend()
    plt.grid()
    plt.show()
    