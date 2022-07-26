

import numpy as np
import matplotlib.pyplot as plt
import os
import sys
sys.path.append(f'{os.environ["PATH_PHD"]}/projects/mwi_bandpass_effects/scripts')
from mwi_info import mwi
from importer import Delta_TB
from path_setter import path_data, path_plot


"""
DESCRIPTION

Evaluation of delta_tb depending on the clouds of the era5 dataset

Not used in the final report
"""


if __name__ == '__main__':
    
    #%% Read IWV and delta_TB data
    # read nc files
    # delta_tb shape: (channel, profile, noise_level, reduction_level)
    # delta_tb.mean_freq_center
    # delta_tb.std_freq_center
    # delta_tb.mean_freq_bw
    # delta_tb.std_freq_bw
    # delta_tb.mean_freq_bw_center
    # delta_tb.std_freq_bw_center
    delta_tb = Delta_TB()
    delta_tb.read_data(file=path_data+'delta_tb/delta_tb_nadir_era5.nc')
    
    #%%
    # index for cloud and no cloud
    delta_tb.mean_freq_center   
    
    #%%
    # colors for plot
    colors = {'arctic': 'blue', 'tropics': 'red', 'mid_lat': 'green'}
    marker = {'hydro_on': 'o',
              'hydro_off': '*'}
    
    #%% plot cloud effect
    
    noise_lev = 0
    reduction_lev = 1
    
    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_subplot(111)
    ax.set_title('Hydrometer effect\nCircle: with hydrometeors, Star: without hydrometeors')
    
    profiles = delta_tb.mean_freq_center.profile.values

    for ch in mwi.channels_str:
        
        for profile in profiles:
            
            col = colors[profile[5:].split('_hydro')[0]]
            mar = marker['hydro_'+profile.split('_')[-1]]
            
            y = delta_tb.mean_freq_center.sel(channel=ch, profile=profile, noise_level=noise_lev, reduction_level=reduction_lev)
            
            ax.scatter(int(ch), y, s=80, marker=mar, facecolors="None", edgecolor=col)

    
    ax.set_ylabel('$\Delta TB = TB_{MWI} - TB_{PAMTRA}$ [K]')
    
    # axis limits
    ax.set_ylim([-0.6, 0.6])
    ax.set_xlim([13.5, 18.5])

    # axis tick settings
    ax.set_xticks(np.arange(14, 19), minor=True)
    ax.set_xticks(np.arange(13.5, 19.5), minor=False)
    ax.set_xticklabels(mwi.freq_txt, minor=True)
    ax.set_xticklabels('', minor=False)
    ax.xaxis.grid(True, which='major')
    ax.yaxis.grid(True)
    ax.tick_params('x', length=0, width=0, which='minor')
    
    # add 0-line
    ax.axhline(y=0, color='k', linestyle='--', linewidth=.75)
    
    # legend
    ax.legend(bbox_to_anchor=(1.05, 0.5), loc='center left', frameon=False)
    
    # layout
    fig.tight_layout()
    
    plt.savefig(path_plot + 'cloud_effect/nadir/cloud_effect_nadir.png', dpi=200)
    
    plt.close()
