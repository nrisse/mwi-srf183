"""
Script to plot reference tb location for visualization in the presentations
"""


import os
import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
from mwi_info import mwi
from dotenv import load_dotenv

load_dotenv()
plt.ion()


if __name__ == '__main__':
    
    # read combined dataset with the different SRF
    ds_com = xr.open_dataset(os.path.join(
        os.environ['PATH_BRT'],
        'TB_radiosondes_2019_MWI.nc'))
    
    #%% plot srf and the estimate frequencies together
    channel = 18
    
    fig, ax = plt.subplots(1, 1, figsize=(8, 3), constrained_layout=True)
    
    ax.spines.top.set_visible(False)
    ax.spines.right.set_visible(False)
    
    # original srf
    f = dict(frequency=~np.isnan(ds_com.srf_orig.sel(channel=channel)))
    ax.plot(ds_com.frequency.sel(**f)*1e-3, 
            ds_com.srf_orig.sel(channel=channel, **f)*1e2, color='coral',
            label='measured SRF', zorder=0)
        
    # center frequency (matches top-hat without scaling, because top-hat has 100 
    # values on each bandpass)
    dct_est_types = {
        'freq_center': 
            dict(label=r'center ($10^{-2}$)', 
                 marker='o'), 
        'freq_bw': 
            dict(label=r'cutoff ($10^{-2}$)', 
                 marker='s'), 
        'freq_bw_center': 
            dict(label=r'center+cutoff ($10^{-2}$)', 
                 marker='D'),
        }
    
    for est_type, kwds in dct_est_types.items():
        ax.scatter(
            ds_com.frequency*1e-3, 
            ds_com.srf_est.sel(channel=channel, est_type=est_type), 
            zorder=2, color='slategray', **kwds)
        
    # top-hat function
    ax.plot(ds_com.frequency.sel(**f)*1e-3, 
            ds_com.srf_est.sel(channel=channel, est_type='top-hat', **f)*1e2, 
            color='skyblue', label='top-hat', zorder=1)
    
    ax.legend(frameon=False, bbox_to_anchor=(1, 0.5), loc='center left')
    
    ax.set_xlim(mwi.absorpt_line-4, mwi.absorpt_line+4)
    
    ax.set_xlabel('Frequency [GHz]')
    ax.set_ylabel('Sensitivity [%]')
        
    plt.savefig(os.path.join(
        os.environ['PATH_PLT'],
        'bandpass_measurement/estimate_frequencies.svg'),
        bbox_inches='tight')
    
    plt.close('all')
