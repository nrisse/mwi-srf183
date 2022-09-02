"""
View ERA-5 scene and the selected region within
"""

import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
import cartopy.crs as ccrs
import matplotlib.ticker as mticker
from string import ascii_lowercase as abc
import os
import sys
sys.path.append(f'{os.environ["PATH_PHD"]}/projects/mwi_bandpass_effects/scripts')
from path_setter import path_data, path_plot

plt.ion()


if __name__ == '__main__':
    
    ds_era5_sl = xr.open_dataset(path_data+'atmosphere/era5-single-'+
                                 'levels_20150331_1200.nc')
    ds_era5_sl = ds_era5_sl.isel(time=0)
    
    ds_com = xr.open_dataset(
        path_data+'brightness_temperature/TB_era5_hyd_MWI.nc')
    
    #%% information on dataset
    print(ds_era5_sl.latitude.min().item())
    print(ds_era5_sl.latitude.max().item())
    print(ds_era5_sl.longitude.min().item())
    print(ds_era5_sl.longitude.max().item())
    
    print(list(ds_era5_sl))
    
    print(ds_com.hydro_wp.max(['grid_x', 'grid_y']))
    
    #%% subset of region of interest
    extent = [-44.75, -40.25, 45.25, 54.75]

    i_lon = (ds_era5_sl.longitude > -45) & (ds_era5_sl.longitude < -40)
    i_lat = (ds_era5_sl.latitude > 45) & (ds_era5_sl.latitude < 55)
    
    ds_era5_sl_sel = ds_era5_sl.isel(longitude=i_lon, latitude=i_lat)
    
    #%% plot on map
    map_proj = ccrs.Mollweide(central_longitude=-30)
    data_proj = ccrs.PlateCarree()
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6, 4),
                                   constrained_layout=True,
                                   subplot_kw=dict(projection=map_proj))
    
    for ax in fig.axes:
        ax.set_extent([-90, 30, -90, 90])
        ax.coastlines()
    
    # tcwv
    # plot entire field
    im1 = ax1.pcolormesh(ds_era5_sl.longitude, 
                         ds_era5_sl.latitude, 
                         ds_era5_sl.tcwv, 
                         cmap='Greys_r', transform=data_proj)
    
    # plot selected field
    im2 = ax1.pcolormesh(ds_era5_sl_sel.longitude, 
                         ds_era5_sl_sel.latitude, 
                         ds_era5_sl_sel.tcwv, 
                         cmap='magma', transform=data_proj)
    
    fig.colorbar(im1, ax=ax1, label='IWV [kg m$^{-2}$]', 
                 orientation='horizontal')
    fig.colorbar(im2, ax=ax1, orientation='horizontal')
    
    # surface pressure
    # plot entire field
    im3 = ax2.pcolormesh(ds_era5_sl.longitude, 
                         ds_era5_sl.latitude, 
                         ds_era5_sl.sp*1e-2, 
                         cmap='Greys_r', transform=data_proj,
                         vmin=980, vmax=1020)
    
    # plot selected field
    im4 = ax2.pcolormesh(ds_era5_sl_sel.longitude, 
                         ds_era5_sl_sel.latitude, 
                         ds_era5_sl_sel.sp*1e-2, 
                         cmap='magma', transform=data_proj)
    
    fig.colorbar(im3, ax=ax2, label='Surface pressure [hPa]', 
                 orientation='horizontal')
    fig.colorbar(im4, ax=ax2, orientation='horizontal')
    
    plt.savefig(path_plot+'data/era5_surface_variables_large_scale.png', 
                dpi=300, bbox_inches='tight')
        
    #%% plot state of atmosphere 
    map_proj = ccrs.PlateCarree()

    fig, axes = plt.subplots(1, 4, figsize=(6, 4), constrained_layout=True,
                             subplot_kw=dict(projection=map_proj))
    
    for i, ax in enumerate(axes.flatten()):
        ax.annotate(f'({abc[i]})', xy=(1, 0), xycoords='axes fraction',
                    ha='right', va='bottom', color='k')
    
    gl = axes[0].gridlines(crs=data_proj, linewidth=0, color='k', 
                      alpha=0.5, draw_labels=True, zorder=2,
                      x_inline=False, y_inline=False)
    gl.top_labels = False
    gl.right_labels = False
    gl.xlocator = mticker.FixedLocator(np.arange(-180, 180, 1))
    gl.ylocator = mticker.FixedLocator(np.arange(-90, 90, 2))
    gl.xlabel_style = {'size': 8}
    gl.ylabel_style = {'size': 8}
    
    for i, ax in enumerate(axes):

        # plot iwv
        cs = ax.contour(ds_com.lon, 
                        ds_com.lat, 
                        ds_com.iwv, 
                        colors='k',
                        transform=data_proj, 
                        linewidths=0.5)
        ax.clabel(cs, inline=1, fontsize=6, fmt='%i')
    
    # plot hydrometeors (0: cloud, 1: ice, 2: rain, 3: snow)
    dct_hyd = {'cwc': 'Cloud liquid', 'iwc': 'Cloud ice', 'rwc': 'Rain',
               'swc': 'Snow'}
    
    dct_col = {'cwc': 'Blues', 
               'iwc': 'Oranges', 
               'rwc': 'Greens',
               'swc': 'Purples'}
    
    dct_ticks = {'cwc': np.arange(0, 0.8, 0.2), 
                 'iwc': np.arange(0, 0.8, 0.2), 
                 'rwc': np.arange(0, 0.6, 0.2),
                 'swc': np.arange(0, 4, 1),
                 }
    
    for i, (hyd, label) in enumerate(dct_hyd.items()):
        
        # cloud liquid
        im = axes[i].pcolormesh(ds_com.lon, ds_com.lat, 
                                ds_com.hydro_wp.sel(hydro_class=hyd), 
                                cmap=dct_col[hyd], transform=data_proj, 
                                vmin=np.min(dct_ticks[hyd]), 
                                vmax=np.max(dct_ticks[hyd]))
        fig.colorbar(im, ax=axes[i], label=label+'\n[kg m$^{-2}$]', 
                     orientation='horizontal', ticks=dct_ticks[hyd])
        
    plt.savefig(path_plot+'data/era5_int_hyd.png', dpi=300, 
                bbox_inches='tight')
    
    plt.close('all')
    
    #%% surface emissivity
    map_proj = ccrs.PlateCarree()

    fig, axes = plt.subplots(1, 4, figsize=(6, 3), constrained_layout=True,
                             subplot_kw=dict(projection=map_proj))
    
    for i, ax in enumerate(axes.flatten()):
        ax.annotate(f'({abc[i]})', xy=(1, 0), xycoords='axes fraction',
                    ha='right', va='bottom', color='white')
    
    gl = axes[0].gridlines(crs=data_proj, linewidth=0, color='k', 
                      alpha=0.5, draw_labels=True, zorder=2,
                      x_inline=False, y_inline=False)
    gl.top_labels = False
    gl.right_labels = False
    gl.xlocator = mticker.FixedLocator(np.arange(-180, 180, 1))
    gl.ylocator = mticker.FixedLocator(np.arange(-90, 90, 2))
    gl.xlabel_style = {'size': 8}
    gl.ylabel_style = {'size': 8}
    
    freqs = np.array([ds_com.frequency.min(), 183367, ds_com.frequency.max()])
    for i, freq in enumerate(freqs):
        
        axes[i].set_title('%g GHz'%(freq*1e-3))
        
        im = axes[i].pcolormesh(
            ds_com.lon,
            ds_com.lat, 
            ds_com.emissivity.sel(frequency=freq).isel(angle=9),
            cmap='magma')
        fig.colorbar(im, ax=axes[i], shrink=0.5)
        
    axes[3].set_title('Diff')
    im = axes[3].pcolormesh(
        ds_com.lon,
        ds_com.lat, 
        ds_com.emissivity.sel(frequency=freqs[0]).isel(angle=9) -\
        ds_com.emissivity.sel(frequency=freqs[2]).isel(angle=9),
        cmap='magma_r')
    fig.colorbar(im, ax=axes[3], shrink=0.5)
    
    plt.savefig(path_plot+'data/era5_emissivity.png', dpi=300, 
                bbox_inches='tight')
    
    plt.close('all')
    
    #%%
    plt.close('all')
    