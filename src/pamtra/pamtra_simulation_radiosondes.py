"""
PAMTRA simulation of radiosondes.
"""


from __future__ import division
import pyPamtra
import os
import numpy as np
import pandas as pd
import xarray as xr
from glob import glob
from dotenv import load_dotenv
from pamtra.pamtra_tools import pam_to_xarray

load_dotenv()


if __name__ == '__main__':
        
    # get radiosonde files
    files = glob(os.path.join(os.environ['PATH_ATM'], '2019/*/*/*.txt'))
    
    # ID for each radiosonde
    rsd_profiles = np.array([file[-25:-4] for file in files])
    lst_ds_pam = []
    
    for i, file in enumerate(files):
        
        print(f'{i+1}/{len(files)} - {file}')
        
        # read radiosonde profile
        df_rsd = pd.read_csv(file, comment='#')
        df_rsd.drop(df_rsd[df_rsd['z [m]'] < 0].index, inplace=True)
        df_rsd.dropna(axis='index', 
                      subset=['p [hPa]', 'z [m]', 'T [C]', 'RH [%]'], 
                      inplace=True)
        
        pam = pyPamtra.pyPamtra()
    
        pam.nmlSet['creator'] = 'Nils Risse'
    
        pam.nmlSet['active'] = False
        pam.nmlSet['passive'] = True
        pam.nmlSet['outpol'] = 'VH'
        pam.set['freqs'] = np.loadtxt(os.path.join(
            os.environ['PATH_BRT'], 'frequencies.txt'))
    
        pam.nmlSet['add_obs_height_to_layer'] = False
    
        pam.nmlSet['gas_mod'] = 'R98'
        pam.nmlSet['emissivity'] = 0.9
        
        # create pamtra profile based on radiosonde data
        pam_profile = dict()
        
        pam_profile['ngridx'] = 1
        pam_profile['ngridy'] = 1
        
        pam_profile['obs_height'] = np.array([[[833000]]])
    
        # time (not important)
        time = np.datetime64('2022-01-01').astype('datetime64[s]').astype('int')
        pam_profile['timestamp'] = np.array([[time]])
    
        # location (not important)
        pam_profile['lat'] = np.array([[79]])
        pam_profile['lon'] = np.array([[0]])
    
        # physical properties
        pam_profile['groundtemp'] = np.array([[np.nan]])
        pam_profile['sfc_salinity'] = np.array([[33]])
        pam_profile['wind10u'] = np.array([[0]])
        pam_profile['wind10v'] = np.array([[0]])
        pam_profile['sfc_slf'] = np.array([[1]])
        pam_profile['sfc_sif'] = np.array([[0]])
        
        # atmosphere
        pam_profile["press"] = df_rsd['p [hPa]'] * 100
        pam_profile["hgt"] = df_rsd['z [m]']
        pam_profile["temp"] = df_rsd['T [C]'] + 273.15
        pam_profile["relhum"] = df_rsd['RH [%]']
        
        # radiative transfer
        pam_profile['sfc_type'] = np.array([[-1]])  # fixed emissivity
        pam_profile['sfc_model'] = np.array([[-1]])  # not used for type=-1
        pam_profile['sfc_refl'] = np.array([['S']])  # specular
    
        pam.createProfile(**pam_profile)
    
        pam.df.addHydrometeor(('ice', -99., -1, 917., 130., 3.0, 0.684, 2., 3, 1,
                               'mono_cosmo_ice', -99., -99., -99., -99., -99., -99.,
                               'mie-sphere', 'heymsfield10_particles', 0.0))
        
        pam.runParallelPamtra(pam.set['freqs'],
                          pp_deltaX=1, 
                          pp_deltaY=1, 
                          pp_deltaF=10, 
                          pp_local_workers="auto")
        pam.addIntegratedValues()
        
        lst_ds_pam.append(pam_to_xarray(pam))
    
    ds_pam = xr.concat(
        lst_ds_pam,
        pd.Index(rsd_profiles, name='profile'))
    
    # write result to file
    file_out = os.path.join(
        os.environ['PATH_SIM'], 
        'TB_radiosondes_2019_complete.nc')
    ds_pam.to_netcdf(file_out)

    # write result with reduced variables to file
    ds_pam_red = ds_pam.sel(grid_x=0, grid_y=0, direction='up', outlevel=0, 
                            polarization='V', hydro_class=0)
    file_out = os.path.join(
        os.environ['PATH_BRT'],
        'TB_radiosondes_2019.nc')
    ds_pam_red.to_netcdf(file_out)
