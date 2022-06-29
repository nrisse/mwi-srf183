

import numpy as np
import matplotlib.pyplot as plt
import os
import sys
sys.path.append(f'{os.environ["PATH_PHD"]}/projects/mwi_bandpass_effects/scripts')
from importer import Sensitivity
from path_setter import *


"""
Compare defined frequency grid and frequency grid from measurement files
"""


if __name__ == '__main__':
    
    # read measurement
    sen_dsb = Sensitivity(path=path_sens, filename='MWI-RX183_DSB_Matlab.xlsx')
    sen = Sensitivity(path=path_sens, filename='MWI-RX183_Matlab.xlsx')
    
    # read pamtra frequencies
    freqs_pamtra = np.loadtxt(path_data + 'frequencies.txt')
    
    # plot frequencies
    plt.figure(figsize=(6, 2))
    
    plt.plot(freqs_pamtra, [1]*len(freqs_pamtra), 'xk', label='pamtra frequencies', alpha=0.6, markeredgecolor=None)
    plt.plot(sen_dsb.data['frequency [GHz]'], [1]*len(sen_dsb.data['frequency [GHz]']), '.r',
             label='MWI-RX183_DSB_Matlab.xlsx', alpha=0.6, markeredgecolor=None)
    plt.plot(sen.data['frequency [GHz]'], [1]*len(sen.data['frequency [GHz]']), '.b',
             label='MWI-RX183_Matlab.xlsx', alpha=0.6, markeredgecolor=None)
    
    plt.axvline(x=183.31, color='gray')
    plt.legend()
    plt.grid()
    
    plt.savefig(path_fig + 'frequencies.png', dpi=400)
