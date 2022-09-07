"""
Data availability of the radiosondes
"""


import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
from dotenv import load_dotenv

load_dotenv()
plt.ion()


if __name__ == '__main__':
    
    # read nc files
    ds_com_rsd = xr.open_dataset(os.path.join(
        os.environ['PATH_BRT'],
        'TB_radiosondes_2019_MWI.nc'))
    
    #%% data availability
    text = 'Data availability of station {} in 2019: {}'
    for station in np.unique(ds_com_rsd.station.values):
        print(f'{station}: {np.sum(ds_com_rsd.station==station).item()/365}')
    
    #%% plot data availability
    fig, ax = plt.subplots(1, 1, figsize=(5, 2), constrained_layout=True)
    
    ax.set_facecolor('#EB3939')
    
    dates = pd.date_range('2019-01-01', '2019-12-31', freq='1D')
    
    df = pd.DataFrame(index=dates, data=0, 
                      columns=np.unique(ds_com_rsd.station))
    for station in df.columns:
        df.loc[ds_com_rsd.time.dt.date.sel(
            profile=ds_com_rsd.station==station), station] = 1
    
    for i, station in enumerate(df.columns):
        
        ax.fill_between(x=dates, y1=-i, y2=df.loc[:, station]-i, step='mid', 
                        color='#2BB443')
        
        ax.axhline(y=-i, color='k', linewidth=1)

    ax.set_xlim([dates[0], dates[-1]])
    ax.set_ylim([-3, 1])
    
    # tick for every month
    months = mdates.MonthLocator()
    months_fmt = mdates.DateFormatter('%b')
    ax.xaxis.set_major_locator(months)
    ax.xaxis.set_major_formatter(months_fmt)
    
    # remove y axis
    ax.set_yticks([])
    ax.set_xlabel('Month')

    # annotate station
    y = np.arange(0.5, -3, -1)
    for i, name in enumerate(df.columns):
        ax.annotate(text=name, xy=(dates[0], y[i]), xycoords='data', 
                    ha='right', va='center')

    plt.savefig(os.path.join(
        os.environ['PATH_PLT'],
        'radiosondes_data_availability.png'), dpi=300)
    