

import numpy as np
import matplotlib.pyplot as plt
import os
import sys
sys.path.append(f'{os.environ["PATH_PHD"]}/projects/mwi_bandpass_effects/scripts')
from importer import Sensitivity
from path_setter import path_data, path_plot


"""
Compare defined frequency grid and frequency grid from measurement files
"""


if __name__ == '__main__':
    
    # read measurement
    sen_dsb = Sensitivity(filename=Sensitivity.files[0])
    sen = Sensitivity(filename=Sensitivity.files[1])
    
    # read pamtra frequencies
    freqs_pamtra = np.loadtxt(path_data + 'brightness_temperature/frequencies.txt')
    
    # plot frequencies
    plt.figure(figsize=(6, 2))
    
    plt.plot(freqs_pamtra, [1]*len(freqs_pamtra), 'xk', label='pamtra frequencies', alpha=0.6, markeredgecolor=None)
    plt.plot(sen_dsb.data.frequency*1e-3, 
             [1]*len(sen_dsb.data.frequency), '.r',
             label='MWI-RX183_DSB_Matlab.xlsx', alpha=0.6, markeredgecolor=None)
    plt.plot(sen.data.frequency, [1]*len(sen.data.frequency), '.b',
             label='MWI-RX183_Matlab.xlsx', alpha=0.6, markeredgecolor=None)
    
    plt.axvline(x=183.31, color='gray')
    plt.legend()
    plt.grid()
    
    plt.savefig(path_plot + 'bandpass_measurement/frequencies.png', dpi=400)
