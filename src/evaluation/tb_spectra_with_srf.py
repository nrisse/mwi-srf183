"""
Detailed visualization for a specific channel and atmospheric profile. The
spectral TB variation is shown together with SRF's. The TB MWI is indicated in
the spectral TB variation.
"""

import matplotlib.pyplot as plt
import xarray as xr
import os
from helpers import mwi
from dotenv import load_dotenv

load_dotenv()
plt.ion()


if __name__ == '__main__':
    
    # read data
    ds_com_rsd = xr.open_dataset(
        os.path.join(os.environ['PATH_BRT'],
                     'TB_radiosondes_2019_MWI.nc'))
    ds_com_rsd['tb'] = ds_com_rsd.tb.transpose('frequency', 'profile', 'angle')
    
    ds_com_era = xr.open_dataset(
        os.path.join(os.environ['PATH_BRT'],
                     'TB_era5_MWI.nc'))
    ds_com_era = ds_com_era.stack({'profile': ('grid_x', 'grid_y')})
    
    ds_com_erh = xr.open_dataset(
        os.path.join(os.environ['PATH_BRT'],
                     'TB_era5_hyd_MWI.nc'))
    ds_com_erh = ds_com_erh.stack({'profile': ('grid_x', 'grid_y')})
    
    #%% calculate cumulative TB mwi for top-hat and for orig srf
    # radiosondes
    ds_com_rsd['tb_mwi_cum_orig'] = (ds_com_rsd.srf_orig * ds_com_rsd['tb'].
                                     isel(angle=9)).cumsum('frequency')
    
    ds_com_rsd['tb_mwi_cum_est'] = (ds_com_rsd.srf_est * ds_com_rsd['tb'].
                                    isel(angle=9)).cumsum('frequency')
    
    # era5
    ds_com_era['tb_mwi_cum_orig'] = (ds_com_era.srf_orig * ds_com_era['tb'].
                                     isel(angle=9)).cumsum('frequency')
    
    ds_com_era['tb_mwi_cum_est'] = (ds_com_era.srf_est * ds_com_era['tb'].
                                    isel(angle=9)).cumsum('frequency')
    
    # era5 hyd
    ds_com_erh['tb_mwi_cum_orig'] = (ds_com_erh.srf_orig * ds_com_erh['tb'].
                                     isel(angle=9)).cumsum('frequency')
    
    ds_com_erh['tb_mwi_cum_est'] = (ds_com_erh.srf_est * ds_com_erh['tb'].
                                    isel(angle=9)).cumsum('frequency')
    
    #%% detailed plot with spectral tb and srf + top-hat together
    # choose a dataset, channel and profile
    # here, extreme dtb values can be inspectred in detail
    ds_com = ds_com_rsd
    channel = 17
    profile = 'ID_01004_201910251200'
    
    i_channel = {a: b for b, a, in enumerate(range(14, 19))}
    
    # plot
    fig, axes = plt.subplots(3, 1, figsize=(6, 4), sharex=True, 
                             constrained_layout=True)
    
    axes[0].set_ylabel('TB [K]')
    axes[1].set_ylabel('Sensitivity [%]')
    axes[2].set_ylabel('cumulative TB [K]')
    axes[-1].set_xlabel('Frequency [GHz]')
    
    # tb
    axes[0].plot(
        ds_com.frequency*1e-3,
        ds_com.tb.isel(angle=9).sel(profile=profile), 
        color='coral')
    
    ylim_values = ds_com.tb.sel(profile=profile).isel(
        angle=9, 
        frequency=ds_com.srf_est.sel(channel=channel, est_type='top-hat') > 0)
    axes[0].set_ylim(ylim_values.min('frequency'), ylim_values.max('frequency'))
    
    axes[1].plot(ds_com.frequency*1e-3,
            ds_com.srf_orig.sel(channel=channel)*100, 
            label='srf', color='magenta'
            )
    axes[1].plot(ds_com.frequency*1e-3,
            ds_com.srf_est.sel(channel=channel, est_type='top-hat')*100,
            label='top-hat', color='skyblue'
            )
    
    axes[2].plot(ds_com.frequency*1e-3,
            ds_com.tb_mwi_cum_orig.sel(channel=channel, profile=profile),
            label='srf',
            marker='.', color='magenta')
    
    axes[2].plot(ds_com.frequency*1e-3,
            ds_com.tb_mwi_cum_est.sel(channel=channel,
                                      est_type='top-hat',
                                      profile=profile),
            label='top-hat',
            marker='.', color='skyblue')
    
    # mark tbs from estimate as horizontal lines
    lst = ['-', '--', '-.', ':']
    for i, est_type in enumerate(ds_com.est_type.values):
        axes[0].axhline(
            ds_com.tb_mwi_est.sel(
                channel=channel,
                est_type=est_type,
                profile=profile), color='skyblue', linestyle=lst[i],
            label=est_type
            )
        
    # mark tb from srf
    axes[0].axhline(
        ds_com.tb_mwi_orig.sel(
            channel=channel,
            profile=profile), color='magenta', label='srf'
        )
    
    # mark channel frequencies
    for i in range(2):
        axes[0].axvline(mwi.freq_center[i_channel[channel], i], color='k')
    
    for i in range(4):
        axes[0].axvline(mwi.freq_bw[i_channel[channel], i], color='k')
    
    axes[0].legend()
    axes[1].legend()
    axes[2].legend()
