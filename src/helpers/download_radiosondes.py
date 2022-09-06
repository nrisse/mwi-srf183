"""
Script to automatically download radiosondes from University of Wyoming website
"""


import requests
from io import StringIO
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()


station_id = {'Ny-Alesund': '01004', 
              'Singapore': '48698', 
              'Essen': '10410',
              'Barbados': '78954'}

id_station = {v: k for k, v in station_id.items()}

if __name__ == '__main__':
    
    # set stations 
    name = {'Ny-Alesund': 'ny_alesund', 
            'Singapore': 'singapore', 
            'Essen': 'essen',
            'Barbados': 'barbados'}
    
    # set times
    dates = pd.date_range(start='2019/01/01 12:00', 
                          end='2019/12/31 12:00', 
                          freq='24H')
        
    colnames = ['p [hPa]', 'z [m]', 'T [C]', 'T_dew [C]', 'RH [%]', 'r [g/kg]', 
                'wdir [deg]',  'SKNT [knot]', 'THTA [K]', 'THTE [K]', 
                'THTV [K]']
    
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
            link = base+'region=np&TYPE=TEXT%3ALIST&YEAR='+year+'&MONTH='+\
                month+'&FROM='+day+hour+'&TO='+day+hour+'&STNM='+\
                    station_id[station]
            html = requests.get(link).text
            
            try:
                # get station name and time from header
                header = html.split('<H2>')[1].split('</H2>')[0]
                
                data_str = html.split('<PRE>')[1].split('</PRE>')[0]
            
                data = pd.read_fwf(StringIO(data_str), skiprows=5, header=None, 
                                   names=colnames)
                
                file = os.path.join(
                    os.environ['PATH_ATM'],
                    year, month, day,
                    'ID_'+station_id[station]+'_'+date_file+'.txt'
                    )
                
                if not os.path.exists(os.path.dirname(file)):
                    os.makedirs(os.path.dirname(file))
                    
                with open(file, 'w') as f:
                    f.write('# '+ header + '\n')
                    data.to_csv(f, index=False)
                    
            except IndexError:
                print('Can not find data for time {}'.format(date))
