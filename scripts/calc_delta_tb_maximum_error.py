

import numpy as np
import re
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
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


if __name__ == '__main__':
    
    # get perturbations and original data (lino)
    pert_names = ['linear1', 'linear2', 'inbalance1', 'inbalance2', 'ripple1', 'ripple2', 'orig']
    ds_per_lino = xr.load_dataset(path_data+'sensitivity/perturbed/MWI-RX183_DSB_Matlab_perturb.nc')
    
    # read pamtra simulations
    file = path_data + 'brightness_temperature/TB_radiosondes_2019.nc'
    ds_tb = xr.load_dataset(file).isel(angle=9)
    ds_tb = ds_tb.assign_coords(frequency=(np.round(ds_tb.frequency.values, 3)*1000).astype(np.int))
    
    #%% plot perturbed SRF together with brightness temperatures
    # not important!
    fig, ax1 = plt.subplots(1, 1, figsize=(5, 5), constrained_layout=True)

    ds_tb_mean = ds_tb.tb.mean('profile')
    ds_tb_std = ds_tb.tb.std('profile')
    ax1.plot(ds_tb_mean.frequency*1e-3, ds_tb_mean, color='k')
    ax1.fill_between(x=ds_tb_mean.frequency*1e-3, y1=ds_tb_mean, y2=ds_tb_mean+ds_tb_std, alpha=0.5, color='k')
    ax1.fill_between(x=ds_tb_mean.frequency*1e-3, y1=ds_tb_mean, y2=ds_tb_mean-ds_tb_std, alpha=0.5, color='k')

    ax1.set_ylim([264, 266])
    
    tb1 = np.dot(ds_per_lino.linear1.sel(channel=14, magnitude=2), ds_tb.tb.sel(profile='ID_01004_201902011200', frequency=ds_per_lino.frequency))
    tb2 = np.dot(ds_per_lino.linear1.sel(channel=14, magnitude=0.1), ds_tb.tb.sel(profile='ID_01004_201902011200', frequency=ds_per_lino.frequency))

    #%% 
    calc_methods = np.array(['freq_center', 'freq_bw', 'freq_bw_center'])
    
    # dimensions
    n_channels = len(mwi.channels_str)
    n_profiles = len(ds_tb.profile.values)
    n_perturbations = len(pert_names)
    n_calc_methods = len(calc_methods)
    
    # create output datasets
    delta_tb = np.full(shape=(n_channels, n_profiles, n_perturbations, n_calc_methods), fill_value=-999., dtype=np.float)
    
    for j, pert_name in enumerate(pert_names):
                
        for i, channel in enumerate(mwi.channels_int):
            
            print('Perturbation name: {}'.format(pert_name))
            print('Channel: {}'.format(channel))
                            
            # calculate virtual MWI measurement
            tb_mwi = calculate_tb_mwi(tb=ds_tb.tb.sel(frequency=ds_per_lino.frequency),
                                      srf=ds_per_lino[pert_name].sel(channel=channel)
                                      )
            
            # freq_center
            tb_pam = ds_tb.tb.sel(frequency=mwi.freq_center_MHz[i, :]).mean('frequency').values
            delta_tb[i, :, j, 0] = tb_mwi - tb_pam
            
            # freq_bw
            tb_pam = ds_tb.tb.sel(frequency=mwi.freq_bw_MHz[i, :]).mean('frequency').values
            delta_tb[i, :, j, 1] = tb_mwi - tb_pam
            
            # freq_bw_center
            tb_pam = ds_tb.tb.sel(frequency=mwi.freq_bw_center_MHz[i, :]).mean('frequency').values
            delta_tb[i, :, j, 2] = tb_mwi - tb_pam
    
    # create nc file
    file = path_data + 'delta_tb/delta_tb_maximum_error.nc'
    with Dataset(file, 'w', format='NETCDF4') as rootgrp:
    
        # global attributes
        rootgrp.author = "Nils Risse"
        rootgrp.history = "created: {}".format(datetime.datetime.now().date().strftime('%Y-%m-%d'))
        
        # create dimension
        rootgrp.createDimension(dimname='channel', size=n_channels)  # 5
        rootgrp.createDimension(dimname='profile', size=n_profiles)   # number of dropsonde profiles
        rootgrp.createDimension(dimname='perturbation', size=n_perturbations)  # number of perturbations
        rootgrp.createDimension(dimname='calc_method', size=n_calc_methods)
        
        # write channel
        var_channel = rootgrp.createVariable(varname='channel', datatype=np.str, dimensions=('channel',))
        var_channel.comment = 'MWI channel number'
        var_channel[:] = mwi.channels_str
        
        # write profile
        var_profile = rootgrp.createVariable(varname='profile', datatype=np.str, dimensions=('profile',))
        var_profile.comment = 'Radiosonde profile ID or ID of ERA5 simulation'
        var_profile[:] = ds_tb.profile.values
        
        # write perturbation
        var_perturbation = rootgrp.createVariable(varname='perturbation', datatype=np.str, dimensions=('perturbation',))
        var_perturbation.comment = 'Perturbation name'
        var_perturbation[:] = np.array(pert_names)
        
        # write reduction_level
        var_reduction_level = rootgrp.createVariable(varname='calc_method', datatype=np.str, dimensions=('calc_method',))
        var_reduction_level.comment = 'Calculation method)'
        var_reduction_level[:] = calc_methods
        
        # write results
        var_delta_tb = rootgrp.createVariable(varname='data', datatype=np.float, dimensions=('channel', 'profile', 'perturbation', 'calc_method'))
        var_delta_tb.comment = 'Calculation: delta_tb = tb_mwi - tb_pamtra'
        var_delta_tb.unit = 'K'
        var_delta_tb[:] = delta_tb
