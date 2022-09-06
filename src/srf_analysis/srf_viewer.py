"""
Script to plot bandpass measurements in various forms.
"""


import numpy as np
import matplotlib.pyplot as plt
import os
from helpers import Sensitivity, mwi
from dotenv import load_dotenv

load_dotenv()
plt.ion()


if __name__ == '__main__':
    
    # read bandpass measurement
    sen_dsb = Sensitivity(filename=Sensitivity.files[0])
    sen = Sensitivity(filename=Sensitivity.files[1])
    
    #%% plot both srf measurements in dB
    # make same x scaling for the subplots
    a = ((sen_dsb.data.frequency.min() - sen_dsb.data.frequency.max()) / \
        (sen.data.frequency.min() - sen.data.frequency.max())).item()
    
    fig, axes = plt.subplots(5, 2, figsize=(7, 8), sharey=True, sharex='col',
                             constrained_layout=True, gridspec_kw=dict(
                                 width_ratios=[a, 1]))
    
    axes[0, 0].annotate('SRF-A', xy=(0.5, 1), xycoords='axes fraction',
                        ha='center', va='bottom')
    axes[0, 1].annotate('SRF-B', xy=(0.5, 1), xycoords='axes fraction',
                        ha='center', va='bottom')
    
    ymin = -110
    ymax = 1
    
    for i, ax in enumerate(axes[:, 1]):
                
        # annotate channel name
        ax.annotate(mwi.freq_txt[i].split('\n')[0], xy=(1, 0.5), 
                    xycoords='axes fraction', ha='right', va='center')
    
    for ax in fig.axes:
        ax.spines.top.set_visible(False)
        ax.spines.right.set_visible(False)
                
        # y axis settings
        ax.set_yticks(np.arange(-100, 25, 25))
        ax.set_ylim([ymin, ymax])
    
    match = np.array([183.362, 191.297])
    f = dict(frequency=slice(*match*1e3))
    for i, channel in enumerate(mwi.channels_int):
        
        # MWI-RX183_DSB_Matlab.xlsx dataset
        axes[i, 0].plot(
            sen_dsb.data.frequency*1e-3, 
            sen_dsb.data.raw.sel(channel=channel),
            color='#666666', label='SRF-A', zorder=2)
        
        axes[i, 0].plot(
            sen_dsb.data.frequency.sel(**f)*1e-3, 
            sen_dsb.data.raw.sel(channel=channel, **f),
            color='#000000', label='SRF-A', zorder=2)
        
        # MWI-RX183_Matlab.xslx
        axes[i, 1].plot(sen.data.frequency*1e-3,
                     sen.data.raw.sel(channel=channel),
                     color='#666666', label='SRF-B', zorder=2)
        
        axes[i, 1].plot(sen.data.frequency.sel(**f)*1e-3,
                     sen.data.raw.sel(channel=channel, **f),
                     color='#000000', label='SRF-B', zorder=2)
        
        for i_ax in range(2):
            
            # add shade for each channel
            axes[i, i_ax].axvspan(
                xmin=mwi.freq_bw[i, 0], 
                xmax=mwi.freq_bw[i, 1],
                ymin=0, ymax=1-(ymax/(ymax-ymin)), color='navajowhite', lw=0, 
                zorder=0)
            
            axes[i, i_ax].axvspan(
                xmin=mwi.freq_bw[i, 2], 
                xmax=mwi.freq_bw[i, 3], 
                ymin=0, ymax=1-(ymax/(ymax-ymin)), color='bisque', lw=0, 
                zorder=0)
    
    
    axes[0, 0].set_xlim(sen_dsb.data.frequency.min()*1e-3,
                        sen_dsb.data.frequency.max()*1e-3)
    axes[0, 1].set_xlim(sen.data.frequency.min()*1e-3,
                        sen.data.frequency.max()*1e-3)
    
    # set axis labels
    axes[2, 0].set_ylabel('Sensitivity [dB]')
    axes[-1, 0].set_xlabel('Frequency [GHz]')
    
    plt.savefig(os.path.join(
        os.environ['PATH_PLT'],
        'srf.png'), 
        dpi=300, bbox_inches='tight')
    
    plt.close('all')
    
    #%% plot srf of dsb measurement after normalization
    fig, axes = plt.subplots(5, 1, sharex=True, figsize=(6, 6), 
                             constrained_layout=True)
    
    for i, channel in enumerate(mwi.channels_int):
        
        # MWI-RX183_DSB_Matlab.xlsx dataset
        axes[i].plot(sen_dsb.data.frequency*1e-3, 
                     sen_dsb.data.lino.sel(channel=channel)*100, 
                     color='k', linewidth=1, zorder=2)
        
        # y axis settings
        axes[i].set_yticks([0, 0.5])
        axes[i].set_ylim([0, 0.85])
                
        # set x-limit
        axes[i].set_xlim([np.min(mwi.freq_bw)-0.1, np.max(mwi.freq_bw)+0.1])
        
        # annotate channel name
        axes[i].annotate(text=mwi.freq_txt[i], xy=(1.01, 0.5), 
                         xycoords='axes fraction', ha='left', va='center')
        
        # add vertical lines
        axes[i].axvline(x=mwi.absorpt_line, color='red', linewidth=0.5, 
                        zorder=0)
        
        for j in range(2):  # mark left/right channel frequency
            axes[i].axvline(x=mwi.freq_center[i, j], color='gray', 
                            linestyle='--', linewidth=0.75, zorder=0)
        
        for j in range(4):  # mark each bandwidth edge
            axes[i].axvline(x=mwi.freq_bw[i, j], color='gray', linestyle=':', 
                            linewidth=0.75, zorder=0)
        
        # add shade for each channel
        axes[i].axvspan(xmin=mwi.freq_bw[i, 0], xmax=mwi.freq_bw[i, 1], 
                        ymin=-10e3, ymax=10e3, color='gray',
                        alpha=0.2)
        axes[i].axvspan(xmin=mwi.freq_bw[i, 2], xmax=mwi.freq_bw[i, 3], 
                        ymin=-10e3, ymax=10e3, color='gray',
                        alpha=0.2)

    # set axis labels
    axes[2].set_ylabel('Sensitivity [%]')
    axes[-1].set_xlabel('Frequency [GHz]')
        
    plt.savefig(os.path.join(
        os.environ['PATH_PLT'],
        'srf_dsb_norm.png'), dpi=300)
    
    plt.close('all')