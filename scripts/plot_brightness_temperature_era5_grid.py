

import matplotlib.pyplot as plt
import xarray as xr
import cartopy.crs as ccrs
import datetime
import matplotlib.ticker as mticker
import numpy as np
import os
import sys
sys.path.append(f'{os.environ["PATH_PHD"]}/projects/mwi_bandpass_effects/scripts')
from path_setter import *
from importer import Sensitivity
from importer import PAMTRA_TB
from mwi_info import mwi
from importer import Delta_TB, IWV
from radiosonde import wyo


if __name__ == '__main__':
    
    # UPDATE PLOT FOR NEW ANGLE
    
    file = path_data+'delta_tb/delta_tb_era5grid.nc'
    data = xr.load_dataset(file)
    
    file = path_data+'delta_tb/delta_tb_era5grid_clearsky.nc'
    data_clearsky = xr.load_dataset(file)
    
    file_iwv = path_data+'iwv/IWV_PAMTRA_ERA5.nc'
    data_iwv = xr.load_dataset(file_iwv)

    file_hyd = path_data+'integrated_hydrometeors/HYDRO_PAMTRA_ERA5.nc'
    data_hyd = xr.load_dataset(file_hyd)
    data_hyd = data_hyd.rename_dims({'class': 'h_class'})
    data_hyd = data_hyd.assign_coords({'h_class': data_hyd['h_class']})
    
    file_tb = path_data+'brightness_temperature/era5/2015/03/31/TB_PAMTRA_ERA5.nc'
    data_tb = xr.load_dataset(file_tb)
    
    #%% read ERA5 data
    #file = path_data+'era5/era5-single-levels_20150331_1200.nc'
    #era5 = xr.open_dataset(file)

    #%% Radiosonde data: Read IWV and delta_TB data
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
    
    #%% map settings
    map_proj = ccrs.PlateCarree()
    data_proj = ccrs.PlateCarree()
    coords = np.array([[-45, 45], [-45, 55], [-40, 55], [-40, 45], [-45, 45]])
    extent = [-44.75, -40.25, 45.25, 54.75]
    
    #%% (not interesting at a single frequency) plot tb
    fig = plt.figure()
    ax = fig.add_subplot(111, projection=map_proj)
    ax.set_extent(extent)
    ax.coastlines()
    im = ax.pcolormesh(data_tb.lon, data_tb.lat, data_tb.tb.isel(frequency=0, angle=9).T, 
                       cmap='inferno', transform=data_proj)
    fig.colorbar(im, ax=ax)

    #%% PROOF plot state of atmosphere 
    fig, axes = plt.subplots(1, 4, figsize=(6, 4), subplot_kw=dict(projection=map_proj))
    fig.suptitle('Integrated hydrometeor content of ERA-5 scene\nBlack contours indicate integrated water vapor [kg m$^{-2}$]')
    
    for i, ax in enumerate(axes):
        ax.set_extent(extent, crs=data_proj)
        ax.coastlines()
        gl = ax.gridlines(crs=data_proj, linewidth=0.25, color='k', alpha=0.5, draw_labels=True, zorder=2,
                          x_inline=False, y_inline=False)
        gl.top_labels = False
        gl.right_labels = False
        if i > 0:
            gl.left_labels = False
    
        # plot iwv
        cs = ax.contour(data_iwv.lon, data_iwv.lat, data_iwv.iwv.T, colors='k', transform=data_proj, linewidths=0.5)
        ax.clabel(cs, inline=1, fontsize=6, fmt='%i')
    
    # plot hydrometeors (0: cloud, 1: ice, 2: rain, 3: snow)
    # cloud liquid
    im = axes[0].pcolormesh(data_hyd.lon, data_hyd.lat, data_hyd.ihydro.sel(h_class=0).T, cmap='Blues', transform=data_proj, 
                            vmin=0, vmax=0.6)
    cbar = fig.colorbar(im, ax=axes[0], label='Cloud liquid\n[kg m$^{-2}$]', orientation='horizontal')
    cbar.solids.set_edgecolor("face")
    
    # cloud ice
    im = axes[1].pcolormesh(data_hyd.lon, data_hyd.lat, data_hyd.ihydro.sel(h_class=1).T, cmap='Oranges', transform=data_proj, 
                            vmin=0, vmax=0.6)
    cbar = fig.colorbar(im, ax=axes[1], label='Cloud ice\n[kg m$^{-2}$]', orientation='horizontal')
    cbar.solids.set_edgecolor("face")
    
    # rain
    im = axes[2].pcolormesh(data_hyd.lon, data_hyd.lat, data_hyd.ihydro.sel(h_class=2).T, cmap='Greens', transform=data_proj, 
                            vmin=0, vmax=0.4)
    cbar = fig.colorbar(im, ax=axes[2], label='Rain\n[kg m$^{-2}$]', orientation='horizontal')
    cbar.solids.set_edgecolor("face")
    
    # snow
    im = axes[3].pcolormesh(data_hyd.lon, data_hyd.lat, data_hyd.ihydro.sel(h_class=3).T, cmap='Purples', transform=data_proj, 
                            vmin=0, vmax=3)
    cbar = fig.colorbar(im, ax=axes[3], label='Snow\n[kg m$^{-2}$]', orientation='horizontal')
    cbar.solids.set_edgecolor("face")
    
    fig.tight_layout()
    
    plt.savefig(path_plot+'era5/integrated_values.png', dpi=300)
    
    #%% PROOF plot delta_tb
    d_sets = ['delta_tb_freq_center', 'delta_tb_freq_bw', 'delta_tb_freq_bw_center']
    
    fig, axes = plt.subplots(3, 5, figsize=(6, 6), subplot_kw=dict(projection=map_proj))
    fig.suptitle('$\Delta$TB of ERA-5 scene\nBlack contours indicate integrated water vapor [kg m$^{-2}$]')
    
    # annotate channel name
    for i, ax in enumerate(axes[0, :]):
        ax.annotate(text=mwi.freq_txt[i], xy=(0.5, 1.01), xycoords='axes fraction', ha='center', va='bottom', fontsize=8)
    
    # annotate dataset
    kwargs = dict(fontsize=8, xy=(1.1, 0.5), ha='left', va='center', xycoords='axes fraction', rotation=90)
    axes[0, -1].annotate(r'$TB_{ref}$ at'+'\n'+r'$\nu_{center}$', **kwargs)
    axes[1, -1].annotate(r'$TB_{ref}$ at'+'\n'+r'$\nu_{center \pm \frac{1}{2} bandwidth}$', **kwargs)
    axes[2, -1].annotate(r'$TB_{ref}$ at'+'\n'+r'$\nu_{center}$ and $\nu_{center \pm \frac{1}{2} bandwidth}$', **kwargs)
    
    for i, ax in enumerate(axes.ravel()):
        ax.set_extent(extent, crs=data_proj)
        ax.coastlines()
        
        if i == 10:
            gl = ax.gridlines(crs=data_proj, linewidth=0.25, color='k', alpha=0.5, draw_labels=True, zorder=2,
                              x_inline=False, y_inline=False)
            gl.top_labels = False
            gl.right_labels = False
        else:
            gl = ax.gridlines(crs=data_proj, linewidth=0.25, color='k', alpha=0.5, draw_labels=False, zorder=2)
    
        # plot iwv
        cs = ax.contour(data_iwv.lon, data_iwv.lat, data_iwv.iwv.T, colors='k', transform=data_proj, linewidths=0.5)
        ax.clabel(cs, inline=1, fontsize=6, fmt='%i')
    
    for i, ds in enumerate(d_sets):
        for j, ch in enumerate(mwi.channels_str):
            im = axes[i, j].pcolormesh(data.lon, data.lat, data[ds].sel(channel=ch).T, cmap='bwr', vmin=-0.7, vmax=0.7, 
                                       shading='nearest', transform=data_proj)
    
    cax = fig.add_axes([0.3, 0.05, 0.4, 0.01])
    cax.set_title('$\Delta$TB [K]', fontsize=10)
    cbar = fig.colorbar(im, cax=cax, orientation='horizontal')
    cbar.solids.set_edgecolor("face")
    
    plt.subplots_adjust(wspace=0.05, hspace=0.05, right=0.95, top=0.85, left=0.07)
    
    plt.savefig(path_plot+'delta_tb/era5_grid.png', dpi=300)
    
    #%% PROOF error as function of ihyd
    data_hyd_l = data_hyd.ihydro[:, :, 0:3:2].sum('h_class')
    data_hyd_i = data_hyd.ihydro[:, :, 1:4:2].sum('h_class')
    
    fig, axes = plt.subplots(5, 3, figsize=(6, 8), sharex=True, sharey=True)
    fig.suptitle('$\Delta$TB (colors) as function of IWP and LWP')
    
    axes[2, 0].set_ylabel('Ice water path (cloud ice + snow) [kg m$^{-2}$]')
    axes[-1, 1].set_xlabel('Liquid water path (cloud liquid + rain) [kg m$^{-2}$]')
    
    axes[0, 0].set_title(r'$TB_{ref}$ at'+'\n'+r'$\nu_{center}$', fontsize=8)
    axes[0, 1].set_title(r'$TB_{ref}$ at'+'\n'+r'$\nu_{center \pm \frac{1}{2} bandwidth}$', fontsize=8)
    axes[0, 2].set_title(r'$TB_{ref}$ at'+'\n'+r'$\nu_{center}$ and $\nu_{center \pm \frac{1}{2} bandwidth}$', fontsize=8)
    
    from string import ascii_lowercase
    label = ['('+c+')' for c in ascii_lowercase]
    for i, ax in enumerate(axes.flatten()):
        
        ax.set_facecolor('grey')
        
        ax.annotate(text=label[i], xy=(0.9, 0.9), ha='right', va='top', xycoords='axes fraction', backgroundcolor='w', fontsize=8)
                
        # x axis
        ax.set_xticks(ticks=np.arange(0, 1.1, 0.5), minor=False)
        ax.set_xticks(ticks=np.arange(0, 1.1, 0.1), minor=True)
        
        # y axis
        ax.set_yticks(ticks=np.arange(0, 4.1, 1), minor=False)
        ax.set_yticks(ticks=np.arange(0, 4.1, 0.25), minor=True)
        
        ax.tick_params(which='major')
        ax.tick_params(which='minor', length=1)
        ax.grid('both', alpha=0.5)
                
        ax.set_ylim([0, 4])
        ax.set_xlim([0, 1])
        
    # annotate channel name
    for i, ax in enumerate(axes[:, -1]):
        ax.annotate(text=mwi.freq_txt[i], xy=(1.1, 0.5), xycoords='axes fraction', backgroundcolor="w",
                    annotation_clip=False, horizontalalignment='left', verticalalignment='center', fontsize=8)
    
    for i, ch in enumerate(mwi.channels_str):
        
        for j, ds in enumerate(d_sets):
        
            kwargs = dict(s=20, alpha=0.5, c=data[ds].sel(channel=ch), linewidths=0, cmap='jet', vmin=-0.7, vmax=0.7)
            im = axes[i, j].scatter(data_hyd_l, data_hyd_i, **kwargs)
    
    fig.tight_layout()
        
    cax = fig.add_axes([0.82, 0.03, 0.16, 0.01])
    cax.set_title('$\Delta$TB [K]', fontsize=8)
    cbar = fig.colorbar(im, cax=cax, orientation='horizontal')
    cbar.solids.set_edgecolor("face")

    plt.savefig(path_plot+'cloud_effect/cloud_effect_LWP_IWP.png', dpi=400)
    
    #%% PROOF error as function of iwv and LWP
    fig, axes = plt.subplots(5, 3, figsize=(6, 8), sharex=True, sharey=True)
    
    axes[2, 0].set_ylabel(r'$\Delta TB = TB_{obs} - TB_{ref}$ [K]')
    axes[-1, 1].set_xlabel('Integrated water vapor [kg m$^{-2}$]')
    
    axes[0, 0].set_title(r'$TB_{ref}$ at'+'\n'+r'$\nu_{center}$', fontsize=8)
    axes[0, 1].set_title(r'$TB_{ref}$ at'+'\n'+r'$\nu_{center \pm \frac{1}{2} bandwidth}$', fontsize=8)
    axes[0, 2].set_title(r'$TB_{ref}$ at'+'\n'+r'$\nu_{center}$ and $\nu_{center \pm \frac{1}{2} bandwidth}$', fontsize=8)
    
    for ax in axes.flatten():
        
        # x axis
        ax.set_xticks(ticks=np.arange(0, 150, 10), minor=False)
        ax.set_xticks(ticks=np.arange(0, 150, 5), minor=True)
        
        # y axis
        ax.set_yticks(ticks=np.arange(-2, 2, 0.5), minor=False)
        ax.set_yticks(ticks=np.arange(-2, 2, 0.1), minor=True)
        
        ax.tick_params(which='major')
        ax.tick_params(which='minor', length=1)
        ax.grid('both', alpha=0.5)
        
        ax.axhline(y=0, color='k', linewidth=1, alpha=0.5)
        
        ax.set_ylim([-1.4, 1.4])
        ax.set_xlim([0, 35])
        
    # annotate channel name
    for i, ax in enumerate(axes[:, -1]):
        ax.annotate(text=mwi.freq_txt[i], xy=(1.1, 0.5), xycoords='axes fraction', backgroundcolor="w",
                    annotation_clip=False, horizontalalignment='left', verticalalignment='center', fontsize=8)
    
    for i, channel in enumerate(mwi.channels_str):
        
        # radiosondes
        axes[i, 0].scatter(iwv_data, delta_tb_freq_center.sel(channel=channel), s=2, c='#777777', linewidths=0, alpha=0.5)
        axes[i, 1].scatter(iwv_data, delta_tb_freq_bw.sel(channel=channel), s=2, c='#777777', linewidths=0, alpha=0.5)
        axes[i, 2].scatter(iwv_data, delta_tb_freq_bw_center.sel(channel=channel), s=2, c='#777777', linewidths=0, alpha=0.5)
    
        # era5 clearsky
        kwargs = dict(s=2, c='#333333', linewidths=0, alpha=0.5)
        axes[i, 0].scatter(data_iwv.iwv, data_clearsky.delta_tb_freq_center.sel(channel=channel), **kwargs)
        im = axes[i, 1].scatter(data_iwv.iwv, data_clearsky.delta_tb_freq_bw.sel(channel=channel), **kwargs)
        axes[i, 2].scatter(data_iwv.iwv, data_clearsky.delta_tb_freq_bw_center.sel(channel=channel), **kwargs)
        
        # era5
        kwargs = dict(s=2, c=data_hyd_l, linewidths=0, alpha=0.5, cmap='jet', vmin=0, vmax=1)
        axes[i, 0].scatter(data_iwv.iwv, data.delta_tb_freq_center.sel(channel=channel), **kwargs)
        im = axes[i, 1].scatter(data_iwv.iwv, data.delta_tb_freq_bw.sel(channel=channel), **kwargs)
        axes[i, 2].scatter(data_iwv.iwv, data.delta_tb_freq_bw_center.sel(channel=channel), **kwargs)
        
    fig.tight_layout()
    
    #plt.subplots_adjust(bottom=0.15)
    
    #cax = fig.add_axes([0.3, 0.05, 0.4, 0.02])  # [left, bottom, width, height]
    cax = fig.add_axes([0.82, 0.03, 0.16, 0.01])
    cax.set_title('LWP [kg m$^{-2}$]', fontsize=8)
    cbar = fig.colorbar(im, cax=cax, orientation='horizontal')
    cbar.solids.set_edgecolor("face")
    
    # radiosonde legend below
    cols = ['#777777', '#333333']
    labs = ['Radiosonde', 'ERA-5 remove\nhydrometeors']
    patches = [plt.plot([],[], marker="o", ms=2, ls="", mec=None, color=cols[i], label=labs[i])[0] for i in range(0, 2)]
    #patches = [plt.plot([],[], marker="o", ms=2, ls="", mec=None, color='#777777', label='Radiosonde')[0] for ]
    leg = axes[-1, -1].legend(handles=patches, bbox_to_anchor=(1.02, 0.35), loc='upper left', frameon=True, ncol=1, fontsize=7)

    #plt.savefig(path_plot+'cloud_effect/cloud_effect_LWP_IWV_with_clear_sky.png', dpi=400)
    plt.savefig(path_plot+'cloud_effect/cloud_effect_LWP_IWV_with_clear_sky_era5clearsky.png', dpi=400)
    
    #%% PROOF error as function of iwv and IWP
    fig, axes = plt.subplots(5, 3, figsize=(6, 8), sharex=True, sharey=True)
    
    axes[2, 0].set_ylabel(r'$\Delta TB = TB_{obs} - TB_{ref}$ [K]')
    axes[-1, 1].set_xlabel('Integrated water vapor [kg m$^{-2}$]')
    
    axes[0, 0].set_title(r'$TB_{ref}$ at'+'\n'+r'$\nu_{center}$', fontsize=8)
    axes[0, 1].set_title(r'$TB_{ref}$ at'+'\n'+r'$\nu_{center \pm \frac{1}{2} bandwidth}$', fontsize=8)
    axes[0, 2].set_title(r'$TB_{ref}$ at'+'\n'+r'$\nu_{center}$ and $\nu_{center \pm \frac{1}{2} bandwidth}$', fontsize=8)
    
    for ax in axes.flatten():
        
        # x axis
        ax.set_xticks(ticks=np.arange(0, 150, 10), minor=False)
        ax.set_xticks(ticks=np.arange(0, 150, 5), minor=True)
        
        # y axis
        ax.set_yticks(ticks=np.arange(-2, 2, 0.5), minor=False)
        ax.set_yticks(ticks=np.arange(-2, 2, 0.1), minor=True)
        
        ax.tick_params(which='major')
        ax.tick_params(which='minor', length=1)
        ax.grid('both', alpha=0.5)
        
        ax.axhline(y=0, color='k', linewidth=1, alpha=0.5)
        
        ax.set_ylim([-1.4, 1.4])
        ax.set_xlim([0, 35])
        
    # annotate channel name
    for i, ax in enumerate(axes[:, -1]):
        ax.annotate(text=mwi.freq_txt[i], xy=(1.1, 0.5), xycoords='axes fraction', backgroundcolor="w",
                    annotation_clip=False, horizontalalignment='left', verticalalignment='center', fontsize=8)
    
    for i, channel in enumerate(mwi.channels_str):
        
        # radiosondes
        kwargs = dict(s=2, c='#777777', linewidths=0, alpha=0.5)
        axes[i, 0].scatter(iwv_data, delta_tb_freq_center.sel(channel=channel), **kwargs)
        axes[i, 1].scatter(iwv_data, delta_tb_freq_bw.sel(channel=channel), **kwargs)
        axes[i, 2].scatter(iwv_data, delta_tb_freq_bw_center.sel(channel=channel), **kwargs)
        
        # era5 clearsky
        kwargs = dict(s=2, c='#333333', linewidths=0, alpha=0.5)
        axes[i, 0].scatter(data_iwv.iwv, data_clearsky.delta_tb_freq_center.sel(channel=channel), **kwargs)
        im = axes[i, 1].scatter(data_iwv.iwv, data_clearsky.delta_tb_freq_bw.sel(channel=channel), **kwargs)
        axes[i, 2].scatter(data_iwv.iwv, data_clearsky.delta_tb_freq_bw_center.sel(channel=channel), **kwargs)
    
        # era5
        kwargs = dict(s=2, c=data_hyd_i, linewidths=0, alpha=0.5, cmap='jet', vmin=0, vmax=4)
        axes[i, 0].scatter(data_iwv.iwv, data.delta_tb_freq_center.sel(channel=channel), **kwargs)
        im = axes[i, 1].scatter(data_iwv.iwv, data.delta_tb_freq_bw.sel(channel=channel), **kwargs)
        axes[i, 2].scatter(data_iwv.iwv, data.delta_tb_freq_bw_center.sel(channel=channel), **kwargs)
        
    fig.tight_layout()
        
    #cax = fig.add_axes([0.3, 0.05, 0.4, 0.02])  # [left, bottom, width, height]
    cax = fig.add_axes([0.82, 0.03, 0.16, 0.01])
    cax.set_title('IWP [kg m$^{-2}$]', fontsize=8)
    cbar = fig.colorbar(im, cax=cax, orientation='horizontal')
    cbar.solids.set_edgecolor("face")
    
    # radiosonde legend below
    cols = ['#777777', '#333333']
    labs = ['Radiosonde', 'ERA-5 remove\nhydrometeors']
    patches = [plt.plot([],[], marker="o", ms=2, ls="", mec=None, color=cols[i], label=labs[i])[0] for i in range(0, 2)]
    #patches = [plt.plot([],[], marker="o", ms=2, ls="", mec=None, color='#777777', label='Radiosonde')[0] for ]
    leg = axes[-1, -1].legend(handles=patches, bbox_to_anchor=(1.02, 0.35), loc='upper left', frameon=True, ncol=1, fontsize=7)

    #plt.savefig(path_plot+'cloud_effect/cloud_effect_IWP_IWV_with_clear_sky.png', dpi=400)
    plt.savefig(path_plot+'cloud_effect/cloud_effect_IWP_IWV_with_clear_sky_era5clearsky.png', dpi=400)
    
    #%% PROOF error as function of iwv and IWP
    fig, axes = plt.subplots(5, 3, figsize=(6, 8), sharex=True, sharey=True)
    
    axes[2, 0].set_ylabel(r'$\Delta TB = TB_{obs} - TB_{ref}$ [K]')
    axes[-1, 1].set_xlabel('Integrated water vapor [kg m$^{-2}$]')
    
    axes[0, 0].set_title(r'$TB_{ref}$ at'+'\n'+r'$\nu_{center}$', fontsize=8)
    axes[0, 1].set_title(r'$TB_{ref}$ at'+'\n'+r'$\nu_{center \pm \frac{1}{2} bandwidth}$', fontsize=8)
    axes[0, 2].set_title(r'$TB_{ref}$ at'+'\n'+r'$\nu_{center}$ and $\nu_{center \pm \frac{1}{2} bandwidth}$', fontsize=8)
    
    for ax in axes.flatten():
        
        # x axis
        ax.set_xticks(ticks=np.arange(0, 150, 10), minor=False)
        ax.set_xticks(ticks=np.arange(0, 150, 5), minor=True)
        
        # y axis
        ax.set_yticks(ticks=np.arange(-2, 2, 0.5), minor=False)
        ax.set_yticks(ticks=np.arange(-2, 2, 0.1), minor=True)
        
        ax.tick_params(which='major')
        ax.tick_params(which='minor', length=1)
        ax.grid('both', alpha=0.5)
        
        ax.axhline(y=0, color='k', linewidth=1, alpha=0.5)
        
        ax.set_ylim([-1.4, 1.4])
        ax.set_xlim([0, 35])
        
    # annotate channel name
    for i, ax in enumerate(axes[:, -1]):
        ax.annotate(text=mwi.freq_txt[i], xy=(1.1, 0.5), xycoords='axes fraction', backgroundcolor="w",
                    annotation_clip=False, horizontalalignment='left', verticalalignment='center', fontsize=8)
    
    for i, channel in enumerate(mwi.channels_str):
        
        # radiosondes
        kwargs = dict(s=2, c='#777777', linewidths=0, alpha=0.5)
        axes[i, 0].scatter(iwv_data, delta_tb_freq_center.sel(channel=channel), **kwargs)
        axes[i, 1].scatter(iwv_data, delta_tb_freq_bw.sel(channel=channel), **kwargs)
        axes[i, 2].scatter(iwv_data, delta_tb_freq_bw_center.sel(channel=channel), **kwargs)
        
        # era5 clearsky
        kwargs = dict(s=2, c='#333333', linewidths=0, alpha=0.5)
        axes[i, 0].scatter(data_iwv.iwv, data_clearsky.delta_tb_freq_center.sel(channel=channel), **kwargs)
        im = axes[i, 1].scatter(data_iwv.iwv, data_clearsky.delta_tb_freq_bw.sel(channel=channel), **kwargs)
        axes[i, 2].scatter(data_iwv.iwv, data_clearsky.delta_tb_freq_bw_center.sel(channel=channel), **kwargs)
    
        # era5
        kwargs = dict(s=2, c=data_hyd.ihydro.isel(h_class=3), linewidths=0, alpha=0.5, cmap='jet', vmin=0, vmax=4)
        axes[i, 0].scatter(data_iwv.iwv, data.delta_tb_freq_center.sel(channel=channel), **kwargs)
        im = axes[i, 1].scatter(data_iwv.iwv, data.delta_tb_freq_bw.sel(channel=channel), **kwargs)
        axes[i, 2].scatter(data_iwv.iwv, data.delta_tb_freq_bw_center.sel(channel=channel), **kwargs)
        
    fig.tight_layout()
        
    #cax = fig.add_axes([0.3, 0.05, 0.4, 0.02])  # [left, bottom, width, height]
    cax = fig.add_axes([0.82, 0.03, 0.16, 0.01])
    cax.set_title('IWP [kg m$^{-2}$]', fontsize=8)
    cbar = fig.colorbar(im, cax=cax, orientation='horizontal')
    cbar.solids.set_edgecolor("face")
    
    # radiosonde legend below
    cols = ['#777777', '#333333']
    labs = ['Radiosonde', 'ERA-5 remove\nhydrometeors']
    patches = [plt.plot([],[], marker="o", ms=2, ls="", mec=None, color=cols[i], label=labs[i])[0] for i in range(0, 2)]
    #patches = [plt.plot([],[], marker="o", ms=2, ls="", mec=None, color='#777777', label='Radiosonde')[0] for ]
    leg = axes[-1, -1].legend(handles=patches, bbox_to_anchor=(1.02, 0.35), loc='upper left', frameon=True, ncol=1, fontsize=7)

    #plt.savefig(path_plot+'cloud_effect/cloud_effect_IWP_IWV_with_clear_sky.png', dpi=400)
    plt.savefig(path_plot+'cloud_effect/cloud_effect_SNOW_IWV_with_clear_sky_era5clearsky.png', dpi=400)