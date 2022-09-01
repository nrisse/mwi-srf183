

import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
import os
import sys
sys.path.append(f'{os.environ["PATH_PHD"]}/projects/mwi_bandpass_effects/scripts')
from mwi_info import mwi
from path_setter import path_plot, path_data
from radiosonde import wyo 


plt.ion()


if __name__ == '__main__':
    
    # read data
    ds_com_rsd = xr.open_dataset(
        path_data+'brightness_temperature/TB_radiosondes_2019_MWI.nc')
    ds_com_rsd['tb'] = ds_com_rsd.tb.transpose('frequency', 'profile', 'angle')
    
    ds_com_era = xr.open_dataset(
        path_data+'brightness_temperature/TB_era5_MWI.nc')
    ds_com_era = ds_com_era.stack({'profile': ('grid_x', 'grid_y')})
    
    ds_com_erh = xr.open_dataset(
        path_data+'brightness_temperature/TB_era5_hyd_MWI.nc')
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
    
    #%% overview plot
    # tb 
    # srf + top-hat
    # cumulative tb srf + tb top-hat
    
    # choose a dataset, channel and profile
    ds_com = ds_com_rsd
    
    for channel in ds_com.channel.values:
        
        print(channel)
        
        for i_profile, profile in enumerate(ds_com.profile.values):
            
            channel = 17
            profile = 'ID_01004_201910251200'
            
            # plot
            fig, axes = plt.subplots(3, 1, figsize=(6, 4), sharex=True, 
                                     constrained_layout=True)
            
            axes[0].set_ylabel('TB [K]')
            axes[1].set_ylabel('Sensitivity [%]')
            axes[2].set_ylabel('cumulative TB [K]')
            axes[-1].set_xlabel('Frequency [GHz]')
            
            axes[0].fill_between(
                x=ds_com.frequency*1e-3,
                y1=0,
                y2=ds_com.srf_est.sel(channel=channel, est_type='top-hat')*1e9
                )
            
            # tb
            axes[0].plot(ds_com.frequency*1e-3,
                    ds_com.tb.isel(angle=9, profile=i_profile), color='k')
            
            ylim_values = ds_com.tb.isel(
                angle=9, 
                profile=i_profile, 
                frequency=ds_com.srf_est.sel(channel=channel, est_type='top-hat') > 0)
            axes[0].set_ylim(ylim_values.min('frequency'), ylim_values.max('frequency'))
            
            axes[1].plot(ds_com.frequency*1e-3,
                    ds_com.srf_orig.sel(channel=channel)*100, 
                    label='srf',
                    )
            axes[1].plot(ds_com.frequency*1e-3,
                    ds_com.srf_est.sel(channel=channel, est_type='top-hat')*100,
                    label='top-hat',
                    )
            
            axes[2].plot(ds_com.frequency*1e-3,
                    ds_com.tb_mwi_cum_orig.sel(channel=channel, profile=profile),
                    label='srf',
                    marker='.')
            
            axes[2].plot(ds_com.frequency*1e-3,
                    ds_com.tb_mwi_cum_est.sel(channel=channel,
                                              est_type='top-hat',
                                              profile=profile),
                    label='top-hat',
                    marker='.')
            
            axes[1].legend()
            
            # annotate difference
            dtb = np.round(ds_com.dtb_mwi_est.sel(
                channel=channel,
                est_type='top-hat',
                profile=profile).item(), 2)
            
            axes[0].annotate(f'{dtb} K', xy=(0.5, 0.5), xycoords='axes fraction',
                             ha='center', va='center')
            
            dtb_txt = '%+1.2f'%dtb
            plt.savefig(path_plot+'evaluation/dtb_details/'+
                        f'{channel}_{dtb_txt}_{profile}.png', dpi=100, 
                        bbox_inches='tight')
            
            plt.close('all')
    
    #%% colors
    colors = {'Ny-Alesund': 'cornflowerblue',
              'Essen': 'seagreen',
              'Singapore': 'palevioletred',
              'Barbados': 'peru',
              }
    
    

    #%% TB difference left and right of bandpass
    # needs to select same frequencies as for srf orig, because the are 
    # mirrored at 183.312 GHz, while the MWI channel frequencies are mirroed
    # at 183.310 GHz, therefore one will compare otherwise frequencies which
    # are not mirrored along the same axis, leading to disruptions in the
    # final difference curve
    freq_srf_orig = ~np.isnan(ds_com_rsd.srf_orig.sel(channel=14))
    ds_com_rsd_tbl = ds_com_rsd.tb.sel(
        frequency=(ds_com_rsd.frequency*1e-3 > mwi.absorpt_line) & freq_srf_orig)
    ds_com_rsd_tbr = ds_com_rsd.tb.sel(
        frequency=(ds_com_rsd.frequency*1e-3 < mwi.absorpt_line) & freq_srf_orig)
    
    ds_com_rsd_tbl['frequency'] = ds_com_rsd_tbr.frequency[::-1]
        
    ds_com_rsd_tb_imb = ds_com_rsd_tbl - ds_com_rsd_tbr
    
    fig, ax = plt.subplots(1, 1)
    
    ds_com_rsd_tb_imb_stack = ds_com_rsd_tb_imb.isel(angle=9).stack(
        {'z': ('frequency', 'profile')})
    c_list = [colors[wyo.id_station[s.split('_')[1]]] for s in ds_com_rsd_tb_imb_stack.profile.values]
    ax.scatter(
        ds_com_rsd_tb_imb_stack.frequency*1e-3,
        ds_com_rsd_tb_imb_stack, 
        color=c_list)
    
    ax.plot(ds_com_rsd_tb_imb.frequency*1e-3,
            ds_com_rsd_tb_imb.mean('profile').isel(angle=9), color='k')
    
    for x in mwi.freq_center.flatten():
        ax.axvline(x)
        
    #%% TB difference neighboring points (spectral gradients)
    # dtb/df for steps of 15 MHz (0.015 GHz), 
    left = dict(
        frequency=(ds_com_rsd.frequency*1e-3 < mwi.absorpt_line) & 
        freq_srf_orig)
    
    right = dict(
        frequency=(ds_com_rsd.frequency*1e-3 > mwi.absorpt_line) & 
        freq_srf_orig)

    ds_com_rsd_dtb_left = ds_com_rsd.tb.isel(angle=9).sel(left).diff(
        'frequency', n=1, label='lower')
            
    ds_com_rsd_dtb_right = ds_com_rsd.tb.isel(angle=9).sel(right).diff(
        'frequency', n=1, label='upper')
    
    fig, ax = plt.subplots(1, 1)

    ax.plot(ds_com_rsd_dtb_left.frequency*1e-3,
            ds_com_rsd_dtb_left/0.015, color='gray')
    
    ax.plot(ds_com_rsd_dtb_left.frequency*1e-3,
            ds_com_rsd_dtb_left.mean('profile')/0.015, color='k')
    
    ax.plot(ds_com_rsd_dtb_right.frequency*1e-3,
            ds_com_rsd_dtb_right/0.015, color='gray')
    
    ax.plot(ds_com_rsd_dtb_right.frequency*1e-3,
            ds_com_rsd_dtb_right.mean('profile')/0.015, color='k')
    
    ax.set_ylim(-15, 15)
    
    ax.axhline(y=0)
    
    # add channel frequencies
    for x in mwi.freq_center.flatten():
        ax.axvline(x)

    #%%
    plt.close('all')
