"""
Script to plot reference tb location for visualization in the presentations
"""


import os
import sys
sys.path.append(f'{os.environ["PATH_PHD"]}/projects/mwi_bandpass_effects/scripts')
import numpy as np
import matplotlib.pyplot as plt

from path_setter import path_plot
from mwi_info import mwi
from importer import Sensitivity


if __name__ == '__main__':
    
    sen_dsb = Sensitivity(filename='MWI-RX183_DSB_Matlab.xlsx')
    
    i = 2
    
    #%%
    fig = plt.figure(figsize=(5, 2))
    ax = fig.add_subplot()
    ax.set_title('Channel MWI-16')
    ax.plot(sen_dsb.data.frequency*1e-3, 
            sen_dsb.data.lino.sel(channel=16), color='k', zorder=1)
    
    # add vertical lines    
    for j in range(2):  # mark left/right channel frequency
        ax.axvline(x=mwi.freq_center[i, j], color='red', linestyle='-', zorder=2)
    
    for j in range(4):  # mark each bandwidth edge
        ax.axvline(x=mwi.freq_bw[i, j], color='blue', linestyle='-', zorder=2)
    
    # add shade for each channel
    ax.axvspan(xmin=mwi.freq_bw[i, 0], xmax=mwi.freq_bw[i, 1], ymin=-10e3, ymax=10e3, color='gray',
                    alpha=0.2, zorder=0)
    ax.axvspan(xmin=mwi.freq_bw[i, 2], xmax=mwi.freq_bw[i, 3], ymin=-10e3, ymax=10e3, color='gray',
                    alpha=0.2, zorder=0)
    
    ax.grid()
    
    ax.set_xlim([np.min(mwi.freq_bw)-0.1, np.max(mwi.freq_bw)+0.1])
    ax.set_yticks([])
    
    ax.set_xlabel('Frequency [GHz]')
    ax.set_ylabel('Sensitivity')
    
    plt.subplots_adjust(bottom=0.3, left=0.07, right=0.99, top=0.85)
    
    plt.savefig(path_plot + 'bandpass_measurement/freq_location.png', dpi=200)
    
    #%% overview for reference tbs
    i = 4
    def fig_maker():
        fig = plt.figure(figsize=(2, 0.75))
        ax = fig.add_subplot()
        ax.plot(sen_dsb.data.frequency*1e-3, 
                sen_dsb.data.lino.sel(channel=18), color='k', zorder=1)
        
        ax.axes.get_xaxis().set_ticks([])
        ax.axes.get_yaxis().set_ticks([])
        
        # add shade for each channel
        ax.axvspan(xmin=mwi.freq_bw[i, 0], xmax=mwi.freq_bw[i, 1], ymin=-10e3, ymax=10e3, color='#bbbbbb', zorder=0)
        ax.axvspan(xmin=mwi.freq_bw[i, 2], xmax=mwi.freq_bw[i, 3], ymin=-10e3, ymax=10e3, color='#bbbbbb', zorder=0)
        
        plt.subplots_adjust(bottom=0.03, left=0.03, right=0.97, top=0.97)
        
        ax.set_xlim([mwi.absorpt_line-3, mwi.absorpt_line+3])
        ax.set_ylim(bottom=0)
    
        return fig, ax
    
    
    # add vertical lines
    # CENTER
    fig, ax = fig_maker()
    for j in range(2):  # mark left/right channel frequency
        ax.axvline(x=mwi.freq_center[i, j], color='red', linestyle='-', zorder=2, linewidth=2)
    plt.savefig(path_plot + 'bandpass_measurement/loc_center.png', dpi=200)
    
    # BANDWIDTH
    fig, ax = fig_maker()
    for j in range(4):  # mark each bandwidth edge
        ax.axvline(x=mwi.freq_bw[i, j], color='red', linestyle='-', zorder=2, linewidth=2)
    plt.savefig(path_plot + 'bandpass_measurement/loc_bw.png', dpi=200)
    
    # BOTH
    fig, ax = fig_maker()
    for j in range(2):  # mark left/right channel frequency
        ax.axvline(x=mwi.freq_center[i, j], color='red', linestyle='-', zorder=2, linewidth=2)
    for j in range(4):  # mark each bandwidth edge
        ax.axvline(x=mwi.freq_bw[i, j], color='red', linestyle='-', zorder=2, linewidth=2)
    plt.savefig(path_plot + 'bandpass_measurement/loc_bw_center.png', dpi=200)
   
