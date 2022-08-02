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

"""


import xarray as xr
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import sys
sys.path.append(f'{os.environ["PATH_PHD"]}/projects/mwi_bandpass_effects/scripts')
from importer import Sensitivity
from mwi_info import mwi

plt.ion()


if __name__ == '__main__':
    
    # read pamtra simulation of radiosondes
    ds_pam = xr.open_dataset(os.environ['PATH_PHD']+'/projects/mwi_bandpass_effects/data/brightness_temperature/TB_radiosondes_2019.nc')
    ds_pam.coords['frequency'] = (ds_pam.frequency*1e3).astype('int')
    
    # read srf data
    srf = Sensitivity(filename='MWI-RX183_DSB_Matlab.xlsx')
    
    #%% create different SRF's used to calculate MWI observation/estimates
    # make another script which creates different SRF and writes them all to 
    # a netcdf file!
    # dimension: (frequency, channel, i_srf)
    # original measured SRF
    srf_orig = srf.data.lino
    
    # todo: add perturbations (types, magnitudes, reduction levels, ...)
    
    # create idealized srf for the modelled mwi observation from mwi_info
    # everywhere nan, except for the specified frequencies
    srf_0 = xr.concat(
        [xr.DataArray(data=np.ones(len(mwi.freq_center_MHz[i, :])),
                      dims=['frequency'],
                      coords=dict(frequency=mwi.freq_center_MHz[i, :]))
         for i in range(5)
         ],
        dim=srf_orig.channel
        )

    srf_1 = xr.concat(
        [xr.DataArray(data=np.ones(len(mwi.freq_bw_MHz[i, :])),
                      dims=['frequency'],
                      coords=dict(frequency=mwi.freq_bw_MHz[i, :]))
         for i in range(5)
         ],
        dim=srf_orig.channel
        )
    
    srf_2 = xr.concat(
        [xr.DataArray(data=np.ones(len(mwi.freq_bw_center_MHz[i, :])),
                      dims=['frequency'],
                      coords=dict(frequency=mwi.freq_bw_center_MHz[i, :]))
         for i in range(5)
         ],
        dim=srf_orig.channel
        )
    
    da_srf = xr.concat([
        srf_orig, srf_0, srf_1, srf_2
        ], dim=pd.Index(['orig', 'freq_center', 'freq_bw', 'freq_bw_center',
                         ], name='srf_type'))
    

    # top hat function
                         
    # normalize all srf
    da_srf = da_srf/da_srf.sum('frequency')
    
    
    #%% combine pamtra simulation and srfs
    ds_com = ds_pam.copy(deep=True)
    ds_com['srf'] = da_srf
    
    #%% calculate mwi tb
    ds_com['tb_mwi'] = (ds_com['srf'] * ds_com['tb'].isel(angle=9)).sum('frequency')
    
    # calculate difference to original srf
    ds_com['dtb_mwi'] = ds_com['tb_mwi'].sel(srf_type='orig') - ds_com['tb_mwi']
    
    #%% evaluate difference
    # scatter
    fig, ax = plt.subplots()
    
    ax.scatter(ds_com['tb_mwi'].sel(channel=18, srf_type='orig'),
               ds_com['tb_mwi'].sel(channel=18, srf_type='freq_center')-
               ds_com['tb_mwi'].sel(channel=18, srf_type='orig'),
               c=ds_com.iwv
               )
    
    #%% iwv
    fig, axes = plt.subplots(5, 3, figsize=(6, 8), sharex=True, sharey=True,
                             constrained_layout=True)
    
    axes[2, 0].set_ylabel(r'$\Delta TB = TB_{obs} - TB_{ref}$ [K]')
    axes[-1, 1].set_xlabel('Integrated water vapor [kg m$^{-2}$]')
    
    axes[0, 0].set_title(r'$TB_{ref}$ at'+'\n'+r'$\nu_{center}$', fontsize=8)
    axes[0, 1].set_title(r'$TB_{ref}$ at'+'\n'+r'$\nu_{center \pm \frac{1}{2} bandwidth}$', fontsize=8)
    axes[0, 2].set_title(r'$TB_{ref}$ at'+'\n'+r'$\nu_{center}$ and $\nu_{center \pm \frac{1}{2} bandwidth}$', fontsize=8)
    
    for ax in axes.flatten():
        
        # x axis
        ax.set_xticks(ticks=np.arange(0, 150, 25), minor=False)
        ax.set_xticks(ticks=np.arange(0, 150, 5), minor=True)
        
        # y axis
        ax.set_yticks(ticks=np.arange(-2, 2, 0.5), minor=False)
        ax.set_yticks(ticks=np.arange(-2, 2, 0.1), minor=True)
        
        ax.tick_params(which='major')
        ax.tick_params(which='minor', length=1)
        ax.grid('both', alpha=0.5)
        
        ax.axhline(y=0, color='k', linewidth=1, alpha=0.5)
        
        ax.set_ylim([-1.4, 1.4])
        ax.set_xlim([0, 75])
        
    # annotate channel name
    for i, ax in enumerate(axes[:, -1]):
        ax.annotate(text=mwi.freq_txt[i], xy=(1.1, 0.5), xycoords='axes fraction', backgroundcolor="w",
                    annotation_clip=False, horizontalalignment='left', verticalalignment='center', fontsize=8)
    
    kwds = dict(s=2, lw=0, alpha=0.5)
    for i, channel in enumerate(mwi.channels_int):
        axes[i, 0].scatter(ds_com.iwv, 
                           ds_com.dtb_mwi.sel(channel=channel,
                                             srf_type='freq_center'), 
                           **kwds)
        axes[i, 1].scatter(ds_com.iwv, 
                           ds_com.dtb_mwi.sel(channel=channel,
                                             srf_type='freq_bw'), 
                           **kwds)
        axes[i, 2].scatter(ds_com.iwv, 
                           ds_com.dtb_mwi.sel(channel=channel,
                                             srf_type='freq_bw_center'), 
                           **kwds)
    
    # legend below
    patches = []
    stations = wyo.station_id.keys()
    for station in stations:
        patches.append(mpatches.Patch(color=colors[wyo.station_id[station]], label=station))
    leg = axes[-1, -1].legend(handles=patches, bbox_to_anchor=(1.05, 0.2), loc='upper left', frameon=False, ncol=1, fontsize=6, title='Radiosonde location:')
    plt.setp(leg.get_title(),fontsize=6)
    
    plt.savefig(fig_all, dpi=400)