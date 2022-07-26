

import matplotlib.pyplot as plt
import xarray as xr
import cartopy.crs as ccrs
import numpy as np
import os
import sys
sys.path.append(f'{os.environ["PATH_PHD"]}/projects/mwi_bandpass_effects/scripts')
from path_setter import path_data, path_plot
from mwi_info import mwi


if __name__ == '__main__':
    
    
    file = path_data+'/delta_tb/delta_tb_era5grid.nc'
    data = xr.load_dataset(file)
    
    file = path_data+'/delta_tb/delta_tb_nadir_era5grid_step_function.nc'
    data_step_fun = xr.load_dataset(file)
    
    file_iwv = path_data+'/iwv/IWV_PAMTRA_ERA5.nc'
    data_iwv = xr.load_dataset(file_iwv)

    file_hyd = path_data+'/integrated_hydrometeors/HYDRO_PAMTRA_ERA5.nc'
    data_hyd = xr.load_dataset(file_hyd)
    data_hyd = data_hyd.rename_dims({'class': 'h_class'})
    
    file_tb = path_data+'/brightness_temperature/era5/2015/03/31/TB_PAMTRA_ERA5.nc'
    data_tb = xr.load_dataset(file_tb)
    
    #%% plot
    # quick test here
    # errors of up to 0.2 occur
    # however, less than using just a few frequencies
    # but taking the effor of simulating the frequencies into account, the
    # error to MWI measurement is still high and needs to be corrected

    
    #%% map settings
    map_proj = ccrs.PlateCarree()
    data_proj = ccrs.PlateCarree()
    coords = np.array([[-45, 45], [-45, 55], [-40, 55], [-40, 45], [-45, 45]])
    extent = [-44.75, -40.25, 45.25, 54.75]
    
    #%% PROOF plot delta_tb    
    fig, axes = plt.subplots(1, 5, figsize=(6, 3), subplot_kw=dict(projection=map_proj))
    fig.suptitle('$\Delta$TB of ERA-5 scene ($TB_{ref}$ calculated with bandpass step function)\nBlack contours indicate integrated water vapor [kg m$^{-2}$]')
    
    # annotate channel name
    for i, ax in enumerate(axes):
        ax.annotate(text=mwi.freq_txt[i], xy=(0.5, 1.01), xycoords='axes fraction', ha='center', va='bottom', fontsize=8)
    
    # annotate dataset
    kwargs = dict(fontsize=8, xy=(1.1, 0.5), ha='left', va='center', xycoords='axes fraction', rotation=90)
    axes[-1].annotate('$TB_{ref}$ at every\nchannel freq.', **kwargs)
    
    for i, ax in enumerate(axes.ravel()):
        ax.set_extent(extent, crs=data_proj)
        ax.coastlines()
        
        if i == 0:
            gl = ax.gridlines(crs=data_proj, linewidth=0.25, color='k', alpha=0.5, draw_labels=True, zorder=2,
                              x_inline=False, y_inline=False)
            gl.top_labels = False
            gl.right_labels = False
        else:
            gl = ax.gridlines(crs=data_proj, linewidth=0.25, color='k', alpha=0.5, draw_labels=False, zorder=2)
    
        # plot iwv
        cs = ax.contour(data_iwv.lon, data_iwv.lat, data_iwv.iwv.T, colors='k', transform=data_proj, linewidths=0.5)
        ax.clabel(cs, inline=1, fontsize=6, fmt='%i')
    
    for i, ch in enumerate(mwi.channels_str):
        im = axes[i].pcolormesh(data_step_fun.lon, data_step_fun.lat, 
                                data_step_fun.delta_tb_step_function.sel(channel=ch).T, cmap='bwr', vmin=-0.7, vmax=0.7, 
                                shading='nearest', transform=data_proj)
    
    fig.tight_layout()
    
    cax = fig.add_axes([0.3, 0.1, 0.4, 0.01])
    cax.set_title('$\Delta$TB [K]', fontsize=10)
    cbar = fig.colorbar(im, cax=cax, orientation='horizontal')
    cbar.solids.set_edgecolor("face")
    
    plt.subplots_adjust(top=0.7, bottom=0.2)
    
    plt.savefig(path_plot+'delta_tb/era5_grid_step_function.png', dpi=300)
