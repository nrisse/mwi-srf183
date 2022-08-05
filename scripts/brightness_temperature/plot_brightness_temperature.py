"""
Plot brightness temperature spectrum of radiosonde profiles
    - annual mean and standard deviation

PROOF
"""


import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
import cartopy.crs as ccrs
from string import ascii_lowercase as abc
import os
import sys
sys.path.append(f'{os.environ["PATH_PHD"]}/projects/mwi_bandpass_effects/scripts')
from mwi_info import mwi
from path_setter import path_data, path_plot

plt.ion()


if __name__ == '__main__':
    
    # read brightness temperatures
    ds_com_rsd = xr.open_dataset(
        path_data+'brightness_temperature/TB_radiosondes_2019_MWI.nc')
    ds_com_era = xr.open_dataset(
        path_data+'brightness_temperature/TB_era5_MWI.nc')
    ds_com_erh = xr.open_dataset(
        path_data+'brightness_temperature/TB_era5_hyd_MWI.nc')
    
    #%% test here
    ds = xr.open_dataset('/home/nrisse/phd/projects/mwi_bandpass_effects/data/delta_tb_old/delta_tb_era5grid.nc')
    
    np.max(np.abs(ds.delta_tb_freq_center.transpose('channel', 'lon', 'lat').values - ds_com_erh.dtb_mwi_est.sel(est_type='freq_center').values))
    
    #%% calculate 2019 mean profiles
    ds_com_rsd_mean = ds_com_rsd.tb.groupby(
        ds_com_rsd.station).mean('profile').isel(angle=9)
    ds_com_rsd_std = ds_com_rsd.tb.groupby(
        ds_com_rsd.station).std('profile').isel(angle=9)
    
    #%% colors for plot
    colors = {'Ny-Alesund': 'b',
              'Essen': 'g',
              'Singapore': 'r',
              'Barbados': 'orange',
              }
    
    #%% PROOF plot mean and std of TB from radiosondes
    fig, ax = plt.subplots(1, 1, figsize=(6, 5), constrained_layout=True)
    
    for station in ds_com_rsd_mean.station.values:
        
        ax.plot(ds_com_rsd.frequency*1e-3, 
                ds_com_rsd_mean.sel(station=station), color=colors[station], 
                linewidth=1.5, label=station, zorder=3)
        ax.fill_between(x=ds_com_rsd.frequency*1e-3, 
                        y1=ds_com_rsd_mean.sel(station=station) -
                           ds_com_rsd_std.sel(station=station), 
                        y2=ds_com_rsd_mean.sel(station=station) +
                           ds_com_rsd_std.sel(station=station), 
                        color=colors[station], alpha=0.1, zorder=1, lw=0)
    
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
        
    plt.savefig(path_plot + 'brightness_temperature/radiosondes_tb_spectra.png', 
                dpi=300)
    
    #%% plot tb spectra from era-5 scene
    fig, ax = plt.subplots(1, 1, figsize=(6, 5), constrained_layout=True)
    
    # stack the spatial coordinates
    ds_com_era_stack = ds_com_era.stack({'grid': ['grid_x', 'grid_y']})
    ds_com_erh_stack = ds_com_erh.stack({'grid': ['grid_x', 'grid_y']})
    
    for grid in ds_com_era_stack.grid.values:
        
        ax.plot(ds_com_era_stack.frequency*1e-3, 
                ds_com_era_stack.tb.sel(grid=grid).isel(angle=9), color='coral', 
                linewidth=0.25, alpha=0.5)
        
        ax.plot(ds_com_erh_stack.frequency*1e-3, 
                ds_com_erh_stack.tb.sel(grid=grid).isel(angle=9), color='skyblue', 
                linewidth=0.25, alpha=0.5)
    
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
    
    ax.set_ylim([210, 275])
    ax.set_xlim(np.min(ds_com_rsd.frequency)*1e-3, 
                np.max(ds_com_rsd.frequency)*1e-3)
    ax.set_xlabel('Frequency [GHz]')
    ax.set_ylabel('TB [K]')
        
    plt.savefig(path_plot + 'brightness_temperature/era5_tb_spectra.png', 
                dpi=300)
    
    plt.close('all')
    
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
    ds_tb_iwv = ds_com_rsd.groupby_bins(group='iwv', labels=labels,
                                        bins=bins).mean('profile')
    
    fig, ax = plt.subplots(1, 1, figsize=(6, 4), constrained_layout=True)
    
    ds_tb_iwv_flat = ds_tb_iwv.tb.stack(flat=('iwv_bins', 'frequency'))
    ax.scatter(ds_tb_iwv_flat.frequency*1e-3, 
               ds_tb_iwv_flat.isel(angle=9), 
               c=ds_tb_iwv_flat.iwv_bins, 
               cmap='magma',
               alpha=0.5)
    
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
    
    plt.savefig(path_plot + 'brightness_temperature/era5_tb_mwi.png', 
                dpi=300, bbox_inches='tight')
    
    plt.close('all')
