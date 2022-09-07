"""
Plot brightness temperature spectrum of radiosonde profiles and ERA-5.
"""


import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
import cartopy.crs as ccrs
from string import ascii_lowercase as abc
import os
from helpers import mwi, colors, wyo
from dotenv import load_dotenv

load_dotenv()
plt.ion()


if __name__ == '__main__':
    
    # read brightness temperatures
    ds_com_rsd = xr.open_dataset(
        os.path.join(os.environ['PATH_BRT'],
                     'TB_radiosondes_2019_MWI.nc'))

    ds_com_era = xr.open_dataset(
        os.path.join(os.environ['PATH_BRT'],
                     'TB_era5_MWI.nc'))
    ds_com_erh = xr.open_dataset(
        os.path.join(os.environ['PATH_BRT'],
                     'TB_era5_hyd_MWI.nc'))
    
    # rearrange radiosonde tb data
    ds_com_rsd['tb'] = ds_com_rsd.tb.transpose('frequency', 'profile', 'angle')
    
    # stack spatial coordinates from era-5
    ds_com_era_stack = ds_com_era.stack({'profile': ('grid_x', 'grid_y')})
    ds_com_erh_stack = ds_com_erh.stack({'profile': ('grid_x', 'grid_y')})
    
    #%% calculate mean and std of profiles
    # radiosondes
    ds_com_rsd_mean = ds_com_rsd.tb.groupby(
        ds_com_rsd.station).mean('profile').isel(angle=9)
    ds_com_rsd_std = ds_com_rsd.tb.groupby(
        ds_com_rsd.station).std('profile').isel(angle=9)
    
    # era5 scene
    # clear-sky
    ds_com_era_mean = ds_com_era.tb.mean(
        ('grid_x', 'grid_y')).isel(angle=9)
    ds_com_era_std = ds_com_era.tb.std(
        ('grid_x', 'grid_y')).isel(angle=9)
    
    # cloudy
    ds_com_erh_mean = ds_com_erh.tb.mean(
        ('grid_x', 'grid_y')).isel(angle=9)
    ds_com_erh_std = ds_com_erh.tb.std(
        ('grid_x', 'grid_y')).isel(angle=9)
    
    #%% plot all spectra and the mean spectrum in separate subplots
    fig, axes = plt.subplots(2, 3, figsize=(7, 5), constrained_layout=True,
                             sharex=True, sharey=True)
    
    for i, ax in enumerate(axes.flatten()):
        ax.annotate(f'({abc[i]})', xy=(0.02, 1.03), xycoords='axes fraction',
                    ha='left', va='bottom')
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
    
    axes[0, 2].set_title('ERA5 (clear-sky)')
    axes[1, 2].set_title('ERA5 (all-sky)')
    
    # radiosondes
    for i, station in enumerate(np.unique(ds_com_rsd.station.values)):
        
        ax = axes.flatten('F')[i]
        
        ax.set_title(station)
        
        # individual profiles
        ax.plot(ds_com_rsd.frequency*1e-3,
                ds_com_rsd.tb.sel(profile=ds_com_rsd.station == station).isel(
                    angle=9), color=colors.colors_rs[station], lw=0.1)
        
        # mean profile
        ax.plot(ds_com_rsd_mean.frequency*1e-3, 
                ds_com_rsd_mean.sel(station=station), 
                color='k', linewidth=1.5, label=station)
        
    # era5    
    # individual profiles
    axes[0, 2].plot(
        ds_com_era_stack.frequency*1e-3, 
        ds_com_era_stack.tb.isel(angle=9), 
        color='gray', lw=0.1)
    
    axes[1, 2].plot(
        ds_com_erh_stack.frequency*1e-3, 
        ds_com_erh_stack.tb.isel(angle=9), 
        color='gray', lw=0.1)
    
    # mean profile
    axes[0, 2].plot(
        ds_com_era_mean.frequency*1e-3,
        ds_com_era_mean, 
        color='k', linewidth=1.5)
    
    axes[1, 2].plot(
        ds_com_erh_mean.frequency*1e-3, 
        ds_com_erh_mean, 
        color='k', linewidth=1.5)
        
    # add MWI channels
    for ax in fig.axes:
        for i, channel in enumerate(mwi.channels_str):
            
            # annotate channel name
            ax.annotate(channel, 
                        xy=(mwi.freq_center[i, 0], 0),
                        xycoords=('data', 'axes fraction'),
                        ha='center', va='bottom', fontsize=6)
            
            ax.annotate(channel,
                        xy=(mwi.freq_center[i, 1], 0),
                        xycoords=('data', 'axes fraction'),
                        ha='center', va='bottom', fontsize=6)
            
            # add vertical lines
            ax.plot([mwi.freq_center[i, 0], mwi.freq_center[i, 0]],
                    [210, 300],
                    color='k', linestyle=':',
                       linewidth=1)  # mark left channel frequency
            ax.plot([mwi.freq_center[i, 1], mwi.freq_center[i, 1]],
                    [210, 300],
                    color='k', linestyle=':',
                    linewidth=1)  # mark right channel frequency
    
    axes[1, 0].set_ylim([205, 290])
    axes[1, 0].set_xlim(np.min(ds_com_rsd.frequency)*1e-3, 
                np.max(ds_com_rsd.frequency)*1e-3)
    axes[1, 0].set_xlabel('Frequency [GHz]')
    axes[1, 0].set_ylabel('TB [K]')
    
    plt.savefig(os.path.join(
        os.environ['PATH_PLT'], 
        'tb_spectra.png'), 
        dpi=300, bbox_inches='tight')
    
    plt.close('all')

    #%% plot mean and std of TB from radiosondes
    fig, ax = plt.subplots(1, 1, figsize=(6, 5), constrained_layout=True)
    
    # radiosondes
    for station in ds_com_rsd_mean.station.values:
        
        ax.plot(ds_com_rsd.frequency*1e-3, 
                ds_com_rsd_mean.sel(station=station), 
                color=colors.colors_rs[station], 
                linewidth=1.5, label=station, zorder=3)
        ax.fill_between(x=ds_com_rsd.frequency*1e-3, 
                        y1=ds_com_rsd_mean.sel(station=station) -
                           ds_com_rsd_std.sel(station=station), 
                        y2=ds_com_rsd_mean.sel(station=station) +
                           ds_com_rsd_std.sel(station=station), 
                        color=colors.colors_rs[station], alpha=0.3, zorder=1, 
                        lw=0)
    
    # add MWI channels
    for i, channel in enumerate(mwi.channels_str):
        
        # annotate channel name
        ax.annotate(text=mwi.freq_txt[i][4:6], xy=[mwi.freq_center[i, 0], 285], 
                    ha='center', va='bottom')
        ax.annotate(text=mwi.freq_txt[i][4:6], xy=[mwi.freq_center[i, 1], 285], 
                    ha='center', va='bottom')
        
        # add vertical lines
        ax.axvline(x=mwi.freq_center[i, 0], color='gray', linestyle=':', 
                   alpha=0.5, linewidth=1)  # mark left channel frequency
        ax.axvline(x=mwi.freq_center[i, 1], color='gray', linestyle=':',
                   alpha=0.5, linewidth=1)  # mark right channel frequency
    ax.axvline(x=mwi.absorpt_line, color='k', linestyle=':', 
               alpha=0.5, linewidth=1)  # mark line center
    
    ax.legend(bbox_to_anchor=(0.5, -0.12), ncol=4, loc='upper center',
              frameon=True, fontsize=8)
    ax.set_ylim([220, 285])
    ax.set_xlim(np.min(ds_com_rsd.frequency)*1e-3, 
                np.max(ds_com_rsd.frequency)*1e-3)
    ax.set_xlabel('Frequency [GHz]')
    ax.set_ylabel('TB [K]')
        
    plt.savefig(os.path.join(
        os.environ['PATH_PLT'], 
        'tb_spectra_radiosondes.png'), 
                dpi=300, bbox_inches='tight')
    
    #%% plot tb from ERA-5 field as would be observed by MWI
    fig, axes = plt.subplots(3, 5, figsize=(6, 4), sharex=True, sharey=True,
                             subplot_kw=dict(projection=ccrs.PlateCarree()),
                             constrained_layout=True)
    
    for i, ax in enumerate(axes.flatten()):
        ax.annotate(f'({abc[i]})', xy=(0.02, 0.98), xycoords='axes fraction',
                    ha='left', va='top', color='white')
    
    # annotate channel name
    for i, ax in enumerate(axes[0, :]):
        ax.annotate(text='MWI-'+mwi.channels_str[i], xy=(0.5, 1.1), 
                    xycoords='axes fraction', ha='center', va='bottom')
    
    for i, channel in enumerate(ds_com_era.channel):
        if i == 4:
            label1 = '$TB_{obs,clear-sky}$ [K]'
            label2 = '$TB_{obs,cloudy}$ [K]'
            label3 = '$\Delta TB_{obs}$ [K]'
        else:
            label1, label2, label3 = ['', '', '']
        
        im0 = axes[0, i].pcolormesh(ds_com_era.lon, 
                              ds_com_era.lat,
                              ds_com_era.tb_mwi_orig.sel(channel=channel),
                              cmap='YlGnBu_r', transform=ccrs.PlateCarree())
        cb = fig.colorbar(im0, ax=axes[0, i], label=label1)
        
        im1 = axes[1, i].pcolormesh(ds_com_erh.lon, 
                              ds_com_erh.lat,
                              ds_com_erh.tb_mwi_orig.sel(channel=channel),
                              cmap='YlGnBu_r', transform=ccrs.PlateCarree(),
                              )
        cb = fig.colorbar(im1, ax=axes[1, i], label=label2)
        
        im2 = axes[2, i].pcolormesh(ds_com_era.lon, 
                              ds_com_era.lat,
                              ds_com_erh.tb_mwi_orig.sel(channel=channel) -
                              ds_com_era.tb_mwi_orig.sel(channel=channel),
                              cmap='magma_r', transform=ccrs.PlateCarree(),
                              vmax=0
                              )
        cb = fig.colorbar(im2, ax=axes[2, i], label=label3)
    
    plt.savefig(os.path.join(
        os.environ['PATH_PLT'], 
        'tb_mwi_era5.png'), 
        dpi=300, bbox_inches='tight')
    
    plt.close('all')
    
    #%% calculation of gradients
    # reduce to frequencies, where srf was measured
    freq_srf_orig = ~np.isnan(ds_com_rsd.srf_orig.sel(channel=14))
    
    ds_com_rsd_tbl = ds_com_rsd.tb.sel(
        frequency=(ds_com_rsd.frequency*1e-3 > mwi.absorpt_line) & freq_srf_orig)
    ds_com_rsd_tbr = ds_com_rsd.tb.sel(
        frequency=(ds_com_rsd.frequency*1e-3 < mwi.absorpt_line) & freq_srf_orig)
    
    #%% tb gradients of radiosonde profiles
    # dtb/df for steps of 15 MHz (0.015 GHz), 
    left = dict(
        frequency=(ds_com_rsd.frequency*1e-3 < mwi.absorpt_line) & 
        freq_srf_orig)
    
    right = dict(
        frequency=(ds_com_rsd.frequency*1e-3 > mwi.absorpt_line) & 
        freq_srf_orig)

    ds_com_rsd_dtb_left = ds_com_rsd.tb.isel(angle=9).sel(left).diff(
        'frequency', n=1, label='lower')
            
    ds_com_rsd_dtb_right = ds_com_rsd.tb.isel(angle=9).sel(right).diff(
        'frequency', n=1, label='upper')
    
    fig, ax = plt.subplots(1, 1)

    ax.plot(ds_com_rsd_dtb_left.frequency*1e-3,
            ds_com_rsd_dtb_left/0.015, color='gray')
    
    ax.plot(ds_com_rsd_dtb_left.frequency*1e-3,
            ds_com_rsd_dtb_left.mean('profile')/0.015, color='k')
    
    ax.plot(ds_com_rsd_dtb_right.frequency*1e-3,
            ds_com_rsd_dtb_right/0.015, color='gray')
    
    ax.plot(ds_com_rsd_dtb_right.frequency*1e-3,
            ds_com_rsd_dtb_right.mean('profile')/0.015, color='k')
    
    ax.set_ylim(-15, 15)
    
    ax.axhline(y=0)
    
    # add channel frequencies
    for x in mwi.freq_center.flatten():
        ax.axvline(x)
        
    #%% tb imbalance lower and upper bandpass    
    ds_com_rsd_tbl['frequency'] = ds_com_rsd_tbr.frequency[::-1]
        
    ds_com_rsd_tb_imb = ds_com_rsd_tbl - ds_com_rsd_tbr
    
    fig, ax = plt.subplots(1, 1)
    
    ds_com_rsd_tb_imb_stack = ds_com_rsd_tb_imb.isel(angle=9).stack(
        {'z': ('frequency', 'profile')})
    c_list = [colors.colors_rs[wyo.id_station[s.split('_')[1]]] 
              for s in ds_com_rsd_tb_imb_stack.profile.values]
    ax.scatter(
        ds_com_rsd_tb_imb_stack.frequency*1e-3,
        ds_com_rsd_tb_imb_stack, 
        color=c_list)
    
    ax.plot(ds_com_rsd_tb_imb.frequency*1e-3,
            ds_com_rsd_tb_imb.mean('profile').isel(angle=9), color='k')
    
    for x in mwi.freq_center.flatten():
        ax.axvline(x)
    