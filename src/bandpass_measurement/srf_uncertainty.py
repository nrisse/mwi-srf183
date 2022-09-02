"""
Comparison of both bandpass measurements at frequencies above 183 GHz.

The DSB SRF is reduced to only above 183.31 GHz and the other SRF is 
interpolated to the remaining DSB frequencies. Then both are scaled to a 
maximum sensitivity of 0 dB. Comparison is done by taking the difference in 
the bandpass region.

Result: Offset can be up to 2 dB, mostly not larger than 1 dB in absolute 
values. It shows, that the assumed offsets are not unrealistic and 2 dB is
actually observed for MWI-18.
"""


import numpy as np
from string import ascii_lowercase as abc
import matplotlib.pyplot as plt
import os
from srf_reader import Sensitivity
from mwi_info import mwi
from dotenv import load_dotenv

load_dotenv()
plt.ion()


if __name__ == '__main__':
    
    # read bandpass measurement
    print(Sensitivity.files)
    sen_dsb = Sensitivity(filename=Sensitivity.files[0])
    sen = Sensitivity(filename=Sensitivity.files[1])
    
    #%% data preparation
    # reduce dsb to above 183 GHz
    sen_dsb.data = sen_dsb.data.sel(
        frequency=sen_dsb.data.frequency > mwi.absorpt_line*1e3)
    
    # match both in frequency
    sen.data = sen.data.interp(frequency=sen_dsb.data.frequency)
    
    # normalize to maximum of 0 dB
    sen_dsb.data['raw'] = sen_dsb.data.raw - sen_dsb.data.raw.max('frequency')
    sen.data['raw'] = sen.data.raw - sen.data.raw.max('frequency')
    
    # linearized again
    sen_dsb.data['lino'] = (('frequency', 'channel'), Sensitivity.normalize_srf(
        Sensitivity.linearize_srf(sen_dsb.data.raw.values)))
    sen.data['lino'] = (('frequency', 'channel'), Sensitivity.normalize_srf(
        Sensitivity.linearize_srf(sen.data.raw.values)))
    
    assert np.all(sen_dsb.data['raw'].max('frequency') == 0)
    assert np.all(sen.data['raw'].max('frequency') == 0)
    assert np.all((sen_dsb.data['lino'].sum('frequency') - 1) < 1e-13)
    assert np.all((sen.data['lino'].sum('frequency') - 1) < 1e-13)
    
    #%% quick check: SRF in dB
    fig, axes = plt.subplots(1, 5, sharey=True)
    
    for i, ax in enumerate(axes):
        
        ax.spines.top.set_visible(False)
        ax.spines.right.set_visible(False)
    
        ax.plot(sen_dsb.data.frequency*1e-3,
                sen_dsb.data.raw.isel(channel=i))
    
        ax.plot(sen.data.frequency*1e-3,
                sen.data.raw.isel(channel=i))
        
        ax.set_xticks(np.arange(0, 300))
        dx = 1.25 - mwi.bandwidth[i]/2
        ax.set_xlim(mwi.freq_bw[i, 2]-dx, mwi.freq_bw[i, 3]+dx)
        
        ax.set_ylim(-10, 1)
    
    #%% quick check: SRF in linear
    fig, axes = plt.subplots(1, 5, sharey=True)
    
    for i, ax in enumerate(axes):
        
        ax.spines.top.set_visible(False)
        ax.spines.right.set_visible(False)
    
        ax.plot(sen_dsb.data.frequency*1e-3,
                sen_dsb.data.lino.isel(channel=i))
    
        ax.plot(sen.data.frequency*1e-3,
                sen.data.lino.isel(channel=i))
        
        ax.set_xticks(np.arange(0, 300))
        dx = 1.25 - mwi.bandwidth[i]/2
        ax.set_xlim(mwi.freq_bw[i, 2]-dx, mwi.freq_bw[i, 3]+dx)
            
        ax.set_ylim(0, 0.015)
    
    #%% difference in log space
    fig, axes = plt.subplots(1, 5, figsize=(6, 2.3), sharey=True, 
                             constrained_layout=True)
    
    for j, (i, ax) in enumerate(zip(sen_dsb.data.channel.values, axes)):
                        
        ax.spines.top.set_visible(False)
        ax.spines.right.set_visible(False)
    
        ax.axhline(y=0, color='k')
        
        # frequencies in bandpass region
        f = dict(frequency=slice(
            (mwi.freq_center[j, 1]-mwi.bandwidth[j]/2)*1e3, 
            (mwi.freq_center[j, 1]+mwi.bandwidth[j]/2)*1e3))
    
        ax.axhline(
            y=(sen_dsb.data.raw.sel(channel=i, **f) - \
               sen.data.raw.sel(channel=i, **f)).mean('frequency'),
            color='coral', linestyle=':'
            )
            
        ax.plot(
            sen_dsb.data.frequency.sel(**f)*1e-3,
            sen_dsb.data.raw.sel(channel=i, **f) - \
                sen.data.raw.sel(channel=i, **f),
            color='coral'
            )
            
        ax.set_xticks(np.arange(0, 300))
        ax.set_xlim(list(f.values())[0].start*1e-3, 
                    list(f.values())[0].stop*1e-3)
        
        ax.set_ylim(-2, 2)
        
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
    
    #%%
    plt.close('all')
