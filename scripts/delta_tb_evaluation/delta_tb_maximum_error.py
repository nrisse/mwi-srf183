

import numpy as np
import datetime
import matplotlib.pyplot as plt
from matplotlib import cm
import matplotlib.patches as mpatches
import xarray as xr
import os
import sys
sys.path.append(f'{os.environ["PATH_PHD"]}/projects/mwi_bandpass_effects/scripts')
from radiosonde import wyo
from mwi_info import mwi
from importer import Delta_TB, IWV, Sensitivity
from path_setter import *
from layout import colors, names


"""
Influence of noise and data reduction on the result

last edited: Nov 4 2020

two figures are used
"""


def diff_tb_pert_tb_orig(srf, epsilon, tb, sum_axis=1):
    """
    srf:      spectral response function in log units (length frequency)
    epsilon:  error of spectral response function in log units (length frequency)
    tb:       brightness temperature simulated with radiative transfer model (length frequency)
    
    returns
    diff:     difference between perturbed virtual observation and unperturbed virtual observation
    """
    
    #tb_orig = np.sum(tb*(10**(0.1*srf)/(np.sum(10**(0.1*srf)))), axis=sum_axis)
    #tb_pert = np.sum(tb*(10**(0.1*(srf + epsilon))/(np.sum(10**(0.1*(srf + epsilon))))), axis=sum_axis)
    
    diff = np.sum(tb*(10**(0.1*(srf + epsilon))/(np.sum(10**(0.1*(srf + epsilon)))) - 
                      10**(0.1*srf)/(np.sum(10**(0.1*srf)))), axis=sum_axis)
    
    return diff


if __name__ == '__main__':
    
    # read nc files
    delta_tb = xr.load_dataset(path_data + 'delta_tb/delta_tb_maximum_error.nc')
    
    # read iwv
    iwv = IWV()
    iwv.read_data()
    iwv.data = iwv.data.sel(profile=delta_tb.profile)  # reorder iwv data based on delta_tb profile order

    #%% create indices for summarizing statistics
    station_id = np.array([x[3:8] for x in delta_tb.profile.values])
    date = np.array([datetime.datetime.strptime(x[-12:], '%Y%m%d%H%M') for x in delta_tb.profile.values])
    year = np.array([x.year for x in date])

    ix_2019 = year == 2019
    
    ix_nya = station_id == wyo.station_id['Ny Alesund']
    ix_snp = station_id == wyo.station_id['Singapore']
    ix_ess = station_id == wyo.station_id['Essen']
    ix_bar = station_id == wyo.station_id['Barbados']
    ix_std = station_id == '00000'
    
    pert_names = ['linear1', 'linear2', 'imbalance1', 'imbalance2', 'ripple1', 'ripple2', 'orig']
    
    #%% iwv from 2019
    iwv_data = iwv.data[ix_2019]
    
    #%% calculate difference between orig and the six perturbations
    delta_tb_diff = delta_tb - delta_tb.sel(perturbation='orig')
    
    (delta_tb_diff.sel(perturbation='linear1') + delta_tb_diff.sel(perturbation='linear2')).mean('profile')
    (delta_tb_diff.sel(perturbation='imbalance1') + delta_tb_diff.sel(perturbation='imbalance2')).mean('profile')
    (delta_tb_diff.sel(perturbation='ripple1') + delta_tb_diff.sel(perturbation='ripple2')).mean('profile')
    
    # calculate MAE (mean absolute error) for each calculation method and channel
    ds_mae_from_delta_tb = np.abs(delta_tb_diff).mean('calc_method').mean('profile')  # independent of calc method
    ds_std_from_delta_tb = np.abs(delta_tb_diff).mean('calc_method').std('profile')  # independent of calc method
    
    #%% direct calculation of difference from TB, srf, epsilon in dB
    # read epsilon, srf and tb
    epsilon = xr.load_dataset(path_data+'sensitivity/perturbed/MWI-RX183_DSB_Matlab_residual.nc')
    
    sen_dsb = Sensitivity(filename='MWI-RX183_DSB_Matlab.xlsx')
    ds_sen = sen_dsb.data
    
    file = path_data + 'brightness_temperature/TB_radiosondes_2019.nc'
    ds_tb = xr.load_dataset(file).isel(angle=9)
    ds_tb = ds_tb.assign_coords(frequency=(np.round(ds_tb.frequency.values, 3)*1000).astype(np.int))
    
    # calculate difference
    perts = np.array(['linear1', 'linear2', 'imbalance1', 'imbalance2', 'ripple1', 'ripple2'])
    ds_diff = xr.Dataset()
    ds_diff.coords['channel'] = ds_sen.channel.values
    ds_diff.coords['profile'] = ds_tb.profile.values
    ds_diff.coords['perturbation'] = perts
    ds_diff.coords['magnitude'] = epsilon.magnitude
    ds_diff['data'] = (('channel', 'magnitude', 'perturbation', 'profile'), np.zeros(shape=list(ds_diff.dims.values())))
    for i, channel in enumerate(ds_diff.channel):
        for j, magn in enumerate(ds_diff.magnitude):
            for k, pert in enumerate(ds_diff.perturbation.values):
                ds_diff.data[i, j, k, :] = diff_tb_pert_tb_orig(srf=ds_sen.raw.sel(channel=channel).T.values, 
                                                                epsilon=epsilon[pert].sel(channel=channel, magnitude=magn).values, 
                                                                tb=ds_tb.tb.sel(frequency=ds_sen.frequency.values).values)
        
    # calculate mae
    ds_mae = np.abs(ds_diff).mean('profile')
    ds_std = np.abs(ds_diff).std('profile')
    ds_q75 = np.abs(ds_diff).quantile(0.75, dim='profile')
    ds_q25 = np.abs(ds_diff).quantile(0.25, dim='profile')
    ds_q50 = np.abs(ds_diff).quantile(0.5, dim='profile')
    
    # compare with MAE from delta_tb (=0 as expected)
    np.sum(ds_mae - ds_mae_from_delta_tb)
    np.sum(ds_std - ds_std_from_delta_tb)
    
    #%% print the result
    for channel in mwi.channels_int:
        print('\n', channel)
        for name in pert_names[:-1]:
            print(name, np.round(ds_mae.data.sel(channel=channel, magnitude=2, perturbation=name).values.item(), 2))
            
    df_mae = np.round(ds_mae.data.sel(magnitude=2).to_pandas(), 2)
    df_mae.to_csv(path_data+'df_mae.csv')
    
    df_q75 = np.round(ds_q75.data.sel(magnitude=2).to_pandas(), 2)
    df_q75.to_csv(path_data+'df_q75.csv')
    
    df_q25 = np.round(ds_q25.data.sel(magnitude=2).to_pandas(), 2)
    df_q25.to_csv(path_data+'df_q25.csv')
    
    df_q50 = np.round(ds_q50.data.sel(magnitude=2).to_pandas(), 2)
    df_q50.to_csv(path_data+'df_q50.csv')
    
    #%% direct calculation of difference from TB, srf, epsilon in dB: Gaussian noise
    # read srf and tb    
    sen_dsb = Sensitivity(filename='MWI-RX183_DSB_Matlab.xlsx')
    ds_sen = sen_dsb.data
    
    # define epsilon
    n_realizations = 50
    realizations = np.arange(0, n_realizations)
    standard_dev = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.7, 1.0, 1.5, 2.0])
    
    epsilon_g = xr.Dataset()
    epsilon_g.attrs = dict(comment='perturbation based on Gaussian noise on raw measurement')
    epsilon_g.coords['frequency'] = ds_sen.raw.frequency
    epsilon_g.coords['channel'] = ds_sen.raw.channel
    epsilon_g.coords['realization'] = realizations
    epsilon_g.coords['standard_dev'] = standard_dev
    epsilon_g['pert'] = (('channel', 'frequency', 'realization', 'standard_dev'), np.zeros(shape=list(epsilon_g.dims.values())))
    for i, std in enumerate(standard_dev):
        epsilon_g.pert[:, :, :, i] = np.random.normal(loc=0, scale=std, size=list(epsilon_g.dims.values())[:-1])
        
    # read profiles
    file = path_data + 'brightness_temperature/TB_radiosondes_2019.nc'
    ds_tb = xr.load_dataset(file).isel(angle=9)
    ds_tb = ds_tb.assign_coords(frequency=(np.round(ds_tb.frequency.values, 3)*1000).astype(np.int))
    
    # calculate difference
    ds_diff_g = xr.Dataset()
    ds_diff_g.coords['channel'] = ds_sen.channel.values
    ds_diff_g.coords['profile'] = ds_tb.profile.values
    ds_diff_g.coords['realization'] = realizations
    ds_diff_g.coords['standard_dev'] = standard_dev
    ds_diff_g['data'] = (('channel', 'profile', 'realization', 'standard_dev'), np.zeros(shape=list(ds_diff_g.dims.values())))
    for i, channel in enumerate(ds_diff_g.channel):
        for j, real in enumerate(ds_diff_g.realization):
            for k, std in enumerate(ds_diff_g.standard_dev):
                print(i, j)
                ds_diff_g.data[i, :, j, k] = diff_tb_pert_tb_orig(srf=ds_sen.raw.sel(channel=channel).T.values, 
                                                                  epsilon=epsilon_g['pert'].sel(channel=channel, realization=real, standard_dev=std).values, 
                                                                  tb=ds_tb.tb.sel(frequency=ds_sen.frequency.values).values)
    
    # calculate mae
    ds_mae_g = np.abs(ds_diff_g).mean(['profile', 'realization'])
    ds_std_g = np.abs(ds_diff_g).std(['profile', 'realization'])
    
    # highest absolute value
    np.max(np.abs(ds_diff_g))
    
    #%% relative effect
    # calculate (delta_tb(obs,pert)-delta_tb(obs,orig))/delta_tb(orig)
    # every difference in absolute values
    ds_rel = xr.Dataset()
    ds_rel.coords['channel'] = ds_sen.channel.values
    ds_rel.coords['profile'] = ds_tb.profile.values
    ds_rel.coords['perturbation'] = perts
    ds_rel.coords['calc_method'] = delta_tb.calc_method.values
    rel = np.zeros(shape=(5, 1342, 6, 3))
    for i, channel in enumerate(ds_diff.channel.values):
        for k, pert in enumerate(ds_diff.perturbation.values):
            for l, calc_m in enumerate(delta_tb.calc_method.values):
            
                rel[i, :, k, l] =  np.abs(ds_diff.data.sel(channel=channel, perturbation=pert, magnitude=0.3)/
                                          delta_tb.data.sel(perturbation='orig', channel=str(channel), calc_method=calc_m))
    ds_rel['data'] = (('channel', 'profile', 'perturbation', 'calc_method'), rel)    
            
    #%% color for figures
    col_lin = '#577590'
    col_inb = '#f3722c'
    col_rip = '#90be6d'
    
    #%% influence of each perturbation on the IWV dependency
    magnitude = 2
    
    fig, axes = plt.subplots(5, 3, figsize=(6, 8), sharex=True, sharey=True)
        
    axes[2, 0].set_ylabel(r'$TB_{obs,pert} - TB_{obs,orig}$ [K]')
    axes[-1, 1].set_xlabel('Integrated water vapor [kg m$^{-2}$]')
    
    axes[0, 0].set_title(r'linear 1+2', fontsize=8)
    axes[0, 1].set_title(r'imbalance 1+2', fontsize=8)
    axes[0, 2].set_title(r'ripple 1+2', fontsize=8)
    
    for ax in axes.flatten():
        
        # x axis
        ax.set_xticks(ticks=np.arange(0, 150, 25), minor=False)
        ax.set_xticks(ticks=np.arange(0, 150, 5), minor=True)
        
        # y axis
        ax.set_yticks(ticks=np.arange(-0.5, 0.5, 0.1), minor=False)
        ax.set_yticks(ticks=np.arange(-0.5, 0.5, 0.025), minor=True)

        ax.axhline(y=0, color='k', linewidth=1, alpha=0.5)
        
        #ax.set_ylim([-0.25, 0.25])
        ax.set_xlim([0, 75])
        
    # annotate channel name
    for i, ax in enumerate(axes[:, -1]):
        ax.annotate(text=mwi.freq_txt[i], xy=(1.1, 0.5), xycoords='axes fraction', backgroundcolor="w",
                    annotation_clip=False, horizontalalignment='left', verticalalignment='center', fontsize=8)
    
    kwargs = dict(s=2, linewidths=0, alpha=0.5)
    for i, channel in enumerate(mwi.channels_int):
        for j, pert_ix in enumerate([0, 2, 4]):
            
            # get perturbations that belong together
            pert1 = ds_diff.perturbation.values[pert_ix]
            pert2 = ds_diff.perturbation.values[pert_ix+1]
            
            axes[i, j].scatter(iwv_data, ds_diff.data.sel(channel=channel, perturbation=pert1, magnitude=magnitude), c='black', **kwargs)
            axes[i, j].scatter(iwv_data, ds_diff.data.sel(channel=channel, perturbation=pert2, magnitude=magnitude), c='gray', **kwargs)
            
    fig.tight_layout()

    # legend below
    patches = []
    labels = ['1', '2']
    colors = ['black', 'gray']
    for i, label in enumerate(labels):
        patches.append(mpatches.Patch(color=colors[i], label=label))
    leg = axes[-1, -1].legend(handles=patches, bbox_to_anchor=(1.05, 0.2), loc='upper left', frameon=False, ncol=1, fontsize=6, title='Perturbation #:')
    plt.setp(leg.get_title(),fontsize=6)
    
    plt.savefig(path_plot+'maximum_error/iwv_all_magnitude_'+str(magnitude)+'.png', dpi=400)
    
    #%% influence of all perturbations on the IWV dependency by taking the absolute value of the difference
    # independent of calculation method
    fig, axes = plt.subplots(5, 1, figsize=(4, 5), sharex=True, sharey=True, constrained_layout=True)
    
    axes[2].set_ylabel(r'abs$(TB_{pert} - TB_{orig})$ [K]')
    axes[-1].set_xlabel('Integrated water vapor [kg m$^{-2}$]')

    for ax in axes.flatten():
        
        # x axis
        ax.set_xticks(ticks=np.arange(0, 150, 25), minor=False)
        ax.set_xticks(ticks=np.arange(0, 150, 5), minor=True)
        
        # y axis
        ax.set_yticks(ticks=np.arange(-0.5, 0.5, 0.1), minor=False)
        ax.set_yticks(ticks=np.arange(-0.5, 0.5, 0.025), minor=True)
        
        ax.axhline(y=0, color='k', linewidth=1, alpha=0.5)
        
        ax.set_ylim([0, 0.22])
        ax.set_xlim([0, 75])
        
    # annotate channel name
    for i, ax in enumerate(axes):
        ax.annotate(text=mwi.freq_txt[i].split('\n')[0], xy=(1.05, 1), xycoords='axes fraction', backgroundcolor="w",
                    annotation_clip=False, horizontalalignment='left', verticalalignment='top')
    
    kwargs = dict(s=5, linewidths=0, alpha=0.75)
    for i, channel in enumerate(mwi.channels_int):
        
        # linear
        kwargs_sel = dict(channel=channel, perturbation='linear1', magnitude=0.3)
        axes[i].scatter(iwv_data, np.abs(ds_diff.data.sel(**kwargs_sel)), c=col_lin, **kwargs)
        
        # imbalance
        kwargs_sel = dict(channel=channel, perturbation='imbalance1', magnitude=0.3)
        axes[i].scatter(iwv_data, np.abs(ds_diff.data.sel(**kwargs_sel)), c=col_inb, **kwargs)
        
        # ripple
        kwargs_sel = dict(channel=channel, perturbation='ripple1', magnitude=0.3)
        axes[i].scatter(iwv_data, np.abs(ds_diff.data.sel(**kwargs_sel)), c=col_rip, **kwargs)
        
    # plot mae
    for i, channel in enumerate(mwi.channels_int):
        
        mae_lin = ds_mae.data.sel(channel=channel, perturbation='linear1', magnitude=0.3)
        mae_inb = ds_mae.data.sel(channel=channel, perturbation='imbalance1', magnitude=0.3)
        mae_rip = ds_mae.data.sel(channel=channel, perturbation='ripple1', magnitude=0.3)
        
        #axes[i].axhline(y=mae_lin, color='white', linewidth=1.5)
        #axes[i].axhline(y=mae_inb, color='white', linewidth=1.5)
        #axes[i].axhline(y=mae_rip, color='white', linewidth=1.5)
        
        #axes[i].axhline(y=mae_lin, color=col_lin, linewidth=1)
        #axes[i].axhline(y=mae_inb, color=col_inb, linewidth=1)
        #axes[i].axhline(y=mae_rip, color=col_rip, linewidth=1)
        
        # annotate mae
        kwargs = dict(xycoords='axes fraction', ha='left', va='top')
        axes[i].annotate(text='$MAE$=%1.2f K'%mae_lin, color=col_lin, xy=(1.05, 0.6), **kwargs)
        axes[i].annotate(text='$MAE$=%1.2f K'%mae_inb, color=col_inb, xy=(1.05, 0.4), **kwargs)
        axes[i].annotate(text='$MAE$=%1.2f K'%mae_rip, color=col_rip, xy=(1.05, 0.2), **kwargs)
    
    # legend below
    patches = []
    labels = ['linear', 'imbalance', 'ripple']
    colors = [col_lin, col_inb, col_rip]
    for i, label in enumerate(labels):
        patches.append(mpatches.Patch(color=colors[i], label=label))
    leg = axes[-1].legend(handles=patches, bbox_to_anchor=(0.5, -0.7), loc='upper center', frameon=False, ncol=3)
    plt.setp(leg.get_title(),fontsize=6)
    
    plt.savefig(path_plot+'maximum_error/iwv_abs.png', dpi=300)
    
    plt.close('all')
    
    #%% histogram of absolute difference
    step = 0.002
    bins = np.arange(0, 10+step, step)
    mag = 0.3
    
    fig, axes = plt.subplots(5, 1, figsize=(4, 5), sharex=True, sharey=True, constrained_layout=True)
    
    axes[2].set_ylabel('Absolute frequency')
    axes[-1].set_xlabel(r'abs$(TB_{obs,pert} - TB_{obs,orig})$ [K]')

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
            ax.set_ylim([0, 80])
    
    # annotate channel name
    for i, ax in enumerate(axes):
        ax.annotate(text=mwi.freq_txt[i].split('\n')[0], xy=(1.05, 1), xycoords='axes fraction', backgroundcolor="w",
                    annotation_clip=False, horizontalalignment='left', verticalalignment='top')
    
    #kwargs = dict(bins=np.arange(0, 0.21, 0.002), linewidth=0, alpha=0.5, density=True)
    kwargs = dict(bins=bins, linewidth=0, alpha=0.75, density=True)
    for i, channel in enumerate(mwi.channels_int):
        
        # linear
        kwargs_sel = dict(channel=channel, magnitude=mag, perturbation='linear1')
        axes[i].hist(np.abs(ds_diff.data.sel(**kwargs_sel)), color=col_lin, **kwargs)
        
        # imbalance
        kwargs_sel = dict(channel=channel, magnitude=mag, perturbation='imbalance1')
        axes[i].hist(np.abs(ds_diff.data.sel(**kwargs_sel)), color=col_inb, **kwargs)
        
        # ripple
        kwargs_sel = dict(channel=channel, magnitude=mag, perturbation='ripple1')
        axes[i].hist(np.abs(ds_diff.data.sel(**kwargs_sel)), color=col_rip, **kwargs)
    
    # annotate mae
    for i, channel in enumerate(mwi.channels_int):
        
        mae_lin = ds_mae.data.sel(channel=channel, magnitude=mag, perturbation='linear1')
        mae_inb = ds_mae.data.sel(channel=channel, magnitude=mag, perturbation='imbalance1')
        mae_rip = ds_mae.data.sel(channel=channel, magnitude=mag, perturbation='ripple1')
        
        std_lin = ds_std.data.sel(channel=channel, magnitude=mag, perturbation='linear1')
        std_inb = ds_std.data.sel(channel=channel, magnitude=mag, perturbation='imbalance1')
        std_rip = ds_std.data.sel(channel=channel, magnitude=mag, perturbation='ripple1')
        
        # annotate mae and std
        kwargs = dict(xycoords='axes fraction', ha='left', va='top')
        axes[i].annotate(text='%1.2f $\pm$ %1.3f K'%(mae_lin, std_lin), color=col_lin, xy=(1.05, 0.6), **kwargs)
        axes[i].annotate(text='%1.2f $\pm$ %1.3f K'%(mae_inb, std_inb), color=col_inb, xy=(1.05, 0.4), **kwargs)
        axes[i].annotate(text='%1.2f $\pm$ %1.3f K'%(mae_rip, std_rip), color=col_rip, xy=(1.05, 0.2), **kwargs)
        
        # annotate std
        #kwargs = dict(xycoords='axes fraction', ha='left', va='top')
        #axes[i].annotate(text='$std$=%1.3f K'%std_lin, color=col_lin, xy=(1.5, 0.6), **kwargs)
        #axes[i].annotate(text='$std$=%1.3f K'%std_inb, color=col_inb, xy=(1.5, 0.4), **kwargs)
        #axes[i].annotate(text='$std$=%1.3f K'%std_rip, color=col_rip, xy=(1.5, 0.2), **kwargs)
        
    # legend below
    patches = []
    labels = ['linear', 'imbalance', 'ripple']
    colors = [col_lin, col_inb, col_rip]
    for i, label in enumerate(labels):
        patches.append(mpatches.Patch(color=colors[i], label=label))
    leg = axes[-1].legend(handles=patches, bbox_to_anchor=(0.5, -0.7), loc='upper center', frameon=False, ncol=3)
    plt.setp(leg.get_title(),fontsize=6)
    
    print('saving magnitude %1.1f'%mag)
    plt.savefig(path_plot+'maximum_error/abs_hist_%1.1f.png'%mag, dpi=300)
    
    plt.close()
    
    #%% relative effect on delta TB dependency
    fig, axes = plt.subplots(5, 3, figsize=(6, 8), sharex=True, sharey=True)
    
    axes[2, 0].set_ylabel(r'$abs\left(\frac{TB_{obs,orig} - TB_{obs,pert}}{TB_{obs,orig} - TB_{ref}} \right)$')
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
        ax.set_yticks(ticks=np.arange(-2, 2, 0.25), minor=True)

        ax.axhline(y=0, color='k', linewidth=1, alpha=0.5)
        
        ax.set_ylim([0, 1])
        ax.set_xlim([0, 75])
        
    # annotate channel name
    for i, ax in enumerate(axes[:, -1]):
        ax.annotate(text=mwi.freq_txt[i], xy=(1.1, 0.5), xycoords='axes fraction', backgroundcolor="w",
                    annotation_clip=False, horizontalalignment='left', verticalalignment='center', fontsize=8)
    
    for i, channel in enumerate(mwi.channels_int):
        for j, calc_m in enumerate(ds_rel.calc_method):
            axes[i, j].scatter(iwv_data, ds_rel.data.sel(channel=channel, calc_method=calc_m, perturbation='linear1'), s=2, c=col_lin, linewidths=0, alpha=0.5)
            axes[i, j].scatter(iwv_data, ds_rel.data.sel(channel=channel, calc_method=calc_m, perturbation='imbalance1'), s=2, c=col_inb, linewidths=0, alpha=0.5)
            axes[i, j].scatter(iwv_data, ds_rel.data.sel(channel=channel, calc_method=calc_m, perturbation='ripple1'), s=2, c=col_rip, linewidths=0, alpha=0.5)
            
    fig.tight_layout()

    # legend below
    patches = []
    labels = ['linear-orig', 'imbalance-orig', 'ripple-orig']
    colors = [col_lin, col_inb, col_rip]
    for i, label in enumerate(labels):
        patches.append(mpatches.Patch(color=colors[i], label=label))
    leg = axes[-1, -1].legend(handles=patches, bbox_to_anchor=(1.05, 0.2), loc='upper left', frameon=False, ncol=1, fontsize=6, title='Perturbation:')
    plt.setp(leg.get_title(),fontsize=6)
    
    plt.savefig(path_plot+'maximum_error/abs_relative_perturb_reference.png', dpi=300)
    
    #%% for different offset levels than 0.3 dB
    fig, axes = plt.subplots(5, 1, figsize=(3, 5), sharex=True, sharey=True)
    
    axes[2].set_ylabel(r'mean(abs$(TB_{obs,pert} - TB_{obs,orig}))$ [K]')
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
    colors = [col_lin, col_inb, col_rip]
    for i, channel in enumerate(mwi.channels_int):
        for j, pert in enumerate(pert_names):
            axes[i].errorbar(ds_mae.magnitude, ds_mae.data.sel(channel=channel, perturbation=pert), 
                             yerr=ds_std.data.sel(channel=channel, perturbation=pert), elinewidth=0.5, capsize=2, color=colors[j],
                             barsabove=True, label=pert.replace('1', ''))
            
        axes[i].errorbar(ds_mae_g.standard_dev, ds_mae_g.data.sel(channel=channel), 
                         yerr=ds_std_g.data.sel(channel=channel), elinewidth=0.5, capsize=1, 
                         barsabove=True, ecolor='r', color='r', label='Gaussian #%s'%n_realizations)
        
    # legend below
    axes[0].legend(bbox_to_anchor=(0.5, 1.2), loc='lower center', frameon=False, fontsize=8, ncol=2)

    fig.tight_layout()
    
    plt.savefig(path_plot+'maximum_error/mae_vs_magnitude.png', dpi=300)
    
    plt.close('all')
    
    #%% evaluation of Gaussian noise
    # influence of all perturbations on the IWV dependency by taking the absolute value of the difference
    # independent of calculation method
    fig, axes = plt.subplots(5, 1, figsize=(6, 8), sharex=True, sharey=True)
    
    axes[2].set_ylabel(r'abs$(TB_{pert} - TB_{orig})$ [K]')
    axes[-1].set_xlabel('Integrated water vapor [kg m$^{-2}$]')

    for ax in axes.flatten():
        
        # x axis
        ax.set_xticks(ticks=np.arange(0, 150, 25), minor=False)
        ax.set_xticks(ticks=np.arange(0, 150, 5), minor=True)
        
        # y axis
        ax.set_yticks(ticks=np.arange(-0.5, 0.5, 0.1), minor=False)
        ax.set_yticks(ticks=np.arange(-0.5, 0.5, 0.025), minor=True)

        ax.axhline(y=0, color='k', linewidth=1, alpha=0.5)
        
        ax.set_ylim([0, 0.25])
        ax.set_xlim([0, 75])
        
    # annotate channel name
    for i, ax in enumerate(axes):
        ax.annotate(text=mwi.freq_txt[i], xy=(1.1, 0.5), xycoords='axes fraction', backgroundcolor="w",
                    annotation_clip=False, horizontalalignment='left', verticalalignment='center', fontsize=8)
    
    kwargs = dict(s=2, linewidths=0, alpha=0.5)
    for i, channel in enumerate(mwi.channels_int):
        for j, real in enumerate(ds_diff_g.realization):
            kwargs_sel = dict(channel=channel, realization=real, standard_dev=5)
            axes[i].scatter(iwv_data, np.abs(ds_diff_g.data.sel(**kwargs_sel)), c='k', **kwargs)

    fig.tight_layout()
    
    plt.savefig(path_plot+'maximum_error/iwv_abs_gaussian.png', dpi=300)
    
    #%% for different offset levels than 0.3 dB
    fig, axes = plt.subplots(5, 1, figsize=(3, 6), sharex=True, sharey=True)
    
    fig.suptitle('For all profiles and realizations (#%s)'%str(n_realizations))
    
    axes[2].set_ylabel(r'mean(abs$(TB_{obs,pert} - TB_{obs,orig}))$ [K]')
    axes[-1].set_xlabel('Noise standard deviation [dB]')

    for ax in axes.flatten():
        
        # x axis
        ax.set_yticks(ticks=np.arange(0, 0.4, 0.1), minor=False)
        ax.set_yticks(ticks=np.arange(0, 0.4, 0.025), minor=True)
        
        # y axis
        ax.set_xticks(ticks=np.arange(0, 2.5, 0.5), minor=False)
        ax.set_xticks(ticks=np.arange(0, 2.5, 0.1), minor=True)

        ax.axhline(y=0, color='k', linewidth=1, alpha=0.5)
        
        ax.axvline(x=0.3, color='k', linewidth=1, linestyle=':')
        
        ax.set_xlim([0, 2.1])
        ax.set_ylim([0, 0.15])
        
    # annotate channel name
    for i, ax in enumerate(axes):
        ax.annotate(text=mwi.freq_txt[i], xy=(1.1, 0.5), xycoords='axes fraction', backgroundcolor="w",
                    annotation_clip=False, horizontalalignment='left', verticalalignment='center', fontsize=8)
    
    for i, channel in enumerate(mwi.channels_int):
        axes[i].errorbar(ds_mae_g.standard_dev, ds_mae_g.data.sel(channel=channel), 
                         yerr=ds_std_g.data.sel(channel=channel), elinewidth=0.5, capsize=2, 
                         barsabove=True, ecolor='k', color='k')
    
    fig.tight_layout()
        
    plt.savefig(path_plot+'maximum_error/mae_vs_std_gaussian.png', dpi=300)
    
    #%% new: 25 Mar 2021
    # calculate TB difference between left/right and center of bandpass for every profile
    # assume a measured SRF with sensitivity of 0.5 at inner (outer) bandpass edge instead of bandpass center
    # what would be the TB difference then?
    ds_delta_max = xr.Dataset()
    ds_delta_max.coords['profile'] = ds_tb.profile.values
    ds_delta_max.coords['channel'] = mwi.channels_str
    ds_delta_max.coords['location'] = ['center', 'wing', 'half_center', 'half_wing', 'quart_center', 'quart_wing']  # location of the peak of SRF (inner or outer bandpass edge)
    ds_delta_max['diff'] = (('channel', 'location', 'profile'), np.zeros(list(ds_delta_max.dims.values())))
    
    for i, channel in enumerate(mwi.channels_str):
        
        m = dict(method='nearest')
        
        # frequencies
        fl = mwi.freq_center_MHz[i, 0]  # left central frequency
        fr = mwi.freq_center_MHz[i, 1]  # right central frequency
        fwl = mwi.freq_bw_MHz[i, 0]  # left bandpass wing frequency (at bandwidth edge)
        fwr = mwi.freq_bw_MHz[i, 3]  # right bandpass wing frequency (at bandwidth edge)
        fcl = mwi.freq_bw_MHz[i, 1]  # left bandpass center frequency (at bandwidth edge)
        fcr = mwi.freq_bw_MHz[i, 2]  # right bandpass center frequency (at bandwidth edge)
        fhwl = (fl + fwl)/2
        fhwr = (fr + fwr)/2
        fhcl = (fl + fcl)/2
        fhcr = (fr + fcr)/2
        fqwl = (fl + fhwl)/2
        fqwr = (fr + fhwr)/2
        fqcl = (fl + fhcl)/2
        fqcr = (fr + fhcr)/2
        
        # for center 
        diff_left = ds_tb.tb.sel(frequency=fl) - ds_tb.tb.sel(frequency=fcl)
        diff_right = ds_tb.tb.sel(frequency=fr) - ds_tb.tb.sel(frequency=fcr)  
        ds_delta_max['diff'][i, 0, :] = (diff_left + diff_right)/2
        
        # for wing 
        diff_left = ds_tb.tb.sel(frequency=fl) - ds_tb.tb.sel(frequency=fwl) 
        diff_right = ds_tb.tb.sel(frequency=fr) - ds_tb.tb.sel(frequency=fwr)
        ds_delta_max['diff'][i, 1, :] = (diff_left.values + diff_right.values)/2
        
        # for half center
        diff_left = ds_tb.tb.sel(frequency=fl) - ds_tb.tb.sel(frequency=fhcl, **m)
        diff_right = ds_tb.tb.sel(frequency=fr) - ds_tb.tb.sel(frequency=fhcr, **m)  
        ds_delta_max['diff'][i, 2, :] = (diff_left + diff_right)/2
        
        # for half wing 
        diff_left = ds_tb.tb.sel(frequency=fl) - ds_tb.tb.sel(frequency=fhwl, **m) 
        diff_right = ds_tb.tb.sel(frequency=fr) - ds_tb.tb.sel(frequency=fhwr, **m)
        ds_delta_max['diff'][i, 3, :] = (diff_left.values + diff_right.values)/2
    
        # for quarter center
        m = dict(method='nearest')
        diff_left = ds_tb.tb.sel(frequency=fl) - ds_tb.tb.sel(frequency=fqcl, **m)
        diff_right = ds_tb.tb.sel(frequency=fr) - ds_tb.tb.sel(frequency=fqcr, **m)  
        ds_delta_max['diff'][i, 4, :] = (diff_left + diff_right)/2
        
        # for quarter wing
        diff_left = ds_tb.tb.sel(frequency=fl) - ds_tb.tb.sel(frequency=fqwl, **m) 
        diff_right = ds_tb.tb.sel(frequency=fr) - ds_tb.tb.sel(frequency=fqwr, **m)
        ds_delta_max['diff'][i, 5, :] = (diff_left.values + diff_right.values)/2

    # plot
    fig, axes = plt.subplots(5, 2, figsize=(6, 6), constrained_layout=True)
    
    ax = axes[:, 0]
    axf = axes[:, 1]
    
    bins = np.arange(-15, 15.1, 0.1)
    xlim = [3, 3, 3, 4, 8]
    
    for i, channel in enumerate(mwi.channels_str):
        
        # bandwidth edges
        ax[i].hist(ds_delta_max['diff'].isel(location=0, channel=i), bins=bins, color='purple', label='towards center')
        ax[i].hist(ds_delta_max['diff'].isel(location=1, channel=i), bins=bins, color='blue', label='towards wing')
        
        # half bandwidth edges
        ax[i].hist(ds_delta_max['diff'].isel(location=2, channel=i), bins=bins, color='purple', alpha=0.5)
        ax[i].hist(ds_delta_max['diff'].isel(location=3, channel=i), bins=bins, color='blue', alpha=0.5)
        
        # quarter bandwidth edges
        ax[i].hist(ds_delta_max['diff'].isel(location=4, channel=i), bins=bins, color='purple', alpha=0.2)
        ax[i].hist(ds_delta_max['diff'].isel(location=5, channel=i), bins=bins, color='blue', alpha=0.2)
        
        #mean0 = ds_delta_max['diff'].isel(location=0, channel=i).mean('profile').values.item()
        #mean1 = ds_delta_max['diff'].isel(location=1, channel=i).mean('profile').values.item()
        #ax[i].annotate('$\mu$={}'.format(np.round(mean0, 1)), xy=(0.99, 0.99), ha='right', va='top', xycoords='axes fraction', color='purple')
        #ax[i].annotate('$\mu$={}'.format(np.round(mean1, 1)), xy=(0.01, 0.99), ha='left', va='top', xycoords='axes fraction', color='blue')

        ax[i].set_xticks(np.arange(-10, 11, 0.25), minor=True)
        ax[i].set_xlim(-xlim[i], xlim[i])
    
    # annotate frequencies
    for i, channel in enumerate(mwi.channels_str):
        
        m = dict(method='nearest')
        
        # frequencies
        fl = mwi.freq_center_MHz[i, 0]  # left central frequency
        fr = mwi.freq_center_MHz[i, 1]  # right central frequency
        fwl = mwi.freq_bw_MHz[i, 0]  # left bandpass wing frequency (at bandwidth edge)
        fwr = mwi.freq_bw_MHz[i, 3]  # right bandpass wing frequency (at bandwidth edge)
        fcl = mwi.freq_bw_MHz[i, 1]  # left bandpass center frequency (at bandwidth edge)
        fcr = mwi.freq_bw_MHz[i, 2]  # right bandpass center frequency (at bandwidth edge)
        fhwl = (fl + fwl)/2
        fhwr = (fr + fwr)/2
        fhcl = (fl + fcl)/2
        fhcr = (fr + fcr)/2
        fqwl = (fl + fhwl)/2
        fqwr = (fr + fhwr)/2
        fqcl = (fl + fhcl)/2
        fqcr = (fr + fhcr)/2
        
        #ax[i].annotate('{}, {}'.format(fwl*1e-3, fwr*1e-3), xy=(0.15, 0.4), xycoords='axes fraction', va='center', ha='center', fontsize=6)
        #ax[i].annotate('{}, {}'.format(fcl*1e-3, fwr*1e-3), xy=(0.85, 0.4), xycoords='axes fraction', va='center', ha='center', fontsize=6)
        #ax[i].annotate('{}, {}'.format(fhwl*1e-3, fhwr*1e-3), xy=(0.25, 0.6), xycoords='axes fraction', va='center', ha='center', fontsize=6)
        #ax[i].annotate('{}, {}'.format(fhcl*1e-3, fhcr*1e-3), xy=(0.75, 0.6), xycoords='axes fraction', va='center', ha='center', fontsize=6)
        #ax[i].annotate('{}, {}'.format(fqwl*1e-3, fqwr*1e-3), xy=(0.35, 0.8), xycoords='axes fraction', va='center', ha='center', fontsize=6)
        #ax[i].annotate('{}, {}'.format(fqcl*1e-3, fqcr*1e-3), xy=(0.65, 0.8), xycoords='axes fraction', va='center', ha='center', fontsize=6)
        
        # plot the SRF/vertical lines
        kw1 = dict(ymin=0, ymax=1, color='k', linewidth=0.75)
        kww = dict(ymin=0, ymax=0.5, color='blue', linewidth=0.75)
        kwc = dict(ymin=0, ymax=0.5, color='purple', linewidth=0.75)
        axf[i].axvline(fl*1e-3, **kw1)
        axf[i].axvline(fr*1e-3, **kw1)
        axf[i].axvline(fwl*1e-3, **kww)
        axf[i].axvline(fwr*1e-3, **kww)
        axf[i].axvline(fcl*1e-3, **kwc)
        axf[i].axvline(fcr*1e-3, **kwc)
        axf[i].axvline(fhwl*1e-3, alpha=0.5, **kww)
        axf[i].axvline(fhwr*1e-3, alpha=0.5, **kww)
        axf[i].axvline(fhcl*1e-3, alpha=0.5, **kwc)
        axf[i].axvline(fhcr*1e-3, alpha=0.5, **kwc)
        axf[i].axvline(fqwl*1e-3, alpha=0.2, **kww)
        axf[i].axvline(fqwr*1e-3, alpha=0.2, **kww)
        axf[i].axvline(fqcl*1e-3, alpha=0.2, **kwc)
        axf[i].axvline(fqcr*1e-3, alpha=0.2, **kwc)
        
        axf[i].set_xlim([mwi.freq_bw[0, 0]-0.5, mwi.freq_bw[0, -1]+0.5])
        
        axf[i].annotate('ch {}'.format(mwi.channels_str[i]), xycoords='axes fraction', xy=(0.5, 0.8), va='center', ha='center')
        
        # read linear perturbations
        ds_per_lino = xr.load_dataset(path_data+'sensitivity/perturbed/MWI-RX183_DSB_Matlab_perturb.nc')
        
        # plot linear srd
        axf[i].plot(ds_sen.frequency*1e-3, ds_sen.lino.isel(channel=i)*100, color='k', linewidth=0.5, label=r'$SRF \times 100$')
        
        # plot linear perturbation 1 for each channel
        axf[i].plot(ds_per_lino.frequency*1e-3, ds_per_lino.linear1.isel(channel=i, magnitude=-1)*100, color='red', linewidth=0.5, label=r'$SRF_{pert,lin1,2dB} \times 100$')
        axf[i].plot(ds_per_lino.frequency*1e-3, ds_per_lino.linear2.isel(channel=i, magnitude=-1)*100, color='orange', linewidth=0.5, label=r'$SRF_{pert,lin2,2dB} \times 100$')

        axf[i].set_ylim([0, 1])
    
    # add plot of perturbed SRF difference
    for i, channel in enumerate(mwi.channels_str):
        ax[i].hist(ds_diff.data.isel(channel=i, perturbation=0, magnitude=-1), color='red', bins=bins, alpha=0.5, label=r'with $SRF_{pert,lin1,2dB}$')
        ax[i].hist(ds_diff.data.isel(channel=i, perturbation=1, magnitude=-1), color='orange', bins=bins, alpha=0.5, label=r'with $SRF_{pert,lin2,2dB}$')    

    axf[0].legend(frameon=False, ncol=1, bbox_to_anchor=(0.5, 1.1), loc='lower center')
    ax[0].legend(frameon=False, ncol=1, bbox_to_anchor=(0.5, 1.1), loc='lower center')
    
    axf[2].set_ylabel('Sensitivity')
    axf[-1].set_xlabel('Frequency [GHz]')
    ax[2].set_ylabel('Count')
    ax[-1].set_xlabel('$\Delta$ TB [K]')
    
    plt.savefig(path_plot+'maximum_error_srf_only_at_bandwidth_edge/maximum_error_srf_only_at_bandwidth_edge.png', dpi=300)
    
    # comment: at channel 14 and 15 some extreme profiles occur - how do they look like?
    # assumption: profiles with very low IWV in the Arctic, where we have a less broad emission line?
    #profiles_sus = ds_delta_max['diff'].sel(location='wing', channel='14')[ds_delta_max['diff'].sel(location='wing', channel='14') < - 6]
    #profiles_sus.profile
   # 
   # plt.plot(ds_tb.tb.sel(profile=profiles_sus.profile).T)
   # plt.plot(ds_tb.tb.T, color='k', alpha=0.2)
    
    #%%
    plt.close('all')
