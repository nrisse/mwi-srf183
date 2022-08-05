"""
Influence of srf sampling reduction on the result
"""


import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import os
import sys
sys.path.append(f'{os.environ["PATH_PHD"]}/projects/mwi_bandpass_effects/scripts')
from mwi_info import mwi
from path_setter import path_data, path_plot


if __name__ == '__main__':
    
    # read nc files
    ds_com = xr.open_dataset(path_data + 'brightness_temperature/'+
                             'TB_radiosondes_2019_MWI.nc')     
    
    #%% difference compared to originally measured srf
    print(ds_com.dtb_mwi_red.min(['profile', 'reduction_level']))
    print(ds_com.dtb_mwi_red.max(['profile', 'reduction_level']))
    
    # error is in the order of 0.001 K
    
    # number of measurements for each reduction level
    for red_lev in ds_com.reduction_level:
        x = np.sum(~np.isnan(ds_com.srf_red.sel(channel=14, 
                                            reduction_level=red_lev))).item()
        print(x)
    
    #%% statics: mean absolute difference and std between MWI from SRF without 
    # reduced sampling and with reduced sampling of different magnitude
    ds_com_red_mae = np.abs(ds_com.dtb_mwi_red).groupby(ds_com.station).mean('profile')
    
    #%% colors
    colors = {
        'Ny-Alesund': 'b',
        'Essen': 'g',
        'Singapore': 'r',
        'Barbados': 'orange',
        }
    
    #%% PROOF influence of data reduction (noise == 0)
    # x-axis: reduction_level 
    # y-axis: standard deviation of delta_tb
    # subplots: one channel per row, in each subplots three lines for three stations
    fig, axes = plt.subplots(5, 1, figsize=(6, 6), sharex=True, sharey=True,
                             constrained_layout=True)
    
    for ax in axes:
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
    
    # sampling interval
    x = np.append(np.array([15]), 15*ds_com.reduction_level.values)
    for i, channel in enumerate(mwi.channels_int):
        
        # annotate channel name
        axes[i].annotate(text=mwi.freq_txt[i], xy=(1.01, 0.5), 
                    xycoords='axes fraction', ha='left', va='center')
        
        for station in np.unique(ds_com.station):
            axes[i].plot(x, 
                         np.append(np.array([0]), 
                                   ds_com_red_mae.sel(channel=channel,
                                                      station=station)), 
                         color=colors[station], label=station, linewidth=1, 
                         marker='.')
        
    # set labels
    axes[-1].set_xlabel('Sampling interval [MHz]')
    axes[2].set_ylabel('$TB_{obs} - TB_{obs,red}$ [K]')
    
    # axis limits
    axes[-1].set_xticks(x)
    axes[-1].set_xlim(15, 150)
    axes[0].set_ylim([0, 0.1])
    
    # annotate station names in legend below
    leg = axes[-1].legend(bbox_to_anchor=(0.5, -0.6), loc='upper center', 
                          frameon=True, ncol=4)

    plt.savefig(path_plot + 'evaluation/radiosondes_srf_reduced_sampling.png', 
                dpi=300, bbox_inches='tight')   

    plt.close('all')
    