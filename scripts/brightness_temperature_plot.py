

import numpy as np
import pandas as pd
from glob import glob
import sys
import matplotlib.pyplot as plt
sys.path.append('/home/nrisse/uniHome/WHK/eumetsat/scripts')
from mwi_183 import MWI183GHz as mwi
from sensitivity import profile_prop

"""
Description

Plot brightness temperature of radiosonde profile
"""


class PAMTRA_TB:
    
    def __init__(self):
        """
        Class to read brightness temperature simulation
        """

        # brightness temperature
        self.pam_data_df = np.nan
        
    def get_filename(self, station_id, year, month, day, hour='12', minute='00'):
        """
        Build filename from station ID and date
        """
        
        yyyy = str(year)
        mm = str(month).zfill(2)
        dd = str(day).zfill(2)
        HH = str(hour).zfill(2)
        MM = str(minute).zfill(2)
        station_id = str(station_id)
        
        path = yyyy + '/' + mm + '/' + dd + '/TB_PAMTRA_ID_' + station_id + '_' + yyyy + mm + dd + HH + MM
        
        return path
        
    def read_all(self, path='/home/nrisse/uniHome/WHK/eumetsat/data/brightness_temperature/'):
        """
        Read data from PAMTRA simulation
        """
        
        files = glob(path + '*/*/*/*.txt')
        files.append(path + 'TB_PAMTRA_standard_atmosphere.txt')
        
        for i, file in enumerate(files):
            
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
    
    def plot_pamtra_simulation(self):
        """
        Plot pamtra simulation
        
        Profiles has to be a list of profiles to be plotted
        """
        
        cols = self.pam_data_df.columns[1:]
        
        profile_class = [self.get_profile_class(p) for p in cols]

        fig = plt.figure(figsize=(9, 6))
        ax = fig.add_subplot(111)
        ax.set_title('PAMTRA simulation at 833 km nadir view (V-pol) and MWI 183.31 GHz channels\nfor different ' +
                     'radiosonde profiles and standard atmosphere (RH=0%)')
        
        for i, profile in enumerate(cols):
            ax.plot(self.pam_data_df['frequency [GHz]'], self.pam_data_df[profile], profile_prop[profile_class[i]]['line_format'],
                    label=profile_prop[profile_class[i]]['label'])
        
        # add MWI channels
        for i, channel in enumerate(mwi.channels_str):
            
            # annotate channel name
            ax.annotate(text=mwi.freq_txt[i][4:6], xy=[mwi.freq_center[i, 0]-0.4, 171], fontsize=7,
                        bbox=dict(boxstyle='square', fc='white', ec='none', pad=0))
            ax.annotate(text=mwi.freq_txt[i][4:6], xy=[mwi.freq_center[i, 1]-0.4, 171], fontsize=7,
                        bbox=dict(boxstyle='square', fc='white', ec='none', pad=0))
            
            # add vertical lines
            ax.axvline(x=183.31, color='pink', linestyle='-', alpha=0.5)  # mark line center
            ax.axvline(x=mwi.freq_center[i, 0], color='gray', linestyle='-', alpha=0.5)  # mark left channel frequency
            ax.axvline(x=mwi.freq_center[i, 1], color='gray', linestyle='-', alpha=0.5)  # mark right channel frequency
            
        ax.legend(bbox_to_anchor=(1.05, 0.5), loc='center left', frameon=False)
        ax.grid(axis='y')
        
        ax.set_ylim([170, 290])
        ax.set_xlim([np.min(self.pam_data_df['frequency [GHz]']), np.max(self.pam_data_df['frequency [GHz]'])])
        
        ax.set_xlabel('Frequency [GHz]')
        ax.set_ylabel('Brightness temperature [K]')
        
        fig.tight_layout()
        
        plt.savefig(self._path_fig + 'pamtra_simulation.png', dpi=200)


if __name__ == '__main__':
    
    # read brightness temperatures
    PAM = PAMTRA_TB()
    PAM.read_all()
    
    PAM.pam_data_df
    PAM.plot_pamtra_simulation()
    

