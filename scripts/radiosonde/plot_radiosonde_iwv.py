

import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
import sys
sys.path.append(f'{os.environ["PATH_PHD"]}/projects/mwi_bandpass_effects/scripts')
from importer import IWV
from radiosonde import wyo
from path_setter import path_plot


"""
Plot IWV of Radiosonde stations
"""


if __name__ == '__main__':

    #$$ Read IWV
    iwv = IWV()
    iwv.read_data()
    
    #%% get indices
    station_id = np.array([x[3:8] for x in iwv.data.profile.values])
    date = np.array([datetime.datetime.strptime(x[-12:], '%Y%m%d%H%M') for x in iwv.data.profile.values])
    year = np.array([x.year for x in date])
    
    # index for 2019 data
    ix_2019 = year == 2019
    
    # station index
    ix_nya = station_id == wyo.station_id['Ny Alesund']
    ix_snp = station_id == wyo.station_id['Singapore']
    ix_ess = station_id == wyo.station_id['Essen']
    ix_bar = station_id == wyo.station_id['Barbados']
    ix_std = station_id == '00000'
    
    #%% sort data in pandas data frame
    df = pd.DataFrame(index=pd.date_range('2019-01-01 12:00', '2019-12-31 12:00', freq='1D'), 
                      columns=['Ny Alesund', 'Singapore', 'Essen', 'Barbados'],
                      data=np.nan)
    
    df.loc[date[ix_2019 & ix_nya], 'Ny Alesund'] = iwv.data.values[ix_2019 & ix_nya]
    df.loc[date[ix_2019 & ix_snp], 'Singapore'] = iwv.data.values[ix_2019 & ix_snp]
    df.loc[date[ix_2019 & ix_ess], 'Essen'] = iwv.data.values[ix_2019 & ix_ess]
    df.loc[date[ix_2019 & ix_bar], 'Barbados'] = iwv.data.values[ix_2019 & ix_bar]
    
    # to monthly mean
    df_mean = df.groupby([df.index.month_name()], sort=False).mean()
    df_std = df.groupby([df.index.month_name()], sort=False).std()
    
    #%% colors for plot
    colors = {'01004': 'b',
              '10410': 'g',
              '48698': 'r',
              '78954': 'orange',
              '00000': 'k',
              }
    
    #%% PROOF Plot integrated water vapor throughout the year for all stations
    fig = plt.figure(figsize=(5, 4))
    ax = fig.add_subplot(111)
    
    xticks = pd.to_datetime(df_mean.index.tolist(), format='%B').sort_values()
    
    for station_name in list(df.columns):
        print(station_name)
        
        c = colors[wyo.station_id[station_name]]
        mean = df_mean[station_name].values
        sd = df_std[station_name].values
        
        ax.plot(xticks, mean, color=c, linewidth=1.5, label=station_name)
        
        ax.fill_between(x=xticks, y1=mean-sd, y2=mean+sd, color=c, alpha=0.2,
                        linewidth=0)
        
    ax.legend(bbox_to_anchor=(0.5, -0.18), ncol=4, loc='upper center', frameon=True, fontsize=8)
    #ax.grid()
    ax.set_ylim(bottom=0)
    ax.set_xlim([np.min(xticks), np.max(xticks)])
    
    # set x ticks monthly
    ax.set_xticks(pd.to_datetime(df_mean.index.tolist(), format='%B').sort_values()) # to show all ticks

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b")) # must be called after plotting both axes

    ax.set_xlabel('Month')
    ax.set_ylabel('Integrated water vapor [kg m$^{-2}$]')
    
    plt.subplots_adjust(right=0.95, bottom=0.2, top=0.9)
    #plt.tight_layout()
    
    plt.savefig(path_plot + 'data/radiosondes_iwv_monthly.png', dpi=300,
                bbox_inches='tight')
