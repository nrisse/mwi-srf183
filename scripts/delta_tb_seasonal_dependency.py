

import numpy as np
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import sys
sys.path.append('/home/nrisse/uniHome/WHK/eumetsat/scripts')
from importer import Sensitivity, Delta_TB
from mwi_info import mwi


"""
Description

Analyze seasonal and regional dependency of the difference between the virtual
MWI measurement and the TB calculated with PAMTRA.

Requires:
    - seven radiosonde profiles
    
Caution: no clouds included
"""


def get_header_mask(array, expression):
    """
    
    """
    
    r = re.compile(expression)
    vmatch = np.vectorize(lambda x:bool(r.match(x)))
    mask = vmatch(array)
    
    return mask


def read_pamtra_simulation(self, path='/home/nrisse/uniHome/WHK/eumetsat/'):
    """
    Read data from PAMTRA simulation
    """
    
    for i, profile in enumerate(profiles):
        
        file = path_data + profiles_tb_data[profile]
        
        if i == 0:
            
            pam_data_df = pd.read_csv(file, delimiter=',', comment='#')
            pam_data_df.rename(columns={'TB': profile}, inplace=True)
        
        else:
            
            pam_data = pd.read_csv(file, delimiter=',', comment='#')
            pam_data_df[profile] = pam_data['TB']
            
            # check if frequencies are identical (!!!) if not, values have to be joined
            assert (pam_data['Frequency [GHz]'] == pam_data_df['Frequency [GHz]']).all
    
    pam_data_df.rename(columns={'Frequency [GHz]': 'frequency [GHz]'}, inplace=True)  # for the join later
    
    return pam_data_df


if __name__ == '__main__':
    
    #%% read nc files
    # delta_tb shape: (channel, profile, noise_level, reduction_level)
    # delta_tb.mean_freq_center
    # delta_tb.std_freq_center
    # delta_tb.mean_freq_bw
    # delta_tb.std_freq_bw
    # delta_tb.mean_freq_bw_center
    # delta_tb.std_freq_bw_center
    delta_tb = Delta_TB()
    delta_tb.read_data()
    
    station_id = np.array([x[3:8] for x in delta_tb.profile])
    date = np.array([datetime.datetime.strptime(x[-12:], '%Y%m%d%H%M') for x in delta_tb.profile])
    
    
    # play with different result matrices  - show std of noise, mean values etc
    # classify the profile indices to make seasonal evaluations
    plt.imshow(delta_tb.std_freq_bw.mean(axis=(0, 1)))
    
    # profile regular expression
    profile_classes_expr = {'Ny-Alesund (Feb 2020)': 'ID_'+wyo.station_id['Ny Alesund']+'_202002',
                            'Ny-Alesund (Aug 2020)': 'ID_'+wyo.station_id['Ny Alesund']+'_202008',
                            'Essen (Feb 2020)': 'ID_'+wyo.station_id['Essen']+'_202002',
                            'Essen (Aug 2020)': 'ID_'+wyo.station_id['Essen']+'_202008',
                            'Singapore (Feb 2020)': 'ID_'+wyo.station_id['Singapore']+'_202002',
                            'Singapore (Aug 2020)': 'ID_'+wyo.station_id['Singapore']+'_202008',
                            'Barbados (Feb 2020)': 'ID_'+wyo.station_id['Barbados']+'_202002',
                            'Barbados (Aug 2020)': 'ID_'+wyo.station_id['Barbados']+'_202008',
                            'Standard atmosphere (RH=0%)': 'standard_atmosphere'}
    
    profile_classes_expr = {'Ny-Alesund (2019)': 'ID_'+wyo.station_id['Ny Alesund']+'_2019',
                            'Essen (2019)': 'ID_'+wyo.station_id['Essen']+'_202002',
                            'Singapore (2019)': 'ID_'+wyo.station_id['Singapore']+'_2019',
                            'Barbados (2019)': 'ID_'+wyo.station_id['Barbados']+'_2019',
                            'Standard atmosphere (RH=0%)': 'standard_atmosphere'}
    
    profile_classes = np.array(list(profile_classes_expr.keys()))

    # numerical interpretation
    # statistics for ever channel
    delta_tb_channel_mean = np.mean(delta_tb, axis=0)
    
    
    # depending on atmosphere    
    mwi_statistics_mean = pd.DataFrame(columns=mwi.channels_str, index=profile_classes, data=-9999)
    
    for profile_class in profile_classes:

        ix = get_header_mask(array=profiles, expression=profile_classes_expr[profile_class])
        mwi_statistics_mean.loc[profile_class, :] = np.mean(delta_tb[ix, :], axis=0)

    plt.imshow(mwi_statistics_mean)
    plt.colorbar()
    plt.xlabel('Channel')
    plt.ylabel('profile_classes')
    
    # graphical interpretation of the resulting difference matrix
    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_subplot(111)
    ax.set_title(title)

    dx = np.linspace(-0.3, 0.3, 7)  # space between boxplots

    for p_id, profile in enumerate(profiles):
        
        for i, ch in enumerate(mwi.channels_str):

            boxprops = dict(facecolor=pam_colors[profile], color=pam_colors[profile])
            flierprops = dict(markeredgecolor='k', markersize=2)
            medianprops = dict(color='k')

            ax.boxplot(x=delta_tb, notch=True, sym="d", positions=[mwi.channels_int[i] + dx[p_id]], widths=0.075,
                       boxprops=boxprops, flierprops=flierprops, medianprops=medianprops, patch_artist=True)

    ax.set_ylabel(r'$\Delta TB = TB_{MWI} - TB_{PAMTRA}$ [K]')

    # axis limits
    ax.set_ylim(ylim)
    ax.set_xlim([13.5, 18.5])

    ax.set_xticks(np.arange(14, 19), minor=True)
    ax.set_xticks(np.arange(13.5, 19.5), minor=False)
    ax.set_xticklabels(mwi.freq_txt, minor=True)
    ax.set_xticklabels('', minor=False)
    ax.xaxis.grid(True, which='major')
    ax.yaxis.grid(True)
    ax.tick_params('x', length=0, width=0, which='minor')

    ax.axhline(y=0, color='k', linestyle='--', linewidth=.75)

    # legend settings
    patches = []
    for profile in profiles:
        patches.append(mpatches.Patch(color=pam_colors[profile], label=pam_label_detail[profile]))

    ax.legend(handles=patches, bbox_to_anchor=(1.05, 0.5), loc='center left', frameon=False)

    fig.tight_layout()

    plt.savefig(self._path_fig + filename, dpi=400)
    #########
    
    # 
    
    # todo: rewrite using the already calculated delta TB !!!
    
    # plot the tb simulation
    pam_data_df = read_pamtra_simulation()
    # for plot see plot_brightness_temperature.py

    
    # Plot result without noise

    # join brightness temperature to the linear sensitivity dataframe
    sens_mwi_dsb = self.join_pam_on_srf(pam=self.pam_data_df, srf=self.mwi_dsb_data_lino)

    # create result for each of the modelled profiles
    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_subplot(111)
    ax.set_title(title)

    for profile in profiles:

        for i, ch in enumerate(mwi.channels_str):
            tb_mwi = self.calculate_tb_mwi(tb=sens_mwi_dsb[profile].values,
                                           srf=sens_mwi_dsb['ch' + ch + ' sensitivity'].values)
            tb_pam = self.calculate_tb_pamtra(freqs=frequencies[i, :], profile=profile)

            delta_tb = tb_mwi - tb_pam

            ax.plot(mwi.channels_int[i], delta_tb, label=pam_label_detail[profile], **pam_point_fmt[profile])

    ax.set_ylabel(r'$\Delta TB = TB_{MWI} - TB_{PAMTRA}$ [K]')
    
    # axis limits
    ax.set_xlim([13.5, 18.5])
    ax.set_ylim(ylim)

    # axis tick settings
    ax.set_xticks(np.arange(14, 19), minor=True)
    ax.set_xticks(np.arange(13.5, 19.5), minor=False)
    ax.set_xticklabels(mwi.freq_txt, minor=True)
    ax.set_xticklabels('', minor=False)
    ax.xaxis.grid(True, which='major')
    ax.yaxis.grid(True)
    ax.tick_params('x', length=0, width=0, which='minor')
    
    # add 0-line
    ax.axhline(y=0, color='k', linestyle='--', linewidth=.75)
    
    # legend
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), bbox_to_anchor=(1.05, 0.5), loc='center left', frameon=False)
    
    # layout
    fig.tight_layout()
    
    plt.savefig(self._path_fig + filename, dpi=200)


    #%% Plot result with noise as boxplot
    # join brightness temperature to the linear sensitivity dataframe
    sens_mwi_dsb = self.join_pam_on_srf(pam=self.pam_data_df, srf=self.mwi_dsb_data_lino)

    # create noise shape=(n_freq, n_noise, len(mwi.channels_str))
    srf_plus_noise = self.create_noise_values(dataframe=self.mwi_dsb_data_lino, std=std)

    # create result for each of the modelled profiles
    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_subplot(111)
    ax.set_title(title)

    dx = np.linspace(-0.3, 0.3, 7)  # space between boxplots

    for p_id, profile in enumerate(profiles):

        for i, ch in enumerate(mwi.channels_str):
            tb_mwi = self.calculate_tb_mwi(tb=sens_mwi_dsb[profile].values,
                                           srf=srf_plus_noise[:, :, i])
            tb_pam = self.calculate_tb_pamtra(freqs=frequencies[i, :], profile=profile)

            delta_tb = tb_mwi - tb_pam

            boxprops = dict(facecolor=pam_colors[profile], color=pam_colors[profile])
            flierprops = dict(markeredgecolor='k', markersize=2)
            medianprops = dict(color='k')

            ax.boxplot(x=delta_tb, notch=True, sym="d", positions=[mwi.channels_int[i] + dx[p_id]], widths=0.075,
                       boxprops=boxprops, flierprops=flierprops, medianprops=medianprops, patch_artist=True)

    ax.set_ylabel(r'$\Delta TB = TB_{MWI} - TB_{PAMTRA}$ [K]')

    # axis limits
    ax.set_ylim(ylim)
    ax.set_xlim([13.5, 18.5])

    ax.set_xticks(np.arange(14, 19), minor=True)
    ax.set_xticks(np.arange(13.5, 19.5), minor=False)
    ax.set_xticklabels(mwi.freq_txt, minor=True)
    ax.set_xticklabels('', minor=False)
    ax.xaxis.grid(True, which='major')
    ax.yaxis.grid(True)
    ax.tick_params('x', length=0, width=0, which='minor')

    ax.axhline(y=0, color='k', linestyle='--', linewidth=.75)

    # legend settings
    patches = []
    for profile in profiles:
        patches.append(mpatches.Patch(color=pam_colors[profile], label=pam_label_detail[profile]))

    ax.legend(handles=patches, bbox_to_anchor=(1.05, 0.5), loc='center left', frameon=False)

    fig.tight_layout()

    plt.savefig(self._path_fig + filename, dpi=400)



    # RESULT 1 (MWI-RX183_DSB_Matlab.xlsx)
    # TB PAMTRA is mean of upper and lower central frequency
    title_res1 = 'MWI virtual measurement minus PAMTRA simulation at channel frequencies\nSensitivity data: ' \
                 'MWI-RX183_DSB_Matlab.xlsx'
    filename_res1 = 'result_1_MWI-RX183_DSB_Matlab.png'
    self.plot_result(frequencies=mwi.freq_center, filename=filename_res1, title=title_res1, ylim=[-0.6, 0.2])

    # RESULT 4 (MWI-RX183_DSB_Matlab.xlsx)
    # TB PAMTRA is mean of the four frequencies at the edge of the bandwidth
    title_res4 = 'MWI virtual measurement minus PAMTRA simulation at channel bandwith edges\nSensitivity data: ' + \
                 'MWI-RX183_DSB_Matlab.xlsx'
    filename_res4 = 'result_4_MWI-RX183_DSB_Matlab.png'
    self.plot_result(frequencies=mwi.freq_bw, filename=filename_res4, title=title_res4, ylim=[-0.1, 0.8])

    # RESULT 5 (MWI-RX183_DSB_Matlab.xlsx)
    # TB PAMTRA is mean of the four frequencies at the edge of the bandwidth
    title_res4 = 'MWI virtual measurement minus PAMTRA simulation at channel bandwith edges and center ' \
                 'frequency\nSensitivity data: MWI-RX183_DSB_Matlab.xlsx'
    filename_res4 = 'result_5_MWI-RX183_DSB_Matlab.png'
    self.plot_result(frequencies=mwi.freq_bw_center, filename=filename_res4, title=title_res4, ylim=[-0.1, 0.8])

    # result with perturbation of varying standard deviation
    standard_deviations = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]) / 100

    for std in standard_deviations:

        title_res1b = 'MWI virtual measurement minus PAMTRA simulation at channel frequencies\n' \
                      'Sensitivity data: 1000 perturbed measurements (MWI-RX183_DSB_Matlab.xlsx)'
        filename_res1b = 'result_1B_'+str(std)+'_MWI-RX183_DSB_Matlab.png'
        self.plot_result_noise(frequencies=mwi.freq_center, std=std, filename=filename_res1b, title=title_res1b,
                               ylim=[-1, 1])

        title_res4b = 'MWI virtual measurement minus PAMTRA simulation at channel bandwith edges\n' \
                      'Sensitivity data: 1000 perturbed measurements (MWI-RX183_DSB_Matlab.xlsx)'
        filename_res4b = 'result_4B_'+str(std)+'_MWI-RX183_DSB_Matlab.png'
        self.plot_result_noise(frequencies=mwi.freq_bw, std=std, filename=filename_res4b, title=title_res4b,
                               ylim=[-1, 1])

        title_res5b = 'MWI virtual measurement minus PAMTRA simulation at channel bandwith edges\n' \
                      'Sensitivity data: 1000 perturbed measurements (MWI-RX183_DSB_Matlab.xlsx)'
        filename_res5b = 'result_5B_'+str(std)+'_MWI-RX183_DSB_Matlab.png'
        self.plot_result_noise(frequencies=mwi.freq_bw_center, std=std, filename=filename_res5b, title=title_res5b,
                               ylim=[-1, 1])
