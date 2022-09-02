"""
Script to plot bandpass measurements in various forms
"""


import numpy as np
import pandas as pd
import xarray as xr
from string import ascii_lowercase as abc
import matplotlib.pyplot as plt
from matplotlib import cm
import os
from io import Sensitivity
from mwi_info import mwi
from dotenv import load_dotenv

load_dotenv()
plt.ion()


if __name__ == '__main__':
    
    # read bandpass measurement
    print(Sensitivity.files)
    sen_dsb = Sensitivity(filename=Sensitivity.files[0])
    sen = Sensitivity(filename=Sensitivity.files[1])
    
    #%% calculate some statistics
    # imbalance for every channel from dsb measurement
    for i, channel in enumerate(sen_dsb.data.channel.values):
        
        left = sen_dsb.data.lino.sel(
            frequency=(sen_dsb.data.frequency < 183310),
            channel=channel).sum('frequency').item()*100
        right = sen_dsb.data.lino.sel(
            frequency=(sen_dsb.data.frequency > 183310),
            channel=channel).sum('frequency').item()*100
    
        print(f'channel {channel}: L{left}|R{right}')
    
    # calculate out-of-band sensitivity
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
        
        print(f'channel {channel}: {sen_l_wing}|{sen_l_cent}-{sen_r_cent}|{sen_r_wing}')
    
    #%% cumulative sensitivity within bandpass region
    fig, axes = plt.subplots(1, 5, constrained_layout=True, sharey=True,
                             sharex=True)
    
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
    
    #%% plot sensitivity data (raw, all, log scale)
    # make same x scaling for the subplots
    a = ((sen_dsb.data.frequency.min() - sen_dsb.data.frequency.max()) / \
        (sen.data.frequency.min() - sen.data.frequency.max())).item()
    
    fig, axes = plt.subplots(5, 2, figsize=(7, 8), sharey=True, sharex='col',
                             constrained_layout=True, gridspec_kw=dict(
                                 width_ratios=[a, 1]))
    
    axes[0, 0].annotate('SRF-A', xy=(0.5, 1), xycoords='axes fraction',
                        ha='center', va='bottom')
    axes[0, 1].annotate('SRF-B', xy=(0.5, 1), xycoords='axes fraction',
                        ha='center', va='bottom')
    
    ymin = -110
    ymax = 1
    
    for i, ax in enumerate(axes[:, 1]):
                
        # annotate channel name
        ax.annotate(mwi.freq_txt[i].split('\n')[0], xy=(1, 0.5), 
                    xycoords='axes fraction', ha='right', va='center')
    
    for ax in fig.axes:
        ax.spines.top.set_visible(False)
        ax.spines.right.set_visible(False)
                
        # y axis settings
        ax.set_yticks(np.arange(-100, 25, 25))
        ax.set_ylim([ymin, ymax])
    
    match = np.array([183.362, 191.297])
    f = dict(frequency=slice(*match*1e3))
    for i, channel in enumerate(mwi.channels_int):
        
        # MWI-RX183_DSB_Matlab.xlsx dataset
        axes[i, 0].plot(
            sen_dsb.data.frequency*1e-3, 
            sen_dsb.data.raw.sel(channel=channel),
            color='#666666', label='SRF-A', zorder=2)
        
        axes[i, 0].plot(
            sen_dsb.data.frequency.sel(**f)*1e-3, 
            sen_dsb.data.raw.sel(channel=channel, **f),
            color='#000000', label='SRF-A', zorder=2)
        
        # MWI-RX183_Matlab.xslx
        axes[i, 1].plot(sen.data.frequency*1e-3,
                     sen.data.raw.sel(channel=channel),
                     color='#666666', label='SRF-B', zorder=2)
        
        axes[i, 1].plot(sen.data.frequency.sel(**f)*1e-3,
                     sen.data.raw.sel(channel=channel, **f),
                     color='#000000', label='SRF-B', zorder=2)
        
        for i_ax in range(2):
            
            # add shade for each channel
            axes[i, i_ax].axvspan(
                xmin=mwi.freq_bw[i, 0], 
                xmax=mwi.freq_bw[i, 1],
                ymin=0, ymax=1-(ymax/(ymax-ymin)), color='navajowhite', lw=0, zorder=0)
            
            axes[i, i_ax].axvspan(
                xmin=mwi.freq_bw[i, 2], 
                xmax=mwi.freq_bw[i, 3], 
                ymin=0, ymax=1-(ymax/(ymax-ymin)), color='bisque', lw=0, zorder=0)
    
    
    axes[0, 0].set_xlim(sen_dsb.data.frequency.min()*1e-3,
                        sen_dsb.data.frequency.max()*1e-3)
    axes[0, 1].set_xlim(sen.data.frequency.min()*1e-3,
                        sen.data.frequency.max()*1e-3)
    
    # set axis labels
    axes[2, 0].set_ylabel('Sensitivity [dB]')
    axes[-1, 0].set_xlabel('Frequency [GHz]')
    
    plt.savefig(os.path.join(
        os.environ['PATH_PLT'],
        'bandpass_measurement/srf.png'), 
        dpi=300, bbox_inches='tight')
    
    plt.close('all')

    #%% plot sensitivity data (raw, dsb, log scale)
    fig, axes = plt.subplots(5, 1, sharex=True, sharey=True, figsize=(6, 5))
    
    for ax in axes:
        ax.spines.top.set_visible(False)
        ax.spines.right.set_visible(False)
        
        ax.axhline(y=0, color='coral')
    
    for i, channel in enumerate(mwi.channels_int):
        
        # MWI-RX183_DSB_Matlab.xlsx dataset
        axes[i].plot(sen_dsb.data.frequency*1e-3, 
                     sen_dsb.data.raw.sel(channel=channel), 
                     color='k', linewidth=1, zorder=2)
        
        # y axis settings
        axes[i].set_yticks(np.arange(-30, 10, 10))
        axes[i].set_ylim([-30, 1])
                
        # set x-limit
        axes[i].set_xlim([np.min(mwi.freq_bw)-0.1, np.max(mwi.freq_bw)+0.1])
        
        # annotate channel name
        axes[i].annotate(text=mwi.freq_txt[i].split('\n')[0], xy=(183.31, -5), 
                         ha='center', va='top')
        
        for j in range(2):  # mark left/right channel frequency
            axes[i].axvline(x=mwi.freq_center[i, j], color='gray', linestyle='--', linewidth=0.75, zorder=0)
        
        for j in range(4):  # mark each bandwidth edge
            axes[i].axvline(x=mwi.freq_bw[i, j], color='gray', linestyle=':', linewidth=0.75, zorder=0)
        
        # add shade for each channel
        axes[i].axvspan(xmin=mwi.freq_bw[i, 0], 
                        xmax=mwi.freq_bw[i, 1], 
                        ymin=-10e3, 
                        ymax=10e3, color='gray', alpha=0.2)
        axes[i].axvspan(xmin=mwi.freq_bw[i, 2],
                        xmax=mwi.freq_bw[i, 3], 
                        ymin=-10e3,
                        ymax=10e3,
                        color='gray', alpha=0.2)
        
    # set axis labels
    axes[2].set_ylabel('Sensitivity [dB]')
    axes[-1].set_xlabel('Frequency [GHz]')
        
    plt.savefig(os.path.join(
        os.environ['PATH_PLT'],
        'bandpass_measurement/bandpass_measurement_dsb.png'),
        bbox_inches='tight', dpi=300)
    
    #%% plot sensitivity data (lino, dsb, lin scale)
    fig, axes = plt.subplots(5, 1, sharex='all', figsize=(6, 6))
    axes = axes.flatten(order='F')
    
    fig.suptitle('Linearized and normalized SRF')
    
    plt.subplots_adjust(#left = 0.1,  # the left side of the subplots of the figure
                        right = 0.8,   # the right side of the subplots of the figure
                        #bottom = 0.1,  # the bottom of the subplots of the figure
                        top = 0.925,     # the top of the subplots of the figure
                        #wspace = 0.2,  # the amount of width reserved for space between subplots,
                                       # expressed as a fraction of the average axis width
                        #hspace = 0.2  # the amount of height reserved for space between subplots,
                                      # expressed as a fraction of the average axis height
                        )
    
    for i, channel in enumerate(mwi.channels_int):
        
        # MWI-RX183_DSB_Matlab.xlsx dataset
        axes[i].plot(sen_dsb.data.frequency*1e-3, sen_dsb.data.lino.sel(channel=channel)*100, color='k', linewidth=1,
                     zorder=2)
        
        # y axis settings
        axes[i].set_yticks([0, 0.5])
        axes[i].set_ylim([0, 0.85])
                
        # set x-limit
        axes[i].set_xlim([np.min(mwi.freq_bw)-0.1, np.max(mwi.freq_bw)+0.1])
        
        # annotate channel name
        axes[i].annotate(text=mwi.freq_txt[i], xy=(1.01, 0.5), xycoords='axes fraction', backgroundcolor="None",
                         annotation_clip=False, horizontalalignment='left', verticalalignment='center')
        
        # add vertical lines
        axes[i].axvline(x=mwi.absorpt_line, color='red', linewidth=0.5, zorder=0)  # mark line center
        
        for j in range(2):  # mark left/right channel frequency
            axes[i].axvline(x=mwi.freq_center[i, j], color='gray', linestyle='--', linewidth=0.75, zorder=0)
        
        for j in range(4):  # mark each bandwidth edge
            axes[i].axvline(x=mwi.freq_bw[i, j], color='gray', linestyle=':', linewidth=0.75, zorder=0)
        
        # add shade for each channel
        axes[i].axvspan(xmin=mwi.freq_bw[i, 0], xmax=mwi.freq_bw[i, 1], ymin=-10e3, ymax=10e3, color='gray',
                        alpha=0.2)
        axes[i].axvspan(xmin=mwi.freq_bw[i, 2], xmax=mwi.freq_bw[i, 3], ymin=-10e3, ymax=10e3, color='gray',
                        alpha=0.2)

        # add grid
        axes[i].grid(zorder=-1)

    # set axis labels
    axes[2].set_ylabel('Sensitivity [%]')
    axes[-1].set_xlabel('Frequency [GHz]')
        
    plt.savefig(os.path.join(
        os.environ['PATH_PLT'],
        'bandpass_measurement/bandpass_measurement_dsb_lino.png'), dpi=300)

    #%% plot all linearized SRF with reduction of measurement points
    pd.options.mode.chained_assignment = None 
    reduction_levels = np.arange(1, 6, 1)
    
    n_orig = 1060
    reduction_levels = np.arange(1, 11)
    number_meas = np.floor(n_orig/reduction_levels)
    sample_width =  191.302 - 175.322
    x = sample_width/number_meas*1000
    x = [int(a) for a in x]
    
    colors = cm.get_cmap('viridis', len(reduction_levels)).colors
    
    fig, axes = plt.subplots(5, 1, sharex='all', figsize=(6, 6))
    axes = axes.flatten(order='F')
    
    fig.suptitle('Data reduction of SRF (not normalized)')
    
    plt.subplots_adjust(#left = 0.1,  # the left side of the subplots of the figure
                        right = 0.8,   # the right side of the subplots of the figure
                        bottom = 0.25,  # the bottom of the subplots of the figure
                        top = 0.925,     # the top of the subplots of the figure
                        #wspace = 0.2,  # the amount of width reserved for space between subplots,
                                       # expressed as a fraction of the average axis width
                        #hspace = 0.2  # the amount of height reserved for space between subplots,
                                      # expressed as a fraction of the average axis height
                        )
    
    for i, channel in enumerate(mwi.channels_int):
        
        # MWI-RX183_DSB_Matlab.xlsx dataset
        for j, reduction_level in enumerate(reduction_levels):
            
            srf_red = sen_dsb.data.lino.sel(frequency=sen_dsb.data.frequency[::reduction_level])
            #srf_values = srf_red.iloc[:, 1:].values.copy()
            #srf_red.iloc[:, 1:] = Sensitivity.normalize_srf(srf_values)
            
            axes[i].plot(srf_red.frequency*1e-3, 
                         srf_red.sel(channel=channel)*100, color=colors[j], linewidth=1,
                         zorder=2, label=x[j])
        
        # y axis settings
        axes[i].set_yticks([0, 0.5])
        axes[i].set_ylim([0, 0.85])
                
        # set x-limit
        axes[i].set_xlim([np.min(mwi.freq_bw)-0.1, np.max(mwi.freq_bw)+0.1])
        
        # annotate channel name
        axes[i].annotate(text=mwi.freq_txt[i], xy=(1.01, 0.5), xycoords='axes fraction', backgroundcolor="None",
                         annotation_clip=False, horizontalalignment='left', verticalalignment='center')
        
        # add vertical lines
        axes[i].axvline(x=mwi.absorpt_line, color='red', linewidth=0.5, zorder=0)  # mark line center
        
        for j in range(2):  # mark left/right channel frequency
            axes[i].axvline(x=mwi.freq_center[i, j], color='gray', linestyle='--', linewidth=0.75, zorder=0)
        
        for j in range(4):  # mark each bandwidth edge
            axes[i].axvline(x=mwi.freq_bw[i, j], color='gray', linestyle=':', linewidth=0.75, zorder=0)
        
        # add shade for each channel
        axes[i].axvspan(xmin=mwi.freq_bw[i, 0], xmax=mwi.freq_bw[i, 1], ymin=-10e3, ymax=10e3, color='gray',
                        alpha=0.2)
        axes[i].axvspan(xmin=mwi.freq_bw[i, 2], xmax=mwi.freq_bw[i, 3], ymin=-10e3, ymax=10e3, color='gray',
                        alpha=0.2)

        # add grid
        axes[i].grid(zorder=-1)
    
    # add legend below
    axes[-1].legend(bbox_to_anchor=(0.5, -1), ncol=5, loc='upper center', frameon=True, fontsize=8, title='Sampling interval [MHz]')

    # set axis labels
    axes[2].set_ylabel('Sensitivity')
    axes[-1].set_xlabel('Frequency [GHz]')
        
    plt.savefig(os.path.join(
        os.environ['PATH_PLT'],
        'bandpass_measurement/bandpass_measurement_dsb_lino_data_reduction.png'), 
        dpi=300)
    
    #%% calculate top-hat function
    sen_dsb.data['top-hat'] = xr.zeros_like(sen_dsb.data.lino)
    
    for i, channel in enumerate(mwi.channels_int):
        
        ix_in = ((sen_dsb.data.frequency > mwi.freq_bw_MHz[i, 0]) & \
                (sen_dsb.data.frequency < mwi.freq_bw_MHz[i, 1])) | \
                ((sen_dsb.data.frequency > mwi.freq_bw_MHz[i, 2]) & \
                (sen_dsb.data.frequency < mwi.freq_bw_MHz[i, 3]))
        
        sen_dsb.data['top-hat'][ix_in, i] = 1
    
    sen_dsb.data['top-hat'] = sen_dsb.data['top-hat']/sen_dsb.data['top-hat'].sum('frequency')
    
    #%% check, that sum along frequency is one
    assert np.all((sen_dsb.data['top-hat'].sum('frequency').values - 1) < 1e-10)
    assert np.all((sen_dsb.data.lino.sum('frequency').values - 1) < 1e-10)
    
    #%% plot sensitivity lino zoomed in to the bandpass region together with
    # top-hat function
    fig, axes = plt.subplots(2, 5, sharey=True, figsize=(7, 4), 
                             constrained_layout=True)
    
    for i, ax in enumerate(fig.axes):
        ax.annotate(f'({abc[i]})', xycoords='axes fraction', va='top',
                    ha='left', xy=(0.01, 1.01))
                
    #axes2 = np.full_like(axes, dtype='object', fill_value='')
    #for i in range(axes.shape[0]):
    #    for j in range(axes.shape[1]):
    #        axes2[i, j] = axes[i, j].twinx()
    
    #for ax2 in axes2[:, :4].flatten():
    #    ax2.set_yticklabels([])
        
    for ax in fig.axes:
        ax.spines.top.set_visible(False)
        ax.spines.right.set_visible(False)

    for i, channel in enumerate(mwi.channels_int):
        for j in range(2):
                       
            ax = axes[j, i]
            #ax2 = axes2[j, i]
        
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
            
            # mark where top-hat is larger than srf and in bandpass region
            #ix = (sen_dsb.data['top-hat'].sel(channel=channel) > \
            #    sen_dsb.data.lino.sel(channel=channel)) & \
            #    (sen_dsb.data['top-hat'].sel(channel=channel) > 0)
            #ax.fill_between(x=sen_dsb.data.frequency.where(ix)*1e-3,
            #                y1=sen_dsb.data['top-hat'].sel(channel=channel).where(ix)*100, 
            #                y2=sen_dsb.data.lino.sel(channel=channel).where(ix)*100, 
            #                color='red', linewidths=0, step='mid')
            
            # mark where top-hat is smaller than srf and in bandpass region
            #ix = (sen_dsb.data['top-hat'].sel(channel=channel) < \
            #    sen_dsb.data.lino.sel(channel=channel)) & \
            #    (sen_dsb.data['top-hat'].sel(channel=channel) > 0)
            #ax.fill_between(x=sen_dsb.data.frequency.where(ix)*1e-3,
            #                y1=sen_dsb.data['top-hat'].sel(channel=channel).where(ix)*100, 
            #                y2=sen_dsb.data.lino.sel(channel=channel).where(ix)*100, 
            #                color='green', linewidths=0, step='mid')
            
            # MWI-RX183_DSB_Matlab.xlsx dataset
            ax.plot(sen_dsb.data.frequency*1e-3, 
                    sen_dsb.data.lino.sel(channel=channel)*100, 
                    color='k', linewidth=1)
            
            # MWI-RX183_DSB_Matlab.xlsx dataset in dB
            #ax2.plot(sen_dsb.data.frequency*1e-3, 
            #        sen_dsb.data.raw.sel(channel=channel), 
            #        color='skyblue', linewidth=1)
            
            #ax2.set_ylim(-40, 0)
            
            # y axis settings
            ax.set_yticks([0, 0.25, 0.5, 0.75, 1])
            ax.set_ylim([0, 0.85])
            
            # set x-limit
            ax.set_xticks(np.arange(0, 300))
            dx = 1.25 - mwi.bandwidth[i]/2
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
    #axes2[1, -1].set_ylabel('Sensitivity [dB]', color='skyblue')
    axes[1, 0].set_xlabel('Frequency [GHz]')
        
    plt.savefig(os.path.join(
        os.environ['PATH_PLT'],
        'bandpass_measurement/bandpass_measurement_dsb_lino_zoom.png'), 
        bbox_inches='tight', dpi=300)

    plt.close('all')