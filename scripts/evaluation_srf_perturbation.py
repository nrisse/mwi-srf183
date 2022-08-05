"""
Influence of perturbatino of srf on the mwi observation

- calculation method is not checked here, only how the SRF perturbations change
  the MWI observation!
"""


import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import xarray as xr
import os
import sys
sys.path.append(f'{os.environ["PATH_PHD"]}/projects/mwi_bandpass_effects/scripts')
from mwi_info import mwi
from path_setter import path_data, path_plot

plt.ion()


if __name__ == '__main__':
    
    # read nc files
    ds_com = xr.open_dataset(path_data + 'brightness_temperature/'+
                             'TB_radiosondes_2019_MWI.nc')    
    
    #%% calculate statistics (mean absolute error)
    ds_com_dtb_mae = np.fabs(ds_com.dtb_mwi_err).mean('profile')
    ds_com_dtb_std = np.fabs(ds_com.dtb_mwi_err).std('profile')
    
    #%% statistics
    magnitude = 2
    for channel in ds_com.channel.values:
        print('\n', channel)
        for err_type in ds_com_dtb_mae.err_type.values:
            mae = np.round(ds_com_dtb_mae.sel(
                channel=channel, 
                magnitude=magnitude, 
                err_type=err_type).values.item(), 2)
            print(f'{err_type}: {mae}')
    
    #%% color for figures
    col_lin = '#577590'
    col_imb = '#f3722c'
    col_rip = '#90be6d'
    
    #%% histogram of absolute difference
    step = 0.002
    bins = np.arange(0, 10+step, step)
    mag = 0.3
    
    fig, axes = plt.subplots(5, 1, figsize=(4, 5), sharex=True, sharey=True, constrained_layout=True)
    
    axes[2].set_ylabel('Absolute frequency')
    axes[-1].set_xlabel(r'abs$(TB_{obs} - TB_{obs,pert})$ [K]')
    
    for ax in axes.flatten():
        
        # x axis
        #ax.set_yticks(ticks=np.arange(0, 600, 25), minor=False)
        #ax.set_yticks(ticks=np.arange(0, 150, 5), minor=True)
        
        # y axis
        ax.set_xticks(ticks=np.arange(-0.5, 0.5, 0.1), minor=False)
        ax.set_xticks(ticks=np.arange(-0.5, 0.5, 0.025), minor=True)

        ax.axhline(y=0, color='k', linewidth=1, alpha=0.5)
        
        if mag == 0.3:
            ax.set_xlim([0, 0.15])
            ax.set_ylim([0, 200])
    
    # annotate channel name
    for i, ax in enumerate(axes):
        ax.annotate(text=mwi.freq_txt[i].split('\n')[0], xy=(1.05, 1), xycoords='axes fraction', backgroundcolor="w",
                    annotation_clip=False, horizontalalignment='left', verticalalignment='top')
    
    kwargs = dict(bins=bins, linewidth=0, alpha=0.75)
    for i, channel in enumerate(mwi.channels_int):
        
        kwargs_sel = dict(channel=channel, magnitude=mag)
        axes[i].hist(
            np.abs(ds_com.dtb_mwi_err.sel(err_type='linear1', **kwargs_sel)), 
                     color=col_lin, **kwargs)
        
        axes[i].hist(
            np.abs(ds_com.dtb_mwi_err.sel(err_type='imbalance1', **kwargs_sel)), 
                     color=col_imb, **kwargs)
        
        axes[i].hist(
            np.abs(ds_com.dtb_mwi_err.sel(err_type='ripple1', **kwargs_sel)), 
                     color=col_rip, **kwargs)
    
        # annotate mae
        mae_lin = ds_com_dtb_mae.sel(err_type='linear1', **kwargs_sel)
        mae_inb = ds_com_dtb_mae.sel(err_type='imbalance1', **kwargs_sel)
        mae_rip = ds_com_dtb_mae.sel(err_type='ripple1', **kwargs_sel)
        
        std_lin = ds_com_dtb_std.sel(err_type='linear1', **kwargs_sel)
        std_inb = ds_com_dtb_std.sel(err_type='imbalance1', **kwargs_sel)
        std_rip = ds_com_dtb_std.sel(err_type='ripple1', **kwargs_sel)
        
        # annotate mae and std
        kwargs_a = dict(xycoords='axes fraction', ha='left', va='top')
        axes[i].annotate('%1.2f $\pm$ %1.3f K'%(mae_lin, std_lin), 
                         color=col_lin, xy=(1.05, 0.6), **kwargs_a)
        axes[i].annotate('%1.2f $\pm$ %1.3f K'%(mae_inb, std_inb), 
                         color=col_imb, xy=(1.05, 0.4), **kwargs_a)
        axes[i].annotate('%1.2f $\pm$ %1.3f K'%(mae_rip, std_rip), 
                         color=col_rip, xy=(1.05, 0.2), **kwargs_a)
    
    # legend below
    patches = []
    labels = ['linear', 'imbalance', 'ripple']
    colors = [col_lin, col_imb, col_rip]
    for i, label in enumerate(labels):
        patches.append(mpatches.Patch(color=colors[i], label=label))
    leg = axes[-1].legend(handles=patches, bbox_to_anchor=(0.5, -0.7), 
                          loc='upper center', frameon=False, ncol=3)
    plt.setp(leg.get_title(),fontsize=6)
    
    print('saving magnitude %1.1f'%mag)
    plt.savefig(path_plot+'srf_perturbation/abs_hist_%1.1f.png'%mag, dpi=300)
    
    plt.close('all')
    
    #%% dependence on offset magnitude
    fig, axes = plt.subplots(5, 1, figsize=(3, 5), sharex=True, sharey=True,
                             constrained_layout=True)
    
    axes[2].set_ylabel(r'MAE$(TB_{obs} - TB_{obs,pert})$ [K]')
    axes[-1].set_xlabel('Perturbation magnitude [dB]')

    for ax in axes.flatten():
        
        # x axis
        ax.set_yticks(ticks=np.arange(0, 1.5, 0.5), minor=False)
        ax.set_yticks(ticks=np.arange(0, 1.5, 0.1), minor=True)
        
        # y axis
        ax.set_xticks(ticks=np.arange(0, 2.5, 0.5), minor=False)
        ax.set_xticks(ticks=np.arange(0, 2.5, 0.1), minor=True)
                
        ax.set_xlim([0, 2.1])
        ax.set_ylim([0, 1])
        
    # annotate channel name
    for i, ax in enumerate(axes):
        ax.annotate(text=mwi.freq_txt[i].split('\n')[0], xy=(0.1, 0.8), xycoords='axes fraction', backgroundcolor="w",
                    annotation_clip=False, horizontalalignment='left', verticalalignment='top', fontsize=8)
    
    pert_names = ['linear1', 'imbalance1', 'ripple1']
    colors = [col_lin, col_imb, col_rip]
    for i, channel in enumerate(ds_com.channel):
        for j, err_type in enumerate(pert_names):
            axes[i].errorbar(ds_com_dtb_mae.magnitude, 
                             ds_com_dtb_mae.sel(channel=channel, 
                                                err_type=err_type), 
                             yerr=ds_com_dtb_std.sel(channel=channel, 
                                                     err_type=err_type), 
                             elinewidth=0.5, capsize=2, color=colors[j],
                             barsabove=True, label=err_type.replace('1', ''))
        
    axes[0].legend(bbox_to_anchor=(0.5, 1.2), loc='lower center', 
                   frameon=False, fontsize=8, ncol=3)
    
    plt.savefig(path_plot+'srf_perturbation/mae_vs_magnitude.png', dpi=300)
    
    plt.close('all')
    
    #%%
    plt.close('all')
