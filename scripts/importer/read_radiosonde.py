

import numpy as np
import pandas as pd


"""
Importer functions
"""


class Radiosonde:

    def __init__(self):
        """
        Class to read radiosonde profiles that are used for MWI analysis
        """

        self.profile = np.nan

    def read_profile(self, station_id, year, month, day, hour='12', minute='00', path='/home/nrisse/uniHome/WHK/eumetsat/data/atmosphere/'):
        """
        Read radiosonde profiles
        """
        
        yyyy = str(year)
        mm = str(month).zfill(2)
        dd = str(day).zfill(2)
        HH = str(hour).zfill(2)
        MM = str(minute).zfill(2)
        station_id = str(station_id)
        
        file = yyyy + '/' + mm + '/' + dd + '/ID_' + station_id + '_' + yyyy + mm + dd + HH + MM + '.txt'

        self.profile = pd.read_csv(path + file, comment='#', sep=',')
