"""
Comparison of virtual MWI observation under original SRF and the four estimates
based on reference frequencies (x3) and top-hat function displayed as map.

All other ways of displaying the relationship are found in other scripts, 
where also the radiosondes are evaluated.

How to use the script:
    - select one of the two era-5 simulations (with and without hydrometeors)
    - select the respective extension, which modifies figure filename
"""


import matplotlib.pyplot as plt
import xarray as xr
import cartopy.crs as ccrs
import numpy as np
import matplotlib.ticker as mticker
from string import ascii_lowercase as abc
import os
import sys
sys.path.append(f'{os.environ["PATH_PHD"]}/projects/mwi_bandpass_effects/scripts')
from path_setter import path_data, path_plot
from mwi_info import mwi

plt.ion()


if __name__ == '__main__':
    
    ds_com_era = xr.open_dataset(
        path_data+'brightness_temperature/TB_era5_MWI.nc')
    ext = ''
    
    ds_com_erh = xr.open_dataset(
        path_data+'brightness_temperature/TB_era5_hyd_MWI.nc')
    ext = '_hyd'

    #%% statistics
    ds_com_era.dtb_mwi_est.max()
    ds_com_era.dtb_mwi_est.min()
    
    ds_com_erh.dtb_mwi_est.max()
    ds_com_erh.dtb_mwi_est.min()
    
    #%% map settings
    map_proj = ccrs.PlateCarree()
    data_proj = ccrs.PlateCarree()
    coords = np.array([[-45, 45], [-45, 55], [-40, 55], [-40, 45], [-45, 45]])
    extent = [-44.75, -40.25, 45.25, 54.75]
    
    #%% tb difference on map for the four calculation methods
    # choose either with or without hydrometeors
    ds_com = ds_com_era
    ext = ''
    
    #ds_com = ds_com_erh
    #ext = '_hyd'
    
    fig, axes = plt.subplots(4, 5, figsize=(6, 6), 
                             sharex=True, sharey=True,
                             subplot_kw=dict(projection=map_proj), 
                             constrained_layout=True)
    
    # annotate channel name
    for i, ax in enumerate(axes[0, :]):
        ax.annotate(text=mwi.freq_txt[i].split('\n')[0], xy=(0.5, 1.01), 
                    xycoords='axes fraction', ha='center', va='bottom',
                    )
    
    for i, ax in enumerate(axes.flatten()):
        ax.annotate(f'({abc[i]})', xy=(1, 0), xycoords='axes fraction',
                    ha='right', va='bottom', color='k')
    
    # annotate dataset
    kwargs = dict(xy=(1.1, 0.5), ha='left', va='center', 
                  xycoords='axes fraction', rotation=90)
    axes[0, -1].annotate('center', **kwargs)
    axes[1, -1].annotate('cutoff', **kwargs)
    axes[2, -1].annotate('center+cutoff', **kwargs)
    axes[3, -1].annotate('top-hat', **kwargs)
    
    for i, ax in enumerate(axes.flatten('F')):
        ax.set_extent(extent, crs=data_proj)
        
        if i == 3:
            gl = ax.gridlines(crs=data_proj, linewidth=0, color='k', 
                              alpha=0.5, draw_labels=True, zorder=2,
                              x_inline=False, y_inline=False)
            gl.top_labels = False
            gl.right_labels = False
            gl.xlocator = mticker.FixedLocator(np.arange(-180, 180, 1))
            gl.ylocator = mticker.FixedLocator(np.arange(-90, 90, 2))
            gl.xlabel_style = {'size': 8}
            gl.ylabel_style = {'size': 8}
    
        # plot iwv
        cs = ax.contour(ds_com.lon, ds_com.lat, ds_com.iwv,
                        colors='k', transform=data_proj, linewidths=0.5)
        ax.clabel(cs, inline=1, fontsize=6, fmt='%i')
    
    for i, channel in enumerate(ds_com.channel):
        for j, est_type in enumerate(ds_com.est_type):
            im = axes[j, i].pcolormesh(
                ds_com.lon, 
                ds_com.lat, 
                ds_com.dtb_mwi_est.sel(channel=channel, est_type=est_type), 
                cmap='BrBG_r', vmin=-0.8, vmax=0.8, shading='nearest', 
                transform=data_proj)
    
    fig.colorbar(im, ax=axes, orientation='vertical', shrink=0.33,
                 label='$\Delta$TB [K]', ticks=np.arange(-0.8, 0.9, 0.4))
        
    plt.savefig(path_plot+'evaluation/dtb_mwi_est_grid_era5'+ext+'.png', dpi=300,
                bbox_inches='tight')
    
    plt.close('all')
    
    #%% difference between with and without hydrometeors
    fig, axes = plt.subplots(4, 5, figsize=(6, 6), 
                             sharex=True, sharey=True,
                             subplot_kw=dict(projection=map_proj), 
                             constrained_layout=True)
    
    # annotate channel name
    for i, ax in enumerate(axes[0, :]):
        ax.annotate(text=mwi.freq_txt[i].split('\n')[0], xy=(0.5, 1.01), 
                    xycoords='axes fraction', ha='center', va='bottom',
                    )
    
    for i, ax in enumerate(axes.flatten()):
        ax.annotate(f'({abc[i]})', xy=(1, 0), xycoords='axes fraction',
                    ha='right', va='bottom', color='k')
    
    # annotate dataset
    kwargs = dict(xy=(1.1, 0.5), ha='left', va='center', 
                  xycoords='axes fraction', rotation=90)
    axes[0, -1].annotate('center', **kwargs)
    axes[1, -1].annotate('cutoff', **kwargs)
    axes[2, -1].annotate('center+cutoff', **kwargs)
    axes[3, -1].annotate('top-hat', **kwargs)
    
    for i, ax in enumerate(axes.flatten('F')):
        ax.set_extent(extent, crs=data_proj)
        
        if i == 3:
            gl = ax.gridlines(crs=data_proj, linewidth=0, color='k', 
                              alpha=0.5, draw_labels=True, zorder=2,
                              x_inline=False, y_inline=False)
            gl.top_labels = False
            gl.right_labels = False
            gl.xlocator = mticker.FixedLocator(np.arange(-180, 180, 1))
            gl.ylocator = mticker.FixedLocator(np.arange(-90, 90, 2))
            gl.xlabel_style = {'size': 8}
            gl.ylabel_style = {'size': 8}
    
        # plot iwv
        cs = ax.contour(ds_com_era.lon, ds_com_era.lat, ds_com_era.iwv,
                        colors='k', transform=data_proj, linewidths=0.5)
        ax.clabel(cs, inline=1, fontsize=6, fmt='%i')
    
    for i, channel in enumerate(ds_com_era.channel):
        for j, est_type in enumerate(ds_com_era.est_type):
            im = axes[j, i].pcolormesh(
                ds_com_era.lon, 
                ds_com_era.lat, 
                ds_com_erh.dtb_mwi_est.sel(channel=channel, est_type=est_type)-\
                ds_com_era.dtb_mwi_est.sel(channel=channel, est_type=est_type), 
                cmap='BrBG_r', vmin=-0.6, vmax=0.6, shading='nearest', 
                transform=data_proj)
    
    fig.colorbar(im, ax=axes, orientation='vertical', shrink=0.33,
                 label='$\Delta$TB$_{\mathrm{all-sky}}$ - $\Delta$TB$_{\mathrm{clear-sky}}$ [K]', ticks=np.arange(-0.8, 0.9, 0.4))
        
    plt.savefig(path_plot+'evaluation/'+
                'dtb_mwi_est_grid_era5_cloud_minus_clear.png', dpi=300,
                bbox_inches='tight')
    
    plt.close('all')