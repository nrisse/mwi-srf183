"""
View defined frequencies for PAMTRA simulation and frequencies from SRF data.
"""


import numpy as np
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv
import sys
sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(__file__), 
    '../src')))
from helpers import Sensitivity, mwi

load_dotenv()


if __name__ == '__main__':
    
    # read measurement
    sen_dsb = Sensitivity(filename=Sensitivity.files[0])
    sen = Sensitivity(filename=Sensitivity.files[1])
    
    # read pamtra frequencies
    freqs_pamtra = np.loadtxt(os.path.join(
        os.environ['PATH_BRT'], 'frequencies.txt'))
    
    # plot frequencies
    fig, ax = plt.subplots(1, 1, figsize=(10, 4), constrained_layout=True)
    
    ax.scatter(freqs_pamtra, 
               np.zeros_like(freqs_pamtra),
               marker='o',
               label='pamtra frequencies')
    
    ax.scatter(sen_dsb.data.frequency*1e-3, 
               np.zeros_like(sen_dsb.data.frequency),
               marker='x',
               label=Sensitivity.files[0])
    
    ax.scatter(sen.data.frequency*1e-3, 
               np.zeros_like(sen.data.frequency),
               marker='+',
               label=Sensitivity.files[1])
    
    for f in mwi.freq_bw_center.flatten():
        ax.axvline(f, color='k')
    
    ax.axvline(x=183.31, color='gray')
    ax.axvline(x=183.312, color='lightgray')
    
    ax.legend()
    ax.grid()
    
    plt.show()
    