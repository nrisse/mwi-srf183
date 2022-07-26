

import numpy as np
import datetime
import matplotlib.pyplot as plt
import os
import sys
sys.path.append(f'{os.environ["PATH_PHD"]}/projects/mwi_bandpass_effects/scripts')
from radiosonde import wyo
from mwi_info import mwi
from importer import Delta_TB
from path_setter import *
from layout import colors, names


"""
Influence of noise and data reduction on the result

last edited: Nov 4 2020

two figures are used
"""


if __name__ == '__main__':
    
    # read nc files
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
    
    ix_red_lev_1 = delta_tb.reduction_level == 1
    ix_noise_lev_0 = delta_tb.noise_level == 0
    
    #%% data availability
    np.sum(ix_2019 & ix_nya)
    np.sum(ix_2019 & ix_snp)
    np.sum(ix_2019 & ix_ess)
    
    #%% summarize data
    # average over profiles
    avg = 'profile'
    
    # all channels, avg over time, all noise, only no data reduction
    noise_nya_abs_mean = np.abs(delta_tb.mean_freq_center[:, ix_nya & ix_2019, :, ix_red_lev_1]).mean(avg).transpose('noise_level', 'channel', 'reduction_level')
    noise_ess_abs_mean = np.abs(delta_tb.mean_freq_center[:, ix_ess & ix_2019, :, ix_red_lev_1]).mean(avg).transpose('noise_level', 'channel', 'reduction_level')
    noise_snp_abs_mean = np.abs(delta_tb.mean_freq_center[:, ix_snp & ix_2019, :, ix_red_lev_1]).mean(avg).transpose('noise_level', 'channel', 'reduction_level')
    
    noise_nya_std = delta_tb.std_freq_center[:, ix_nya & ix_2019, :, ix_red_lev_1].mean(avg).transpose('noise_level', 'channel', 'reduction_level')
    noise_ess_std = delta_tb.std_freq_center[:, ix_ess & ix_2019, :, ix_red_lev_1].mean(avg).transpose('noise_level', 'channel', 'reduction_level')
    noise_snp_std = delta_tb.std_freq_center[:, ix_snp & ix_2019, :, ix_red_lev_1].mean(avg).transpose('noise_level', 'channel', 'reduction_level')
    
    # all channels, avg over time, no noise, all data reduction
    red_nya_abs_mean = np.abs(delta_tb.mean_freq_center[:, ix_nya & ix_2019, ix_noise_lev_0, :]).mean(avg).transpose('reduction_level', 'channel', 'noise_level')
    red_ess_abs_mean = np.abs(delta_tb.mean_freq_center[:, ix_ess & ix_2019, ix_noise_lev_0, :]).mean(avg).transpose('reduction_level', 'channel', 'noise_level')
    red_snp_abs_mean = np.abs(delta_tb.mean_freq_center[:, ix_snp & ix_2019, ix_noise_lev_0, :]).mean(avg).transpose('reduction_level', 'channel', 'noise_level')
    
    red_nya_std = delta_tb.std_freq_center[:, ix_nya & ix_2019, ix_noise_lev_0, :].mean(avg).transpose('reduction_level', 'channel', 'noise_level')
    red_ess_std = delta_tb.std_freq_center[:, ix_ess & ix_2019, ix_noise_lev_0, :].mean(avg).transpose('reduction_level', 'channel', 'noise_level')
    red_snp_std = delta_tb.std_freq_center[:, ix_snp & ix_2019, ix_noise_lev_0, :].mean(avg).transpose('reduction_level', 'channel', 'noise_level')
    
    # indexing: .sel(channel='15') with channel being one dimension
    
    #%% PROOF influence of noise (data_reduction == 1)
    # x-axis: standard deviation of noise
    # y-axis: standard deviation of delta_tb
    # subplots: one channel per row, in each subplots three lines for three stations
    
    fig, axes = plt.subplots(5, 1, figsize=(6, 6), sharex=True, sharey=True)
    fig.suptitle('Perturbation of SRF')
    
    kwargs = {'linewidth': 1, 'marker': 'x'}

    for i, channel in enumerate(mwi.channels_str):
        
        li = axes[i].plot(delta_tb.noise_level, noise_nya_std.sel(channel=channel), color=colors[0], label=names[0], **kwargs)  # Ny Alesund
        li = axes[i].plot(delta_tb.noise_level, noise_ess_std.sel(channel=channel), color=colors[1], label=names[1], **kwargs)  # Essen
        li = axes[i].plot(delta_tb.noise_level, noise_snp_std.sel(channel=channel), color=colors[2], label=names[2], **kwargs)  # Singapore
 
    # set labels
    axes[-1].set_xlabel('Standard deviation of perturbation')
    axes[2].set_ylabel('Standard deviation of $\Delta TB$')
    
    # axis limits
    #axes[0].set_xlim([np.min(delta_tb.noise_level), np.max(delta_tb.noise_level)])
    #axes[0].set_ylim([0, 0.025])
    
    plt.subplots_adjust(right=0.8)
    
    for i, ax in enumerate(axes):
        ax.set_yticks(np.arange(0, 0.03, 0.01))
        ax.grid(True)
        ax.set_axisbelow(True)
        
        # annotate channel name
        ax.annotate(text=mwi.freq_txt[i], xy=(1.01, 0.5), xycoords='axes fraction', ha='left', va='center')
        
    # annotate station names in legend below
    leg = axes[-1].legend(bbox_to_anchor=(1.05, -0.1), loc='upper left', frameon=True, ncol=1, fontsize=6)
    
    plt.savefig(path_plot + 'noise_dependency/noise_rs_2019.png', dpi=200)
    
    #%% PROOF influence of data reduction (noise == 0)
    # x-axis: reduction_level 
    # y-axis: standard deviation of delta_tb
    # subplots: one channel per row, in each subplots three lines for three stations
    
    fig, axes = plt.subplots(5, 1, figsize=(6, 6), sharex=True, sharey=True)
    fig.suptitle('Data reduction of SRF')
    
    # number of measurements
    n_orig = 1060
    number_meas = np.floor(n_orig/delta_tb.reduction_level)
    sample_width =  191.302 - 175.322
    x = sample_width/number_meas*1000
    
    names = ['Ny Alesund', 'Essen', 'Singapore']
    colors = ['#002375', '#008B00', '#AE0000']
    kwargs = {'linewidth': 1, 'marker': 'x'}
    
    for i, channel in enumerate(mwi.channels_str):
        
        li = axes[i].plot(x, red_nya_abs_mean.sel(channel=channel)-red_nya_abs_mean.sel(channel=channel, reduction_level=1), color=colors[0], label=names[0], **kwargs)  # Ny Alesund
        li = axes[i].plot(x, red_ess_abs_mean.sel(channel=channel)-red_ess_abs_mean.sel(channel=channel, reduction_level=1), color=colors[1], label=names[1], **kwargs)  # Essen
        li = axes[i].plot(x, red_snp_abs_mean.sel(channel=channel)-red_snp_abs_mean.sel(channel=channel, reduction_level=1), color=colors[2], label=names[2], **kwargs)  # Singapore
    
    # set labels
    axes[-1].set_xlabel('Sampling interval [MHz]')
    axes[2].set_ylabel('$\Delta TB_s - \Delta TB_{s=15 MHz}$')
    
    # axis limits
    axes[-1].set_xticks(range(15, 80, 15))
    axes[0].set_ylim([-0.011, 0.011])
    
    plt.subplots_adjust(right=0.8)
    
    for i, ax in enumerate(axes):
        ax.grid(True)
        ax.set_axisbelow(True)
                
        # annotate channel name
        ax.annotate(text=mwi.freq_txt[i], xy=(1.01, 0.5), xycoords='axes fraction', ha='left', va='center')
        
    # annotate station names in legend below
    leg = axes[-1].legend(bbox_to_anchor=(1.05, -0.1), loc='upper left', frameon=True, ncol=1, fontsize=6)

    plt.savefig(path_plot + 'data_reduction_dependency/data_reduction_rs_2019.png', dpi=200)

    #%% UNUSED conjunct effect of noise and less data
    # x: noise_level
    # y: reduction_level
    # values: mean of all realizations or actual value and standard deviation
    
    # seems not to be helpful and also hard to explain in a short period of time
    
    
    
    #%% HELPER
    # create twin axis and add labels on top most plot
    ax_top = axes[0].secondary_xaxis('top')
    ax_top.set_xticks(x)
    
    ax_top.set_xticklabels([str(int(i)) for i in x], fontsize=8)
    
    for tick in ax_top.xaxis.get_major_ticks():
        tick.label.set_fontsize(5)
    
    #%% DEPRECATED influence of noise (data_reduction == 1)
    # x-axis: Channels
    # y-axis: standard deviation of noise
    # size: mean
    # color: standard deviation
    # comment: the stations NYA, SNP and ESS are shifted in position around center line of channel
    
    fig, axes = plt.subplots(3, 1, figsize=(8, 5), sharex=True, sharey=True)
    fig.suptitle('Influence of perturbed spectral responce function\nsize: mean absolute error of $\Delta TB$, color: sensitivity of $\Delta TB$ to perturbation')
    
    x, y = np.meshgrid(mwi.channels_int, delta_tb.noise_level)
    names = ['Ny Alesund\n(2019)', 'Essen\n(2019)', 'Singapore\n(2019)']
    
    kwargs = {'vmin': 0, 'vmax': 0.02, 'cmap': 'jet', 'linewidths': 0, 'edgecolors': 'None', 'marker': 's'}
    # Ny Alesund
    sc = axes[0].scatter(x=x, y=y, s=np.abs(noise_nya_abs_mean)*100, c=noise_nya_std, **kwargs)  # Ny Alesund
    sc = axes[1].scatter(x=x, y=y, s=np.abs(noise_ess_abs_mean)*100, c=noise_ess_std, **kwargs)  # Essen
    sc = axes[2].scatter(x=x, y=y, s=np.abs(noise_snp_abs_mean)*100, c=noise_snp_std, **kwargs)  # Singapore
        
    plt.subplots_adjust(right=0.87)
    
    # set labels
    axes[1].set_ylabel('Standard deviation of perturbation')
    
    # axis limits
    axes[1].set_ylim([-0.01, 0.11])
    axes[2].set_xlim([13.5, 18.5])
    
    for i, ax in enumerate(axes):
        ax.set_xticks(np.arange(14, 19), minor=True)
        ax.set_xticks(np.arange(13.5, 19.5), minor=False)
        ax.set_xticklabels(mwi.freq_txt, minor=True)
        ax.set_xticklabels('', minor=False)
        ax.xaxis.grid(True, which='major')
        ax.yaxis.grid(True)
        ax.tick_params('x', length=0, width=0, which='minor')
        
        ax.set_axisbelow(True)
        
        # annotate station name
        ax.annotate(text=names[i], xy=(1.01, 0.5), xycoords='axes fraction', ha='left', va='center')
