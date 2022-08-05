"""
DESCRIPTION

Evaluation of delta_tb depending on the IWV of the radiosonde profiles

srf:
    - orig
    - estimates

new finding: for low IWV, this depends strongly on the surface emissivity.
At emissivity of 0.6, differences can become very large

RESULT
the IWV explains the error for the channel very well, except for channel 18 (closest to maximum)
for this, temperature can be included

differences in the calculation method ....

under clear-sky conditions the deviation from MWI measurement and model
simulation at the MWI-frequencies can be corrected if the IWV of the atmosphere
measured by MWI is known

how do clouds influence this pattern? Suggestion: ice clouds strongly perturb 
the simple pattern. Thin liquid clouds may not change the result

PROOF
"""


import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import xarray as xr
from string import ascii_lowercase as abc
import os
import sys
sys.path.append(f'{os.environ["PATH_PHD"]}/projects/mwi_bandpass_effects/scripts')
from mwi_info import mwi
from radiosonde import wyo
from path_setter import path_plot, path_data


plt.ion()


if __name__ == '__main__':
    
    #%% read data
    ds_com = xr.open_dataset(path_data+'/brightness_temperature/'+
                             'TB_radiosondes_2019_MWI.nc')
    
    assert np.all(ds_com.time.dt.year == 2019)
    
    #%% print some statistics
    for channel in ds_com.channel:
        for est_type in ds_com.est_type:
            s = dict(channel=channel, est_type=est_type)

            dtb_max = np.round(np.abs(ds_com.dtb_mwi_est).max('profile')
                               .sel(**s).item(), 1)
            print(f'channel {channel.item()}, est_type {est_type.item()}: '+
                  f'{dtb_max}')
    
    np.abs(ds_com.dtb_mwi_est).max(['profile', 'channel'])
    
    #%% colors for plot
    colors = {'Ny-Alesund': 'b',
              'Essen': 'g',
              'Singapore': 'r',
              'Barbados': 'orange',
              }
    
    c_list = [colors[p] for p in ds_com.station.values]
    
    #%% scatter plot and histogram
    # x: TB obs
    # y: TB obs - TB mod
    # scatter + histogram of TB obs on secondary x axis
    
    fig, axes = plt.subplots(5, 4, figsize=(6, 7), sharex=True, sharey=True)
    
    axes_twin = np.zeros_like(axes, dtype='object')
    for i in range(axes.shape[0]):
        for j in range(axes.shape[1]):
            axes_twin[i, j] = axes[i, j].twiny()
    axes_twin[0, 0].get_shared_x_axes().join(*axes_twin.flatten())        
    
    axes[-1, 0].set_ylabel('$TB_{obs} - TB_{mod}$ [K]')
    axes[-1, 0].set_xlabel('$TB_{obs}$ [K]')
    
    axes[0, 0].set_title(r'center', fontsize=8)
    axes[0, 1].set_title(r'cutoff', fontsize=8)
    axes[0, 2].set_title(r'center+cutoff', fontsize=8)
    axes[0, 3].set_title(r'tophat', fontsize=8)
    
    axes_twin[0, 0].set_xlabel('#')
    axes_twin[0, 1].set_xlabel('#')
    axes_twin[0, 2].set_xlabel('#')
    axes_twin[0, 3].set_xlabel('#')
    
    for i, ax in enumerate(axes_twin.flatten('F')):
        
        ax.set_xticks([0, 1000])
        ax.set_xticks(np.arange(0, 2000, 100), minor=True)
        ax.set_xlim(0, len(ds_com.profile))
    
    for ax in axes_twin.flatten()[4:]:
        ax.set_xticklabels([])
    
    for i, ax in enumerate(axes.flatten('F')):
        
        ax.annotate(f'({abc[i]})', xy=(0.02, 0.98), xycoords='axes fraction',
                    ha='left', va='top')
        
        # x axis
        ax.set_xticks(ticks=np.arange(100, 400, 25), minor=False)
        ax.set_xticks(ticks=np.arange(100, 400, 5), minor=True)
        
        # y axis
        ax.set_yticks(ticks=np.arange(-2, 2, 0.5), minor=False)
        ax.set_yticks(ticks=np.arange(-2, 2, 0.1), minor=True)
        
        ax.tick_params(which='major')
        ax.tick_params(which='minor', length=1)
        ax.grid('both', alpha=0.5)
        
        ax.axhline(y=0, color='k', linewidth=1, alpha=0.5)
        
        ax.set_ylim([-1.4, 1.4])
        ax.set_xlim([235, 290])
        
    # annotate channel name
    for i, ax in enumerate(axes[:, -1]):
        ax.annotate(text=mwi.freq_txt[i], xy=(1.1, 0.5), xycoords='axes fraction', backgroundcolor="w",
                    annotation_clip=False, horizontalalignment='left', verticalalignment='center', fontsize=8)
    
    for i, channel in enumerate(mwi.channels_int):
        for j, est_type in enumerate(['freq_center', 'freq_bw', 'freq_bw_center', 'tophat']):
            
            # histogram
            hist, bin_edges = np.histogram(ds_com.dtb_mwi_est.sel(channel=channel, 
                                                est_type=est_type),
                         bins=np.arange(-1.5, 1.6, 0.05))
            axes_twin[i, j].fill_betweenx(
                y=bin_edges[:-1], 
                x1=hist,
                x2=0,
                step='post',
                color='gray', alpha=0.5, zorder=0, lw=0)
            
            
            # scatter
            axes[i, j].scatter(ds_com.tb_mwi_orig.sel(channel=channel), 
                               ds_com.dtb_mwi_est.sel(channel=channel,
                                                      est_type=est_type), 
                               s=2, c=c_list, linewidths=0, alpha=0.5, zorder=1)
    
    fig.tight_layout()
    
    # legend below
    patches = []
    stations = wyo.station_id.keys()
    for station in stations:
        patches.append(mpatches.Patch(color=colors[station], label=station))
    leg = axes[-1, -1].legend(handles=patches, bbox_to_anchor=(1.05, 0.2), loc='upper left', frameon=False, ncol=1, fontsize=6, title='Radiosonde location:')
    plt.setp(leg.get_title(),fontsize=6)
    
    plt.savefig(path_plot+'iwv_dependency/scatter_tb_dtb.png', dpi=400,
                bbox_inches='tight')
    
    plt.close('all')
    
    #%% IWV dependence
    fig, axes = plt.subplots(5, 4, figsize=(6, 7), sharex=True, sharey=True)
    
    axes[-1, 0].set_ylabel('$TB_{obs} - TB_{mod}$ [K]')
    axes[-1, 0].set_xlabel('IWV [kg m$^{-2}$]')
    
    axes[0, 0].set_title(r'center', fontsize=8)
    axes[0, 1].set_title(r'cutoff', fontsize=8)
    axes[0, 2].set_title(r'center+cutoff', fontsize=8)
    axes[0, 3].set_title(r'tophat', fontsize=8)
    
    for i, ax in enumerate(axes.flatten('F')):
        
        ax.annotate(f'({abc[i]})', xy=(0.02, 0.98), xycoords='axes fraction',
                    ha='left', va='top')
        
        # x axis
        ax.set_xticks(ticks=np.arange(0, 150, 25), minor=False)
        ax.set_xticks(ticks=np.arange(0, 150, 5), minor=True)
        
        # y axis
        ax.set_yticks(ticks=np.arange(-2, 2, 0.5), minor=False)
        ax.set_yticks(ticks=np.arange(-2, 2, 0.1), minor=True)
        
        ax.tick_params(which='major')
        ax.tick_params(which='minor', length=1)
        ax.grid('both', alpha=0.5)
        
        ax.axhline(y=0, color='k', linewidth=1, alpha=0.5)
        
        ax.set_ylim([-1.4, 1.4])
        ax.set_xlim([0, 75])
        
    # annotate channel name
    for i, ax in enumerate(axes[:, -1]):
        ax.annotate(text=mwi.freq_txt[i], xy=(1.1, 0.5), xycoords='axes fraction', backgroundcolor="w",
                    annotation_clip=False, horizontalalignment='left', verticalalignment='center', fontsize=8)
    
    for i, channel in enumerate(mwi.channels_int):
        for j, est_type in enumerate(['freq_center', 'freq_bw', 'freq_bw_center', 'tophat']):
            axes[i, j].scatter(ds_com.iwv, 
                               ds_com.dtb_mwi_est.sel(channel=channel,
                                                      est_type=est_type), 
                               s=2, c=c_list, linewidths=0, alpha=0.5)
    
    fig.tight_layout()
    
    # legend below
    patches = []
    stations = wyo.station_id.keys()
    for station in stations:
        patches.append(mpatches.Patch(color=colors[station], label=station))
    leg = axes[-1, -1].legend(handles=patches, bbox_to_anchor=(1.05, 0.2), loc='upper left', frameon=False, ncol=1, fontsize=6, title='Radiosonde location:')
    plt.setp(leg.get_title(),fontsize=6)
    
    plt.savefig(path_plot+'iwv_dependency/iwv_dependency.png', dpi=400,
                bbox_inches='tight')
    
    plt.close('all')
    
    #%% 2d histogram iwv and tb dependence
    # plots are too small, either just plot one of the calculation methods
    # or nothing!
    # x: TB MWI
    # y: IWV
    # color: dTb    
    fig, axes = plt.subplots(5, 4, figsize=(6, 7), sharex=True, sharey=True,
                             constrained_layout=True)
    
    axes[-1, 0].set_ylabel('$TB_{obs}$ [K]')
    axes[-1, 0].set_xlabel('IWV [kg m$^{-2}$]')
    
    axes[0, 0].set_title(r'center', fontsize=8)
    axes[0, 1].set_title(r'cutoff', fontsize=8)
    axes[0, 2].set_title(r'center+cutoff', fontsize=8)
    axes[0, 3].set_title(r'tophat', fontsize=8)
    
    for i, ax in enumerate(axes.flatten('F')):
        
        ax.annotate(f'({abc[i]})', xy=(0.02, 0.98), xycoords='axes fraction',
                    ha='left', va='top')
        
        # x axis
        #ax.set_xticks(ticks=np.arange(0, 150, 25), minor=False)
        #ax.set_xticks(ticks=np.arange(0, 150, 5), minor=True)
        
        # y axis
        #ax.set_yticks(ticks=np.arange(-2, 2, 0.5), minor=False)
        #ax.set_yticks(ticks=np.arange(-2, 2, 0.1), minor=True)
        
        ax.tick_params(which='major')
        ax.tick_params(which='minor', length=1)
                
        ax.set_ylim([235, 290])
        ax.set_xlim([0, 75])
        
    # annotate channel name
    for i, ax in enumerate(axes[:, -1]):
        ax.annotate(text=mwi.freq_txt[i], xy=(1.1, 0.5), xycoords='axes fraction', backgroundcolor="w",
                    annotation_clip=False, horizontalalignment='left', verticalalignment='center', fontsize=8)
    
    for i, channel in enumerate(mwi.channels_int):
        for j, est_type in enumerate(['freq_center', 'tophat']):
            
            im = axes[i, j].scatter(ds_com.iwv, 
                               ds_com.tb_mwi_orig.sel(channel=channel),
                               c=np.abs(ds_com.dtb_mwi_est.sel(channel=channel,
                                                        est_type=est_type)), 
                               cmap='jet',
                               s=2, linewidths=0)
            fig.colorbar(im, ax=axes[i, j], orientation='horizontal')
    
    plt.savefig(path_plot+'iwv_dependency/iwv_tb_dependency.png', dpi=400,
                bbox_inches='tight')
    
    plt.close('all')
    
    #%% dependence on systematic perturbation
    
    