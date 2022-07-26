"""
Plot brightness temperature spectrum of radiosonde profiles
    - annual mean and standard deviation

PROOF
"""


import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
import datetime
import os
import sys
sys.path.append(f'{os.environ["PATH_PHD"]}/projects/mwi_bandpass_effects/scripts')
from mwi_info import mwi
from radiosonde import wyo
from path_setter import path_data, path_plot
from importer import IWV

plt.ion()


if __name__ == '__main__':
    
    # read brightness temperatures
    # read pamtra simulations
    #Pam = PAMTRA_TB()
    #Pam.read_all()
    #Pam.pam_data_df
    #Pam.pam_data_df.to_csv(path_data+'brightness_temperature/TB_all.txt')
    # aboves read takes about 2 min
    #Pam.pam_data_df = pd.read_csv(path_data+'brightness_temperature/TB_all_nadir.txt', sep=',', index_col=0)
    data = xr.load_dataset(path_data+'brightness_temperature/TB_radiosondes_2019.nc')
    pam_data_xr = data.isel(angle=9)
    pam_data_xr = pam_data_xr.transpose('profile', 'frequency')
    #Pam.pam_data_df
    
    # to xarray
    #profiles = Pam.pam_data_df.columns.values
    #profiles = np.delete(profiles, profiles=='frequency [GHz]')
    #profiles[profiles == 'standard_atmosphere'] = 'ID_00000_190001010000'
    #kwargs = {'dims': ('profile', 'frequency'), 
    #                   'coords': { 'profile': profiles, 'frequency': Pam.pam_data_df['frequency [GHz]'].values},
    #                   'attrs': {'unit': 'K', 'name': 'brightness temperature as function of frequency in GHz', 'source': 'WYO and PAMTRA'}
    #                 }
    #pam_data_xr = xr.DataArray(data=Pam.pam_data_df.iloc[:, 1:].values.T, **kwargs)
    
    #%% Read IWV
    iwv = IWV()
    iwv.read_data()
    
    #%% combine iwv with tb
    pam_data_xr['iwv'] = iwv.data.sel(profile=pam_data_xr.profile)
    
    #%% get indices
    station_id = np.array([x[3:8] for x in pam_data_xr.profile.values])
    date = np.array([datetime.datetime.strptime(x[-12:], '%Y%m%d%H%M') for x in pam_data_xr.profile.values])
    year = np.array([x.year for x in date])
    
    # index for 2019 data
    ix_2019 = year == 2019
    
    # station index
    ix_nya = station_id == wyo.station_id['Ny Alesund']
    ix_snp = station_id == wyo.station_id['Singapore']
    ix_ess = station_id == wyo.station_id['Essen']
    ix_bar = station_id == wyo.station_id['Barbados']
    ix_std = station_id == '00000'
    
    #%% calculate 2019 mean profilesplot_brightness_temperature_era5_grid_step_function.py
    mean_dict = dict()
    std_dict = dict()
    
    mean_dict['Ny Alesund'] = pam_data_xr.tb.sel(profile=ix_nya & ix_2019).mean('profile')
    mean_dict['Singapore'] = pam_data_xr.tb.sel(profile=ix_snp & ix_2019).mean('profile')
    mean_dict['Essen'] = pam_data_xr.tb.sel(profile=ix_ess & ix_2019).mean('profile')
    mean_dict['Barbados'] = pam_data_xr.tb.sel(profile=ix_bar & ix_2019).mean('profile')
    
    std_dict['Ny Alesund'] = pam_data_xr.tb.sel(profile=ix_nya & ix_2019).std('profile')
    std_dict['Singapore'] = pam_data_xr.tb.sel(profile=ix_snp & ix_2019).std('profile')
    std_dict['Essen'] = pam_data_xr.tb.sel(profile=ix_ess & ix_2019).std('profile')
    std_dict['Barbados'] = pam_data_xr.tb.sel(profile=ix_bar & ix_2019).std('profile')
    
    #%% colors for plot
    colors = {'01004': 'b',
              '10410': 'g',
              '48698': 'r',
              '78954': 'orange',
              }
    
    # also put standard atmosphere to station ID's
    id_station = wyo.id_station
    station_id = wyo.station_id
    
    #%%  PROOF
    fig = plt.figure(figsize=(4, 5))
    ax = fig.add_subplot(111)
    fig.suptitle('Annual mean$\pm$sd of simulated TB\nfor radiosondes')
    
    for station_name in list(mean_dict.keys()):
        
        c = colors[wyo.station_id[station_name]]
        mean = mean_dict[station_name]
        sd = std_dict[station_name]
        
        ax.plot(mean.frequency, mean, color=c, linewidth=1.5, label=station_name, zorder=3)
        ax.fill_between(x=mean.frequency, y1=mean-sd, y2=mean+sd, color=c, alpha=0.1, zorder=1)
    
    # add MWI channels
    ax.annotate(text='[channel]', xy=(1.1, 1), xycoords='axes fraction', fontsize=7, ha='center', va='bottom')
    for i, channel in enumerate(mwi.channels_str):
        
        # annotate channel name
        ax.annotate(text=mwi.freq_txt[i][4:6], xy=[mwi.freq_center[i, 0], 285], fontsize=7, ha='center', va='bottom')
        ax.annotate(text=mwi.freq_txt[i][4:6], xy=[mwi.freq_center[i, 1], 285], fontsize=7, ha='center', va='bottom')
        
        # add vertical lines
        ax.axvline(x=mwi.freq_center[i, 0], color='gray', linestyle=':', alpha=0.5, linewidth=1)  # mark left channel frequency
        ax.axvline(x=mwi.freq_center[i, 1], color='gray', linestyle=':', alpha=0.5, linewidth=1)  # mark right channel frequency
    ax.axvline(x=mwi.absorpt_line, color='k', linestyle=':', alpha=0.5, linewidth=1)  # mark line center
    
    ax.legend(bbox_to_anchor=(0.5, -0.25), ncol=3, loc='upper center', frameon=True, fontsize=8)
    ax.grid(axis='y')
    ax.set_ylim([220, 285])
    ax.set_xlim([np.min(mean.frequency), np.max(mean.frequency)])
    ax.set_xlabel('Frequency [GHz]')
    ax.set_ylabel('Brightness temperature [K]')
    
    #plt.subplots_adjust(right=0.95, bottom=0.2, top=0.9)
    fig.tight_layout()
    
    plt.savefig(path_plot + 'brightness_temperature/mean_2019_spectra.png', dpi=300)

    #%% spectra as function of IWV to see why we have this strong dependence
    # of delta tb at low IWV
    # clearly the effect at low IWV can be seen, variability at center of
    # absorption line can not be explained by IWV
    # in principle, a correction can only be applied if spectral variation
    # of TB is known - IWV good proxi at outer bands and low IWV, at inner
    # bands, IWV is not enough - temperature profile etc needed as pamtra
    # uses - train ML algorithm to make spectral emissivity variation
    # from a-priori profiles of atmosphere - no perfect solution available,
    # especially for clouds it becomes impossible in my opinion
    bins = np.arange(0, 60, 1)
    labels = (bins[1:]+bins[:-1])/2
    ds_tb_iwv = pam_data_xr.groupby_bins(group='iwv', labels=labels,
                                         bins=bins).mean('profile')
    
    fig, ax = plt.subplots(1, 1, figsize=(6, 4), constrained_layout=True)
    
    ds_tb_iwv_flat = ds_tb_iwv.tb.stack(flat=('iwv_bins', 'frequency'))
    ax.scatter(ds_tb_iwv_flat.frequency, 
               ds_tb_iwv_flat, 
               c=ds_tb_iwv_flat.iwv_bins, 
               cmap='magma',
               alpha=0.5)
    
    #%% with broken axis: nice example, but no standard atmosphere anymore
    assert True == False
    # make y-axis have same ratios
    ylim1 = [215, 288]
    ylim2 = [175, 185]
    ylimratio = (ylim1[1]-ylim1[0])/(ylim2[1]-ylim2[0]+ylim1[1]-ylim1[0])
    ylim2ratio = (ylim2[1]-ylim2[0])/(ylim2[1]-ylim2[0]+ylim1[1]-ylim1[0])
    
    fig, [ax1, ax2] = plt.subplots(2, 1, figsize=(4, 5), gridspec_kw={'height_ratios': [ylimratio, ylim2ratio], 'hspace': 0.05}, sharex=True)
    fig.suptitle('Annual mean$\pm$sd of simulated TB in 2019\nfor radiosondes and standard atmosphere')
    
    for ax in [ax1, ax2]:
        for station_name in list(mean_dict.keys()):
            
            c = colors[wyo.station_id[station_name]]
            mean = mean_dict[station_name]
            sd = std_dict[station_name]
            
            ax.plot(mean.frequency, mean, color=c, linewidth=1.5, label=station_name, zorder=3)
            ax.fill_between(x=mean.frequency, y1=mean-sd, y2=mean+sd, color=c, alpha=0.1, zorder=1)
    
    # add MWI channels
    ax1.annotate(text='[channel]', xy=(1.1, 1), xycoords='axes fraction', fontsize=7, ha='center', va='bottom')
    for i, channel in enumerate(mwi.channels_str):
        
        # annotate channel name
        ax1.annotate(text=mwi.freq_txt[i][4:6], xy=[mwi.freq_center[i, 0], 288], fontsize=7, ha='center', va='bottom')
        ax1.annotate(text=mwi.freq_txt[i][4:6], xy=[mwi.freq_center[i, 1], 288], fontsize=7, ha='center', va='bottom')
        
        for ax in [ax1, ax2]:
            # add vertical lines
            ax.axvline(x=mwi.freq_center[i, 0], color='gray', linestyle=':', alpha=0.5, linewidth=1)  # mark left channel frequency
            ax.axvline(x=mwi.freq_center[i, 1], color='gray', linestyle=':', alpha=0.5, linewidth=1)  # mark right channel frequency
    
    for ax in [ax1, ax2]:
        ax.axvline(x=mwi.absorpt_line, color='k', linestyle=':', alpha=0.5, linewidth=1)  # mark line center
        
    # hide the spines between ax and ax2
    ax1.spines['bottom'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    ax1.tick_params(axis=u'x', which=u'both',length=0)  # remove ticks of ax1
    
    ax2.legend(bbox_to_anchor=(0.5, -1.6), ncol=3, loc='upper center', frameon=True, fontsize=8)
    ax1.grid(axis='y')
    ax2.grid(axis='y')
    ax1.set_ylim(ylim1)
    ax2.set_ylim(ylim2)
    ax2.set_yticks([180])
    #ax2.tick_params(axis="y", colors="#888888")
    ax2.set_xlim([np.min(mean.frequency), np.max(mean.frequency)])
    ax2.set_xlabel('Frequency [GHz]')
    ax1.set_ylabel('Brightness temperature [K]')
    
    # add diagonal lines
    xd = .015  # how big to make the diagonal lines in axes coordinates
    yd = .015
    # arguments to pass to plot, just so we don't keep repeating them
    kwargs = dict(transform=ax1.transAxes, color='k', clip_on=False)
    ax1.plot((-xd, +xd), (-yd, +yd), **kwargs)        # top-left diagonal
    ax1.plot((1 - xd, 1 + xd), (-yd, +yd), **kwargs)  # top-right diagonal
    
    yd = yd * ylimratio/ylim2ratio
    kwargs.update(transform=ax2.transAxes)  # switch to the bottom axes
    ax2.plot((-xd, +xd), (1 - yd, 1 + yd), **kwargs)  # bottom-left diagonal
    ax2.plot((1 - xd, 1 + xd), (1 - yd, 1 + yd), **kwargs)  # bottom-right diagonal
    
    plt.subplots_adjust(right=0.85, bottom=0.25, left=0.15, top=0.825)
    
    plt.savefig(path_plot + 'brightness_temperature/mean_2019_spectra_broken_axes.png', dpi=300)
    