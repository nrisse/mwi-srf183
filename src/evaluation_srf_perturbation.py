"""
Influence of SRF perturbations on the MWI observation

The difference between the MWI observation under perturbed SRF and under the
original SRF is analyzed. For the radiosondes, statistics are calculated over
all profiles, and for the ERA-5 field, statistics are calculated for all grid
cells, by stacking x and y grids on a new dimension named profile.

The figure only shows the error types1, as they are similar to the error types
2 except for the sign of the difference.

How to use the script:
    - choose one of the three nc files which contain the PAMTRA simulation
      and the pre-calculated MWI observations based on the different SRF types
    - choose a file extension corresponding to the nc file, to name the final
      plot
"""


import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
from string import ascii_lowercase as abc
import os
import sys
sys.path.append(f'{os.environ["PATH_PHD"]}/projects/mwi_bandpass_effects/scripts')
from mwi_info import mwi
from path_setter import path_data, path_plot

plt.ion()


if __name__ == '__main__':
    
    # read nc files
    ds_com = xr.open_dataset(path_data + 'brightness_temperature/'+
                             'TB_radiosondes_2019_MWI.nc')    
    ext = '_radiosondes'    
    
    #ds_com = xr.open_dataset(path_data + 'brightness_temperature/'+
    #                         'TB_era5_hyd_MWI.nc')  
    #ext = '_era5_hyd'
    
    #ds_com = xr.open_dataset(path_data + 'brightness_temperature/'+
    #                         'TB_era5_MWI.nc')  
    #ext = '_era5'
    
    #ds_com = ds_com.stack({'profile': ['grid_x', 'grid_y']})
    
    #%% calculate statistics (mean absolute error)
    ds_com_dtb_mae = np.fabs(ds_com.dtb_mwi_err).mean('profile')
    ds_com_dtb_std = np.fabs(ds_com.dtb_mwi_err).std('profile')
    
    #%% statistics
    magnitude = 2
    for channel in ds_com.channel.values:
        print('\n', channel)
        for err_type in ds_com_dtb_mae.err_type.values:
            mae = np.round(ds_com_dtb_mae.sel(
                channel=channel, 
                magnitude=magnitude, 
                err_type=err_type).values.item(), 2)
            print(f'{err_type}: {mae}')
    
    magnitude = 2
    for channel in ds_com.channel.values:
        print('\n', channel)
        for err_type in ds_com.err_type.values:
            mae = np.round(ds_com.dtb_mwi_err.sel(
                channel=channel, 
                magnitude=magnitude, 
                err_type=err_type).mean('profile').values.item(), 2)
            print(f'{err_type}: {mae}')
            
    #%% color for figures
    err_type_c = {
        'linear1': '#577590', 
        'imbalance1': '#f3722c', 
        'sine1': '#90be6d',
        }
    
    #%% histogram of absolute difference and dependence on magnitude
    step = 0.01
    min_max = 0.3
    bins = np.arange(-min_max, min_max+step, step)
    mag = 0.5
    
    fig, axes = plt.subplots(5, 2, figsize=(7, 4), sharex='col', 
                             constrained_layout=True)
    
    axes1, axes2 = [axes[:, 0], axes[:, 1]]
                    
    axes1[-1].set_ylabel('#')
    axes1[-1].set_xlabel(r'$\Delta TB$ [K]')
    
    axes2[-1].set_ylabel(r'MAE [K]')
    axes2[-1].set_xlabel('Perturbation magnitude [dB]')

    for i, ax in enumerate(axes.flatten('F')):    
        ax.annotate(f'({abc[i]})', xy=(0.02, 1), xycoords='axes fraction',
                    ha='left', va='top')
    
    for i, ax in enumerate(axes1.flatten()):
        
        ax.spines.right.set_visible(False)
        ax.spines.top.set_visible(False)

        # y axis
        ax.set_xticks(ticks=np.arange(-0.5, 0.5, 0.1), minor=False)
        ax.set_xticks(ticks=np.arange(-0.5, 0.5, 0.025), minor=True)

        ax.axvline(x=0, color='k', linewidth=1)
        
        if mag == 0.5:
            ax.set_xlim([-0.1, 0.3])
            ax.set_ylim(0, 1e3)
    
    for ax in axes2.flatten():
        
        ax.spines.right.set_visible(False)
        ax.spines.top.set_visible(False)
        
        # x axis
        ax.set_yticks(ticks=np.arange(0, 1.5, 0.5), minor=False)
        ax.set_yticks(ticks=np.arange(0, 1.5, 0.1), minor=True)
        
        # y axis
        ax.set_xticks(ticks=np.arange(0, 2.5, 0.5), minor=False)
        ax.set_xticks(ticks=np.arange(0, 2.5, 0.1), minor=True)
                
        ax.set_xlim([0, 2.1])
        ax.set_ylim([0, 1])
    
    # annotate channel name
    for i, ax in enumerate(axes2):
        ax.annotate(text=mwi.freq_txt[i].split('\n')[0], xy=(0.5, 1), 
                    xycoords='axes fraction',
                    ha='center', va='top')
    
    kwargs = dict(bins=bins, linewidth=0, alpha=0.75)
    
    for i, channel in enumerate(ds_com.channel):
        for err_type, color in err_type_c.items():
        
            kwargs_sel = dict(channel=channel, magnitude=mag)
            axes1[i].hist(
                ds_com.dtb_mwi_err.sel(err_type=err_type, **kwargs_sel), 
                         color=color, label=err_type, **kwargs)

            axes2[i].errorbar(ds_com_dtb_mae.magnitude, 
                             ds_com_dtb_mae.sel(channel=channel, 
                                                err_type=err_type), 
                             yerr=ds_com_dtb_std.sel(channel=channel, 
                                                     err_type=err_type), 
                             elinewidth=0.5, capsize=2, color=color,
                             barsabove=True, label=err_type.replace('1', ''))
    
    axes1[-1].legend(ncol=2, frameon=False, fontsize=8)
    
    plt.savefig(path_plot+'evaluation/perturbation_effect'+ext+'.png', dpi=300)
    
    plt.close('all')
