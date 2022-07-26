

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
sys.path.append(f'{os.environ["PATH_PHD"]}/projects/mwi_bandpass_effects/scripts')
from importer import Radiosonde
from radiosonde import wyo
from path_setter import path_plot, path_data


"""
Plot mean radiosonde profiles
"""

class Standard_Atmosphere:
    
    def __init__(self):
        
        self.data = np.nan
        
    def read_data(self):
        """
        Read one profile each
        """
        
        file_standard = path_data + 'atmosphere/standard_atmosphere.txt'
        self.data = pd.read_csv(file_standard, delimiter=',', comment='#', 
                                names=['z [m]', 'p [hPa]', 'T [K]', 'RH [%]'])
        

if __name__ == '__main__':
    
    # read one radiosonde profile and standard atmosphere
    RS = Radiosonde()
    RS.make_mean_profile()
    St = Standard_Atmosphere()
    St.read_data()
    
    #%% colors for plot
    colors = {'01004': 'b',
              '10410': 'g',
              '48698': 'r',
              '78954': 'orange',
              '00000': 'k',
              }
    
    #%% plot radiosonde mean profiles
    fig, axes = plt.subplots(1, 2, figsize=(5, 4), sharey=True)
    
    # plot standard atmosphere
    #axes[0].plot(St.data['T [K]']-273.15, St.data['p [hPa]'], color='k', label='Standard atmosphere')
    #axes[1].plot(St.data['RH [%]'], St.data['p [hPa]'], color='k')
        
    for station_id in list(wyo.id_station.keys()):
        
        print(station_id)
        
        c = colors[station_id]
        
        for i, var in enumerate(['T [C]', 'RH [%]']):
        
            mean = RS.data[station_id]['mean'][var].values
            sd = RS.data[station_id]['std'][var].values
            
            axes[i].plot(mean, RS.data['p [hPa]'], color=c, linewidth=1.5, label=wyo.id_station[station_id])
            axes[i].fill_betweenx(y=RS.data['p [hPa]'], x1=mean-sd, x2=mean+sd, 
                                  color=c, alpha=0.2, linewidth=0)
        
    axes[0].legend(bbox_to_anchor=(1.09, -0.2), ncol=4, loc='upper center', frameon=True, fontsize=8)

    axes[0].set_ylim([np.max(RS.data['p [hPa]']), np.min(RS.data['p [hPa]'])])
    axes[1].set_xlim([0, 100])

    axes[0].set_xlabel('Temperature [°C]')
    axes[1].set_xlabel('Relative humidity [%]')
    axes[0].set_ylabel('Pressure [hPa]')
    
    plt.subplots_adjust(right=0.95, bottom=0.25, top=0.9, left=0.15)
    
    plt.savefig(path_plot + 'data/radiosondes_t_rh.png', 
                dpi=300, bbox_inches='tight')
