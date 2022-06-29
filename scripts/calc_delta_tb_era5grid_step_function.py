

import numpy as np
import re
import pandas as pd
import matplotlib.pyplot as plt
from netCDF4 import Dataset
import datetime
import xarray as xr
import os
import sys
sys.path.append(f'{os.environ["PATH_PHD"]}/projects/mwi_bandpass_effects/scripts')
from path_setter import *
from importer import Sensitivity
from importer import PAMTRA_TB
from mwi_info import mwi


"""
Calculates difference Delta_TB between TB_MWI and TB_PAMTRA

for grid of ERA5 model (lat-lon, single event)

Compare step function with the real measured SRF
"""


def join_pam_on_srf(pam, srf):
    """
    Combine PAMTRA brightness temperature dataframe and linearized and normalized sensitivity
    data at matching frequencies.
    
    here: convert frequency to join - float to int and then back int to float
    """

    N = 10000
    
    # make copy of data 
    pam = pam.copy(deep=True)
    srf = srf.copy(deep=True)
    
    # convert frequency to integer and use as join
    pam['frequency [GHz]'] = np.round(pam['frequency [GHz]']*N).astype(int)
    srf['frequency [GHz]'] = np.round(srf['frequency [GHz]']*N).astype(int)
    
    # merge the data on the matching frequencies and convert frequency to float again
    srf_pam = pd.merge(pam, srf, on='frequency [GHz]')
    srf_pam['frequency [GHz]'] = srf_pam['frequency [GHz]'] / N
    
    return srf_pam


def calculate_tb_mwi(tb, srf):
    """
    Calculate virtual MWI temperature
    """
    
    tb_mwi = np.dot(tb, srf)
    
    return tb_mwi


def create_noise_values(data_lino, std=0.1, n=1000):
    """
    Create gaussian perturbation of the spectral response function
    """
    
    np.random.seed(0)

    n_freq = data_lino.shape[0]
    
    noise = np.random.normal(loc=1, scale=std, size=(n_freq, n))
    
    # add realizations to each of the measurements and shiw result as boxplot
    srf_plus_noise = np.full(shape=(n_freq, n, len(mwi.channels_str)), fill_value=np.nan)
    
    for i, channel in enumerate(mwi.channels_str):

        srf_plus_noise[:, :, i] = noise * np.array(data_lino['ch'+channel+' sensitivity'])[:, np.newaxis]
        srf_plus_noise[:, :, i] = Sensitivity.normalize_srf(srf_plus_noise[:, :, i])

    return srf_plus_noise



if __name__ == '__main__':

    filename_out = 'delta_tb_era5grid_step_function.nc'
    
    # read bandpass measurement
    sen_dsb = Sensitivity(path=path_data + 'sensitivity/', filename='MWI-RX183_DSB_Matlab.xlsx')

    # read pamtra simulations
    pam = xr.load_dataset(path_data+'brightness_temperature/era5/2015/03/31/TB_PAMTRA_ERA5.nc')
    
    # create step function for every channel
    f = sen_dsb.data_lino['frequency [GHz]'].values
    step_fun = np.zeros(shape=(sen_dsb.data_lino.shape[0], 5))
    i = 0
    for a, b, c, d in mwi.freq_bw:
        step_fun[(f>a) & (f<b), i] = 1
        step_fun[(f>c) & (f<d), i] = 1
        step_fun[:, i] /= step_fun[:, i].sum()  # normalize step function
        i += 1
    step_fun_df = sen_dsb.data_lino.copy(deep=True)
    step_fun_df.iloc[:, 1:] = step_fun
    
    # get index of the frequencies belonging to srf 
    ix = np.array([], dtype=int)
    for f in sen_dsb.data_lino['frequency [GHz]'].values:
        ix = np.append(ix, np.where(pam.frequency.values == f))
    
    pam_srf = pam.isel(frequency=ix)
    
    # double-check that orders of frequencies are matching now
    assert (np.round(pam_srf.frequency.values*1000, 0) == np.round(sen_dsb.data_lino['frequency [GHz]'].values*1000, 0)).all()
    
    # dimensions
    n_lon = len(pam.lon)
    n_lat = len(pam.lat)
    n_channels = len(mwi.channels_str)
    
    # create six output datasets
    delta_tb = np.full(shape=(n_lon, n_lat, n_channels), fill_value=-999, dtype=np.float)
            
    for i, channel in enumerate(mwi.channels_str):
        
        print('Channel: {}'.format(channel))
        
        for j in range(n_lon):
            
            for k in range(n_lat):
        
                # calculate virtual MWI measurement (1,)
                tb_mwi = calculate_tb_mwi(tb=pam_srf.tb.isel(lon=j, lat=k).values,  # (freq,)
                                          srf=sen_dsb.data_lino.loc[:, 'ch'+channel+' sensitivity'].values    # (freq,)
                                          )
                
                # step function
                tb_pam = calculate_tb_mwi(tb=pam_srf.tb.isel(lon=j, lat=k).values,  # (freq,)
                                          srf=step_fun_df.loc[:, 'ch'+channel+' sensitivity'].values    # (freq,)
                                          )
                delta_tb[j, k, i] = tb_mwi - tb_pam  # (scalar)
    
    # create nc file
    file = path_data + 'delta_tb/' + filename_out
    with Dataset(file, 'w', format='NETCDF4') as rootgrp:
    
        # global attributes
        rootgrp.author = "Nils Risse"
        rootgrp.history = "created: {}".format(datetime.datetime.now().date().strftime('%Y-%m-%d'))
        
        # create dimension
        rootgrp.createDimension(dimname='lon', size=n_lon)
        rootgrp.createDimension(dimname='lat', size=n_lat)
        rootgrp.createDimension(dimname='channel', size=n_channels)  # 5
        
        # write lon
        var_lon = rootgrp.createVariable(varname='lon', datatype=np.float, dimensions=('lon',))
        var_lon.comment = 'Longitude'
        var_lon[:] = pam.lon.values
        
        # write lat
        var_lat = rootgrp.createVariable(varname='lat', datatype=np.float, dimensions=('lat',))
        var_lat.comment = 'Latitude'
        var_lat[:] = pam.lat.values
        
        # write channel
        var_channel = rootgrp.createVariable(varname='channel', datatype=np.str, dimensions=('channel',))
        var_channel.comment = 'MWI channel number'
        var_channel[:] = mwi.channels_str
        
        # write result wit step function
        var_delta_tb_freq_center = rootgrp.createVariable(varname='delta_tb_step_function', datatype=np.float, dimensions=('lon', 'lat', 'channel',))
        var_delta_tb_freq_center.comment = 'Calculation: delta_tb = tb_mwi - tb_pamtra'
        var_delta_tb_freq_center.unit = 'K'
        var_delta_tb_freq_center[:] = delta_tb
