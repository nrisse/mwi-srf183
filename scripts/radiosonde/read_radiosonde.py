"""
Import radiosonde profiles. Calculates 2019 mean and std profile
"""


import numpy as np
import pandas as pd
from glob import glob
from datetime import datetime
import os
import sys
sys.path.append(f'{os.environ["PATH_PHD"]}/projects/mwi_bandpass_effects/scripts')
from path_setter import path_data
from radiosonde import wyo


import xarray as xr


if __name__ == '__main__':

    files = glob(path_data + 'atmosphere/2019/*/*/*.txt')

    # get maximum length
    lengths = []
    for file in files:
        df = pd.read_csv(file, comment='#')
        lengths.append(len(df.index))
    print(np.max(lengths))


    for i, file in enumerate(files):
        
        station = wyo.id_station[file[-22:-17]]
        time = np.datetime64(datetime.strptime(file[-16:-4], '%Y%m%d%H%M%S')).astype('datetime64[s]')
        
        df = pd.read_csv(file, comment='#')
        
        if i == 0:
            
            ds = xr.Dataset()
            ds.coords['station'] = np.array([station])
            ds.coords['lev'] = np.arange(200)
            ds.coords['time'] = np.array([time])
            for var in list(df):
                ds[var] = (('lev', 'station', 'time'), np.full((200, 1, 1), fill_value=np.nan))
                ds[var][:len(df.index), 0, 0] = df[var].values  
            
        else:
            
            ds_other = xr.Dataset()
            ds_other.coords['station'] = np.array([station])
            ds_other.coords['lev'] = np.arange(200)
            ds_other.coords['time'] = np.array([time])
            for var in list(df):
                ds_other[var] = (('lev', 'station', 'time'), np.full((200, 1, 1), fill_value=np.nan))
                ds_other[var][:len(df.index), 0, 0] = df[var].values  
            
            ds = ds.merge(ds_other)


    # interpolate on regular height grid - not sure how though!

    ds['z [m]'] = ds['z [m]'].ffill(dim='lev')
    ds['z [m]'] = ds['z [m]'].bfill(dim='lev')
    ds['z [m]'] = ds['z [m]'].fillna(0)

    import matplotlib.pyplot as plt


    fig, ax = plt.subplots()

    ax.pcolormesh(ds['time'].values,
                ds['z [m]'].sel(station='Ny-Alesund'),
                ds['r [g/kg]'].sel(station='Ny-Alesund'),
                shading='nearest'
                )



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
