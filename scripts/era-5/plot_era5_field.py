"""
View ERA-5 scene and the selected region within
"""

import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import os
import sys
sys.path.append(f'{os.environ["PATH_PHD"]}/projects/mwi_bandpass_effects/scripts')
from path_setter import path_data, path_plot

plt.ion()


if __name__ == '__main__':
    
    file = path_data+'era5/era5-single-levels_20150331_1200.nc'
    ds_era5 = xr.open_dataset(file)
    ds_era5 = ds_era5.isel(time=0)  # collapse time dimension
    
    #%% information on dataset
    print(ds_era5.latitude.min().item())
    print(ds_era5.latitude.max().item())
    print(ds_era5.longitude.min().item())
    print(ds_era5.longitude.max().item())
    
    print(list(ds_era5))
    
    #%% subset of region of interest
    i_lon = (ds_era5.longitude > -45) & (ds_era5.longitude < -40)
    i_lat = (ds_era5.latitude > 45) & (ds_era5.latitude < 55)
    
    ds_era5_sel = ds_era5.isel(longitude=i_lon, latitude=i_lat)
    
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
    im1 = ax1.pcolormesh(ds_era5.longitude, 
                        ds_era5.latitude, 
                        ds_era5.tcwv, 
                        cmap='Greys_r', transform=data_proj)
    
    # plot selected field
    im2 = ax1.pcolormesh(ds_era5_sel.longitude, 
                        ds_era5_sel.latitude, 
                        ds_era5_sel.tcwv, 
                        cmap='magma', transform=data_proj)
    
    fig.colorbar(im1, ax=ax1, label='IWV [kg m$^{-2}$]', 
                 orientation='horizontal')
    fig.colorbar(im2, ax=ax1, orientation='horizontal')
    
    # surface pressure
    # plot entire field
    im3 = ax2.pcolormesh(ds_era5.longitude, 
                        ds_era5.latitude, 
                        ds_era5.sp*1e-2, 
                        cmap='Greys_r', transform=data_proj,
                        vmin=980, vmax=1020)
    
    # plot selected field
    im4 = ax2.pcolormesh(ds_era5_sel.longitude, 
                        ds_era5_sel.latitude, 
                        ds_era5_sel.sp*1e-2, 
                        cmap='magma', transform=data_proj)
    
    fig.colorbar(im3, ax=ax2, label='Surface pressure [hPa]', 
                 orientation='horizontal')
    fig.colorbar(im4, ax=ax2, orientation='horizontal')
    
    plt.savefig(path_plot+'era5/surface_variables.png', dpi=300, 
                bbox_inches='tight')
    
    #%%
    plt.close('all')
    