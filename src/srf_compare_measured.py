"""
Comparison of both bandpass measurements at frequencies above 183 GHz.

The SRF measurement of MWI-RX183_Matlab.xlsx is a xombination between the upper
and lower DSB measurements. Both sides are nearly weighted the same, but one
side can also be weighted more than the other side.

This script calculates MWI-RX183_Matlab.xlsx from the DSB measurements in the
file MWI-RX183_DSB_Matlab.xlsx by averaging the lower and upper frequencies.
Then, both measurements are compared by interpolation, because they measure not 
at the same frequencies.

Outcome:
    Difference between both measurements is spectrally correlated for different
    channels. This can be seen clear when looking at differences in linear
    scale for overlapping bandpasses of channels 14 and 15, and 15 and 16.
    Correlation is higher for differences in dB (0.97, 0.92) than in linear
    values (0.85, 0.83) for channels 14/15 and 15/16 when using only the band
    pass region. When using all frequencies, the correlation is lower with 
    values below 0.5
    
    How large is the offset?
"""


import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import os
from string import ascii_lowercase as abc
from dotenv import load_dotenv
from helpers import mwi, Sensitivity

plt.ion()
load_dotenv()


if __name__ == '__main__':
    
    sen1 = Sensitivity(filename=Sensitivity.files[0]).data
    sen2 = Sensitivity(filename=Sensitivity.files[1]).data
    
    #%% average sen1 double sideband sensitivity measurements 
    freq_center = 183312  # where sen1 is mirrored
    
    sen1_left = sen1.lino.sel(
        frequency=sen1.frequency < freq_center).sortby(
            'frequency', ascending=False)
    sen1_left['frequency'] = 2*freq_center - sen1_left['frequency']
    
    sen1_right = sen1.lino.sel(frequency=sen1.frequency > freq_center)
    
    assert (sen1_left['frequency'] == sen1_right['frequency']).all()
    
    # add both sides and normalize to a sum of 1
    sen2_from_sen1 = sen1_left + sen1_right
    sen2_from_sen1 = sen2_from_sen1/sen2_from_sen1.sum('frequency')
    
    # interpolate sen2 on same frequencies as sen2_from_sen1
    sen2_interp = sen2.lino.interp({'frequency': sen2_from_sen1.frequency},
                                   method='linear')
    sen2_interp = sen2_interp/sen2_interp.sum('frequency')
    
    # combine in dataset
    ds = xr.Dataset()
    ds['sen2_from_sen1'] = sen2_from_sen1
    ds['sen2_interp'] = sen2_interp
    
    # convert to dB and shift to maximum of 0 dB
    for name in ['sen2_from_sen1', 'sen2_interp']:
        ds[name+'_dB'] = 10*np.log10(ds[name])
        ds[name+'_dB'] -= np.max(ds[name+'_dB'])
    
    assert ds[['sen2_from_sen1_dB', 'sen2_interp_dB']].max() == 0
    
    # calculate difference
    ds['sen2_diff'] = ds['sen2_interp'] - ds['sen2_from_sen1']
    ds['sen2_diff_dB'] = ds['sen2_interp_dB'] - ds['sen2_from_sen1_dB']
    
    assert (ds['sen2_diff'].sum('frequency') < 1e-15).all()
    
    # normalized difference
    ds['sen2_diff_norm'] = ds['sen2_diff'] / ds['sen2_interp']
    
    # correlation
    sen2_diff_corr = ds['sen2_diff'].to_pandas().corr()
    sen2_diff_dB_corr = ds['sen2_diff_dB'].to_pandas().corr()
    sen2_diff_norm = ds['sen2_diff_norm'].to_pandas().corr()

    # correlation only in bandpass region
    ds['sen2_diff_bp'] = ds['sen2_diff'].copy()
    ds['sen2_diff_dB_bp'] = ds['sen2_diff_dB'].copy()
    for i in range(5):
        ix = (ds.frequency > mwi.freq_bw_MHz[i, 2]) & \
            (ds.frequency < mwi.freq_bw_MHz[i, 3])
        ds['sen2_diff_bp'][:, i] = ds['sen2_diff_bp'][:, i].where(ix)
        ds['sen2_diff_dB_bp'][:, i] = ds['sen2_diff_dB_bp'][:, i].where(ix)
    
    sen2_diff_bp_corr = ds['sen2_diff_bp'].to_pandas().corr()
    sen2_diff_dB_bp_corr = ds['sen2_diff_dB_bp'].to_pandas().corr()
    
    # mean over bandpass region
    ds['sen2_diff_dB_bp'].mean('frequency')
    ds['sen2_diff_dB'].mean('frequency')
    
    #%% visualization: sensitivity graphs
    # linear
    fig, axes = plt.subplots(5, 1, figsize=(5, 7), sharex=True, sharey=True,
                             constrained_layout=True)
    
    for i, ax in enumerate(axes):
        
        channel = mwi.channels_int[i]
        
        ax.plot(ds.frequency*1e-3,
                ds['sen2_interp'].isel(channel=i), 
                marker='o', markersize=2, label='measured')
        
        ax.plot(ds.frequency*1e-3, 
                ds['sen2_from_sen1'].isel(channel=i), 
                marker='o', markersize=2, label='calculated from DSB')
    
    axes[0].legend()
    axes[-1].set_xlabel('Frequency [GHz]')
    axes[2].set_ylabel('Sensitivity')
    
    # logarithmic
    fig, axes = plt.subplots(5, 1, figsize=(5, 7), sharex=True, sharey=True,
                             constrained_layout=True)
    
    for i, ax in enumerate(axes):
        
        channel = mwi.channels_int[i]
        
        ax.plot(ds.frequency*1e-3, 
                ds['sen2_interp_dB'].isel(channel=i), 
                marker='o', markersize=2, label='measured')
        
        ax.plot(ds.frequency*1e-3, 
                ds['sen2_from_sen1_dB'].isel(channel=i), 
                marker='o', markersize=2, label='calculated from DSB')
        
    axes[0].legend()
    axes[-1].set_xlabel('Frequency [GHz]')
    axes[2].set_ylabel('Sensitivity [dB]')
    
    #%% visualization: sensitivity graphs for bandpass region only
    fig, axes = plt.subplots(1, 5, sharey=True)
    
    for i, ax in enumerate(axes):
        
        ax.spines.top.set_visible(False)
        ax.spines.right.set_visible(False)
    
        ax.plot(ds.frequency*1e-3,
                ds.sen2_interp.isel(channel=i))
    
        ax.plot(ds.frequency*1e-3,
                ds.sen2_from_sen1.isel(channel=i))
        
        ax.set_xticks(np.arange(0, 300))
        dx = 1.25 - mwi.bandwidths[i]/2
        ax.set_xlim(mwi.freq_bw[i, 2]-dx, mwi.freq_bw[i, 3]+dx)
            
    # logarithmic
    fig, axes = plt.subplots(1, 5, sharey=True)
    
    for i, ax in enumerate(axes):
        
        ax.spines.top.set_visible(False)
        ax.spines.right.set_visible(False)
    
        ax.plot(ds.frequency*1e-3,
                ds.sen2_interp_dB.isel(channel=i))
    
        ax.plot(ds.frequency*1e-3,
                ds.sen2_from_sen1_dB.isel(channel=i))
        
        ax.set_xticks(np.arange(0, 300))
        dx = 1.25 - mwi.bandwidths[i]/2
        ax.set_xlim(mwi.freq_bw[i, 2]-dx, mwi.freq_bw[i, 3]+dx)
        
        ax.set_ylim(-10, 1)
    
    #%% visualization: sensitivity differences
    # difference between linear
    fig, axes = plt.subplots(5, 1, figsize=(5, 7), sharex=True, sharey=True,
                             constrained_layout=True)
    
    for i, ax in enumerate(axes):
        
        channel = mwi.channels_int[i]
        
        ax.plot(ds.frequency*1e-3, 
                ds.sen2_diff.isel(channel=i), 
                marker='o', markersize=2)
    
    axes[-1].set_xlabel('Frequency [GHz]')
    axes[2].set_ylabel('Sensitivity: meas - calc(DSB)')
    
    # differences between dB
    fig, axes = plt.subplots(5, 1, figsize=(5, 7), sharex=True, sharey=True,
                             constrained_layout=True)
    
    for i, ax in enumerate(axes):
        
        channel = mwi.channels_int[i]
        
        ax.plot(ds.frequency*1e-3, 
                ds.sen2_diff_dB.isel(channel=i), 
                marker='o', markersize=2)
        
    axes[-1].set_xlabel('Frequency [GHz]')
    axes[2].set_ylabel('Sensitivity: meas - calc(DSB) [dB]')
    
    #%% visualization: differences between dB for bandpass region with labels
    fig, axes = plt.subplots(1, 5, figsize=(6, 2.3), sharey=True, 
                             constrained_layout=True)
    
    for j, (i, ax) in enumerate(zip(ds.channel.values, axes)):
                        
        ax.spines.top.set_visible(False)
        ax.spines.right.set_visible(False)
    
        ax.axhline(y=0, color='k', linewidth=0.8)
        
        # frequencies in bandpass region
        f = dict(frequency=slice(
            (mwi.freq_center[j, 1]-mwi.bandwidths[j]/2)*1e3, 
            (mwi.freq_center[j, 1]+mwi.bandwidths[j]/2)*1e3))
        
        #ax.axhline(
        #    y=ds.sen2_diff_dB.sel(channel=i, **f).mean('frequency'),
        #    color='coral', linestyle=':'
        #    )
            
        ax.plot(
            ds.frequency.sel(**f)*1e-3,
            ds.sen2_diff_dB.sel(channel=i, **f),
            color='gray', linewidth=0.8,
            )
        
        # fit line
        a, b = ds.sen2_diff_dB.sel(channel=i, **f).polyfit(
            dim='frequency', deg=1).polyfit_coefficients
        ax.plot(
            ds.frequency.sel(**f)*1e-3,
            ds.frequency.sel(**f)*a + b,
            color='coral'
            )
        
        ax.set_xticks(np.arange(0, 300))
        ax.set_xlim(list(f.values())[0].start*1e-3, 
                    list(f.values())[0].stop*1e-3)
        
        ax.set_ylim(-.5, .5)
        
        ax.annotate(f'({abc[j]})', xy=(0.01, .99), 
                    xycoords='axes fraction', ha='left', va='top')
        
        ax.annotate(mwi.freq_txt[j].split('\n')[0], xy=(0.5, 1), 
                    xycoords='axes fraction', ha='center', va='bottom')
    
    axes[0].set_xlabel('Frequency [GHz]')
    axes[0].set_ylabel('Sensitivity difference [dB]')
    
    plt.savefig(os.path.join(
        os.environ['PATH_PLT'],
        'bandpass_measurement/bandpass_measurement_diff.png'),
        dpi=300, bbox_inches='tight')
    
    #%% visualization: sensitivity differences normalized
    # difference between linear
    fig, axes = plt.subplots(5, 1, figsize=(5, 7), sharex=True, sharey=True,
                             constrained_layout=True)
    
    for i, ax in enumerate(axes):
        
        channel = mwi.channels_int[i]
        
        ax.plot(ds.frequency*1e-3, 
                ds.sen2_diff_norm.isel(channel=i), 
                marker='o', markersize=2)
    
    axes[-1].set_xlabel('Frequency [GHz]')
    axes[2].set_ylabel('Sensitivity: meas - calc(DSB)')
      
    #%% visualization: scatter of differences
    # differences linear
    fig, axes = plt.subplots(5, 5, constrained_layout=True)
    
    for (i, j), ax in np.ndenumerate(axes):
        ax.scatter(
            ds.sen2_diff.isel(channel=i), 
            ds.sen2_diff.isel(channel=j), 
            s=2, c='k', alpha=0.5)
    
    # differences linear, where linear sensitivity is high enough
    fig, axes = plt.subplots(5, 5, constrained_layout=True)
    
    for (i, j), ax in np.ndenumerate(axes):
        
        ix = (ds.sen2_interp.isel(channel=i) > 0.001) & \
             (ds.sen2_interp.isel(channel=j) > 0.001)
        
        ax.scatter(
            ds.sen2_diff.isel(channel=i).sel(frequency=ix),
            ds.sen2_diff.isel(channel=j).sel(frequency=ix),
            s=2, c='k', alpha=0.5)
    
    # differences log
    fig, axes = plt.subplots(5, 5, constrained_layout=True)
    
    for (i, j), ax in np.ndenumerate(axes):
        ax.scatter(
            ds.sen2_diff_dB.isel(channel=i), 
            ds.sen2_diff_dB.isel(channel=j), 
            s=2, c='k', alpha=0.5)
        
    # normalized differences linear
    fig, axes = plt.subplots(5, 5, constrained_layout=True)
    
    for (i, j), ax in np.ndenumerate(axes):
        ax.scatter(
            ds.sen2_diff_norm.isel(channel=i), 
            ds.sen2_diff_norm.isel(channel=j), 
            s=2, c='k', alpha=0.5)
        
    #%% visualization: correlation
    fig, axes = plt.subplots(1, 3, figsize=(8, 4), constrained_layout=True)
    
    dfs = [
        sen2_diff_corr,
        sen2_diff_dB_corr,
        sen2_diff_norm,
        ]
    
    for i, ax in enumerate(axes):
        
        df = dfs[i]
        
        im = ax.pcolormesh(
            df.index, 
            df.index, 
            df, 
            cmap='PuOr', shading='nearest', vmin=-1, vmax=1)
                
        for (i, j), z in np.ndenumerate(df.values):
            ax.annotate(text='{:0.2f}'.format(np.round(z,1)), xy=(14+j, 14+i), 
                        xycoords='data', ha='center', va='center',
                        color='gray')
    
    fig.colorbar(im, ax=axes)
    
    #%%
    plt.close('all')