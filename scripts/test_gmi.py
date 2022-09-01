"""
Bandpass effect for GMI sensor

Parts are taken from tb_mwi_calculation.py which es specifically for MWI

Comparison with MWI:
    MWI channel 14 and GMI channel 13 (+/- 7 GHz) --> 0.06 K vs. 0.17 K
    MWI channel 17 and GMI channel 12 (+/- 3.4 and 3.0 GHz) --> 0.17 K vs. 0.2 K

Bandwidth is same! Specified bandwidth on WMO oscar for GMI channel 12 is more
1500 MHz than 2000 MHz based on the SRF!

Comparison shows that MWI channel is more accurate (maybe).

Unfortunately, the bias calculated for GMI is not matching with the RTTOV 
report, especially for channel 13 where the RTTOV gives an order of magnitude
less. At this point, I would question the report! BUT: It could be also related
to the selection of the "divers" profiles as mentioned in the report.
"""


import numpy as np
import xarray as xr
import os
import matplotlib.pyplot as plt
import sys
sys.path.append(f'{os.environ["PATH_PHD"]}/projects/mwi_bandpass_effects/'+
                'scripts')
from path_setter import path_data

plt.ion()


def read_gmi(channel):
    """
    Read spectral response file of a GMI channel
    """
    
    file = path_data+'/sensitivity/rtcoef_gpm_1_gmi_srf_srf/rtcoef_gpm_1_gmi'+\
        f'_srf_srf_ch{str(channel)}.txt'
    
    data = np.loadtxt(file, skiprows=4)

    # create dataset
    ds = xr.Dataset()
    ds.coords['frequency'] = np.round(data[:, 0] * 29.9792458 * 1e3).astype('int')
    ds.coords['channel'] = np.array([int(channel)])
    ds['srf_orig'] = (('frequency', 'channel'), data[:, 1][:, np.newaxis]/data[:, 1].sum())
    
    return ds


if __name__ == '__main__':
    
    # read SRF data from GMI    
    ds1 = read_gmi(12)
    ds2 = read_gmi(13)
    
    ds = xr.merge([ds1, ds2])
    
    #%% define top-hat functions
    bw = np.array([2000, 2000])
    bw = np.array([1500, 2000])
    offset = np.array([3000, 7000])
    center = np.array([183310, 183310])
    
    ds['srf_est'] = xr.zeros_like(ds['srf_orig'])
    
    for i, channel in enumerate(ds.channel.values):
        
        ix = ((center[i]-offset[i]-bw[i]/2 < ds.frequency) & \
             (center[i]-offset[i]+bw[i]/2 > ds.frequency)) | \
             ((center[i]+offset[i]-bw[i]/2 < ds.frequency) & \
             (center[i]+offset[i]+bw[i]/2 > ds.frequency))
        
        ds['srf_est'][ix, i] = 1
        
    ds['srf_est'] = ds['srf_est']/ds['srf_est'].sum('frequency')
    
    #%% plot srf measurement
    fig, ax = plt.subplots(1, 1, )
    
    for channel in ds.channel.values:
        
        ax.scatter(ds.frequency, ds.srf_orig.sel(channel=channel),
                   label=channel)
        ax.plot(ds.frequency, ds.srf_est.sel(channel=channel))
    
    ax.legend()
    
    #%% read radiative transfer simulations
    file_tb = 'TB_radiosondes_2019'
    ds_pam = xr.open_dataset(path_data+'brightness_temperature/'+file_tb+'.nc')
    ds_pam.coords['frequency'] = (ds_pam.frequency*1e3).astype('int')
    
    #%% match srf with radiative transfer simulations
    # interpolate tb spectrally
    ds_com = ds_pam['tb'].interp({'frequency': ds.frequency})
    ds_com = xr.merge([ds_com, ds])
    
    #%% calculate mwi tb
    srf_vars = [x for x in list(ds_com) if ('srf' in x) and ('dB' not in x)]
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
        
    #%%
    # compare bias of the two channels with the saunders report
    np.abs(ds_com.dtb_mwi_est).mean('profile')
    
    #%% compare with MWI channels
    ds_com_rsd = xr.open_dataset(
        path_data+'brightness_temperature/TB_radiosondes_2019_MWI.nc')
    
    np.abs(ds_com_rsd.dtb_mwi_est).sel(est_type='top-hat').mean('profile')
    