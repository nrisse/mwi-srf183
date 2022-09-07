"""
Plot IWV of Radiosonde stations.
"""


import pandas as pd
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import os
from helpers import colors
from dotenv import load_dotenv

load_dotenv()


if __name__ == '__main__':

    # read data
    ds_com = xr.open_dataset(os.path.join(
        os.environ['PATH_BRT'],
        'TB_radiosondes_2019_MWI.nc'))
    
    #%% re-arrange data by making profile index to time/station index
    da_time = ds_com.time
    da_station = ds_com.station
    
    # drop time and station variables
    ds_com = ds_com.drop(['time', 'station'])
    
    # add multi index time and station
    ds_com['ts'] = (('profile'), pd.MultiIndex.from_arrays(
        arrays=[da_time.values, da_station.values],
        names=['time', 'station'],
        ))
    
    # swap dimensions
    ds_com = ds_com.swap_dims({'profile': 'ts'})
    
    # unstack - missing times for some profiles are filled with nan
    ds_com = ds_com.unstack()
    
    #%% calculate iwv statistics
    ds_iwv_mean = ds_com.iwv.groupby(ds_com.time.dt.month).mean('time')
    ds_iwv_std = ds_com.iwv.groupby(ds_com.time.dt.month).std('time')
    
    #%% integrated water vapor throughout the year for all stations
    fig, ax = plt.subplots(1, 1, figsize=(5, 4), constrained_layout=True)
        
    for station in list(ds_iwv_mean.station.values):

        ax.plot(ds_iwv_mean.month, 
                ds_iwv_mean.sel(station=station), 
                color=colors.colors_rs[station], 
                linewidth=1.5, label=station)
        
        ax.fill_between(x=ds_iwv_mean.month, 
                        y1=ds_iwv_mean.sel(station=station) - \
                            ds_iwv_std.sel(station=station), 
                        y2=ds_iwv_mean.sel(station=station) + \
                            ds_iwv_std.sel(station=station), 
                        color=colors.colors_rs[station], 
                        alpha=0.2, linewidth=0)
        
    ax.legend(bbox_to_anchor=(0.5, -0.18), ncol=4, loc='upper center', 
              frameon=True, fontsize=8)
    ax.set_ylim(bottom=0)
    ax.set_xlim([np.min(ds_iwv_mean.month), np.max(ds_iwv_mean.month)])
    
    # set x ticks monthly
    ax.set_xticks(ds_iwv_mean.month)
    
    ax.set_xlabel('Month')
    ax.set_ylabel('IWV [kg m$^{-2}$]')
        
    plt.savefig(os.path.join(
        os.environ['PATH_PLT'],
        'radiosondes_iwv_monthly.png'),
        dpi=300, bbox_inches='tight')
    
    plt.close('all')
    