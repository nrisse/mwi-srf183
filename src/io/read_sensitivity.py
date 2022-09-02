"""
Read SRF from excel files to xarray Dataset
"""


import numpy as np
import pandas as pd
import xarray as xr
import os
from mwi_info import mwi
from dotenv import load_dotenv

load_dotenv()


class Sensitivity:
    
    files = ['MWI-RX183_DSB_Matlab.xlsx', 'MWI-RX183_Matlab.xlsx']
    
    def __init__(self, filename='MWI-RX183_DSB_Matlab.xlsx'):
        """
        Read sensitivity data and prepare (linearize and normalize)
        """
        
        self.data = self.get_data(filename)

    @staticmethod
    def linearize_srf(values):
        """
        Convert spectral response function from dB to linear units
        number of rows:    number of frequencies
        number of columns: number of channel
        """
        
        values_lin = 10**(0.1 * values)
        
        return values_lin
    
    @staticmethod
    def normalize_srf(values_lin):
        """
        Normalize linear spectral response function to a sum along each 
        column of 1
        number of rows:    number of frequencies
        number of columns: number of channel
        """
        
        values_norm = values_lin / values_lin.sum(axis=0, keepdims=True)
        
        return values_norm
        
    def get_data(self, filename):
        """
        Read sensitivity measurement from excel file
        """
        
        # read data from excel sheet
        file = os.path.join(
            os.environ['PATH_SRF'], filename)
        data_ch14 = pd.read_excel(file, sheet_name='Ch14', usecols=[0, 1],
                                  names=['frequency [GHz]', 'sensitivity [dB]'], 
                                  header=None)
        data_ch15 = pd.read_excel(file, sheet_name='Ch15', usecols=[0, 1],
                                  names=['frequency [GHz]', 'sensitivity [dB]'],
                                  header=None)
        data_ch16 = pd.read_excel(file, sheet_name='Ch16', usecols=[0, 1],
                                  names=['frequency [GHz]', 'sensitivity [dB]'], 
                                  header=None)
        data_ch17 = pd.read_excel(file, sheet_name='Ch17', usecols=[0, 1],
                                  names=['frequency [GHz]', 'sensitivity [dB]'],
                                  header=None)
        data_ch18 = pd.read_excel(file, sheet_name='Ch18', usecols=[0, 1],
                                  names=['frequency [GHz]', 'sensitivity [dB]'],
                                  header=None)
        
        # check if frequencies are the same
        assert np.sum(data_ch14.iloc[:, 0] != data_ch15.iloc[:, 0]) == 0
        assert np.sum(data_ch14.iloc[:, 0] != data_ch16.iloc[:, 0]) == 0
        assert np.sum(data_ch14.iloc[:, 0] != data_ch17.iloc[:, 0]) == 0
        assert np.sum(data_ch14.iloc[:, 0] != data_ch18.iloc[:, 0]) == 0
        
        # combine data to numpy array
        sens_data = np.array([data_ch14.iloc[:, 1],
                              data_ch15.iloc[:, 1],
                              data_ch16.iloc[:, 1],
                              data_ch17.iloc[:, 1],
                              data_ch18.iloc[:, 1]
                              ]).T
        
        # linearized and normalized
        sens_data_lino = self.normalize_srf(
            values_lin=self.linearize_srf(sens_data))
        
        # write data to xarray
        data = xr.Dataset(
            data_vars=dict(raw=(('frequency', 'channel'), 
                                sens_data, 
                                dict(units='dB')),
                           lino=(('frequency', 'channel'), 
                                 sens_data_lino,
                                 dict(unit='-')),
                           ),
            coords=dict(frequency=(('frequency'),
                                   (data_ch14.iloc[:, 0].values*1e3).astype(
                                       'int'), 
                                   dict(unit='MHz')),
                        channel=(('channel'), 
                                 mwi.channels_int, 
                                 dict(unit='-'))),
            attrs=dict(source='European Space Agency',
                       file=file,
                       comment='Spectral response function of MWI channels')
                          )
        
        return data
