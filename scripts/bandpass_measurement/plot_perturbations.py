

import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
import os
import sys
sys.path.append(f'{os.environ["PATH_PHD"]}/projects/mwi_bandpass_effects/scripts')
from path_setter import path_plot, path_data
from importer import Sensitivity
from mwi_info import mwi


if __name__ == '__main__':
    
    # read bandpass measurement
    sen_dsb = Sensitivity(filename='MWI-RX183_DSB_Matlab.xlsx')
    ds_sen = sen_dsb.data
    
    # perturbed = raw + residual
    # ds_per = ds_raw + ds_res
    
    #%% create xr dataset with perturbations
    pert_names = ['linear1', 'linear2', 'inbalance1', 'inbalance2', 'ripple1', 'ripple2']
    offset_magnitude = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.7, 1.0, 1.5, 2.0])
    ds_res = xr.Dataset()
    ds_res.coords['frequency'] = ds_sen.frequency.values
    ds_res.coords['channel'] = ds_sen.channel.values
    ds_res.coords['magnitude'] = offset_magnitude
    for n in pert_names:
        ds_res[n] = (list(ds_res.dims.keys()), np.zeros(shape=list(ds_res.dims.values())))

    # fill perturbations
    for i, channel in enumerate(mwi.channels_str):
        for j, magn in enumerate(offset_magnitude):
            
            # bandwidth frequencies in MHz
            f0, f1, f2, f3 = (np.round(mwi.freq_bw[i], 3)*1000).astype(np.int)
            left_ix = np.where((ds_res.frequency.values > f0) & (ds_res.frequency.values < f1))[0]
            right_ix = np.where((ds_res.frequency.values > f2) & (ds_res.frequency.values < f3))[0]
            
            y = [1, -1]
            
            for k, ix in enumerate([left_ix, right_ix]):
                
                # linear slope
                ds_res.linear1[ix, i, j] = np.linspace(-magn, magn, len(ix)) * y[k]
                ds_res.linear2[ix, i, j] = np.linspace(magn, -magn, len(ix)) * y[k]
                
                # inbalance
                if k == 0: # left
                    ds_res.inbalance1[ix, i, j] = magn
                if k == 1:  # right
                    ds_res.inbalance2[ix, i, j] = magn
    
                # define new ripples
                ds_res.ripple1[ix, i, j] = magn*np.sin(np.linspace(0, 2*np.pi, len(ix))) * y[k]
                ds_res.ripple2[ix, i, j] = -magn*np.sin(np.linspace(0, 2*np.pi, len(ix))) * y[k]
    
    ds_res.to_netcdf(path_data+'sensitivity/perturbed/MWI-RX183_DSB_Matlab_residual.nc')
    
    # comment: added 'magnitude' to ds_res. Scripts below are only for magnitude 0.3 (!)
    # if plots need to be made new, then take this into account!
    
    #%% apply perturbations on raw data
    ds_per_log = xr.Dataset()
    ds_per_log.coords['frequency'] = ds_sen.frequency.values
    ds_per_log.coords['channel'] = ds_sen.channel.values
    ds_per_log.coords['magnitude'] = offset_magnitude
    for name in pert_names:
        for j, magn in enumerate(offset_magnitude):
            ds_per_log[name] = ds_res[name] + ds_sen['raw']
    
    # linearize
    ds_per_li = xr.Dataset()
    ds_per_li.coords['frequency'] = ds_sen.frequency.values
    ds_per_li.coords['channel'] = ds_sen.channel.values
    ds_per_log.coords['magnitude'] = offset_magnitude
    for name in pert_names:
        ds_per_li[name] = 10**(0.1*ds_per_log[name])
        
    # linearize and normalize
    ds_per_lino = xr.Dataset()
    ds_per_lino.attrs = {'comment': 'perturbations in [dB] were added to raw data, then linearized and normalized.'}
    ds_per_lino.coords['frequency'] = ds_sen.frequency.values
    ds_per_lino.coords['channel'] = ds_sen.channel.values
    ds_per_lino.coords['magnitude'] = offset_magnitude
    for name in pert_names:
        ds_per_lino[name] = ds_per_li[name]/ds_per_li[name].sum('frequency')
    ds_per_lino['orig'] = ds_sen['lino']
    
    # write to netCDF file
    ds_per_lino.to_netcdf(path_data+'sensitivity/perturbed/MWI-RX183_DSB_Matlab_perturb.nc')
    
    #%% plot settings
    cols = ['#577590', '#577590',
            '#f3722c', '#f3722c',
            '#90be6d', '#90be6d']
    
    lst = ['-', '--', '-', '--', '-', '--']
    
    #%% plot pure spectral perturbations for a single frequency and magnitude
    # choose first a frequency and a magnitude, which should be shown
    mag = 2
    channel = 18
    i = 4  # channel index: 0, 1, 2, 3, 4
    
    fig, ax = plt.subplots(1, 1, sharex='all', figsize=(5, 4), constrained_layout=True)
    
    for j, name in enumerate(pert_names):
        
        ax.plot(ds_res['frequency']/1e3, ds_res[name].sel(channel=channel, magnitude=mag), color=cols[j], linewidth=2, label=name, linestyle=lst[j])
    
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
    for j in range(2):  # mark left/right channel frequency
        ax.annotate('|---- 1.5 GHz ----|', xy=(mwi.freq_center[i, j], 1.01), xycoords=('data', 'axes fraction'), ha='center', va='bottom')
        
    # set axis labels
    ax.set_ylabel('Sensitivity [dB]')
    ax.set_xlabel('Frequency [GHz]')
        
    # add legend below
    leg = ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.4), ncol=3, frameon=True)
    
    plt.savefig(path_plot + 'bandpass_measurement/perturbation/perturbation_single_%1.1f.png'%mag, bbox_inches='tight', dpi=300)
    
    plt.close('all')
    
    #%% plot pure spectral perturbations  
    for k, mag in enumerate(offset_magnitude):
        
        fig, axes = plt.subplots(5, 1, sharex='all', figsize=(5, 4), constrained_layout=True)
        axes = axes.flatten(order='F')
        
        for i, channel in enumerate(mwi.channels_str):
            
            for j, name in enumerate(pert_names):
                
                axes[i].plot(ds_res['frequency']/1e3, ds_res[name].isel(channel=i, magnitude=k), color=cols[j], linewidth=1, label=name, linestyle=lst[j])
            
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
    i = 4  # channel index: 0, 1, 2, 3, 4
    pert_kind = '2'  # plots only one kind of perturbation, to keep the plot clean, either 1 or 2
            
    fig, ax = plt.subplots(1, 1, sharex='all', figsize=(7, 3), constrained_layout=True, sharey=True)
                
    # original
    ax.plot(ds_sen['frequency']/1e3, 100*ds_sen['lino'].isel(channel=i), color='k', linewidth=1, label='original')
    
    for j, name in enumerate(pert_names):
        
        if pert_kind in name:
            ax.plot(ds_per_lino['frequency']/1e3, 100*ds_per_lino[name].sel(channel=channel, magnitude=mag), color=cols[j], linewidth=2, label=name, linestyle=lst[j])
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
    for k, mag in enumerate(offset_magnitude):
        
        fig, axes = plt.subplots(5, 1, sharex='all', figsize=(5, 5), constrained_layout=True, sharey=True)
        axes = axes.flatten(order='F')
            
        for i, channel in enumerate(mwi.channels_str):
            
            # original
            axes[i].plot(ds_sen['frequency']/1e3, 100*ds_sen['lino'].isel(channel=i), color='k', linewidth=0.9, label='original')
            
            for j, name in enumerate(pert_names):
                
                axes[i].plot(ds_per_lino['frequency']/1e3, 100*ds_per_lino[name].isel(channel=i, magnitude=k), color=cols[j], linewidth=0.5, label=name, linestyle=lst[j])
            
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
    for k, mag in enumerate(offset_magnitude):
    
        fig, axes = plt.subplots(5, 1, sharex='all', figsize=(9, 6), constrained_layout=True)
        axes = axes.flatten(order='F')
            
        for i, channel in enumerate(mwi.channels_str):
            
            # original
            axes[i].plot(ds_sen['frequency']/1e3, ds_sen['raw'].isel(channel=i), color='k', linewidth=0.9, label='original')
            
            for j, name in enumerate(pert_names):
                
                axes[i].plot(ds_per_log['frequency']/1e3, ds_per_log[name].isel(channel=i, magnitude=k), color=cols[j], linewidth=0.5, label=name)
            
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
