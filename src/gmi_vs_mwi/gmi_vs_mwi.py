"""
Comparison between the effect of neglecting SRF for GMI and MWI. Most parts are
taken from tb_mwi_calculation.py, which is not working for different sensors
yet.

Two channels can be directly compared:
    MWI channel 14 and GMI channel 13 (+/- 7 GHz) 
    MWI channel 17 and GMI channel 12 (+/- 3.4 and 3.0 GHz)
Bandwidths are the same (based on WMO OSCAR database)
"""


import numpy as np
import xarray as xr
import os
import matplotlib.pyplot as plt
from dotenv import load_dotenv

load_dotenv()
plt.ion()


def read_gmi(channel):
    """
    Read spectral response file of a GMI channel
    """
    
    file = os.path.join(
        os.environ['PATH_SRF'],
        f'rtcoef_gpm_1_gmi_srf_srf_ch{str(channel)}.txt')
    
    data = np.loadtxt(file, skiprows=4)

    # create dataset
    ds = xr.Dataset()
    ds.coords['frequency'] = np.round(data[:, 0]*29.9792458*1e3).astype('int')
    ds.coords['channel'] = np.array([int(channel)])
    ds['srf_orig'] = (('frequency', 'channel'), 
                      data[:, 1][:, np.newaxis]/data[:, 1].sum())
    
    return ds


if __name__ == '__main__':
    
    # read SRF data from GMI    
    ds1 = read_gmi(12)
    ds2 = read_gmi(13)
    ds_srf = xr.merge([ds1, ds2])
    
    # read forward simulation
    ds_pam = xr.open_dataset(
        os.path.join(os.environ['PATH_BRT'], 'TB_radiosondes_2019.nc'))
    ds_pam.coords['frequency'] = (ds_pam.frequency*1e3).astype('int')
    
    # read results for mwi
    ds_com_rsd_mwi = xr.open_dataset(
        os.path.join(os.environ['PATH_BRT'], 
                     'TB_radiosondes_2019_MWI.nc'))
    
    #%% match srf with radiative transfer simulations
    # interpolate tb spectrally
    ds_com = ds_pam['tb'].interp({'frequency': ds_srf.frequency})
    ds_com = xr.merge([ds_com, ds_srf])
    
    #%% define top-hat functions
    # gmi channel specifications
    bw = np.array([2000, 2000])
    offset = np.array([3000, 7000])
    center = np.array([183310, 183310])
    
    ds_com['srf_est'] = xr.zeros_like(ds_com['srf_orig'])
    
    for i, channel in enumerate(ds_com.channel.values):
        
        ix = ((center[i]-offset[i]-bw[i]/2 < ds_com.frequency) & \
             (center[i]-offset[i]+bw[i]/2 > ds_com.frequency)) | \
             ((center[i]+offset[i]-bw[i]/2 < ds_com.frequency) & \
             (center[i]+offset[i]+bw[i]/2 > ds_com.frequency))
        
        ds_com['srf_est'][ix, i] = 1
    
    ds_com['srf_est'] = ds_com['srf_est']/ds_com['srf_est'].sum('frequency')
    
    #%% plot srf measurement and top-hat
    fig, ax = plt.subplots(1, 1)
    
    for channel in ds_com.channel.values:
        
        ax.scatter(ds_com.frequency, 
                   ds_com.srf_orig.sel(channel=channel),
                   label=channel)
        
        ax.plot(ds_com.frequency, 
                ds_com.srf_est.sel(channel=channel))
    
    ax.legend()
    
    #%% calculate mwi tb
    # get relevant variable names
    srf_vars = [x for x in list(ds_com) if ('srf' in x) and ('dB' not in x)]
    tb_gmi_vars = [s.replace('srf', 'tb_gmi') for s in srf_vars]
    
    # normalize all srf
    ds_com[srf_vars] = ds_com[srf_vars]/ds_com[srf_vars].sum('frequency')
    
    # calculate mwi tb
    ds_com[tb_gmi_vars] = (ds_com[srf_vars] * \
                           ds_com['tb'].isel(angle=9)).sum('frequency')
    
    # calculate difference between original srf and other srfs
    ds_com['dtb_gmi_est'] = (ds_com['tb_gmi_orig'] - \
                                   ds_com['tb_gmi_est'])
    
    #%% compare gmi bias with mwi bias
    ds_com.dtb_gmi_est.mean('profile')
    
    ds_com_rsd_mwi.dtb_mwi_est.sel(
        est_type='top-hat', channel=[17, 14]).mean('profile')
    