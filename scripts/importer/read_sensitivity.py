

import numpy as np
import pandas as pd


"""
Importer functions
"""


class Sensitivity:
    
    def __init__(self, path, filename='MWI-RX183_DSB_Matlab.xlsx'):
        """
        Read sensitivity data and prepare (linearize and normalize)
        """
        
        self.file = path+filename
        self.data = self.get_data()
        self.data_lino = self.prepare_data()
        
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
        Normalize linear spectral response function to a sum along each column of 1
        number of rows:    number of frequencies
        number of columns: number of channel
        """
        
        values_norm = values_lin / values_lin.sum(axis=0)
        
        return values_norm
        
    def get_data(self):
        """
        Read sensitivity measurement from excel file
        """
        
        # read data from excel sheet
        data_ch14 = pd.read_excel(self.file, sheet_name='Ch14', usecols=[0, 1],
                                  names=['frequency [GHz]', 'sensitivity [dB]'], header=None)
        data_ch15 = pd.read_excel(self.file, sheet_name='Ch15', usecols=[0, 1],
                                  names=['frequency [GHz]', 'sensitivity [dB]'], header=None)
        data_ch16 = pd.read_excel(self.file, sheet_name='Ch16', usecols=[0, 1],
                                  names=['frequency [GHz]', 'sensitivity [dB]'], header=None)
        data_ch17 = pd.read_excel(self.file, sheet_name='Ch17', usecols=[0, 1],
                                  names=['frequency [GHz]', 'sensitivity [dB]'], header=None)
        data_ch18 = pd.read_excel(self.file, sheet_name='Ch18', usecols=[0, 1],
                                  names=['frequency [GHz]', 'sensitivity [dB]'], header=None)
        
        # check if frequencies are the same
        assert np.sum(data_ch14.iloc[:, 0] != data_ch15.iloc[:, 0]) == 0
        assert np.sum(data_ch14.iloc[:, 0] != data_ch16.iloc[:, 0]) == 0
        assert np.sum(data_ch14.iloc[:, 0] != data_ch17.iloc[:, 0]) == 0
        assert np.sum(data_ch14.iloc[:, 0] != data_ch18.iloc[:, 0]) == 0
        
        # write data into single dataframe
        data = pd.DataFrame()
        data['frequency [GHz]'] = data_ch14.iloc[:, 0]  # use frequency from channel 14
        data['ch14 sensitivity [dB]'] = data_ch14.iloc[:, 1]
        data['ch15 sensitivity [dB]'] = data_ch15.iloc[:, 1]
        data['ch16 sensitivity [dB]'] = data_ch16.iloc[:, 1]
        data['ch17 sensitivity [dB]'] = data_ch17.iloc[:, 1]
        data['ch18 sensitivity [dB]'] = data_ch18.iloc[:, 1]
        
        return data
        
    def prepare_data(self):
        """
        Linearize and normalize measured spectral response functions
        """
        
        freqs = self.data.values[:, 0]  # get frequencies
        values = self.data.values[:, 1:]  # get sensitivity in dB
        
        values_lino = self.normalize_srf(values_lin=self.linearize_srf(values))
        
        # add to data frames
        data_lino = pd.DataFrame()    
        data_lino['frequency [GHz]'] = freqs
        data_lino['ch14 sensitivity'] = values_lino[:, 0]
        data_lino['ch15 sensitivity'] = values_lino[:, 1]
        data_lino['ch16 sensitivity'] = values_lino[:, 2]
        data_lino['ch17 sensitivity'] = values_lino[:, 3]
        data_lino['ch18 sensitivity'] = values_lino[:, 4]
        
        return data_lino
