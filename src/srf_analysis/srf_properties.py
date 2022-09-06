"""
Calculation of SRF properties.
"""


import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from helpers import Sensitivity, mwi
from dotenv import load_dotenv

plt.ion()
load_dotenv()


if __name__ == '__main__':
    
    # read bandpass measurement
    print(Sensitivity.files)
    sen_dsb = Sensitivity(filename=Sensitivity.files[0])
    sen = Sensitivity(filename=Sensitivity.files[1])
    
    #%% number of measurements in bandwidth
    for i, ds in enumerate([sen_dsb.data, sen.data]):
        
        print(Sensitivity.files[i])
        
        for i, ch in enumerate(mwi.channels_int):
            
            f = dict(frequency=
                ((mwi.freq_bw[i, 0] <= ds.frequency*1e-3) & \
                 (mwi.freq_bw[i, 1] >= ds.frequency*1e-3)) | \
                ((mwi.freq_bw[i, 2] <= ds.frequency*1e-3) & \
                 (mwi.freq_bw[i, 3] >= ds.frequency*1e-3))
                )
            
            print(len(ds.frequency.sel(**f)))
    
    #%% imbalance for every channel from dsb measurement
    for i, channel in enumerate(sen_dsb.data.channel.values):
        
        left = sen_dsb.data.lino.sel(
            frequency=(sen_dsb.data.frequency < 183310),
            channel=channel).sum('frequency').item()*100
        right = sen_dsb.data.lino.sel(
            frequency=(sen_dsb.data.frequency > 183310),
            channel=channel).sum('frequency').item()*100
    
        print(f'channel {channel}: L{left}|R{right}')
    
    #%% out-of-band sensitivity
    for i, channel in enumerate(sen_dsb.data.channel.values):
        
        ix_in = ((sen_dsb.data.frequency > mwi.freq_bw_MHz[i, 0]) & \
                (sen_dsb.data.frequency < mwi.freq_bw_MHz[i, 1])) | \
                ((sen_dsb.data.frequency > mwi.freq_bw_MHz[i, 2]) & \
                (sen_dsb.data.frequency < mwi.freq_bw_MHz[i, 3]))
                
        sen_in = sen_dsb.data.lino.sel(frequency=ix_in, 
                              channel=channel).sum('frequency').item()*100
        sen_out = sen_dsb.data.lino.sel(frequency=~ix_in, 
                              channel=channel).sum('frequency').item()*100
        
        print(f'channel {channel}: {sen_in}|{sen_out}')
        
    # more details on out-of-band sensitivity
    for i, channel in enumerate(sen_dsb.data.channel.values):
        
        if channel == 18:
            break
        
        ix_l_wing = sen_dsb.data.frequency < mwi.freq_bw_MHz[i, 0]  
        ix_r_wing = sen_dsb.data.frequency > mwi.freq_bw_MHz[i, 3]                  
        ix_l_cent = (sen_dsb.data.frequency > mwi.freq_bw_MHz[i, 1]) & \
                    (sen_dsb.data.frequency < mwi.absorpt_line*1e3) 
        ix_r_cent = (sen_dsb.data.frequency < mwi.freq_bw_MHz[i, 2]) & \
                    (sen_dsb.data.frequency > mwi.absorpt_line*1e3) 

        sen_l_wing = np.round(sen_dsb.data.lino.sel(frequency=ix_l_wing, 
                              channel=channel).sum('frequency').item()*100, 2)
        sen_r_wing = np.round(sen_dsb.data.lino.sel(frequency=ix_r_wing, 
                              channel=channel).sum('frequency').item()*100, 2)
        sen_l_cent = np.round(sen_dsb.data.lino.sel(frequency=ix_l_cent, 
                              channel=channel).sum('frequency').item()*100, 2)
        sen_r_cent = np.round(sen_dsb.data.lino.sel(frequency=ix_r_cent, 
                              channel=channel).sum('frequency').item()*100, 2)
        
        print(f'channel {channel}: {sen_l_wing}|{sen_l_cent}-{sen_r_cent}|'+
              '{sen_r_wing}')
        
    #%% cumulative sensitivity within bandpass region
    fig, axes = plt.subplots(1, 5, figsize=(8, 3), constrained_layout=True, 
                             sharey=True)
    
    colors = ['skyblue', 'green', 'magenta', 'coral', 'gold']
    
    for i, channel in enumerate(sen_dsb.data.channel.values):
        
        ax = axes[i]
        
        ix_l = ((sen_dsb.data.frequency > mwi.freq_bw_MHz[i, 0]) & \
                (sen_dsb.data.frequency < mwi.freq_bw_MHz[i, 1]))
        ix_r = ((sen_dsb.data.frequency > mwi.freq_bw_MHz[i, 2]) & \
                (sen_dsb.data.frequency < mwi.freq_bw_MHz[i, 3]))
        
        sen_cum_l = sen_dsb.data.lino.sel(frequency=ix_l, channel=channel)
        sen_cum_r = sen_dsb.data.lino.sel(frequency=ix_r, channel=channel)
            
        # frequency from outer cutoff frequency to inner
        sen_cum_l['frequency'] = sen_cum_l['frequency'] - mwi.freq_bw_MHz[i, 0] - 2
        sen_cum_r['frequency'] = 2 + mwi.freq_bw_MHz[i, 3] - sen_cum_r['frequency']
        
        sen_cum_r = sen_cum_r.sel(frequency=np.sort(sen_cum_r.frequency))
        
        sen_cum_l = sen_cum_l.cumsum('frequency')
        sen_cum_r = sen_cum_r.cumsum('frequency')
        
        ax.plot(sen_cum_l.frequency, sen_cum_l, color=colors[i], label=channel)
        ax.plot(sen_cum_r.frequency, sen_cum_r, linestyle='--', color=colors[i])
        
        ax.legend()

    for ax in axes[1:]:
        ax.plot([0, 1500], [0, 0.5], color='k')
        
    axes[0].plot([0, 2000], [0, 0.5], color='k')
    
    plt.show()
    
    #%% calculate top-hat function
    sen_dsb.data['top-hat'] = xr.zeros_like(sen_dsb.data.lino)
    
    for i, channel in enumerate(mwi.channels_int):
        
        ix_in = ((sen_dsb.data.frequency > mwi.freq_bw_MHz[i, 0]) & \
                (sen_dsb.data.frequency < mwi.freq_bw_MHz[i, 1])) | \
                ((sen_dsb.data.frequency > mwi.freq_bw_MHz[i, 2]) & \
                (sen_dsb.data.frequency < mwi.freq_bw_MHz[i, 3]))
        
        sen_dsb.data['top-hat'][ix_in, i] = 1
    
    sen_dsb.data['top-hat'] = sen_dsb.data['top-hat'] / \
        sen_dsb.data['top-hat'].sum('frequency')
    
    # check, that sum along frequency is one
    assert np.all((sen_dsb.data['top-hat'].sum('frequency').values-1) < 1e-10)
    assert np.all((sen_dsb.data.lino.sum('frequency').values-1) < 1e-10)
    
    #%% plot sensitivity lino zoomed in to the bandpass region together with
    # top-hat function
    fig, axes = plt.subplots(2, 5, sharey=True, figsize=(7, 4), 
                             constrained_layout=True)
        
    for ax in fig.axes:
        ax.spines.top.set_visible(False)
        ax.spines.right.set_visible(False)

    for i, channel in enumerate(mwi.channels_int):
        for j in range(2):
                       
            ax = axes[j, i]
        
            # mark where top-hat is smaller than srf and not in bandpass region
            ix = (sen_dsb.data['top-hat'].sel(channel=channel) == 0).values
            ix[1:] = ix[:-1] | ix[1:]
            ix[:-1] = ix[:-1] | ix[1:]
            ax.fill_between(x=sen_dsb.data.frequency*1e-3,
                            y1=sen_dsb.data['top-hat'].sel(channel=channel)*100, 
                            y2=sen_dsb.data.lino.sel(channel=channel)*100,
                            where=ix,
                            color='magenta', linewidths=0, step='mid')
            
            ax.fill_between(x=sen_dsb.data.frequency*1e-3,
                            y1=sen_dsb.data['top-hat'].sel(channel=channel)*100, 
                            y2=0, 
                            color='skyblue', linewidths=0, step='mid')
            
            # srf
            ax.plot(sen_dsb.data.frequency*1e-3, 
                    sen_dsb.data.lino.sel(channel=channel)*100, 
                    color='k', linewidth=1)
            
            # y axis settings
            ax.set_yticks([0, 0.25, 0.5, 0.75, 1])
            ax.set_ylim([0, 0.85])
            
            # set x-limit
            ax.set_xticks(np.arange(0, 300))
            dx = 1.25 - mwi.bandwidths[i]/2
            ax.set_xlim(mwi.freq_bw[i, j*2]-dx, mwi.freq_bw[i, j*2+1]+dx)
            
            # annotate channel name
            if j == 0:
                ax.annotate(mwi.freq_txt[i].split('\n')[0], xy=(0.5, 1.01), 
                            xycoords='axes fraction', ha='center', va='bottom')
            
            # center frequency
            ax.axvline(x=mwi.freq_center[i, j], color='gray', linestyle='--',
                       linewidth=0.75, zorder=3)

    # set axis labels
    axes[1, 0].set_ylabel('Sensitivity [%]')
    axes[1, 0].set_xlabel('Frequency [GHz]')
    
    plt.show()
    