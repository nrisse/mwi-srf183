

import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
import os
import sys
sys.path.append(f'{os.environ["PATH_PHD"]}/projects/mwi_bandpass_effects/scripts')
from path_setter import path_plot, path_data
from mwi_info import mwi


if __name__ == '__main__':
    
    # read dataset with different perturbed srf
    ds_com = xr.open_dataset(path_data+'/brightness_temperature/'+
                             'TB_radiosondes_2019_MWI.nc')
    
    # remove frequencies, at which no original srf was measured
    # this makes the line plots nicer, becuase otherwise bandpass frequencies
    # cause gaps in the lines
    ds_com = ds_com.sel(frequency=~np.isnan(ds_com.srf_orig.sel(channel=14).values))
    
    #%% plot settings
    cols = ['#577590', '#577590',
            '#f3722c', '#f3722c',
            '#90be6d', '#90be6d']
    
    lst = ['-', '--', '-', '--', '-', '--']
    
    #%% plot pure spectral perturbations for a single frequency and magnitude
    # choose first a frequency and a magnitude, which should be shown
    mag = 1
    channel = 18
    i = 4  # channel index: 0, 1, 2, 3, 4
    
    fig, ax = plt.subplots(1, 1, sharex='all', figsize=(5, 4), constrained_layout=True)
    
    for j, err_type in enumerate(ds_com.err_type.values):
        
        ax.plot(ds_com['frequency']/1e3, 
                ds_com.srf_err_offset_dB.sel(channel=channel, magnitude=mag, 
                                      err_type=err_type), 
                color=cols[j], linewidth=2, label=err_type, linestyle=lst[j])
    
    # y axis settings
    ax.set_yticks([-mag, 0, mag])
    ax.set_ylim([-mag-0.1*mag, mag+0.1*mag])
    
    # set x-limit
    ax.set_xticks(np.arange(170, 190, 1))
    ax.set_xlim([183.31-3-0.1, 183.31+3+0.1])
    
    # annotate channel name
    ax.annotate(text=mwi.freq_txt[i], xy=(0.5, 1.01), xycoords='axes fraction', backgroundcolor='None',
                     annotation_clip=False, horizontalalignment='center', verticalalignment='bottom')
    
    # add vertical lines
    ax.axvline(x=mwi.absorpt_line, color='k', linewidth=1, zorder=0)  # mark line center
    
    #for j in range(2):  # mark left/right channel frequency
    #    ax.axvline(x=mwi.freq_center[i, j], color='gray', linestyle='--', linewidth=0.75, zorder=0)
    
    #for j in range(4):  # mark each bandwidth edge
    #    ax.axvline(x=mwi.freq_bw[i, j], color='gray', linestyle=':', linewidth=0.75, zorder=0)
    
    # add shade for each channel
    ax.axvspan(xmin=mwi.freq_bw[i, 0], xmax=mwi.freq_bw[i, 1], ymin=-10e3, ymax=10e3, color='gray',
                    alpha=0.2, linewidth=0)
    ax.axvspan(xmin=mwi.freq_bw[i, 2], xmax=mwi.freq_bw[i, 3], ymin=-10e3, ymax=10e3, color='gray',
                    alpha=0.2, linewidth=0)
    
    # annotate bandwidth
    #for j in range(2):  # mark left/right channel frequency
    #    ax.annotate('|---- 1.5 GHz ----|', xy=(mwi.freq_center[i, j], 1.01), xycoords=('data', 'axes fraction'), ha='center', va='bottom')
        
    # set axis labels
    ax.set_ylabel('Sensitivity [dB]')
    ax.set_xlabel('Frequency [GHz]')
        
    # add legend below
    leg = ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.4), ncol=3, frameon=True)
    
    plt.savefig(path_plot + 'bandpass_measurement/perturbation/perturbation_single_%1.1f.png'%mag, 
                bbox_inches='tight', dpi=300)
    
    plt.close('all')
    
    #%% plot pure spectral perturbations  
    for k, mag in enumerate(ds_com.magnitude):
        
        fig, axes = plt.subplots(5, 1, sharex='all', figsize=(5, 4), constrained_layout=True)
        axes = axes.flatten(order='F')
        
        for i, channel in enumerate(ds_com.channel.values):
            
            for j, err_type in enumerate(ds_com.err_type.values):
                
                axes[i].plot(ds_com['frequency']/1e3,
                             ds_com.srf_err_offset_dB.sel(channel=channel, 
                                                          magnitude=mag,
                                                          err_type=err_type), 
                             color=cols[j], linewidth=1, label=err_type, 
                             linestyle=lst[j])
            
            # y axis settings
            axes[i].set_yticks([-mag, 0, mag])
            axes[i].set_ylim([-mag-0.1*mag, mag+0.1*mag])
                    
            # set x-limit
            axes[i].set_xticks(np.arange(160, 200, 2))
            axes[i].set_xlim([np.min(mwi.freq_bw)-0.1, np.max(mwi.freq_bw)+0.1])
            
            # annotate channel name
            axes[i].annotate(text=mwi.freq_txt[i], xy=(1.01, 0.5), xycoords='axes fraction', backgroundcolor='None',
                             annotation_clip=False, horizontalalignment='left', verticalalignment='center')
            
            # add vertical lines
            axes[i].axvline(x=mwi.absorpt_line, color='k', linewidth=1, zorder=0)  # mark line center
            
            #for j in range(2):  # mark left/right channel frequency
            #    axes[i].axvline(x=mwi.freq_center[i, j], color='gray', linestyle='--', linewidth=0.75, zorder=0)
            
            #for j in range(4):  # mark each bandwidth edge
            #    axes[i].axvline(x=mwi.freq_bw[i, j], color='gray', linestyle=':', linewidth=0.75, zorder=0)
            
            # add shade for each channel
            axes[i].axvspan(xmin=mwi.freq_bw[i, 0], xmax=mwi.freq_bw[i, 1], ymin=-10e3, ymax=10e3, color='gray',
                            alpha=0.2, linewidth=0)
            axes[i].axvspan(xmin=mwi.freq_bw[i, 2], xmax=mwi.freq_bw[i, 3], ymin=-10e3, ymax=10e3, color='gray',
                            alpha=0.2, linewidth=0)
            
        # set axis labels
        axes[2].set_ylabel('Sensitivity [dB]')
        axes[-1].set_xlabel('Frequency [GHz]')
            
        # add legend below
        leg = axes[0].legend(loc='lower center', bbox_to_anchor=(0.5, 1.1), ncol=3, frameon=False)
        leg.set_in_layout(False)
        # trigger a draw so that constrained_layout is executed once
        # before we turn it off when printing....
        fig.canvas.draw()
        # we want the legend included in the bbox_inches='tight' calcs.
        leg.set_in_layout(True)
        # we don't want the layout to change at this point.
        fig.set_constrained_layout(False)
        
        plt.savefig(path_plot + 'bandpass_measurement/perturbation/perturbation_%1.1f.png'%mag, bbox_inches='tight', dpi=300)
    
    plt.close('all')
    
    #%% plot perturbed data for single frequency and magnitude
    # choose first a frequency and a magnitude, which should be shown
    mag = 0.5
    channel = 18
    pert_kind = '1'  # plots only one kind of perturbation, to keep the plot clean, either 1 or 2
            
    fig, ax = plt.subplots(1, 1, sharex='all', figsize=(7, 3), constrained_layout=True, sharey=True)
                
    # original
    ax.plot(ds_com['frequency']/1e3, 
            100*ds_com['srf_orig'].sel(channel=channel), color='k', 
            linewidth=1, label='original')
    
    for j, err_type in enumerate(ds_com.err_type.values):
        
        if pert_kind in err_type:
            ax.plot(ds_com['frequency']/1e3, 
                    100*ds_com.srf_err.sel(channel=channel, magnitude=mag,
                                           err_type=err_type), 
                    color=cols[j], linewidth=2, label=err_type, linestyle=lst[j])
        else:
            continue
    
    # y axis settings
    ax.set_ylim([0, 1])
            
    # set x-limit
    ax.set_xticks(np.arange(170, 190, 1))
    ax.set_xlim([183.31-3-0.1, 183.31+3+0.1])
    
    # annotate channel name
    ax.annotate(text=mwi.freq_txt[i], xy=(0.5, 1.01), xycoords='axes fraction', backgroundcolor='None',
                     annotation_clip=False, horizontalalignment='center', verticalalignment='bottom')
    
    # add vertical lines
    ax.axvline(x=mwi.absorpt_line, color='k', linewidth=1, zorder=0)  # mark line center
    
    #for j in range(2):  # mark left/right channel frequency
    #    ax.axvline(x=mwi.freq_center[i, j], color='gray', linestyle='--', linewidth=0.75, zorder=0)
    
    #for j in range(4):  # mark each bandwidth edge
    #    ax.axvline(x=mwi.freq_bw[i, j], color='gray', linestyle=':', linewidth=0.75, zorder=0)
    
    # add shade for each channel
    ax.axvspan(xmin=mwi.freq_bw[i, 0], xmax=mwi.freq_bw[i, 1], ymin=-10e3, ymax=10e3, color='gray',
                    alpha=0.2, linewidth=0)
    ax.axvspan(xmin=mwi.freq_bw[i, 2], xmax=mwi.freq_bw[i, 3], ymin=-10e3, ymax=10e3, color='gray',
                    alpha=0.2, linewidth=0)
        
    # annotate bandwidth
    for j in range(2):  # mark left/right channel frequency
        ax.annotate('|---- 1.5 GHz ----|', xy=(mwi.freq_center[i, j], 1.01), xycoords=('data', 'axes fraction'), ha='center', va='bottom')
        
    # set axis labels
    ax.set_ylabel('Sensitivity [%]')
    ax.set_xlabel('Frequency [GHz]')
        
    # add legend below
    leg = ax.legend(loc='center left', bbox_to_anchor=(1.1, 0.5), ncol=1, frameon=False)
    
    plt.savefig(path_plot + 'bandpass_measurement/perturbation/perturbed_sensitivity_linear_single_%1.1f_kind%s.png'%(mag, pert_kind), bbox_inches='tight', dpi=300)
    
    plt.close('all')
    
    #%% plot perturbed data
    for k, mag in enumerate(ds_com.magnitude.values):
        
        fig, axes = plt.subplots(5, 1, sharex='all', figsize=(5, 5), constrained_layout=True, sharey=True)
        axes = axes.flatten(order='F')
            
        for i, channel in enumerate(ds_com.channel.values):
            
            # original
            axes[i].plot(ds_com['frequency']/1e3, 
                         100*ds_com['srf_orig'].sel(channel=channel), 
                         color='k', linewidth=0.9, label='original')
            
            for j, err_type in enumerate(ds_com.err_type.values):
                
                axes[i].plot(ds_com['frequency']/1e3, 
                             100*ds_com.srf_err.sel(channel=channel, 
                                                       magnitude=mag,
                                                       err_type=err_type),
                             color=cols[j], linewidth=0.5, label=err_type, 
                             linestyle=lst[j])
            
            # y axis settings
            axes[i].set_ylim([0, 1.1])
                    
            # set x-limit
            axes[i].set_xticks(np.arange(160, 200, 2))
            axes[i].set_xlim([np.min(mwi.freq_bw)-0.1, np.max(mwi.freq_bw)+0.1])
            
            # annotate channel name
            axes[i].annotate(text=mwi.freq_txt[i], xy=(1.01, 0.5), xycoords='axes fraction', backgroundcolor='None',
                             annotation_clip=False, horizontalalignment='left', verticalalignment='center')
            
            # add vertical lines
            axes[i].axvline(x=mwi.absorpt_line, color='k', linewidth=1, zorder=0)  # mark line center
            
            #for j in range(2):  # mark left/right channel frequency
            #    axes[i].axvline(x=mwi.freq_center[i, j], color='gray', linestyle='--', linewidth=0.75, zorder=0)
            
            #for j in range(4):  # mark each bandwidth edge
            #    axes[i].axvline(x=mwi.freq_bw[i, j], color='gray', linestyle=':', linewidth=0.75, zorder=0)
            
            # add shade for each channel
            axes[i].axvspan(xmin=mwi.freq_bw[i, 0], xmax=mwi.freq_bw[i, 1], ymin=-10e3, ymax=10e3, color='gray',
                            alpha=0.2, linewidth=0)
            axes[i].axvspan(xmin=mwi.freq_bw[i, 2], xmax=mwi.freq_bw[i, 3], ymin=-10e3, ymax=10e3, color='gray',
                            alpha=0.2, linewidth=0)
            
        # set axis labels
        axes[2].set_ylabel('Sensitivity [%]')
        axes[-1].set_xlabel('Frequency [GHz]')
            
        # add legend below
        leg = axes[0].legend(loc='lower center', bbox_to_anchor=(0.5, 1.1), ncol=3, frameon=False)
        leg.set_in_layout(False)
        # trigger a draw so that constrained_layout is executed once
        # before we turn it off when printing....
        fig.canvas.draw()
        # we want the legend included in the bbox_inches='tight' calcs.
        leg.set_in_layout(True)
        # we don't want the layout to change at this point.
        fig.set_constrained_layout(False)
        
        plt.savefig(path_plot + 'bandpass_measurement/perturbation/perturbed_sensitivity_linear_%1.1f.png'%mag, bbox_inches='tight', dpi=300)
    
    plt.close('all')
    
    #%% plot perturbed data
    for k, mag in enumerate(ds_com.magnitude):
    
        fig, axes = plt.subplots(5, 1, sharex='all', figsize=(9, 6), constrained_layout=True)
        axes = axes.flatten(order='F')
            
        for i, channel in enumerate(ds_com.channel):
            
            # original
            axes[i].plot(ds_com['frequency']/1e3, 
                         ds_com['srf_orig'].isel(channel=i), color='k', 
                         linewidth=0.9, label='original')
            
            for j, err_type in enumerate(ds_com.err_type.values):
                
                axes[i].plot(ds_com['frequency']/1e3, 
                             ds_com.srf_err.sel(channel=channel, 
                                                magnitude=mag,
                                                err_type=err_type),
                             color=cols[j], linewidth=0.5, label=err_type)
            
            # y axis settings
            axes[i].set_ylim([-4, 0.5])
                    
            # set x-limit
            axes[i].set_xlim([np.min(mwi.freq_bw)-0.1, np.max(mwi.freq_bw)+0.1])
            
            # annotate channel name
            axes[i].annotate(text=mwi.freq_txt[i], xy=(1.01, 0.5), xycoords='axes fraction', backgroundcolor='None',
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
        axes[2].set_ylabel('Sensitivity [dB]')
        axes[-1].set_xlabel('Frequency [GHz]')
            
        # add legend below
        leg = axes[-1].legend(loc='upper center', bbox_to_anchor=(0.9, -0.4), ncol=3)
        leg.set_in_layout(False)
        # trigger a draw so that constrained_layout is executed once
        # before we turn it off when printing....
        fig.canvas.draw()
        # we want the legend included in the bbox_inches='tight' calcs.
        leg.set_in_layout(True)
        # we don't want the layout to change at this point.
        fig.set_constrained_layout(False)
        
        plt.savefig(path_plot + 'bandpass_measurement/perturbation/perturbed_sensitivity_db_%1.1f.svg'%mag, 
                    bbox_inches='tight', dpi=300)
        
    plt.close('all')

    #%%
    plt.close('all')
