

import numpy as np
import pandas as pd
import xarray as xr
from path_setter import path_data


"""
Script to read IWV data 
"""

class IWV:
    
    def __init__(self):
        
        # data as pandas data frame
        self.data_df = np.nan
        self.data = np.nan
        
    def read_data(self):
        """
        Read data
        """
        
        self.iwv_df = pd.read_csv(path_data + 'iwv/iwv_pamtra.txt', index_col=0, comment='#')
        self.iwv_df.loc['iwv', 'ID_00000_190001010000'] = 0  # standard atmosphere
        
        self.adjust_data()
        self.to_xarray()
        
    def to_xarray(self):
        """
        Convert pandas data frame to xarray
        """
        
        kwargs = {'dims': ('profile'), 
                  'coords': {'profile': self.iwv_df.columns.values},
                  'attrs': {'unit': 'kg m-2', 'name': 'integrated water vapor', 'source': 'WYO and PAMTRA'}
                 }
        
        self.data = xr.DataArray(data=self.iwv_df.values.flatten(), **kwargs)
        
    def adjust_data(self):
        """
        Add IWV value for standard atmosphere
        """
        
        self.iwv_df.loc['iwv', 'ID_00000_190001010000'] = 0
