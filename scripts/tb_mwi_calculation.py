"""
Comparisong MWI observation calculated with different SRF.

The MWI estimations are also treated as SRF, but with values only at the
few specified frequencies. This makes the code much shorter and easier
to understand.

Advantage: TB values are retained

Future interesting thing:
    - create dimension i_srf which counts the many different versions of MWI
      SRF from real measured, reduced, perturbed, estimate at few frequencies,
      etc. making calculation and evaluation very easy and obvious.

Implemented SRF:
    - original
    - tophat
    - freq center
    - freq bw
    - freq bw center
"""


import xarray as xr
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime
import sys
sys.path.append(f'{os.environ["PATH_PHD"]}/projects/mwi_bandpass_effects/'+
                'scripts')
from importer import Sensitivity
from mwi_info import mwi
from radiosonde import wyo

plt.ion()


if __name__ == '__main__':
    
    # input file of simulated brightness temperatures
    file_tb = 'TB_radiosondes_2019'
    #file_tb = 'TB_era5_hyd'
    #file_tb = 'TB_era5'
    
    # read pamtra simulation of radiosondes
    ds_pam = xr.open_dataset(os.environ['PATH_PHD']+'/projects/mwi_bandpass'+
                             '_effects/data/brightness_temperature/'+file_tb+
                             '.nc')
    ds_pam.coords['frequency'] = (ds_pam.frequency*1e3).astype('int')
    
    # new dataset to combine with srfs
    ds_com = ds_pam.copy(deep=True)
    
    # read srf data
    srf = Sensitivity(filename='MWI-RX183_DSB_Matlab.xlsx')
    
    # read srf with systematic perturbations
    srf_pert = xr.open_dataset(os.environ['PATH_PHD']+'/projects/mwi_bandpass'+
                               '_effects/data/sensitivity/perturbed/'+
                               'MWI-RX183_DSB_Matlab_perturb.nc')
    
    #%% clean profile id
    # add array for radiosonde name based on the profile id
    if file_tb == 'TB_radiosondes_2019':
        ds_com['station'] = (('profile'), 
                             np.array([wyo.id_station[p.split('_')[1]] 
                                       for p in ds_com.profile.values]))
        
        # add array for sounding launch time based on profile id
        ds_com['time'] = (('profile'), 
                             np.array([datetime.strptime(p.split('_')[2], 
                                                         '%Y%m%d%H%M%S')
                                       for p in ds_com.profile.values]))
    
    #%% create different SRF's used to calculate MWI observation/estimates
    # make another script which creates different SRF and writes them all to 
    # a netcdf file!
    # dimension: (frequency, channel, i_srf)
    # original measured SRF
    ds_com['srf_orig'] = srf.data.lino
    
    # data reduction of srf
    lst_da_red = []
    red_levs = np.arange(2, 12)
    for red_lev in red_levs:
        lst_da_red.append(srf.data.lino.sel(
            frequency=srf.data.lino.frequency[::red_lev]))
    da_red = xr.concat(lst_da_red, dim=pd.Index(red_levs, 
                                                name='reduction_level'))
    ds_com['srf_red'] = da_red/da_red.sum('frequency')
        
    # systematic srf errors (types, magnitudes, reduction levels, ...)
    ds_com['srf_err'] = xr.concat([
        srf_pert['linear1'], srf_pert['linear2'], srf_pert['imbalance1'], 
        srf_pert['imbalance2'], srf_pert['ripple1'], srf_pert['ripple2']],
        dim=pd.Index(['linear1', 'linear2', 'imbalance1', 'imbalance2',
                      'ripple1', 'ripple2'], name='err_type'))
    
    # create idealized srf for the modelled mwi observation from mwi_info
    # everywhere nan, except for the specified frequencies
    srf_0 = xr.concat(
        [xr.DataArray(data=np.ones(len(mwi.freq_center_MHz[i, :])),
                      dims=['frequency'],
                      coords=dict(frequency=mwi.freq_center_MHz[i, :]))
         for i in range(5)
         ],
        dim=ds_com.channel
        )

    srf_1 = xr.concat(
        [xr.DataArray(data=np.ones(len(mwi.freq_bw_MHz[i, :])),
                      dims=['frequency'],
                      coords=dict(frequency=mwi.freq_bw_MHz[i, :]))
         for i in range(5)
         ],
        dim=ds_com.channel
        )
    
    srf_2 = xr.concat(
        [xr.DataArray(data=np.ones(len(mwi.freq_bw_center_MHz[i, :])),
                      dims=['frequency'],
                      coords=dict(frequency=mwi.freq_bw_center_MHz[i, :]))
         for i in range(5)
         ],
        dim=ds_com.channel
        )
    
    # top hat function (defined at same frequencies as original SRF)
    srf_tophat = xr.zeros_like(ds_com['srf_orig'])
    for i, (a, b, c, d) in enumerate(mwi.freq_bw_MHz):
        f = srf_tophat.frequency
        srf_tophat[(f > a) & (f < b), i] = 1
        srf_tophat[(f > c) & (f < d), i] = 1
    
    # merge the srfs
    ds_com['srf_est'] = xr.concat([
        srf_0, srf_1, srf_2, srf_tophat
        ], dim=pd.Index(['freq_center', 'freq_bw', 'freq_bw_center',
                         'tophat'
                         ], name='est_type'))
    
    #%% normalize all srf
    for srf_name in [ 'srf_orig', 'srf_red', 'srf_err', 'srf_est']:
        ds_com[srf_name] = ds_com[srf_name]/ds_com[srf_name].sum('frequency')
    
    #%% calculate mwi tb
    srf_vars = [x for x in list(ds_com) if 'srf' in x]
    for srf_var in srf_vars:
        tb_mwi_var = srf_var.replace('srf', 'tb_mwi')
        ds_com[tb_mwi_var] = (ds_com[srf_var] * 
                              ds_com['tb'].isel(angle=9)).sum('frequency')
    
    #%% calculate difference between original srf and other srfs
    tb_mwi_vars = [x for x in list(ds_com) 
                   if 'tb_mwi' in x and 'orig' not in x]
    for tb_mwi_var in tb_mwi_vars:
        dtb_mwi_var = tb_mwi_var.replace('tb_mwi', 'dtb_mwi')
        ds_com[dtb_mwi_var] = ds_com['tb_mwi_orig'] - ds_com[tb_mwi_var]
        
    #%% write result to file
    ds_com.to_netcdf(os.environ['PATH_PHD']+'/projects/mwi_bandpass_effects/'+
                     'data/brightness_temperature/'+file_tb+'_MWI.nc')
    
    #%%
    plt.close('all')
        