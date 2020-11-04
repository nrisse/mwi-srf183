

import numpy as np
from radiosonde import wyo
from mwi_info import mwi


"""
Influence of noise and data reduction on the result
"""

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

    #%% create indices for summarizing statistics
    station_id = np.array([x[3:8] for x in delta_tb.profile])
    date = np.array([datetime.datetime.strptime(x[-12:], '%Y%m%d%H%M') for x in delta_tb.profile])
    year = np.array([x.year for x in date])
    month = np.array([x.month for x in date])
    
    ix_nya = station_id == wyo.station_id['Ny Alesund']
    ix_snp = station_id == wyo.station_id['Singapore']
    ix_ess = station_id == wyo.station_id['Essen']
    ix_bar = station_id == wyo.station_id['Barbados']
    ix_std = station_id == '00000'
    
    ix_2019 = year == 2019
    ix_2020 = year == 2020
    
    ix_djf = np.isin(month, [12, 1, 2])
    ix_mam = np.isin(month, [3, 4, 5])
    ix_jja = np.isin(month, [6, 7, 8])
    ix_son = np.isin(month, [9, 10, 11])
    
    ix_red_lev_1 = delta_tb.reduction_level == 1
    
    #%% summarize data
    # average over profiles
    avg = 'profile'
    
    # averages Ny Alesund
    mean_nya = delta_tb.mean_freq_bw[:, ix_nya & ix_2019, :, :].mean(avg)  # 2019
    mean_nya_djf = delta_tb.mean_freq_bw[:, ix_nya & ix_2019 & ix_djf, :, :].mean(avg)  # DJF 2019
    mean_nya_mam = delta_tb.mean_freq_bw[:, ix_nya & ix_2019 & ix_mam, :, :].mean(avg)  # MAM 2019
    mean_nya_jja = delta_tb.mean_freq_bw[:, ix_nya & ix_2019 & ix_jja, :, :].mean(avg)  # JJA 2019
    mean_nya_son = delta_tb.mean_freq_bw[:, ix_nya & ix_2019 & ix_son, :, :].mean(avg)  # SON 2019
    
    # averages Singapore
    mean_snp = delta_tb.mean_freq_bw[:, ix_snp & ix_2019, :, :].mean(avg)  # 2019
    mean_snp_djf = delta_tb.mean_freq_bw[:, ix_snp & ix_2019 & ix_djf, :, :].mean(avg)  # DJF 2019
    mean_snp_mam = delta_tb.mean_freq_bw[:, ix_snp & ix_2019 & ix_mam, :, :].mean(avg)  # MAM 2019
    mean_snp_jja = delta_tb.mean_freq_bw[:, ix_snp & ix_2019 & ix_jja, :, :].mean(avg)  # JJA 2019
    mean_snp_son = delta_tb.mean_freq_bw[:, ix_snp & ix_2019 & ix_son, :, :].mean(avg)  # SON 2019
    
    # all channels, avg over time, all noise, only no data reduction
    noise_nya_mean = delta_tb.mean_freq_center[:, ix_nya & ix_2019, :, ix_red_lev_1].mean(avg)
    noise_nya_std = delta_tb.std_freq_center[:, ix_nya & ix_2019, :, ix_red_lev_1].mean(avg)
    noise_snp_mean = delta_tb.mean_freq_center[:, ix_snp & ix_2019, :, ix_red_lev_1].mean(avg)
    noise_snp_std = delta_tb.std_freq_center[:, ix_snp & ix_2019, :, ix_red_lev_1].mean(avg)
    noise_ess_mean = delta_tb.mean_freq_center[:, ix_ess & ix_2019, :, ix_red_lev_1].mean(avg)
    noise_ess_std = delta_tb.std_freq_center[:, ix_ess & ix_2019, :, ix_red_lev_1].mean(avg)
    
    # indexing: .sel(channel='15') with channel being one dimension
    
    #%% influence of noise (data_reduction == 1)
    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_subplot(111)
    ax.set_title('')

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
    