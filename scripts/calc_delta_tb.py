

import numpy as np
import sys
import re
import pandas as pd
import matplotlib.pyplot as plt
from netCDF4 import Dataset
import datetime

sys.path.append('/home/nrisse/uniHome/WHK/eumetsat/scripts')

from path_setter import *
from importer import Sensitivity
from plot_brightness_temperature import PAMTRA_TB
from mwi_info import mwi


"""
Calculates difference Delta_TB between TB_MWI and TB_PAMTRA

Results are stored in a single netCDF file

TB_PAMTRA is calculated on three ways:
    - central frequency
    - frequency at bandwidth
    - frequency at center and bandwidth
The TB at these frequencies are averaged.

Based on the TB_PAMTRA calculation, Delta_TB is named

TB_MWI is calcuated based on the MWI spectral response function. There are two modifications
of this function included:
    - reduction of measurements (take only every i_th measurement)
    - noise perturbation (create n realizations of a certain random perturbation)
The resulting array of Delta_TB (one value per perturbed SRF) is then averaged and the std
is calculated. Only these two variables are then stored in netCDF file

In other scripts this file can be evaluated, looking at:
    - seasonal effects
    - effect of perturbation
    - effect of reduction of measurements
    - etc
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


def calculate_tb_pamtra(tb, avg_freq, profile):
    """
    Calculate TB from PAMTRA at frequencies for a specific profile
    
    tb:  pandas dataframe with TB of profile
    """
    
    tb_pam = tb.loc[tb['frequency [GHz]'].isin(avg_freq)][profile].mean()
    
    return tb_pam


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
    
    # read bandpass measurement
    sen_dsb = Sensitivity(path=path_sens, filename='MWI-RX183_DSB_Matlab.xlsx')

    # read pamtra simulations
    Pam = PAMTRA_TB()
    Pam.read_all()
    Pam.pam_data_df
    
    # combine spectral response function and modelled brightness temperature
    pam_srf = join_pam_on_srf(pam=Pam.pam_data_df, srf=sen_dsb.data_lino)
    
    # write data to arrays for calculation of vierual MWI TB
    profiles = np.array(pam_srf.columns[1:-5], dtype=str)
    tb = pam_srf.iloc[:, 1:-5]  
    srf = pam_srf.iloc[:, -5:]
    
    # noise levels added on the bandpass measurement
    noise_levels = np.arange(0, 0.11, 0.01)  # 0 to 10 % with step pf 1 %
    
    # reduction of number of measurements
    reduction_levels = np.arange(1, 6, 1)  # every, only every second, only every third, only every fourth, only ever fifth
    
    # dimensions
    n_channels = len(mwi.channels_str)
    n_profiles = len(profiles)
    n_noise_levels = len(noise_levels)
    n_reduction_levels = len(reduction_levels)
    
    # create six output datasets
    delta_tb_mean_freq_center = np.full(shape=(n_channels, n_profiles, n_noise_levels, n_reduction_levels), fill_value=-999, dtype=np.float)
    delta_tb_std_freq_center = np.full(shape=(n_channels, n_profiles, n_noise_levels, n_reduction_levels), fill_value=-999, dtype=np.float)
    delta_tb_mean_freq_bw = np.full(shape=(n_channels, n_profiles, n_noise_levels, n_reduction_levels), fill_value=-999, dtype=np.float)
    delta_tb_std_freq_bw = np.full(shape=(n_channels, n_profiles, n_noise_levels, n_reduction_levels), fill_value=-999, dtype=np.float)
    delta_tb_mean_freq_bw_center = np.full(shape=(n_channels, n_profiles, n_noise_levels, n_reduction_levels), fill_value=-999, dtype=np.float)
    delta_tb_std_freq_bw_center = np.full(shape=(n_channels, n_profiles, n_noise_levels, n_reduction_levels), fill_value=-999, dtype=np.float)
    
    for l, reduction_level in enumerate(reduction_levels):
        
        # reduce datasets tb calculated with pamtra and lino srf
        tb_red = tb.iloc[::reduction_level, :]
        srf_red = srf.iloc[::reduction_level, :]
        
        for k, noise_level in enumerate(noise_levels):
            
            # perturb srf dataset
            srf_red_per = create_noise_values(srf_red, std=noise_level, n=1000)
            
            for i, channel in enumerate(mwi.channels_str):
                
                print('Reduction level: {}'.format(reduction_level))
                print('Noise level: {}'.format(noise_level))
                print('Channel: {}'.format(channel))
                
                for j, profile in enumerate(profiles):
                
                    # calculate virtual MWI measurement (noise,)
                    tb_mwi = calculate_tb_mwi(tb=tb_red[profile].values,  # (freq,)
                                              srf=srf_red_per[:, :, i]    # (freq, noise,)
                                              )
                    
                    # freq_center
                    tb_pam = calculate_tb_pamtra(tb=Pam.pam_data_df, avg_freq=mwi.freq_center[i, :], profile=profile)  # (scalar)
                    delta_tb = tb_mwi - tb_pam   # (noise,)
                    delta_tb_mean_freq_center[i, j, k, l] = np.mean(delta_tb)  # (scalar)
                    delta_tb_std_freq_center[i, j, k, l] = np.std(delta_tb)  # (scalar)
                    
                    # freq_bw
                    tb_pam = calculate_tb_pamtra(tb=Pam.pam_data_df, avg_freq=mwi.freq_bw[i, :], profile=profile)  # (scalar)
                    delta_tb = tb_mwi - tb_pam   # (noise,)
                    delta_tb_mean_freq_bw[i, j, k, l] = np.mean(delta_tb)  # (scalar)
                    delta_tb_std_freq_bw[i, j, k, l] = np.std(delta_tb)  # (scalar)
                                        
                    # freq_bw_center
                    tb_pam = calculate_tb_pamtra(tb=Pam.pam_data_df, avg_freq=mwi.freq_bw_center[i, :], profile=profile)
                    delta_tb = tb_mwi - tb_pam   # (noise,)
                    delta_tb_mean_freq_bw_center[i, j, k, l] = np.mean(delta_tb)  # (scalar)
                    delta_tb_std_freq_bw_center[i, j, k, l] = np.std(delta_tb)  # (scalar)
    
    # create nc file
    file = path_data + 'delta_tb/delta_tb.nc'
    with Dataset(file, 'w', format='NETCDF4') as rootgrp:
    
        # global attributes
        rootgrp.author = "Nils Risse"
        rootgrp.history = "created: {}".format(datetime.datetime.now().date().strftime('%Y-%m-%d'))
        
        # create dimension
        rootgrp.createDimension(dimname='channel', size=n_channels)  # 5
        rootgrp.createDimension(dimname='profile', size=n_profiles)   # number of dropsonde profiles
        rootgrp.createDimension(dimname='noise_level', size=n_noise_levels)  # number of noise std
        rootgrp.createDimension(dimname='reduction_level', size=n_reduction_levels)
        
        # write channel
        var_channel = rootgrp.createVariable(varname='channel', datatype=np.str, dimensions=('channel',))
        var_channel.comment = 'MWI channel number'
        var_channel[:] = mwi.channels_str
        
        # write profile
        var_profile = rootgrp.createVariable(varname='profile', datatype=np.str, dimensions=('profile',))
        var_profile.comment = 'Radiosonde profile ID'
        var_profile[:] = profiles
        
        # write noise_level
        var_noise_level = rootgrp.createVariable(varname='noise_level', datatype=np.float, dimensions=('noise_level',))
        var_noise_level.comment = 'Standard deviation of perturbation'
        var_noise_level[:] = noise_levels
        
        # write reduction_level
        var_reduction_level = rootgrp.createVariable(varname='reduction_level', datatype=np.int, dimensions=('reduction_level',))
        var_reduction_level.comment = 'Reduction of number of measurement (3 --> every third measurement)'
        var_reduction_level[:] = reduction_levels
        
        # write results
        # write mean freq_center
        var_delta_tb_mean_freq_center = rootgrp.createVariable(varname='delta_tb_mean_freq_center', datatype=np.float, dimensions=('channel', 'profile', 'noise_level', 'reduction_level'))
        var_delta_tb_mean_freq_center.comment = 'Calculation: delta_tb = tb_mwi - tb_pamtra. If no perturbation, this value is equal to the actual value.'
        var_delta_tb_mean_freq_center.unit = 'K'
        var_delta_tb_mean_freq_center.statistics = 'Arithemtic mean'
        var_delta_tb_mean_freq_center[:] = delta_tb_mean_freq_center
        
        # write standard deviation freq_center
        var_delta_tb_std_freq_center = rootgrp.createVariable(varname='delta_tb_std_freq_center', datatype=np.float, dimensions=('channel', 'profile', 'noise_level', 'reduction_level'))
        var_delta_tb_std_freq_center.comment = 'Calculation: delta_tb = tb_mwi - tb_pamtra. If no perturbation, this value is equal to the actual value.'
        var_delta_tb_std_freq_center.unit = 'K'
        var_delta_tb_std_freq_center.statistics = 'Standard deviation'
        var_delta_tb_std_freq_center[:] = delta_tb_std_freq_center
        
        # write mean freq_bw
        var_delta_tb_mean_freq_bw = rootgrp.createVariable(varname='delta_tb_mean_freq_bw', datatype=np.float, dimensions=('channel', 'profile', 'noise_level', 'reduction_level'))
        var_delta_tb_mean_freq_bw.comment = 'Calculation: delta_tb = tb_mwi - tb_pamtra. If no perturbation, this value is equal to the actual value.'
        var_delta_tb_mean_freq_bw.unit = 'K'
        var_delta_tb_mean_freq_bw.statistics = 'Arithemtic mean'
        var_delta_tb_mean_freq_bw[:] = delta_tb_mean_freq_bw
        
        # write standard deviation freq_bw
        var_delta_tb_std_freq_bw = rootgrp.createVariable(varname='delta_tb_std_freq_bw', datatype=np.float, dimensions=('channel', 'profile', 'noise_level', 'reduction_level'))
        var_delta_tb_std_freq_bw.comment = 'Calculation: delta_tb = tb_mwi - tb_pamtra. If no perturbation, this value is equal to the actual value.'
        var_delta_tb_std_freq_bw.unit = 'K'
        var_delta_tb_std_freq_bw.statistics = 'Standard deviation'
        var_delta_tb_std_freq_bw[:] = delta_tb_std_freq_bw
        
        # write mean freq_bw_center
        var_delta_tb_mean_freq_bw_center = rootgrp.createVariable(varname='delta_tb_mean_freq_bw_center', datatype=np.float, dimensions=('channel', 'profile', 'noise_level', 'reduction_level'))
        var_delta_tb_mean_freq_bw_center.comment = 'Calculation: delta_tb = tb_mwi - tb_pamtra. If no perturbation, this value is equal to the actual value.'
        var_delta_tb_mean_freq_bw_center.unit = 'K'
        var_delta_tb_mean_freq_bw_center.statistics = 'Arithemtic mean'
        var_delta_tb_mean_freq_bw_center[:] = delta_tb_mean_freq_bw_center
        
        # write standard deviation freq_bw_center
        var_delta_tb_std_freq_bw_center = rootgrp.createVariable(varname='delta_tb_std_freq_bw_center', datatype=np.float, dimensions=('channel', 'profile', 'noise_level', 'reduction_level'))
        var_delta_tb_std_freq_bw_center.comment = 'Calculation: delta_tb = tb_mwi - tb_pamtra. If no perturbation, this value is equal to the actual value.'
        var_delta_tb_std_freq_bw_center.unit = 'K'
        var_delta_tb_std_freq_bw_center.statistics = 'Standard deviation'
        var_delta_tb_std_freq_bw_center[:] = delta_tb_std_freq_bw_center
