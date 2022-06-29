

import numpy as np
from netCDF4 import Dataset
import numpy.ma as ma
import xarray as xr


class Delta_TB:
    
    def __init__(self):
        """
        Class to read the delta_tb nc file
        
        delta_tb shape: (channel, profile, noise_level, reduction_level)
        """
        
        # dimensions
        self.channel = np.nan
        self.profile = np.nan
        self.noise_level = np.nan
        self.reduction_level = np.nan
        
        # delta_tb
        self.mean_freq_center = np.nan
        self.std_freq_center = np.nan
        self.mean_freq_bw = np.nan
        self.std_freq_bw = np.nan
        self.mean_freq_bw_center = np.nan
        self.std_freq_bw_center = np.nan
        
    def read_data(self, file=path_data+'/delta_tb/delta_tb.nc'):
        """
        Read data
        """
        
        with Dataset(file, 'r') as nc:
            
            # dimensions
            self.channel = nc.variables['channel'][:]
            self.profile = nc.variables['profile'][:]
            self.noise_level = ma.getdata(nc.variables['noise_level'][:])
            self.reduction_level = ma.getdata(nc.variables['reduction_level'][:])
            
            # delta_tb
            self.mean_freq_center = ma.getdata(nc.variables['delta_tb_mean_freq_center'][:])
            self.std_freq_center = ma.getdata(nc.variables['delta_tb_std_freq_center'][:])
            self.mean_freq_bw = ma.getdata(nc.variables['delta_tb_mean_freq_bw'][:])
            self.std_freq_bw = ma.getdata(nc.variables['delta_tb_std_freq_bw'][:])
            self.mean_freq_bw_center = ma.getdata(nc.variables['delta_tb_mean_freq_bw_center'][:])
            self.std_freq_bw_center = ma.getdata(nc.variables['delta_tb_std_freq_bw_center'][:])
        
        self.adjust_data()
        self.to_xarray()
    
    def to_xarray(self):
        """
        Convert numpy ndarrays to xarray objects
        """
        
        kwargs = {'dims': ('channel', 'profile', 'noise_level', 'reduction_level'), 
                  'coords': {'channel': self.channel, 
                             'profile': self.profile, 
                             'noise_level': self.noise_level, 
                             'reduction_level': self.reduction_level},
                  'attrs': {'unit': 'K'}
                 }

        self.mean_freq_center = xr.DataArray(data=self.mean_freq_center, **kwargs)
        self.std_freq_center = xr.DataArray(data=self.std_freq_center, **kwargs)
        self.mean_freq_bw = xr.DataArray(data=self.mean_freq_bw, **kwargs)
        self.std_freq_bw = xr.DataArray(data=self.std_freq_bw, **kwargs)
        self.mean_freq_bw_center = xr.DataArray(data=self.mean_freq_bw_center, **kwargs)
        self.std_freq_bw_center = xr.DataArray(data=self.std_freq_bw_center, **kwargs)
            
    def adjust_data(self):
        """
        Change ID of standard atmosphere
        """
        
        self.profile[self.profile == 'standard_atmosphere'] = 'ID_00000_190001010000'


if __name__ == '__main__':
    
    delta_tb = Delta_TB()
    delta_tb.read_data()
