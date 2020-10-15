

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import sys
sys.path.append('/home/nrisse/uniHome/WHK/eumetsat/scripts')
from mwi_183 import MWI183GHz as mwi
from importer import Radiosonde
import radiosondes_download_wyo as wio

"""
DESCRIPTION

Evaluation of delta_tb depending on the LWP of the profiles

"""


def calculate_iwv(z, T, p, r):
    """
    Calculate IWV of profile
    
    z   height in m
    T   temperature in C
    p   pressure in hPa
    r   water vapor mixing ratio in g/kg
    """
    
    Rd = 287  # J / kg K
    
    T = T + 273.15  # K
    p = p * 100  # Pa
    r = r * 1e-3  # kg/kg
    
    # density of water vapor [kg/m3]
    rho_v = p / (Rd * T) * r / (1 - 1.608 * r)
    
    # integrated water vapor [kg/m2]
    dz = z[1:] - z[:-1]
    iwv = np.nansum(rho_v[:-1] * dz)
    
    return iwv


if __name__ == '__main__':
    
    # todo: get only 2019 profiles here and add the year to header
    # todo: include data availability within that year for every profile
    
    path_base = '/home/nrisse/uniHome/WHK/eumetsat/'
    
    file_iwv = path_base + 'data/iwv/iwv.txt'
    file_freq_center = path_base + 'data/delta_tb/' + 'delta_tb_freq_center.txt'
    file_freq_bw = path_base + 'data/delta_tb/' + 'delta_tb_freq_bw.txt'
    file_freq_bw_center = path_base + 'data/delta_tb/' + 'delta_tb_freq_bw_center.txt'
    
    # figures
    fig_freq_center = path_base + 'plots/iwv_dependency/iwv_dependency_freq_center.png'
    fig_freq_bw = path_base + 'plots/iwv_dependency/iwv_dependency_freq_bw.png'
    fig_freq_bw_center = path_base + 'plots/iwv_dependency/iwv_dependency_freq_bw_center.png'
    
    fig_all = path_base + 'plots/iwv_dependency/iwv_dependency_all.png'
    
    #%%
    # calculate iwv of radiosonde profiles
    RS = Radiosonde()
    profiles = delta_tb_freq_center.columns
    profiles = profiles.drop('standard_atmosphere')
    
    iwv = pd.DataFrame(columns=delta_tb_freq_center.columns, data=np.nan, index=['iwv'])
    
    iwv.loc['iwv', 'standard_atmosphere'] = 0
    
    for i, profile in enumerate(profiles):
        
        print('profile {}/{}'.format(i, len(profiles)))
        
        station_id = profile[3:8]
        year = profile[9:13]
        month = profile[13:15]
        day = profile[15:17]
        
        RS.read_profile(station_id=station_id, year=year, month=month, day=day)
        
        iwv.loc['iwv', profile] = calculate_iwv(z=RS.profile['z [m]'].values, T=RS.profile['T [C]'].values, 
                                                p=RS.profile['p [hPa]'].values, r=RS.profile['r [g/kg]'].values)
    
    # save iwv to file
    iwv.to_csv(file_iwv, sep=',')
    
    #%%
    # read iwv from file
    iwv = pd.read_csv(file_iwv, index_col=0)
    
    # read delta_tb from file
    delta_tb_freq_center = pd.read_csv(file_freq_center, sep=',', comment='#', index_col=0)
    delta_tb_freq_bw = pd.read_csv(file_freq_bw, sep=',', comment='#', index_col=0)
    delta_tb_freq_bw_center = pd.read_csv(file_freq_bw_center, sep=',', comment='#', index_col=0)
        
    # colors for plot
    colors = {'01004': 'b',
              '10410': 'g',
              '48698': 'r',
              '78954': 'orange',
              }
    
    #%%
    # plot for delta_tb_freq_center
    fig, axes = plt.subplots(5, 1, figsize=(6, 6), sharex=True, sharey=True)
    fig.suptitle('Deviation of virtual MWI measurement from TB calculated at central channel frequencies\n' +
                 'as function of integrated water vapor')
    
    axes[2].set_ylabel('$\Delta TB$')
    axes[-1].set_xlabel('Integrated water vapor [kg m$^{-2}$]')
    
    for i, ax in enumerate(axes):
        
        ax.scatter(iwv.loc['iwv', 'standard_atmosphere'], delta_tb_freq_center.loc[14+i, 'standard_atmosphere'], color='k')
        
        for profile in colors.keys():
            
            ix = [x[3:8] == profile for x in profiles]
            ix.append(False)
            
            ax.scatter(iwv.loc['iwv', ix], delta_tb_freq_center.loc[14+i, ix], color=colors[profile[:8]], edgecolor=None, alpha=0.5)
   
   plt.savefig(fig_freq_center) 
   
    #%%
    # plot for delta_tb_freq_bw
    fig, axes = plt.subplots(5, 1, figsize=(6, 6), sharex=True, sharey=True)
    fig.suptitle('Deviation of virtual MWI measurement from TB calculated at channel bandwidth edge frequencies\n' +
                 'as function of integrated water vapor')

    axes[2].set_ylabel('$\Delta TB$')
    axes[-1].set_xlabel('Integrated water vapor [kg m$^{-2}$]')
    
    for i, ax in enumerate(axes):
        
        ax.scatter(iwv.loc['iwv', 'standard_atmosphere'], delta_tb_freq_bw.loc[14+i, 'standard_atmosphere'], color='k')
        
        for profile in colors.keys():
            
            ix = [x[3:8] == profile for x in profiles]
            ix.append(False)
            
            ax.scatter(iwv.loc['iwv', ix], delta_tb_freq_bw.loc[14+i, ix], color=colors[profile[:8]], edgecolor=None, alpha=0.5)
   
   plt.savefig(fig_freq_bw)
   
    #%%
    # plot for delta_tb_freq_bw_center
    fig, axes = plt.subplots(5, 1, figsize=(6, 6), sharex=True, sharey=True)
    fig.suptitle('Deviation of virtual MWI measurement from TB calculated at channel bandwidth edge and central frequencies\n' +
                 'as function of integrated water vapor')
    
    axes[2].set_ylabel('$\Delta TB$')
    axes[-1].set_xlabel('Integrated water vapor [kg m$^{-2}$]')
    
    for i, ax in enumerate(axes):
        
        ax.scatter(iwv.loc['iwv', 'standard_atmosphere'], delta_tb_freq_bw_center.loc[14+i, 'standard_atmosphere'], color='k')
        
        for profile in colors.keys():
            
            ix = [x[3:8] == profile for x in profiles]
            ix.append(False)
            
            ax.scatter(iwv.loc['iwv', ix], delta_tb_freq_bw_center.loc[14+i, ix], color=colors[profile[:8]], edgecolor=None, alpha=0.5)
   
   plt.savefig(fig_freq_bw_center)

    #%% ALL IN ONE
    fig, axes = plt.subplots(5, 3, figsize=(6, 8), sharex=True, sharey=True)
    fig.suptitle('Deviation as function of integrated water vapor\nAtmosphere from daily 12 UTC radiosonde observations in 2019')
    
    axes[2, 0].set_ylabel(r'$\Delta TB = TB_{MWI} - TB_{PAMTRA}$ [K]')
    axes[-1, 1].set_xlabel('Integrated water vapor [kg m$^{-2}$]')
    
    axes[0, 0].set_title(r'$TB_{PAMTRA}$ at'+'\n'+r'$\nu_{center}$', fontsize=8)
    axes[0, 1].set_title(r'$TB_{PAMTRA}$ at'+'\n'+r'$\nu_{center \pm \frac{1}{2} bandwidth}$', fontsize=8)
    axes[0, 2].set_title(r'$TB_{PAMTRA}$ at'+'\n'+r'$\nu_{center}$ and $\nu_{center \pm \frac{1}{2} bandwidth}$', fontsize=8)
    
    c_list = [colors[profile[3:8]] for profile in profiles]
    c_list.append('k')
    
    for ax in axes.flatten():
        
        # x axis
        ax.set_xticks(ticks=np.arange(0, 150, 25), minor=False)
        ax.set_xticks(ticks=np.arange(0, 150, 5), minor=True)
        
        # y axis
        ax.set_yticks(ticks=np.arange(-2, 2, 0.5), minor=False)
        ax.set_yticks(ticks=np.arange(-2, 2, 0.1), minor=True)
        
        ax.tick_params(which='major')
        ax.tick_params(which='minor', length=1)
        ax.grid('both', alpha=0.5)
        
        ax.axhline(y=0, color='k', linewidth=1, alpha=0.5)
        
        ax.set_ylim([-1.4, 1.4])
        ax.set_xlim([0, 85])
        
    # annotate channel name
    for i, ax in enumerate(axes[:, -1]):
        ax.annotate(text=mwi.freq_txt[i], xy=(1.1, 0.5), xycoords='axes fraction', backgroundcolor="w",
                    annotation_clip=False, horizontalalignment='left', verticalalignment='center', fontsize=8)
    
    for i, ax in enumerate(axes[:, 0]):
        ax.scatter(iwv.loc['iwv', :], delta_tb_freq_center.loc[14+i, :], s=2, c=c_list, linewidths=0, alpha=0.5)
    
    for i, ax in enumerate(axes[:, 1]):
        
        ax.scatter(iwv.loc['iwv', :], delta_tb_freq_bw.loc[14+i, :], s=2, c=c_list, linewidths=0, alpha=0.5)
    
    for i, ax in enumerate(axes[:, 2]):
        
        ax.scatter(iwv.loc['iwv', :], delta_tb_freq_bw_center.loc[14+i, :], s=2, c=c_list, linewidths=0, alpha=0.5)
    
    fig.tight_layout()

    # legend below
    patches = []
    stations = wio.station_id.keys()
    for station in stations:
        patches.append(mpatches.Patch(color=colors[wio.station_id[station]], label=station))
    patches.append(mpatches.Patch(color='k', label='Standard atm.'))
    leg = axes[-1, -1].legend(handles=patches, bbox_to_anchor=(1.05, 0.2), loc='upper left', frameon=False, ncol=1, fontsize=6, title='Radiosonde location:')
    plt.setp(leg.get_title(),fontsize=6)
    
    plt.savefig(fig_all, dpi=400)
    
    #%%
    """
    RESULT
    the IWV explains the error for the channel very well, except for channel 18 (closest to maximum)
    for this, temperature can be included
    
    differences in the calculation method ....
    
    under clear-sky conditions the deviation from MWI measurement and model
    simulation at the MWI-frequencies can be corrected if the IWV of the atmosphere
    measured by MWI is known
    
    how do clouds influence this pattern? Suggestion: ice clouds strongly perturb 
    the simple pattern. Thin liquid clouds may not change the result
    """
