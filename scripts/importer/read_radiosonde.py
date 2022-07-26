"""
Import radiosonde profiles. Calculates 2019 mean and std profile
"""


import numpy as np
import pandas as pd
from glob import glob
import os
import sys
sys.path.append(f'{os.environ["PATH_PHD"]}/projects/mwi_bandpass_effects/scripts')
from path_setter import path_data
from radiosonde import wyo


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
            files = glob(path_data + 'atmosphere/2019/*/*/ID_'+station_id+'*.txt')
            
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
