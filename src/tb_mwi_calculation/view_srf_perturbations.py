"""
Visualization of the systematic SRF perturbations.
"""

import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
import os
from helpers import mwi
from dotenv import load_dotenv

load_dotenv()


if __name__ == '__main__':
    
    # read dataset with different perturbed srf
    ds_com = xr.open_dataset(os.path.join(
        os.environ['PATH_BRT'], 'TB_radiosondes_2019_MWI.nc'))
    
    # remove frequencies, at which no srf was measured
    ds_com = ds_com.sel(
        frequency=~np.isnan(ds_com.srf_orig.sel(channel=14).values))
    
    #%% print imbalance of perturbations
    for i, channel in enumerate(ds_com.channel.values):
        
        for magnitude in ds_com.magnitude.values:
            
            left = np.round(ds_com.srf_err.sel(
                frequency=(ds_com.srf_err.frequency < 183310),
                err_type='imbalance2',
                magnitude=magnitude,
                channel=channel).sum('frequency').item()*100, 1)
            right = np.round(ds_com.srf_err.sel(
                frequency=(ds_com.srf_err.frequency > 183310),
                err_type='imbalance2',
                magnitude=magnitude,
                channel=channel).sum('frequency').item()*100, 1)
            
            print(f'channel {channel} ({magnitude}): {left} | {right}')
            
        print('\n')
    
    #%% plot settings
    cols = ['#577590', '#577590',
            '#f3722c', '#f3722c',
            '#90be6d', '#90be6d']
    
    lst = ['-', '--', '-', '--', '-', '--']
    
    #%% plot pure spectral perturbations for a single frequency and magnitude
    # choose first a frequency and a magnitude, which should be shown
    mag = 0.5
    channel = 18
    i = 4  # channel index: 0, 1, 2, 3, 4
    
    fig, ax = plt.subplots(1, 1, sharex='all', figsize=(7, 2.5), 
                           constrained_layout=True)
    
    ax.spines.top.set_visible(False)
    ax.spines.right.set_visible(False)
    
    for j, err_type in enumerate(ds_com.err_type.values):
        
        ax.plot(ds_com['frequency']/1e3, 
                ds_com.srf_err_offset_dB.sel(channel=channel, magnitude=mag, 
                                      err_type=err_type), 
                color=cols[j], linewidth=2, label=err_type, linestyle=lst[j])
    
    # y axis settings
    ax.set_yticks([-mag, 0, mag])
    ax.set_ylim([-mag-0.1*mag, mag+0.1*mag])
    
    # set x-limit
    ax.set_xticks(np.arange(170, 190, 1))
    ax.set_xlim([183.31-3-0.1, 183.31+3+0.1])
    
    # add vertical lines
    ax.axvline(x=mwi.absorpt_line, color='k', linewidth=1, zorder=0)
    
    # add shade for each channel
    ax.axvspan(xmin=mwi.freq_bw[i, 0], xmax=mwi.freq_bw[i, 1], ymin=-10e3,
               ymax=10e3, color='gray',
                    alpha=0.2, linewidth=0)
    ax.axvspan(xmin=mwi.freq_bw[i, 2], xmax=mwi.freq_bw[i, 3], ymin=-10e3, 
               ymax=10e3, color='gray',
                    alpha=0.2, linewidth=0)
    
    # set axis labels
    ax.set_ylabel('Sensitivity [dB]')
    ax.set_xlabel('Frequency [GHz]')
        
    # add legend below
    leg = ax.legend(loc='center left', bbox_to_anchor=(1.01, 0.5), ncol=1, 
                    frameon=False)
    
    plt.savefig(os.path.join(
        os.environ['PATH_PLT'],
        f'srf_error_ch{channel}_mag{mag}.png'), 
        bbox_inches='tight', dpi=300)
        
    #%% plot perturbed data for single frequency and magnitude
    # choose first a frequency and a magnitude, which should be shown
    mag = 0.5
    channel = 18
    pert_kind = '1'  # plots only one kind of perturbation (1 or 2)
            
    fig, ax = plt.subplots(1, 1, sharex='all', figsize=(7, 3), 
                           constrained_layout=True, sharey=True)
                
    # original
    ax.plot(ds_com['frequency']/1e3, 
            100*ds_com['srf_orig'].sel(channel=channel), color='k', 
            linewidth=1, label='original')
    
    for j, err_type in enumerate(ds_com.err_type.values):
        
        if pert_kind in err_type:
            ax.plot(ds_com['frequency']/1e3, 
                    100*ds_com.srf_err.sel(channel=channel, magnitude=mag,
                                           err_type=err_type), 
                    color=cols[j], linewidth=2, label=err_type, 
                    linestyle=lst[j])
        else:
            continue
    
    # y axis settings
    ax.set_ylim([0, 1])
            
    # set x-limit
    ax.set_xticks(np.arange(170, 190, 1))
    ax.set_xlim([183.31-3-0.1, 183.31+3+0.1])
    
    # annotate channel name
    ax.annotate(text=mwi.freq_txt[i], xy=(0.5, 1.01), xycoords='axes fraction',
                ha='center', va='bottom')
    
    # add vertical lines
    ax.axvline(x=mwi.absorpt_line, color='k', linewidth=1, zorder=0)
    
    # add shade for each channel
    ax.axvspan(xmin=mwi.freq_bw[i, 0], xmax=mwi.freq_bw[i, 1], ymin=-10e3, 
               ymax=10e3, color='gray',
                    alpha=0.2, linewidth=0)
    ax.axvspan(xmin=mwi.freq_bw[i, 2], xmax=mwi.freq_bw[i, 3], ymin=-10e3, 
               ymax=10e3, color='gray',
                    alpha=0.2, linewidth=0)
        
    # annotate bandwidth
    for j in range(2):  # mark left/right channel frequency
        ax.annotate('|---- 1.5 GHz ----|', xy=(mwi.freq_center[i, j], 1.01),
                    xycoords=('data', 'axes fraction'), ha='center',
                    va='bottom')
        
    # set axis labels
    ax.set_ylabel('Sensitivity [%]')
    ax.set_xlabel('Frequency [GHz]')
        
    # add legend below
    leg = ax.legend(loc='center left', bbox_to_anchor=(1.1, 0.5), ncol=1, 
                    frameon=False)
    
    plt.savefig(os.path.join(
        os.environ['PATH_PLT'],
        f'srf_perturbed_ch{channel}_mag{mag}_kind{pert_kind}.png'), 
        bbox_inches='tight', dpi=300)

    #%%
    plt.close('all')
