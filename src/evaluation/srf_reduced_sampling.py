"""
Influence of SRF sampling reduction on the MWI observation

The difference between the MWI observation under reduced SRF and under the
original SRF is analyzed. For the radiosondes, statistics are calculated over
all profiles, and for the ERA-5 field, statistics are calculated for all grid
cells, by stacking x and y grids on a new dimension named profile.

The figure shows the mean absolute difference over all profiles as a function
of the sampling interval.

How to use the script:
    - choose one of the three nc files which contain the PAMTRA simulation
      and the pre-calculated MWI observations based on the different SRF types
    - choose a file extension corresponding to the nc file, to name the final
      plot
"""

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from string import ascii_lowercase as abc
import os
from helpers import mwi, colors
from dotenv import load_dotenv

load_dotenv()
plt.ion()


if __name__ == '__main__':
    
    # read nc files
    ds_com = xr.open_dataset(os.path.join(
        os.environ['PATH_BRT'],
        'TB_radiosondes_2019_MWI.nc'
        ))
    ext = '_radiosondes'    
    
    #ds_com = xr.open_dataset(os.path.join(
    #    os.environ['PATH_BRT'],
    #    'TB_era5_hyd_MWI.nc')  
    #ext = '_era5_hyd'
    
    #ds_com = xr.open_dataset(os.path.join(
    #    os.environ['PATH_BRT'],
    #    'TB_era5_MWI.nc')  
    #ext = '_era5'
    
    #ds_com = ds_com.stack({'profile': ['grid_x', 'grid_y']})  
    
    #%% statistics
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
    if 'station' in list(ds_com):
        ds_com_red_mae = np.abs(ds_com.dtb_mwi_red).groupby(ds_com.station).mean('profile')
    
    else:
        ds_com_red_mae = np.abs(ds_com.dtb_mwi_red).mean('profile')
    
    #%% influence of data reduction
    # x-axis: reduction_level 
    # y-axis: mean absolute difference
    # subplots: one channel per column
    fig, axes = plt.subplots(1, 5, figsize=(8, 2.5), sharex=True, sharey=True,
                             constrained_layout=True)
    
    for i, ax in enumerate(axes):
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        ax.annotate(f'({abc[i]})', xy=(0.02, 1), xycoords='axes fraction',
                    ha='left', va='top')
    
    # sampling interval
    x = np.append(np.array([15]), 15*ds_com.reduction_level.values)
    for i, channel in enumerate(mwi.channels_int):
        
        # annotate channel name
        axes[i].annotate(text=mwi.freq_txt[i].split('\n')[0], 
                         xy=(0.5, 1), 
                         xycoords='axes fraction', ha='center', va='top')
        
        if 'station' in list(ds_com):  # radiosondes
            for station in np.unique(ds_com.station):
                axes[i].plot(x, 
                             np.append(np.array([0]), 
                                       ds_com_red_mae.sel(channel=channel,
                                                          station=station)), 
                             color=colors.colors_rs[station], label=station, 
                             linewidth=1, marker='.')
                
        else:  # era5
            axes[i].plot(x, 
                         np.append(np.array([0]), 
                                   ds_com_red_mae.sel(channel=channel)), 
                         color='k', label='ERA-5', linewidth=1, 
                         marker='.')
        
    # set labels
    axes[0].set_xlabel('Sampling interval [MHz]')
    axes[0].set_ylabel('MAE [K]')
    
    # axis limits
    axes[0].set_xlim(15, 150)
    axes[0].set_ylim([0, 0.07])
    
    # annotate station names in legend below
    axes[0].legend(frameon=False, fontsize=8, loc='center')

    plt.savefig(os.path.join(
        os.environ['PATH_PLT'],
         'evaluation/reduced_srf_sampling'+ext+'.png'), 
        dpi=300, bbox_inches='tight')   

    plt.close('all')
    