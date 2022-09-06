"""
Comparison of virtual MWI observation with estimates based on a top-hat SRF
and selected frequencies.
"""


import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import xarray as xr
from string import ascii_lowercase as abc
import os
from helpers import mwi, wyo, colors
from dotenv import load_dotenv

load_dotenv()
plt.ion()


if __name__ == '__main__':
    
    # read data
    ds_com_rsd = xr.open_dataset(os.path.join(
        os.environ['PATH_BRT'],
        'TB_radiosondes_2019_MWI.nc'))
    
    ds_com_era = xr.open_dataset(os.path.join(
        os.environ['PATH_BRT'],
        'TB_era5_MWI.nc'))
    ds_com_era = ds_com_era.stack({'profile': ('grid_x', 'grid_y')})
    
    ds_com_erh = xr.open_dataset(os.path.join(
        os.environ['PATH_BRT'],
        'TB_era5_hyd_MWI.nc'))
    ds_com_erh = ds_com_erh.stack({'profile': ('grid_x', 'grid_y')})
    
    c_list = [colors.colors_rs[p] for p in ds_com_rsd.station.values]
    
    #%% print some statistics
    for channel in ds_com_rsd.channel:
        for est_type in ds_com_rsd.est_type:
            s = dict(channel=channel, est_type=est_type)

            dtb_max_rsd = np.round(np.abs(ds_com_rsd.dtb_mwi_est)
                                   .max('profile').sel(**s).item(), 1)
            
            dtb_max_era = np.round(np.abs(ds_com_era.dtb_mwi_est)
                                   .max('profile').sel(**s).item(), 1)
            
            dtb_max_erh = np.round(np.abs(ds_com_erh.dtb_mwi_est)
                                   .max('profile').sel(**s).item(), 1)
            
            print(f'channel {channel.item()}, est_type {est_type.item()}: '+
                  f'{dtb_max_rsd} | {dtb_max_era} | {dtb_max_erh}')
    
    print(np.abs(ds_com_rsd.dtb_mwi_est).max(['profile', 'channel']))
    print(np.abs(ds_com_era.dtb_mwi_est).max(['profile', 'channel']))
    print(np.abs(ds_com_erh.dtb_mwi_est).max(['profile', 'channel']))
    
    print(ds_com_rsd.dtb_mwi_est.min(['profile', 'channel', 'est_type']).item())
    print(ds_com_era.dtb_mwi_est.min(['profile', 'channel', 'est_type']).item())
    print(ds_com_erh.dtb_mwi_est.min(['profile', 'channel', 'est_type']).item())
    
    print(ds_com_rsd.dtb_mwi_est.max(['profile', 'channel', 'est_type']).item())
    print(ds_com_era.dtb_mwi_est.max(['profile', 'channel', 'est_type']).item())
    print(ds_com_erh.dtb_mwi_est.max(['profile', 'channel', 'est_type']).item())    
    
    #%% scatter plot and histogram
    # x: TB obs or IWV
    # y: TB obs - TB mod
    
    # choose x axis style
    styles = ['tb_obs', 'iwv']
    style = styles[1]
    
    # choose if with or without era-5
    era5 = True  # this is just as a test to see if clear sky matches
    
    fig, axes = plt.subplots(5, 4, figsize=(7, 6), sharex=True, sharey=True,
                             constrained_layout=True)
    
    axes[-1, 0].set_ylabel('$\Delta$TB [K]')
    
    if style == 'tb_obs':
        axes[-1, 0].set_xlabel('$TB_{obs}$ [K]')
    elif style == 'iwv':
        axes[-1, 0].set_xlabel('IWV [kg m$^{-2}$]')
    
    kwargs = dict(xy=(0.5, 1), xycoords='axes fraction', ha='center', 
                  va='bottom')
    axes[0, 0].annotate('center', **kwargs)
    axes[0, 1].annotate('cutoff', **kwargs)
    axes[0, 2].annotate('center+cutoff', **kwargs)
    axes[0, 3].annotate('top-hat', **kwargs)
    
    for i, ax in enumerate(axes.flatten('F')):
        
        ax.spines.top.set_visible(False)
        ax.spines.right.set_visible(False)
        
        ax.annotate(f'({abc[i]})', xy=(0.02, 0.98), xycoords='axes fraction',
                    ha='left', va='top')
        
        # x axis
        ax.set_xticks(ticks=np.arange(0, 400, 25), minor=False)
        ax.set_xticks(ticks=np.arange(0, 400, 5), minor=True)
        
        # y axis
        ax.set_yticks(ticks=np.arange(-2, 2, 0.5), minor=False)
        ax.set_yticks(ticks=np.arange(-2, 2, 0.1), minor=True)
        
        ax.tick_params(which='major')
        ax.tick_params(which='minor', length=1)
        
        ax.axhline(y=0, color='k', linewidth=1)
        
        ax.set_ylim([-0.9, 1.4])
        
        if style == 'tb_obs':
            ax.set_xlim([235, 290])
        elif style == 'iwv':
            ax.set_xlim([0, 75])
        
    # annotate channel name
    for i, ax in enumerate(axes[:, -1]):
        ax.annotate(text=mwi.freq_txt[i].split('\n')[0], xy=(1.1, 0.5),
                    xycoords='axes fraction', ha='left', va='center',
                    rotation=90)
    
    for i, channel in enumerate(mwi.channels_int):
        for j, est_type in enumerate(['freq_center', 'freq_bw', 
                                      'freq_bw_center', 'top-hat']):
            
            if style == 'tb_obs':
                x = ds_com_rsd.tb_mwi_orig.sel(channel=channel)
            elif style == 'iwv':
                x = ds_com_rsd.iwv
            
            # radiosondes
            axes[i, j].scatter(x, 
                               ds_com_rsd.dtb_mwi_est.sel(channel=channel,
                                                          est_type=est_type), 
                               s=2, c=c_list, linewidths=0)
            
            if era5: 
                if style == 'tb_obs':
                    x = ds_com_era.tb_mwi_orig.sel(channel=channel)
                elif style == 'iwv':
                    x = ds_com_era.iwv
                    
                # era5 without hydrometeors
                axes[i, j].scatter(x, 
                                   ds_com_era.dtb_mwi_est.sel(channel=channel,
                                                              est_type=est_type), 
                                   s=2, c='k', linewidths=0)
                
                # era5 with hydrometeors
                axes[i, j].scatter(x, 
                                   ds_com_erh.dtb_mwi_est.sel(channel=channel,
                                                              est_type=est_type), 
                                   s=2, c='gray', linewidths=0, alpha=0.01)
    
    # legend below
    patches = []
    stations = wyo.station_id.keys()
    for station in stations:
        patches.append(mpatches.Patch(color=colors[station], label=station))
    axes[0, 0].legend(handles=patches[:2], frameon=False, fontsize=7)
    axes[0, 1].legend(handles=patches[2:], frameon=False, fontsize=7)
    
    if era5:
        ext = '_era5'
    else:
        ext = ''
    
    plt.savefig(os.path.join(
        os.environ['PATH_PLT'],
        'evaluation/dtb_mwi_est_vs_'+style+'_radiosondes'+ext+'.png'), 
        dpi=400, bbox_inches='tight')
    
    plt.close('all')
    
    #%% 2d histogram iwv and tb dependence
    # x: TB MWI
    # y: IWV
    # color: dTb    
    fig, axes = plt.subplots(5, 4, figsize=(7, 6), sharex=True, sharey=True,
                             constrained_layout=True)      
    
    axes[-1, 0].set_ylabel('$\Delta$TB [K]')
    
    axes[-1, 0].set_ylabel('$TB_{obs}$ [K]')
    axes[-1, 0].set_xlabel('IWV [kg m$^{-2}$]')
    
    kwargs = dict(xy=(0.5, 1), xycoords='axes fraction', ha='center', 
                  va='bottom')
    axes[0, 0].annotate('center', **kwargs)
    axes[0, 1].annotate('cutoff', **kwargs)
    axes[0, 2].annotate('center+cutoff', **kwargs)
    axes[0, 3].annotate('top-hat', **kwargs)
    
    for i, ax in enumerate(axes.flatten('F')):
        
        ax.spines.top.set_visible(False)
        ax.spines.right.set_visible(False)
        
        ax.annotate(f'({abc[i]})', xy=(0.02, 0.98), xycoords='axes fraction',
                    ha='left', va='top')
        
        # x axis
        ax.set_xticks(ticks=np.arange(0, 400, 25), minor=False)
        ax.set_xticks(ticks=np.arange(0, 400, 5), minor=True)
        
        # y axis
        ax.set_xticks(ticks=np.arange(0, 400, 25), minor=False)
        ax.set_xticks(ticks=np.arange(0, 400, 5), minor=True)
        
        ax.tick_params(which='major')
        ax.tick_params(which='minor', length=1)
        
        ax.axhline(y=0, color='k', linewidth=1)
        
        ax.set_ylim([235, 290])
        ax.set_xlim([0, 75])
        
    # annotate channel name
    for i, ax in enumerate(axes[:, -1]):
        ax.annotate(text=mwi.freq_txt[i].split('\n')[0], xy=(1.1, 0.5),
                    xycoords='axes fraction', ha='left', va='center',
                    rotation=90)
    
    for i, channel in enumerate(mwi.channels_int):
        for j, est_type in enumerate(['freq_center', 'freq_bw', 
                                      'freq_bw_center', 'top-hat']):
            
            c_max = np.max(np.fabs(ds_com_rsd.dtb_mwi_est.sel(channel=channel,
                                         est_type=est_type)))
            
            im = axes[i, j].scatter(
                ds_com_rsd.iwv,
                ds_com_rsd.tb_mwi_orig.sel(channel=channel),
                c=ds_com_rsd.dtb_mwi_est.sel(channel=channel,
                                             est_type=est_type), 
                               cmap='BrBG_r',
                               s=2, linewidths=0, vmin=-c_max, vmax=c_max)
            fig.colorbar(im, ax=axes[i, j], orientation='horizontal')
            
    plt.savefig(os.path.join(
        os.environ['PATH_BRT'],
        'evaluation/dtb_mwi_est_vs_tb_obs_vs_iwv_radiosondes.png'), 
        dpi=400, bbox_inches='tight')
    
    plt.close('all')
    