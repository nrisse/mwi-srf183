"""
Plot radiosonde profiles
"""


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from glob import glob
import os
import sys
sys.path.append(f'{os.environ["PATH_PHD"]}/projects/mwi_bandpass_effects/scripts')
from radiosonde import wyo
from path_setter import path_plot, path_data


class Radiosonde:

    def __init__(self):
        """
        Class to read radiosonde profiles that are used for MWI analysis
        """

        self.data = {}
        
    @staticmethod
    def read_single(file):
        """
        Read single radiosonde profile
        """
        
        profile = pd.read_csv(file, comment='#', sep=',')
        
        return profile
    
    def make_mean_profile(self):
        """
        Read all radiosonde profiles
            - Data is read and resampled on a common pressure grid
        """

        print('getting all radiosonde files...')
        
        for station_id in list(wyo.id_station.keys()):
            
            print(station_id)
            
            # get all 2019 data
            files = glob(path_data + f'atmosphere/2019/*/*/*{station_id}*.txt')
            
            # get all values for the station ID
            values = np.array([])
            
            for i, file in enumerate(files):
                
                print('{}/{}'.format(i+1, len(files)))
                
                profile = self.read_single(file)
                
                if i == 0:
                    
                    values = profile.values
                    
                else:
                    
                    values = np.concatenate((values, profile.values), axis=0)
            
            # resample on height grid of length n
            n = 50
            p_grid = np.linspace(1013.25, 0, n)
            
            p = values[:, 0]  # pressure of data
    
            # get index of bins to which each value in ind_var belongs
            # interval does not include the right edge
            # left bin end is open: bins[i-1] <= x < bins[i] (if True, array get value i at position of x)
            digitized = np.digitize(x=p, bins=p_grid)
        
            # calculate means over time and height for every height bin
            # bins are indiced until the UPPER edge thus not starting with h_bin=0m
    
            # initialize arrays for statistics
            mean = np.full(shape=(n, values.shape[1]), fill_value=np.nan)
            std = np.full(shape=(n, values.shape[1]), fill_value=np.nan)
    
            # loop of length of bins
            for i in range(n):
    
                # get values within the bin (digitized has same shape as values)
                values_bin = values[digitized == i, :]
    
                # calculate mean and standard deviation
                if np.sum(~np.isnan(values_bin)) > 0:  # check if array has at least one non-NaN value
                
                    mean[i, :] = np.nanmean(values_bin, axis=0)
                    std[i, :] = np.nanstd(values_bin, axis=0)
                    
                else:
                    
                    mean[i, :] = np.nan
                    std[i, :] = np.nan
            
            # to dataframe
            result = dict()
            result['mean'] = pd.DataFrame(columns=profile.columns, data=mean)
            result['std'] = pd.DataFrame(columns=profile.columns, data=std)
            
            # combine with overall data dictionary
            self.data[station_id] = result
            self.data['p [hPa]'] = p_grid


if __name__ == '__main__':
    
    # read one radiosonde profile and standard atmosphere
    RS = Radiosonde()
    RS.make_mean_profile()
    
    #%% colors for plot
    colors = {'Ny-Alesund': 'cornflowerblue',
              'Essen': 'seagreen',
              'Singapore': 'palevioletred',
              'Barbados': 'peru',
              }
    
    #%% plot radiosonde mean profiles
    fig, axes = plt.subplots(1, 2, figsize=(5, 4), sharey=True)
        
    for station_id in list(wyo.id_station.keys()):
        
        print(station_id)
        
        c = colors[wyo.id_station[station_id]]
        
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
