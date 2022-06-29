

import numpy as np
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.dates as mdates
import os
import sys
sys.path.append(f'{os.environ["PATH_PHD"]}/projects/mwi_bandpass_effects/scripts')
from importer import Sensitivity, Delta_TB
from mwi_info import mwi
from layout import colors, names
from radiosonde import wyo
from path_setter import *


"""
Description

Analyze seasonal and regional dependency of the difference between the virtual
MWI measurement and the TB calculated with PAMTRA.

Requires:
    - seven radiosonde profiles
    
Caution: no clouds included
"""


if __name__ == '__main__':
    
    # format for boxplot
    pam_colors = {'ess_djf': '#008B00', 'ess_mam': '#51FF51', 
                    'arctic_winter': '#002375', 'arctic_summer': '#6594FF', 
                    'tropics_february': '#AE0000', 'tropics_august': '#FF5555',
                    'standard': '#000000'}
    
    #%% read nc files
    # delta_tb shape: (channel, profile, noise_level, reduction_level)
    # delta_tb.mean_freq_center
    # delta_tb.std_freq_center
    # delta_tb.mean_freq_bw
    # delta_tb.std_freq_bw
    # delta_tb.mean_freq_bw_center
    # delta_tb.std_freq_bw_center
    delta_tb = Delta_TB()
    delta_tb.read_data()

    #%% create indices for summarizing statistics
    station_id = np.array([x[3:8] for x in delta_tb.profile])
    date = np.array([datetime.datetime.strptime(x[-12:], '%Y%m%d%H%M') for x in delta_tb.profile])
    year = np.array([x.year for x in date])
    month = np.array([x.month for x in date])
    
    ix_nya = station_id == wyo.station_id['Ny Alesund']
    ix_snp = station_id == wyo.station_id['Singapore']
    ix_ess = station_id == wyo.station_id['Essen']
    ix_bar = station_id == wyo.station_id['Barbados']
    ix_std = station_id == '00000'
    
    ix_2019 = year == 2019
    ix_2020 = year == 2020
    
    ix_djf = np.isin(month, [12, 1, 2])
    ix_mam = np.isin(month, [3, 4, 5])
    ix_jja = np.isin(month, [6, 7, 8])
    ix_son = np.isin(month, [9, 10, 11])
    
    ix_noise_lev_0 = delta_tb.noise_level == 0
    ix_red_lev_1 = delta_tb.reduction_level == 1

    #%% data availability
    len_2019 = 365
    text = 'Data availability of station {} in 2019: {}'
    print(text.format('Ny Alesund', np.sum(ix_2019 & ix_nya)/len_2019))
    print(text.format('Singapore', np.sum(ix_2019 & ix_snp)/len_2019))
    print(text.format('Essen', np.sum(ix_2019 & ix_ess)/len_2019))
    print(text.format('Barbados', np.sum(ix_2019 & ix_bar)/len_2019))
    
    #%% PROOF plot data availability
    fig = plt.figure(figsize=(5, 2))
    ax = fig.add_subplot(111, facecolor='#2BB443')
    ax.set_title('Data availability in 2019')
    dates = pd.date_range('2019-01-01', '2019-12-31', freq='1D')
    df = pd.DataFrame(index=dates, data=1, columns=['nya', 'ess', 'bar', 'snp'])
    date_nya = [x.date() for x in date[ix_2019 & ix_nya]]
    date_ess = [x.date() for x in date[ix_2019 & ix_ess]]
    date_bar = [x.date() for x in date[ix_2019 & ix_bar]]
    date_snp = [x.date() for x in date[ix_2019 & ix_snp]]
    
    y1 = np.zeros(len(dates))
    df.loc[date_nya, 'nya'] = 0
    df.loc[date_ess, 'ess'] = 0
    df.loc[date_snp, 'snp'] = 0
    df.loc[date_bar, 'bar'] = 0
    
    ax.fill_between(x=dates, y1=y1, y2=df.loc[:, 'nya'], step='mid', color='#EB3939')
    ax.fill_between(x=dates, y1=y1-1, y2=df.loc[:, 'ess']-1, step='mid', color='#EB3939')
    ax.fill_between(x=dates, y1=y1-2, y2=df.loc[:, 'snp']-2, step='mid', color='#EB3939')
    ax.fill_between(x=dates, y1=y1-3, y2=df.loc[:, 'bar']-3, step='mid', color='#EB3939')
    
    ax.set_xlim([dates[0], dates[-1]])
    ax.set_ylim([-3, 1])
    
    ax.axhline(y=0, color='k', linewidth=1)
    ax.axhline(y=-1, color='k', linewidth=1)
    ax.axhline(y=-2, color='k', linewidth=1)
    
    # tick for every month
    months = mdates.MonthLocator()
    months_fmt = mdates.DateFormatter('%m')
    ax.xaxis.set_major_locator(months)
    ax.xaxis.set_major_formatter(months_fmt)
    
    # remove y axis
    ax.set_yticks([])
    ax.set_xlabel('Month')

    # annotate station
    y = np.arange(0.5, -3, -1)
    for i, name in enumerate(['Ny Alesund', 'Essen', 'Singapore', 'Barbados']):
        ax.annotate(text=name, xy=(dates[0], y[i]), xycoords='data', ha='right', va='center')

    plt.subplots_adjust(right=0.99, top=0.85, left=0.16, bottom=0.25)

    plt.savefig(path_plot + 'radiosonde_profiles/data_availability.png', dpi=200)
    
    #%% slice data and store in dictionary
    seas = {}  # overall dataset for seasonal analysis
    
    center = {}  # overall dataset for center
    
    # Ny Alesund (Seasons 2019)
    nya = {}
    nya['all'] = delta_tb.mean_freq_center[:, ix_nya & ix_2019, ix_noise_lev_0, ix_red_lev_1]  # 2019
    nya['djf'] = delta_tb.mean_freq_center[:, ix_nya & ix_2019 & ix_djf, ix_noise_lev_0, ix_red_lev_1]  # DJF 2019
    nya['mam'] = delta_tb.mean_freq_center[:, ix_nya & ix_2019 & ix_mam, ix_noise_lev_0, ix_red_lev_1]  # MAM 2019
    nya['jja'] = delta_tb.mean_freq_center[:, ix_nya & ix_2019 & ix_jja, ix_noise_lev_0, ix_red_lev_1]  # JJA 2019
    nya['son'] = delta_tb.mean_freq_center[:, ix_nya & ix_2019 & ix_son, ix_noise_lev_0, ix_red_lev_1]  # SON 2019
    center['nya'] = nya  # put in overall dataset

    # averages Essen
    ess = {}
    ess['all'] = delta_tb.mean_freq_center[:, ix_ess & ix_2019, ix_noise_lev_0, ix_red_lev_1]  # 2019
    ess['djf'] = delta_tb.mean_freq_center[:, ix_ess & ix_2019 & ix_djf, ix_noise_lev_0, ix_red_lev_1]  # DJF 2019
    ess['mam'] = delta_tb.mean_freq_center[:, ix_ess & ix_2019 & ix_mam, ix_noise_lev_0, ix_red_lev_1]  # MAM 2019
    ess['jja'] = delta_tb.mean_freq_center[:, ix_ess & ix_2019 & ix_jja, ix_noise_lev_0, ix_red_lev_1]  # JJA 2019
    ess['son'] = delta_tb.mean_freq_center[:, ix_ess & ix_2019 & ix_son, ix_noise_lev_0, ix_red_lev_1]  # SON 2019
    center['ess'] = ess  # put in overall dataset
    
    # averages Singapore
    snp = {}
    snp['all'] = delta_tb.mean_freq_center[:, ix_snp & ix_2019, ix_noise_lev_0, ix_red_lev_1]  # 2019
    snp['djf'] = delta_tb.mean_freq_center[:, ix_snp & ix_2019 & ix_djf, ix_noise_lev_0, ix_red_lev_1]  # DJF 2019
    snp['mam'] = delta_tb.mean_freq_center[:, ix_snp & ix_2019 & ix_mam, ix_noise_lev_0, ix_red_lev_1]  # MAM 2019
    snp['jja'] = delta_tb.mean_freq_center[:, ix_snp & ix_2019 & ix_jja, ix_noise_lev_0, ix_red_lev_1]  # JJA 2019
    snp['son'] = delta_tb.mean_freq_center[:, ix_snp & ix_2019 & ix_son, ix_noise_lev_0, ix_red_lev_1]  # SON 2019
    center['snp'] = snp
    
    seas['center'] = center # put center in overall dataset
    
    bw = {}  # overall dataset for bw
    
    # Ny Alesund (Seasons 2019)
    nya = {}
    nya['all'] = delta_tb.mean_freq_bw[:, ix_nya & ix_2019, ix_noise_lev_0, ix_red_lev_1]  # 2019
    nya['djf'] = delta_tb.mean_freq_bw[:, ix_nya & ix_2019 & ix_djf, ix_noise_lev_0, ix_red_lev_1]  # DJF 2019
    nya['mam'] = delta_tb.mean_freq_bw[:, ix_nya & ix_2019 & ix_mam, ix_noise_lev_0, ix_red_lev_1]  # MAM 2019
    nya['jja'] = delta_tb.mean_freq_bw[:, ix_nya & ix_2019 & ix_jja, ix_noise_lev_0, ix_red_lev_1]  # JJA 2019
    nya['son'] = delta_tb.mean_freq_bw[:, ix_nya & ix_2019 & ix_son, ix_noise_lev_0, ix_red_lev_1]  # SON 2019
    bw['nya'] = nya  # put in overall dataset

    # averages Essen
    ess = {}
    ess['all'] = delta_tb.mean_freq_bw[:, ix_ess & ix_2019, ix_noise_lev_0, ix_red_lev_1]  # 2019
    ess['djf'] = delta_tb.mean_freq_bw[:, ix_ess & ix_2019 & ix_djf, ix_noise_lev_0, ix_red_lev_1]  # DJF 2019
    ess['mam'] = delta_tb.mean_freq_bw[:, ix_ess & ix_2019 & ix_mam, ix_noise_lev_0, ix_red_lev_1]  # MAM 2019
    ess['jja'] = delta_tb.mean_freq_bw[:, ix_ess & ix_2019 & ix_jja, ix_noise_lev_0, ix_red_lev_1]  # JJA 2019
    ess['son'] = delta_tb.mean_freq_bw[:, ix_ess & ix_2019 & ix_son, ix_noise_lev_0, ix_red_lev_1]  # SON 2019
    bw['ess'] = ess  # put in overall dataset
    
    # averages Singapore
    snp = {}
    snp['all'] = delta_tb.mean_freq_bw[:, ix_snp & ix_2019, ix_noise_lev_0, ix_red_lev_1]  # 2019
    snp['djf'] = delta_tb.mean_freq_bw[:, ix_snp & ix_2019 & ix_djf, ix_noise_lev_0, ix_red_lev_1]  # DJF 2019
    snp['mam'] = delta_tb.mean_freq_bw[:, ix_snp & ix_2019 & ix_mam, ix_noise_lev_0, ix_red_lev_1]  # MAM 2019
    snp['jja'] = delta_tb.mean_freq_bw[:, ix_snp & ix_2019 & ix_jja, ix_noise_lev_0, ix_red_lev_1]  # JJA 2019
    snp['son'] = delta_tb.mean_freq_bw[:, ix_snp & ix_2019 & ix_son, ix_noise_lev_0, ix_red_lev_1]  # SON 2019
    bw['snp'] = snp
    
    seas['bw'] = bw # put bw in overall dataset
    
    bw_center = {}  # overall dataset for bw_center
    
    # Ny Alesund (Seasons 2019)
    nya = {}
    nya['all'] = delta_tb.mean_freq_bw_center[:, ix_nya & ix_2019, ix_noise_lev_0, ix_red_lev_1]  # 2019
    nya['djf'] = delta_tb.mean_freq_bw_center[:, ix_nya & ix_2019 & ix_djf, ix_noise_lev_0, ix_red_lev_1]  # DJF 2019
    nya['mam'] = delta_tb.mean_freq_bw_center[:, ix_nya & ix_2019 & ix_mam, ix_noise_lev_0, ix_red_lev_1]  # MAM 2019
    nya['jja'] = delta_tb.mean_freq_bw_center[:, ix_nya & ix_2019 & ix_jja, ix_noise_lev_0, ix_red_lev_1]  # JJA 2019
    nya['son'] = delta_tb.mean_freq_bw_center[:, ix_nya & ix_2019 & ix_son, ix_noise_lev_0, ix_red_lev_1]  # SON 2019
    bw_center['nya'] = nya  # put in overall dataset

    # averages Essen
    ess = {}
    ess['all'] = delta_tb.mean_freq_bw_center[:, ix_ess & ix_2019, ix_noise_lev_0, ix_red_lev_1]  # 2019
    ess['djf'] = delta_tb.mean_freq_bw_center[:, ix_ess & ix_2019 & ix_djf, ix_noise_lev_0, ix_red_lev_1]  # DJF 2019
    ess['mam'] = delta_tb.mean_freq_bw_center[:, ix_ess & ix_2019 & ix_mam, ix_noise_lev_0, ix_red_lev_1]  # MAM 2019
    ess['jja'] = delta_tb.mean_freq_bw_center[:, ix_ess & ix_2019 & ix_jja, ix_noise_lev_0, ix_red_lev_1]  # JJA 2019
    ess['son'] = delta_tb.mean_freq_bw_center[:, ix_ess & ix_2019 & ix_son, ix_noise_lev_0, ix_red_lev_1]  # SON 2019
    bw_center['ess'] = ess  # put in overall dataset
    
    # averages Singapore
    snp = {}
    snp['all'] = delta_tb.mean_freq_bw_center[:, ix_snp & ix_2019, ix_noise_lev_0, ix_red_lev_1]  # 2019
    snp['djf'] = delta_tb.mean_freq_bw_center[:, ix_snp & ix_2019 & ix_djf, ix_noise_lev_0, ix_red_lev_1]  # DJF 2019
    snp['mam'] = delta_tb.mean_freq_bw_center[:, ix_snp & ix_2019 & ix_mam, ix_noise_lev_0, ix_red_lev_1]  # MAM 2019
    snp['jja'] = delta_tb.mean_freq_bw_center[:, ix_snp & ix_2019 & ix_jja, ix_noise_lev_0, ix_red_lev_1]  # JJA 2019
    snp['son'] = delta_tb.mean_freq_bw_center[:, ix_snp & ix_2019 & ix_son, ix_noise_lev_0, ix_red_lev_1]  # SON 2019
    bw_center['snp'] = snp
    
    seas['bw_center'] = bw_center # put bw_center in overall dataset
    
    #%%
    freq_pos_label =  {'center': r'$TB_{ref}$ at'+'\n'+r'$\nu_{center}$',
                       'bw': r'$TB_{ref}$ at'+'\n'+r'$\nu_{center \pm \frac{1}{2} bandwidth}$',
                       'bw_center': r'$TB_{ref}$ at'+'\n'+r'$\nu_{center}$ and $\nu_{center \pm \frac{1}{2} bandwidth}$',
                       }
    
    #%% Seasonal evaluation of Ny Alesund
    # usage: choose dataset for analyses and choose outfile name
    for freq_pos in list(seas.keys()):
    
        data = seas[freq_pos]
        
        fig, axes = plt.subplots(3, 1, figsize=(6, 7), sharex=True)#, sharey=True)
        plt.suptitle('2019 all year and seasonal variability')
        
        seasons = ['all', 'djf', 'mam', 'jja', 'son']
        seasons_col = ['#777777', '#0076BC', '#00CC4C', '#FF9400', '#B200BF']
        dx = np.linspace(-0.3, 0.3, 5)  # space between boxplots (every season next to each other)
        
        flierprops = dict(markeredgecolor='k', markersize=1)
        medianprops = dict(color='k')
        kwargs = dict(sym="d", widths=0.075, patch_artist=True)
    
        for i, season in enumerate(seasons):
    
            # NYA
            boxprops = dict(facecolor=seasons_col[i], color=seasons_col[i])
            axes[0].boxplot(x=data['nya'][season].isel(noise_level=0, reduction_level=0).T, positions=mwi.channels_int + dx[i],
                            boxprops=boxprops, flierprops=flierprops, medianprops=medianprops, **kwargs)
            
            # ESS
            boxprops = dict(facecolor=seasons_col[i], color=seasons_col[i])
            axes[1].boxplot(x=data['ess'][season].isel(noise_level=0, reduction_level=0).T, positions=mwi.channels_int + dx[i],
                            boxprops=boxprops, flierprops=flierprops, medianprops=medianprops, **kwargs)
            
            # SNP
            boxprops = dict(facecolor=seasons_col[i], color=seasons_col[i])
            axes[2].boxplot(x=data['snp'][season].isel(noise_level=0, reduction_level=0).T, positions=mwi.channels_int + dx[i],
                            boxprops=boxprops, flierprops=flierprops, medianprops=medianprops, **kwargs)
            
        axes[1].set_ylabel(r'$\Delta TB = TB_{obs} - TB_{ref}$ [K]')
        
        # axis limits
        axes[-1].set_xlim([13.5, 18.5])
        
        for ax in axes:
            ax.set_yticks(np.arange(-1.5, 1.6, 0.75))
            
            ax.set_xticks(np.arange(14, 19), minor=True)
            ax.set_xticks(np.arange(13.5, 19.5), minor=False)
            ax.set_xticklabels([x.replace('183.31', '') for x in mwi.freq_txt], minor=True)
            ax.set_xticklabels('', minor=False)
            ax.xaxis.grid(True, which='major')
            ax.yaxis.grid(True)
            ax.tick_params('x', length=0, width=0, which='minor')
    
            ax.axhline(y=0, color='k', linestyle='--', linewidth=.75)
        
        # add season on top
        #ax_top = axes[0].secondary_xaxis('top')
        #loc = np.sort(np.array([x+dx for x in mwi.channels_int]).flatten())
        #ax_top.set_xticks(loc)
        seasons_cap = [x.upper() for x in seasons]
        #ax_top.set_xticklabels(seasons_cap*5, rotation=70)
        
        # vertical line for every month
        #for ax in axes:
        #    for l in loc:
        #        ax.axvline(l, linewidth=0.5, color='blue', alpha=0.5)
    
        patches = []
        for i, s in enumerate(seasons_cap):
            patches.append(mpatches.Patch(color=seasons_col[i], label=s))
        le = axes[0].legend(handles=patches, bbox_to_anchor=(0.75, 1.3), ncol=3, loc='center', frameon=False, title='months:', fontsize=7)
        le.get_title().set_fontsize(7)
    
        # annotate location
        for i, name in enumerate(names):
            axes[i].annotate(text=name, xy=(1.01, 0.5), va='center', ha='left', xycoords='axes fraction')
    
        axes[0].annotate(text=freq_pos_label[freq_pos], xy=(0.25, 1.3), xycoords='axes fraction', va='center', ha='center', fontsize=7)
    
        plt.subplots_adjust(top=0.85, bottom=0.1, right=0.85, left=0.15)
        
        plt.savefig(path_plot + 'seasonal_dependency/seasonal_2019_freq_'+freq_pos+'.png', dpi=200)
        plt.close()
