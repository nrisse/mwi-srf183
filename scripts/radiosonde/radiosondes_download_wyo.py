

import requests
from bs4 import BeautifulSoup
from io import StringIO
import pandas as pd
import numpy as np
import datetime
import os


station_id = {'Ny Alesund': '01004', 'Singapore': '48698', 'Essen': '10410',
              'Barbados': '78954'}

id_station = {'01004': 'Ny Alesund', '48698': 'Singapore', '10410': 'Essen',
              '78954': 'Barbados'}

if __name__ == '__main__':
    
    # set stations 
    name = {'Ny Alesund': 'ny_alesund', 'Singapore': 'singapore', 'Essen': 'essen',
            'Barbados': 'barbados'}
    
    # set times
    #dates_feb = pd.date_range(start='2020/02/01 12:00', end='2020/02/28 12:00', freq='24H')
    #dates_aug = pd.date_range(start='2020/08/01 12:00', end='2020/08/31 12:00', freq='24H')
    
    dates_2019 = pd.date_range(start='2019/01/01 12:00', end='2019/12/31 12:00', freq='24H')
    
    dates = dates_2019  # dates_feb.append(dates_aug)
    
    colnames = ['p [hPa]', 'z [m]', 'T [C]', 'T_dew [C]', 'RH [%]', 'r [g/kg]', 'wdir [deg]',
                'SKNT [knot]', 'THTA [K]', 'THTE [K]', 'THTV [K]']
    
    stations = station_id.keys()
    
    for station in stations:
        
        print(station)
        
        for date in dates:
            
            print(date)
            
            date_file = date.strftime('%Y%m%d%H%M')
        
            day = date.strftime('%d')
            month = date.strftime('%m')
            year = date.strftime('%Y')
            hour = date.strftime('%H')
            
            # get data
            base = 'http://weather.uwyo.edu/cgi-bin/sounding?'
            link = base+'region=np&TYPE=TEXT%3ALIST&YEAR='+year+'&MONTH='+month+'&FROM='+day+hour+'&TO='+day+hour+'&STNM='+station_id[station]
            html = requests.get(link).text
            
            try:
                # get station name and time from header
                header = html.split('<H2>')[1].split('</H2>')[0]
                
                data_str = html.split('<PRE>')[1].split('</PRE>')[0]
            
                data = pd.read_fwf(StringIO(data_str), skiprows=5, header=None, names=colnames)
                
                folder = '/home/nrisse/uniHome/WHK/eumetsat/data/atmosphere/'+year+'/'+month+'/'+day+'/'
                file = 'ID_'+station_id[station]+'_'+date_file+'.txt'
                
                if not os.path.exists(folder):
                    os.makedirs(folder)
                    
                with open(folder+file, 'w') as f:
                    f.write('# '+ header + '\n')
                    data.to_csv(f, index=False)
                    
            except IndexError:
                print('Can not find data for time {}'.format(date))
