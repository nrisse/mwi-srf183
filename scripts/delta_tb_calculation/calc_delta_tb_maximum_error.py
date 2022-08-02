"""
The output of the script is not used later. Only the calculation under original
SRF. Also this script is not working, because the loop over the perturbation
magnitude is missing!
"""


import numpy as np
import matplotlib.pyplot as plt
from netCDF4 import Dataset
import datetime
import xarray as xr
import os
import sys
sys.path.append(f'{os.environ["PATH_PHD"]}/projects/mwi_bandpass_effects/scripts')
from path_setter import path_data
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
    
    #%% read data
    # perturbations and original data (lino)
    ds_per_lino = xr.load_dataset(path_data+'sensitivity/perturbed/MWI-RX183_DSB_Matlab_perturb.nc')
    
    # read pamtra simulations
    ds_tb = xr.load_dataset(path_data + 'brightness_temperature/TB_radiosondes_2019.nc').isel(angle=9)
    ds_tb = ds_tb.assign_coords(frequency=(np.round(ds_tb.frequency.values, 3)*1000).astype('int'))

    #%% calculate tb differences as a function of
    # channel, profile, perturbation_type, perturbation_magnitude, 
    # and calculation_method
    ds_dtb = xr.Dataset()
    
    # dimensions
    ds_dtb.coords['channel'] = mwi.channels_str
    ds_dtb.coords['profile'] = ds_tb.profile.values
    ds_dtb.coords['perturbation'] = list(ds_per_lino)
    ds_dtb.coords['magnitude'] = ds_per_lino.magnitude.values
    ds_dtb.coords['calc_method'] = np.array(['freq_center', 'freq_bw', 'freq_bw_center'])
    
    # dimension attributes
    ds_dtb.coords['channel'].attrs = dict(comment='MWI channel number')
    ds_dtb.coords['profile'].attrs = dict(comment='Radiosonde profile ID or ID of ERA5 simulation')
    ds_dtb.coords['perturbation'].attrs = dict(comment='Perturbation name')
    ds_dtb.coords['magnitude'].attrs = dict(comment='Perturbation magnitude')
    ds_dtb.coords['calc_method'].attrs = dict(comment='Calculation method')
    
    # global attributes
    ds_dtb.attrs = dict(
        author='Nils Risse',
        history=f'created: {datetime.datetime.now().strftime("%Y-%m-%d")}'
        )
        
    # calculate difference
    dim_key, dim_val = np.array(list(ds_dtb.dims.items())).T
    ds_dtb['data'] = (dim_key, np.full(dim_val.astype('int'), fill_value=-999))
    ds_dtb['data'].attrs = dict(comment='Calculation: delta_tb = tb_mwi - tb_pamtra', 
                                units='K')
        
    for i, channel in enumerate(ds_dtb.channel.values):
        
        for j, pert_name in enumerate(ds_dtb.perturbation.values):
            
                for k, magn in enumerate(ds_dtb.magnitude.values):
                    
                    print('Perturbation name: {}'.format(pert_name))
                    print('Channel: {}'.format(channel))
                                    
                    # calculate virtual MWI measurement
                    if pert_name == 'orig':
                        kwd = dict()
                    else:
                        kwd = dict(magnitude=magn)
                        
                    tb_mwi = calculate_tb_mwi(
                        tb=ds_tb.tb.sel(frequency=ds_per_lino.frequency),
                        srf=ds_per_lino[pert_name].sel(channel=int(channel),
                                                       **kwd)
                        )
                    
                    # freq_center
                    tb_pam = ds_tb.tb.sel(
                        frequency=mwi.freq_center_MHz[i, :]).mean('frequency').values
                    ds_dtb['data'][i, :, j, k, 0] = tb_mwi - tb_pam
                    
                    # freq_bw
                    tb_pam = ds_tb.tb.sel(
                        frequency=mwi.freq_bw_MHz[i, :]).mean('frequency').values
                    ds_dtb['data'][i, :, j, k, 1] = tb_mwi - tb_pam
                    
                    # freq_bw_center
                    tb_pam = ds_tb.tb.sel(
                        frequency=mwi.freq_bw_center_MHz[i, :]).mean('frequency').values
                    ds_dtb['data'][i, :, j, k, 2] = tb_mwi - tb_pam
    
    #%% write output file
    file_out = path_data + 'delta_tb/delta_tb_maximum_error.nc'
    ds_dtb.to_netcdf(file_out)

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
