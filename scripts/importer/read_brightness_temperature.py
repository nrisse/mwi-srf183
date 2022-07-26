

import numpy as np
import pandas as pd
from glob import glob
import os
import sys
sys.path.append(f'{os.environ["PATH_PHD"]}/projects/mwi_bandpass_effects/scripts')
from path_setter import path_data


class PAMTRA_TB:
    
    def __init__(self):
        """
        Class to read brightness temperature simulation
        """

        # brightness temperature
        self.pam_data_df = np.nan
        
    def get_filename(self, station_id, year, month, day, hour='12', minute='00'):
        """
        Build filename from station ID and date (for radiosondes)
        """
        
        yyyy = str(year)
        mm = str(month).zfill(2)
        dd = str(day).zfill(2)
        HH = str(hour).zfill(2)
        MM = str(minute).zfill(2)
        station_id = str(station_id)
        
        path = yyyy + '/' + mm + '/' + dd + '/TB_PAMTRA_ID_' + station_id + '_' + yyyy + mm + dd + HH + MM
        
        return path
        
    def read_all(self, path=path_data+'brightness_temperature/', era5=False):
        """
        Read data from PAMTRA simulation
        """
        
        if era5:
            path += 'era5/'
        
        # get all txt files in path structure
        # for radiosondes: add the simulation from standard atmosphere
        files = glob(path + '*/*/*/*.txt')
        
        if not era5:
            files.append(path + 'TB_PAMTRA_standard_atmosphere.txt')
        
        for i, file in enumerate(files):
            
            print(file)
            
            header = file.split('TB_PAMTRA_')[1][:-4]
                        
            if i == 0:
                
                self.pam_data_df = pd.read_csv(file, delimiter=',', comment='#')
                self.pam_data_df.rename(columns={'TB': header}, inplace=True)
            
            else:
                
                pam_data = pd.read_csv(file, delimiter=',', comment='#')
                self.pam_data_df[header] = pam_data['TB']
                
                # check if frequencies are identical (!!!) if not, values have to be joined
                assert (pam_data['Frequency [GHz]'] == self.pam_data_df['Frequency [GHz]']).all
                
        self.pam_data_df.rename(columns={'Frequency [GHz]': 'frequency [GHz]'}, inplace=True)
