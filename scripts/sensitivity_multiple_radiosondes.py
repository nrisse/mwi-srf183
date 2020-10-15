

import numpy as np
import sys
import re
import pandas as pd
import matplotlib.pyplot as plt

sys.path.append('/home/nrisse/uniHome/WHK/eumetsat/scripts')
from importer import Sensitivity
from brightness_temperature_plot import PAMTRA_TB
from sensitivity import MicrowaveImager
from mwi_183 import MWI183GHz as mwi
import radiosondes_download_wyo as wyo


def get_header_mask(array, expression):
    """
    
    """
    
    r = re.compile(expression)
    vmatch = np.vectorize(lambda x:bool(r.match(x)))
    mask = vmatch(array)
    
    return mask


if __name__ == '__main__':
    
    # set paths
    path_base = '/home/nrisse/uniHome/WHK/eumetsat/'
    sys.path.append(path_base)
    
    # read sensitivity data
    Sens = Sensitivity(path=path_base+'sensitivity/')
    
    # linearize and normalize sensitivity data
    mwi_dsb_data_prep = Sens.prepare_data(Sens.mwi_dsb_data)
    
    # read pamtra simulations
    Pam = PAMTRA_TB()
    Pam.read_all()
    Pam.pam_data_df
    
    # combine spectral response function and modelled brightness temperature
    pam_srf = MicrowaveImager.join_pam_on_srf(pam=Pam.pam_data_df, srf=mwi_dsb_data_prep)
    
    # write data to arrays for calculation of vierual MWI TB
    profiles = np.array(pam_srf.columns[1:-5], dtype=str)
    tb = pam_srf.iloc[:, 1:-5]  
    srf = pam_srf.iloc[:, -5:]
    
    # calculate difference between TB Pamtra and TB MWI
    delta_tb_freq_center = pd.DataFrame(index=mwi.channels_str, columns=profiles, data=np.nan)
    delta_tb_freq_bw = pd.DataFrame(index=mwi.channels_str, columns=profiles, data=np.nan)
    delta_tb_freq_bw_center = pd.DataFrame(index=mwi.channels_str, columns=profiles, data=np.nan)
    
    for i, channel in enumerate(mwi.channels_str):
        
        for j, profile in enumerate(profiles):
            
            # calculate virtual MWI measurement
            tb_mwi = MicrowaveImager.calculate_tb_mwi(tb=tb[profile].values, srf=srf['ch'+channel+' sensitivity'])
            
            # freq_center
            tb_pam = MicrowaveImager.calculate_tb_pamtra(tb=Pam.pam_data_df, avg_freq=mwi.freq_center[i, :], profile=profile)
            delta_tb_freq_center.iloc[i, j] = tb_mwi - tb_pam
            
            # freq_bw
            tb_pam = MicrowaveImager.calculate_tb_pamtra(tb=Pam.pam_data_df, avg_freq=mwi.freq_bw[i, :], profile=profile)
            delta_tb_freq_bw.iloc[i, j] = tb_mwi - tb_pam
            
            # freq_bw__center
            tb_pam = MicrowaveImager.calculate_tb_pamtra(tb=Pam.pam_data_df, avg_freq=mwi.freq_bw_center[i, :], profile=profile)
            delta_tb_freq_bw_center.iloc[i, j] = tb_mwi - tb_pam
    
    # write result to textfile.
    outfile_freq_center = path_base + 'data/delta_tb/' + 'delta_tb_freq_center.txt'
    header = '# delta_tb = tb_mwi - tb_pamtra\n' + \
             '# tb_pamtra calculated from two center frequencies of each channel\n'
    with open(outfile_freq_center, 'w') as f:
        f.write(header)
        delta_tb_freq_center.to_csv(f, index_label='MWI-channel')
    
    outfile_freq_bw = path_base + 'data/delta_tb/' + 'delta_tb_freq_bw.txt'
    header = '# delta_tb = tb_mwi - tb_pamtra\n' + \
             '# tb_pamtra calculated from four bandwidth edge frequencies of each channel\n'
    with open(outfile_freq_bw, 'w') as f:
        f.write(header)
        delta_tb_freq_bw.to_csv(f, index_label='MWI-channel')
        
    outfile_freq_bw_center = path_base + 'data/delta_tb/' + 'delta_tb_freq_bw_center.txt'
    header = '# delta_tb = tb_mwi - tb_pamtra\n' + \
             '# tb_pamtra calculated from two center frequencies and four bandwidth edge frequencies of each channel\n'
    with open(outfile_freq_bw_center, 'w') as f:
        f.write(header)
        delta_tb_freq_bw_center.to_csv(f, index_label='MWI-channel')
    
    # TODO: this step for each of the TB calculations. noise, less measurements
    # These difference files can then be evaluated, seasonal, whatever. No more calculations than these needed afterall

    
    
    # put next steps in new script to access the data needed
    
    
    import matplotlib.pyplot as plt
    plt.imshow(delta_tb)
    
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
    
    
    # Delta as function of LWP for every channel
