"""
Comparison of MWI observation calculated with different SRF.

The MWI estimations are also treated as SRF, but with values only at the
few specified frequencies. This makes the code much shorter.

Implemented SRF:
    - original
    - top-hat
    - center
    - cutoff
    - cutoff+center
"""


import xarray as xr
import numpy as np
import pandas as pd
import os
from datetime import datetime
from helpers import Sensitivity, mwi, wyo
from dotenv import load_dotenv

load_dotenv()


if __name__ == '__main__':
    
    # input file of simulated brightness temperatures
    file_tb = 'TB_radiosondes_2019'
    #file_tb = 'TB_era5_hyd'
    #file_tb = 'TB_era5'
    
    # read pamtra simulation
    ds_pam = xr.open_dataset(os.path.join(
        os.environ['PATH_BRT'], file_tb+'.nc'))
    ds_pam.coords['frequency'] = (ds_pam.frequency*1e3).astype('int')
    
    # new dataset to combine with srfs
    ds_com = ds_pam.copy(deep=True)
    
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
    # original measured SRF
    srf = Sensitivity(filename='MWI-RX183_DSB_Matlab.xlsx')
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
    
    # systematic perturbation of srf
    # (type, magnitude, frequency=srf_orig_frequency)
    # perturbed = raw + residual
    err_types = ['linear1', 'linear2', 
                  'imbalance1', 'imbalance2', 
                  'sine1', 'sine2']
    offset_magnitude = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.7, 1.0, 1.5, 2.0])
    
    ds_srf_err = xr.Dataset()
    ds_srf_err.coords['frequency'] = srf.data.frequency.values
    ds_srf_err.coords['channel'] = srf.data.channel.values
    ds_srf_err.coords['magnitude'] = offset_magnitude
    ds_srf_err.coords['err_type'] = err_types
    ds_srf_err['srf_err_offset_dB'] = (
        list(ds_srf_err.dims.keys()), 
        np.zeros(shape=list(ds_srf_err.dims.values())))

    # fill perturbations
    for i, channel in enumerate(mwi.channels_str):
        for j, magn in enumerate(offset_magnitude):
            
            # bandwidth frequencies in MHz
            f0, f1, f2, f3 = (np.round(mwi.freq_bw[i], 3)*1000).astype('int')
            left_ix = np.where((ds_srf_err.frequency.values > f0) & 
                               (ds_srf_err.frequency.values < f1))[0]
            right_ix = np.where((ds_srf_err.frequency.values > f2) & 
                                (ds_srf_err.frequency.values < f3))[0]
            
            y = [1, -1]
            
            for k, ix in enumerate([left_ix, right_ix]):
                
                # linear slope
                ds_srf_err.srf_err_offset_dB[ix, i, j, 0] = \
                    np.linspace(-magn, magn, len(ix)) * y[k]
                ds_srf_err.srf_err_offset_dB[ix, i, j, 1] = \
                    np.linspace(magn, -magn, len(ix)) * y[k]
                
                # imbalance
                if k == 0: # left
                    ds_srf_err.srf_err_offset_dB[ix, i, j, 2] = magn
                if k == 1:  # right
                    ds_srf_err.srf_err_offset_dB[ix, i, j, 3] = magn
    
                # define new ripples using sine curve
                ds_srf_err.srf_err_offset_dB[ix, i, j, 4] = \
                    -magn*np.sin(np.linspace(0, 2*np.pi, len(ix))) * y[k]
                ds_srf_err.srf_err_offset_dB[ix, i, j, 5] = \
                    magn*np.sin(np.linspace(0, 2*np.pi, len(ix))) * y[k]
    
    # apply perturbations on raw srf data
    ds_srf_err['srf_err_dB'] = srf.data['raw'] + ds_srf_err['srf_err_offset_dB']
    ds_srf_err['srf_err'] = 10**(0.1*ds_srf_err['srf_err_dB'])
    ds_com['srf_err_offset_dB'] = ds_srf_err['srf_err_offset_dB']
    ds_com['srf_err_dB'] = ds_srf_err['srf_err_dB']
    ds_com['srf_err'] = ds_srf_err['srf_err']
    
    # create idealized srf
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
    srf_top_hat = xr.zeros_like(ds_com['srf_orig'])
    f = srf_top_hat.frequency
    for i, (a, b, c, d) in enumerate(mwi.freq_bw_MHz):
        srf_top_hat[(f > a) & (f < b), i] = 1
        srf_top_hat[(f > c) & (f < d), i] = 1
    
    # top-hat should be nan, if srf is nan to keep the spacing of 15 MHz in
    # the top-hat srf.
    srf_top_hat = srf_top_hat.where(~np.isnan(ds_com['srf_orig']))
        
    # merge the srfs
    ds_com['srf_est'] = xr.concat([
        srf_0, srf_1, srf_2, srf_top_hat
        ], dim=pd.Index(['freq_center', 'freq_bw', 'freq_bw_center',
                         'top-hat'
                         ], name='est_type'))
    
    #%% calculations
    # get relevant variable names
    srf_vars = [x for x in list(ds_com) if ('srf' in x) and ('dB' not in x)]
    tb_mwi_vars = [s.replace('srf', 'tb_mwi') for s in srf_vars]
    tb_mwi_vars_no_orig = [s for s in tb_mwi_vars if s != 'tb_mwi_orig']
    dtb_mwi_vars_no_orig = ['d'+s for s in tb_mwi_vars_no_orig]
    
    # normalize all srf
    ds_com[srf_vars] = ds_com[srf_vars]/ds_com[srf_vars].sum('frequency')
    
    # calculate mwi tb
    ds_com[tb_mwi_vars] = (ds_com[srf_vars] * \
                           ds_com['tb'].isel(angle=9)).sum('frequency')
    
    # calculate difference between original srf and other srfs
    ds_com[dtb_mwi_vars_no_orig] = ds_com['tb_mwi_orig'] - \
                                   ds_com[tb_mwi_vars_no_orig]
    
    #%% write result to file
    ds_com.to_netcdf(os.path.join(
        os.environ['PATH_BRT'], file_tb+'_MWI.nc'))
