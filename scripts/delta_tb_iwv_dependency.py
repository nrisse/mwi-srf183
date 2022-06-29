

import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import xarray as xr
import os
import sys
sys.path.append(f'{os.environ["PATH_PHD"]}/projects/mwi_bandpass_effects/scripts')
from mwi_info import mwi
from importer import Delta_TB, IWV
from radiosonde import wyo
from path_setter import *


"""
DESCRIPTION

Evaluation of delta_tb depending on the IWV of the profiles

PROOF
"""


if __name__ == '__main__':
    
    #%% figure paths
    fig_freq_center = path_plot + 'iwv_dependency/iwv_dependency_freq_center.png'
    fig_freq_bw = path_plot + 'iwv_dependency/iwv_dependency_freq_bw.png'
    fig_freq_bw_center = path_plot + 'iwv_dependency/iwv_dependency_freq_bw_center.png'
    fig_all = path_plot + 'iwv_dependency/iwv_dependency_all.png'
    
    #%% Read IWV and delta_TB data
    # read nc files
    # delta_tb shape: (channel, profile, noise_level, reduction_level)
    # delta_tb.mean_freq_center
    # delta_tb.std_freq_center
    # delta_tb.mean_freq_bw
    # delta_tb.std_freq_bw
    # delta_tb.mean_freq_bw_center
    # delta_tb.std_freq_bw_center
    #delta_tb = Delta_TB()
    #delta_tb.read_data()
    delta_tb = xr.load_dataset(path_data+'delta_tb/delta_tb.nc')
    
    iwv = IWV()
    iwv.read_data()
    iwv.data = iwv.data.sel(profile=delta_tb.profile)  # reorder iwv data based on delta_tb profile order
    
    #%% get only 2019 profiles
    station_id = np.array([x[3:8] for x in delta_tb.profile.values])
    date = np.array([datetime.datetime.strptime(x[-12:], '%Y%m%d%H%M') for x in delta_tb.profile.values])
    year = np.array([x.year for x in date])
    ix_2019 = year == 2019
    
    # station index
    ix_nya = station_id == wyo.station_id['Ny Alesund']
    ix_snp = station_id == wyo.station_id['Singapore']
    ix_ess = station_id == wyo.station_id['Essen']
    ix_bar = station_id == wyo.station_id['Barbados']
    ix_std = station_id == '00000'
    
    # no noise, no data reduction
    ix_noise_lev_0 = delta_tb.noise_level == 0
    ix_red_lev_1 = delta_tb.reduction_level == 1
    
    # get data for 2019
    delta_tb_freq_center = delta_tb.delta_tb_mean_freq_center.isel(noise_level=0, reduction_level=0)  # 2019
    delta_tb_freq_bw = delta_tb.delta_tb_mean_freq_bw[:, ix_2019, ix_noise_lev_0, ix_red_lev_1].isel(noise_level=0, reduction_level=0)  # 2019
    delta_tb_freq_bw_center = delta_tb.delta_tb_mean_freq_bw_center[:, ix_2019, ix_noise_lev_0, ix_red_lev_1].isel(noise_level=0, reduction_level=0)  # 2019
    iwv_data = iwv.data[ix_2019]

    #%% colors for plot
    colors = {'01004': 'b',
              '10410': 'g',
              '48698': 'r',
              '78954': 'orange',
              }
    
    c_list = [colors[p[3:8]] for p in iwv_data.profile.values]

    #%% PROOF all in one
    fig, axes = plt.subplots(5, 3, figsize=(6, 8), sharex=True, sharey=True)
    
    axes[2, 0].set_ylabel(r'$\Delta TB = TB_{obs} - TB_{ref}$ [K]')
    axes[-1, 1].set_xlabel('Integrated water vapor [kg m$^{-2}$]')
    
    axes[0, 0].set_title(r'$TB_{ref}$ at'+'\n'+r'$\nu_{center}$', fontsize=8)
    axes[0, 1].set_title(r'$TB_{ref}$ at'+'\n'+r'$\nu_{center \pm \frac{1}{2} bandwidth}$', fontsize=8)
    axes[0, 2].set_title(r'$TB_{ref}$ at'+'\n'+r'$\nu_{center}$ and $\nu_{center \pm \frac{1}{2} bandwidth}$', fontsize=8)
    
    for ax in axes.flatten():
        
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
    
    for i, channel in enumerate(mwi.channels_str):
        axes[i, 0].scatter(iwv_data, delta_tb_freq_center.sel(channel=channel), s=2, c=c_list, linewidths=0, alpha=0.5)
        axes[i, 1].scatter(iwv_data, delta_tb_freq_bw.sel(channel=channel), s=2, c=c_list, linewidths=0, alpha=0.5)
        axes[i, 2].scatter(iwv_data, delta_tb_freq_bw_center.sel(channel=channel), s=2, c=c_list, linewidths=0, alpha=0.5)
    
    fig.tight_layout()

    # legend below
    patches = []
    stations = wyo.station_id.keys()
    for station in stations:
        patches.append(mpatches.Patch(color=colors[wyo.station_id[station]], label=station))
    leg = axes[-1, -1].legend(handles=patches, bbox_to_anchor=(1.05, 0.2), loc='upper left', frameon=False, ncol=1, fontsize=6, title='Radiosonde location:')
    plt.setp(leg.get_title(),fontsize=6)
    
    plt.savefig(fig_all, dpi=400)
    
    #%%
    """
    RESULT
    the IWV explains the error for the channel very well, except for channel 18 (closest to maximum)
    for this, temperature can be included
    
    differences in the calculation method ....
    
    under clear-sky conditions the deviation from MWI measurement and model
    simulation at the MWI-frequencies can be corrected if the IWV of the atmosphere
    measured by MWI is known
    
    how do clouds influence this pattern? Suggestion: ice clouds strongly perturb 
    the simple pattern. Thin liquid clouds may not change the result
    """
