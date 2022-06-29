

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import xarray as xr
import datetime
import os
import sys
sys.path.append(f'{os.environ["PATH_PHD"]}/projects/mwi_bandpass_effects/scripts')
from mwi_info import mwi
from layout import profile_prop
from importer import PAMTRA_TB
from radiosonde import wyo
from path_setter import *


"""
Description

Plot brightness temperature spectrum of radiosonde profiles
    - annual mean and standard deviation

"""


if __name__ == '__main__':
    
    # read brightness temperatures
    # read pamtra simulations
    Pam = PAMTRA_TB()
    Pam.read_all(era5=True)
    Pam.pam_data_df
    #Pam.pam_data_df.to_csv(path_data+'brightness_temperature/TB_all.txt')
    # aboves read takes about 2 min
    #Pam.pam_data_df = pd.read_csv(path_data+'brightness_temperature/TB_all.txt', sep=',', index_col=0)
    
    # to xarray
    profiles = Pam.pam_data_df.columns.values
    profiles = np.delete(profiles, profiles=='frequency [GHz]')
    kwargs = {'dims': ('profile', 'frequency'), 
                       'coords': { 'profile': profiles, 'frequency': Pam.pam_data_df['frequency [GHz]'].values},
                       'attrs': {'unit': 'K', 'name': 'brightness temperature as function of frequency in GHz', 'source': 'WYO and PAMTRA'}
                     }
    pam_data_xr = xr.DataArray(data=Pam.pam_data_df.iloc[:, 1:].values.T, **kwargs)
    
    #%% get             
    profile_name = np.array([x[5:].split('_hydro')[0] for x in pam_data_xr.profile.values])
    hydro_status = ['hydro_'+x.split('_')[-1] for x in pam_data_xr.profile.values]
        
    # station index
    ix_arc = profile_name == 'arctic'
    ix_tro = profile_name == 'tropics'
    ix_mid = profile_name == 'mid_lat'
    
    # hydro status index
    ix_hyd_on = hydro_status == 'hydro_on'
    ix_hyd_off = hydro_status == 'hydro_off'
    
    #%% colors and linestyles for plot
    colors = {'arctic': 'blue', 'tropics': 'red', 'mid_lat': 'green'}
    line = {'hydro_on': ':',
            'hydro_off': '-'}
    
    #%% OK, but take below Plot integrated water vapor throughout the year for all stations
    fig = plt.figure(figsize=(4, 5))
    ax = fig.add_subplot(111)
    fig.suptitle('Simulated brightness temperature\ndotted: with hydrometeors')
    
    for i, profile in enumerate(pam_data_xr.profile.values):
        
        c = colors[profile_name[i]]
        s = line[hydro_status[i]]
        
        y = pam_data_xr.sel(profile=profile)
        
        ax.plot(pam_data_xr.frequency, y, color=c, linewidth=1.5, label=profile_name[i]+' '+hydro_status[i], zorder=3, linestyle=s)
    
    # add MWI channels
    ax.annotate(text='[channel]', xy=(1.1, 1), xycoords='axes fraction', fontsize=7, ha='center', va='bottom')
    for i, channel in enumerate(mwi.channels_str):
        
        # annotate channel name
        ax.annotate(text=mwi.freq_txt[i][4:6], xy=[mwi.freq_center[i, 0], 288], fontsize=7, ha='center', va='bottom')
        ax.annotate(text=mwi.freq_txt[i][4:6], xy=[mwi.freq_center[i, 1], 288], fontsize=7, ha='center', va='bottom')
        
        # add vertical lines
        ax.axvline(x=mwi.freq_center[i, 0], color='gray', linestyle=':', alpha=0.5, linewidth=1)  # mark left channel frequency
        ax.axvline(x=mwi.freq_center[i, 1], color='gray', linestyle=':', alpha=0.5, linewidth=1)  # mark right channel frequency
    ax.axvline(x=mwi.absorpt_line, color='k', linestyle=':', alpha=0.5, linewidth=1)  # mark line center
    
    ax.legend(bbox_to_anchor=(0.5, -0.25), ncol=3, loc='upper center', frameon=True, fontsize=6)
    ax.grid(axis='y')
    ax.set_ylim([205, 288])
    ax.set_xlim([np.min(pam_data_xr.frequency), np.max(pam_data_xr.frequency)])
    ax.set_xlabel('Frequency [GHz]')
    ax.set_ylabel('Brightness temperature [K]')
    
    plt.subplots_adjust(right=0.85, bottom=0.25, top=0.83, left=0.2)
    
    plt.savefig(path_plot + 'brightness_temperature/tb_era5.png', dpi=300)
    
    plt.close()
