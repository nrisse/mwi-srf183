

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


class MicrowaveImager:
    
    # frequencies of channels (2 frequencies per channel)
    ch_14_f = np.array([183.31-7.0, 183.31+7.0])
    ch_15_f = np.array([183.31-6.1, 183.31+6.1])
    ch_16_f = np.array([183.31-4.9, 183.31+4.9])
    ch_17_f = np.array([183.31-3.4, 183.31+3.4])
    ch_18_f = np.array([183.31-2.0, 183.31+2.0])

    ch_f_arr = np.array([ch_14_f, ch_15_f, ch_16_f, ch_17_f, ch_18_f])
    
    # bandwidth frequencies of channels (4 frequencies a)
    ch_14_bw = 2
    ch_15_bw = 1.5
    ch_16_bw = 1.5
    ch_17_bw = 1.5
    ch_18_bw = 1.5

    ch_14_f_bw = np.array([183.31-7.0-.5*ch_14_bw, 183.31-7.0+.5*ch_14_bw, 
                           183.31+7.0-.5*ch_14_bw, 183.31+7.0+.5*ch_14_bw])
    ch_15_f_bw = np.array([183.31-6.1-.5*ch_15_bw, 183.31-6.1+.5*ch_15_bw, 
                           183.31+6.1-.5*ch_15_bw, 183.31+6.1+.5*ch_15_bw])
    ch_16_f_bw = np.array([183.31-4.9-.5*ch_16_bw, 183.31-4.9+.5*ch_16_bw, 
                           183.31+4.9-.5*ch_16_bw, 183.31+4.9+.5*ch_16_bw])
    ch_17_f_bw = np.array([183.31-3.4-.5*ch_17_bw, 183.31-3.4+.5*ch_17_bw, 
                           183.31+3.4-.5*ch_17_bw, 183.31+3.4+.5*ch_17_bw])
    ch_18_f_bw = np.array([183.31-2.0-.5*ch_18_bw, 183.31-2.0+.5*ch_18_bw, 
                           183.31+2.0-.5*ch_18_bw, 183.31+2.0+.5*ch_18_bw])

    ch_f_bw_arr = np.array([ch_14_f_bw, ch_15_f_bw, ch_16_f_bw, ch_17_f_bw, ch_18_f_bw])
    
    # label for every channel
    freq_txt = ('MWI-14\n183.31±7.0 GHz', 'MWI-15\n183.31±6.1 GHz', 'MWI-16\n183.31±4.9 GHz', 'MWI-17\n183.31±3.4 GHz',
                         'MWI-18\n183.31±2.0 GHz')
    
    def __init__(self, path_sensitivity, path_fig, path_data):
        
        
        self.mwi_dsb_data = self.read_excel(path_sensitivity + 'MWI-RX183_DSB_Matlab.xlsx')
        self.mwi_data = self.read_excel(path_sensitivity + 'MWI-RX183_Matlab.xlsx')

    def print_info():
        """
        Print information on MWI
        """

        print(
        """
        https://www.eumetsat.int/website/home/Satellites/FutureSatellites/EUMETSATPolarSystemSecondGeneration/MWI/index.html
        
        The Microwave Imager (MWI) is a conically scanning radiometer, capable of measuring 
        thermal radiance emitted by the Earth, at high spatial resolution in the microwave 
        region of the electromagnetic spectrum.
        
        Channels above 89 GHz are measured at V polarisation only.
        
        Channel 	Frequency 	Bandwidth 	Polarisation 	Radiometric Sensitivity (***NEΔT) 	Footprint Size at 3dB
        MWI-14 	183.31±7.0 GHz 	2x2000 MHz 	V 	1.3 	10 km
        MWI-15 	183.31±6.1 GHz 	2x1500 MHz 	V 	1.2 	10 km
        MWI-16 	183.31±4.9 GHz 	2x1500 MHz 	V 	1.2 	10 km
        MWI-17 	183.31±3.4 GHz 	2x1500 MHz 	V 	1.2 	10 km
        MWI-18 	183.31±2.0 GHz 	2x1500 MHz 	V 	1.3 	10 km
        """
        )

  
if __name__ == '__main__':
    
    info()
    
    # set paths
    path_fig = '/home/nrisse/uniHome/WHK/eumetsat/plots/'
    path_sensitivity = '/home/nrisse/uniHome/WHK/eumetsat/sensitivity/'
    path_data = '/home/nrisse/uniHome/WHK/eumetsat/data/'
    
    #%% read data from MWI-RX183_DSB_Matlab.xlsx
    file_excel_dsb = path_sensitivity + 'MWI-RX183_DSB_Matlab.xlsx'
    
    data_dsb_ch14 = pd.read_excel(file_excel_dsb, sheet_name='Ch14', usecols=[0, 1], names=['frequency [GHz]', 'sensitivity [dB]'], header=None)
    data_dsb_ch15 = pd.read_excel(file_excel_dsb, sheet_name='Ch15', usecols=[0, 1], names=['frequency [GHz]', 'sensitivity [dB]'], header=None)
    data_dsb_ch16 = pd.read_excel(file_excel_dsb, sheet_name='Ch16', usecols=[0, 1], names=['frequency [GHz]', 'sensitivity [dB]'], header=None)
    data_dsb_ch17 = pd.read_excel(file_excel_dsb, sheet_name='Ch17', usecols=[0, 1], names=['frequency [GHz]', 'sensitivity [dB]'], header=None)
    data_dsb_ch18 = pd.read_excel(file_excel_dsb, sheet_name='Ch18', usecols=[0, 1], names=['frequency [GHz]', 'sensitivity [dB]'], header=None)
    
    # check if frequencies are the same
    assert np.sum(data_dsb_ch14.iloc[:, 0] != data_dsb_ch15.iloc[:, 0]) == 0
    assert np.sum(data_dsb_ch14.iloc[:, 0] != data_dsb_ch16.iloc[:, 0]) == 0
    assert np.sum(data_dsb_ch14.iloc[:, 0] != data_dsb_ch17.iloc[:, 0]) == 0
    assert np.sum(data_dsb_ch14.iloc[:, 0] != data_dsb_ch18.iloc[:, 0]) == 0
    
    # write measurement into single dataframe
    mwi_dsb_data = pd.DataFrame()
    mwi_dsb_data['frequency [GHz]'] = data_dsb_ch14.iloc[:, 0]  # use frequency from channel 14
    mwi_dsb_data['ch14 sensitivity [dB]'] = data_dsb_ch14.iloc[:, 1]
    mwi_dsb_data['ch15 sensitivity [dB]'] = data_dsb_ch15.iloc[:, 1]
    mwi_dsb_data['ch16 sensitivity [dB]'] = data_dsb_ch16.iloc[:, 1]
    mwi_dsb_data['ch17 sensitivity [dB]'] = data_dsb_ch17.iloc[:, 1]
    mwi_dsb_data['ch18 sensitivity [dB]'] = data_dsb_ch18.iloc[:, 1]
    
    del data_dsb_ch14, data_dsb_ch15, data_dsb_ch16, data_dsb_ch17, data_dsb_ch18
    
    #%% read data from MWI-RX183_Matlab.xslx
    file_excel = path_sensitivity + 'MWI-RX183_Matlab.xlsx'

    data_ch14 = pd.read_excel(file_excel, sheet_name='Ch14', usecols=[0, 1], names=['frequency [GHz]', 'sensitivity [dB]'], header=None)
    data_ch15 = pd.read_excel(file_excel, sheet_name='Ch15', usecols=[0, 1], names=['frequency [GHz]', 'sensitivity [dB]'], header=None)
    data_ch16 = pd.read_excel(file_excel, sheet_name='Ch16', usecols=[0, 1], names=['frequency [GHz]', 'sensitivity [dB]'], header=None)
    data_ch17 = pd.read_excel(file_excel, sheet_name='Ch17', usecols=[0, 1], names=['frequency [GHz]', 'sensitivity [dB]'], header=None)
    data_ch18 = pd.read_excel(file_excel, sheet_name='Ch18', usecols=[0, 1], names=['frequency [GHz]', 'sensitivity [dB]'], header=None)
    
    # check if frequencies are the same
    assert np.sum(data_ch14.iloc[:, 0] != data_ch15.iloc[:, 0]) == 0
    assert np.sum(data_ch14.iloc[:, 0] != data_ch16.iloc[:, 0]) == 0
    assert np.sum(data_ch14.iloc[:, 0] != data_ch17.iloc[:, 0]) == 0
    assert np.sum(data_ch14.iloc[:, 0] != data_ch18.iloc[:, 0]) == 0
    
    # write measurement into single dataframe
    mwi_data = pd.DataFrame()    
    mwi_data['frequency [GHz]'] = data_ch14.iloc[:, 0]  # use frequency from channel 14
    mwi_data['ch14 sensitivity [dB]'] = data_ch14.iloc[:, 1]
    mwi_data['ch15 sensitivity [dB]'] = data_ch15.iloc[:, 1]
    mwi_data['ch16 sensitivity [dB]'] = data_ch16.iloc[:, 1]
    mwi_data['ch17 sensitivity [dB]'] = data_ch17.iloc[:, 1]
    mwi_data['ch18 sensitivity [dB]'] = data_ch18.iloc[:, 1]
    
    del data_ch14, data_ch15, data_ch16, data_ch17, data_ch18

    #%% plot sensitivity measurement
    fig, axes = plt.subplots(5, 1, sharex=True, figsize=(9, 6))
    fig.suptitle('Bandpass measurements of MWI channels 14 to 18')
    axes = axes.flatten(order='F')
    
    channels = [str(x).zfill(2) for x in range(14, 19)]
    
    for i, channel in enumerate(channels):
        
        # MWI-RX183_DSB_Matlab.xlsx dataset
        axes[i].plot(mwi_dsb_data['frequency [GHz]'], mwi_dsb_data['ch'+channel+' sensitivity [dB]'], color='k', linewidth=0.9,
                     label='MWI-RX183_DSB_Matlab.xlsx')
    
        # MWI-RX183_Matlab.xslx
        axes[i].plot(mwi_data['frequency [GHz]'], mwi_data['ch'+channel+' sensitivity [dB]'], color='blue', alpha=0.5, linewidth=0.9,
                     label='MWI-RX183_Matlab.xlsx')

        # annotate channel name
        axes[i].annotate(text=freq_txt[i], xy=[197.5, -50], backgroundcolor="w")
        
        # set y ticks
        axes[i].set_yticks(np.arange(-100, 25, 25))
        
        # set ax limits
        axes[i].set_ylim([-110, 5])
        axes[i].set_xlim([175, 202])
        
        # add vertical lines
        axes[i].axvline(x=183.31, color='red', linestyle='--')  # mark line center
         
        for j in range(2):  # mark left/right channel frequency
            axes[i].axvline(x=ch_f_arr[i, j], color='gray', linestyle='--') 
        
        for j in range(4):  # mark each bandwidth edge
            axes[i].axvline(x=ch_f_bw_arr[i, j], color='gray', linestyle=':')
        
        # add shade for each channel
        axes[i].axvspan(xmin=ch_f_bw_arr[i, 0], xmax=ch_f_bw_arr[i, 1], ymin=-10e3, ymax=10e3, color='gray', alpha=0.2)
        axes[i].axvspan(xmin=ch_f_bw_arr[i, 2], xmax=ch_f_bw_arr[i, 3], ymin=-10e3, ymax=10e3, color='gray', alpha=0.2)

        # add grid
        axes[i].grid(zorder=2)
        
        # add legend
        if i == 4:
            axes[i].legend(bbox_to_anchor=(0, -1), loc='center left', frameon=False, ncol=3)
            
    axes[2].set_ylabel('Sensitivity [dB]')
    
    axes[-1].set_xlabel('Frequency [GHz]')
    
    fig.tight_layout()
        
    plt.savefig(path_fig + 'sensitivity_measurement.png', dpi=200)
    
    #%% find matching frequency array for all channels
    # UPDATE: not necessary. Frequencies for Pamtra are set identical to the measurements.
    
    #df_mwi_dsb = mwi_dsb_data['frequency [GHz]'].values[1:] - mwi_dsb_data['frequency [GHz]'].values[:-1]
    #df_mwi = mwi_data['frequency [GHz]'].values[1:] - mwi_data['frequency [GHz]'].values[:-1]

    #print(np.max(df_mwi_dsb))
    #ix = np.where(df_mwi_dsb==np.max(df_mwi_dsb))[0][0]
    #print(mwi_dsb_data['frequency [GHz]'].values[ix])
    #print(mwi_dsb_data['frequency [GHz]'].values[ix+1])
    
    #print(np.max(df_mwi))  # constant
    
    # min always constant 0.015
    #print(np.min(df_mwi_dsb))
    #print(np.min(df_mwi))

    # do the frequencies overlap?
    #mwi_dsb_data['frequency [GHz]'].values[ix:ix+10]
    #mwi_data['frequency [GHz]'].values[:10]
    
    # comment: df_mwi_dsb has jump in frequency between 183.257 GHz (index 529) and 183.367 GHz (index 530) (difference is 1.1!)
    # comment: df_mwi step in frequency is always 0.015
    # comment: the frequencies from both files do not overlap, the values are shiftet by 0.005 GHz 
    # comment: however, this can be corrected by interpolating the modelled brightness temperatures to the used frequencies
    # comment: a regular grid of modelled brightness temperatures is defined with step width 0.015
    
    #%% create frequency array 
    
    #matches most measurement points (except right wing from dsb file)
    #df = 0.015
    #f_min1 = 183.31-12+0.007
    #f_max1 = 183.31+12+0.007
    #freqs_pamtra1 = np.arange(f_min1, f_max1+df, df)
    
    # add frequencies for right wing of dsb file
    #f_min2 = 183.31+0.057
    #f_max2 = 191.302
    #freqs_pamtra2 = np.arange(f_min2, f_max2+df, df)
    
    #freqs_pamtra = np.append(freqs_pamtra1, freqs_pamtra2)
    
    # based on where the measurements where taken
    freqs_pamtra = mwi_dsb_data['frequency [GHz]'].values  # frequencies from dsb file
    freqs_pamtra = np.append(freqs_pamtra, mwi_data['frequency [GHz]'].values)  # frequencies from other file
    freqs_pamtra = np.append(freqs_pamtra, 2*183.31 - mwi_data['frequency [GHz]'].values)  # frequencies from other file mirrored at line center
    
    # add frequencies of channels to pamtra frequencies
    freqs_pamtra = np.append(freqs_pamtra, ch_f_arr.flatten())
    
    # add frequencies of edge of bandwidth for each channel
    freqs_pamtra = np.append(freqs_pamtra, ch_f_bw_arr.flatten())    
    
    # remove duplicates
    freqs_pamtra = np.unique(np.sort(freqs_pamtra))
    
    # write frequencies to file
    np.savetxt(path_data + 'frequencies.txt', freqs_pamtra)
    
    #%% compare defined frequency grid and frequency grid from measurement files
    fig = plt.figure()
    plt.plot(freqs_pamtra, [1]*len(freqs_pamtra), 'xk', label='pamtra frequencies', alpha=0.6, markeredgecolor=None)
    plt.plot(mwi_dsb_data['frequency [GHz]'], [1]*len(mwi_dsb_data['frequency [GHz]']), '.r', label='MWI-RX183_DSB_Matlab.xlsx', alpha=0.6, markeredgecolor=None)
    plt.plot(mwi_data['frequency [GHz]'], [1]*len(mwi_data['frequency [GHz]']), '.b', label='MWI-RX183_Matlab.xlsx', alpha=0.6, markeredgecolor=None)
    plt.axvline(x=183.31, color='gray')
    plt.legend()
    plt.grid()
    
    # comment: for left side, use the sensitivity from the corresponding mirrored right measurement
    
    #%% read data from pamtra simulation
    file = path_data + 'mwi_pamtra_tb.txt'  # here specify files for the 6 different profiles
    
    pam_data_df = pd.read_csv(file, delimiter=',')
    pam_data_df.rename(columns={'frequency_GHz': 'frequency [GHz]'}, inplace=True)  # for the join later

    profiles = np.sort(pam_data_df.columns.drop('frequency [GHz]'))  # list of the different atmospheres
    
    # put standard atmosphere to the end
    profiles = np.array(['arctic_winter', 'arctic_summer',
                         'central_europe_winter', 'central_europe_summer', 
                         'tropics_february', 'tropics_august',
                         'standard'])
    
    # format for boxplot
    pam_colors = {'central_europe_winter': '#008B00', 'central_europe_summer': '#51FF51', 
                    'arctic_winter': '#002375', 'arctic_summer': '#6594FF', 
                    'tropics_february': '#AE0000', 'tropics_august': '#FF5555',
                    'standard': '#000000'}
    
    # format for line plot
    pam_line_fmt = {'central_europe_winter': 'g:', 'central_europe_summer': 'g-', 
               'arctic_winter': 'b:', 'arctic_summer': 'b-', 
               'tropics_february': 'r:', 'tropics_august': 'r-',
               'standard': 'k-'}
    
    # format for point
    pam_point_fmt = {'central_europe_winter': dict(marker='*', fillstyle='none', markersize=7, markeredgecolor='g', linestyle = 'None'), 
                     'central_europe_summer': dict(marker='o', fillstyle='none', markersize=7, markeredgecolor='g', linestyle = 'None'), 
                     'arctic_winter': dict(marker='*', fillstyle='none', markersize=7, markeredgecolor='b', linestyle = 'None'), 
                     'arctic_summer': dict(marker='o', fillstyle='none', markersize=7, markeredgecolor='b', linestyle = 'None'), 
                     'tropics_february': dict(marker='*', fillstyle='none', markersize=7, markeredgecolor='r', linestyle = 'None'), 
                     'tropics_august': dict(marker='o', fillstyle='none', markersize=7, markeredgecolor='r', linestyle = 'None'),
                     'standard': dict(marker='o', fillstyle='none', markersize=7, markeredgecolor='k', linestyle = 'None')}
    
    # label for legend
    pam_label = {'central_europe_winter': 'Central Europe\n(Winter)','central_europe_summer': 'Central Europe\n(Summer)', 
               'arctic_winter': 'Arctic\n(Winter)', 'arctic_summer': 'Arctic\n(Summer)', 
               'tropics_february': 'Tropics\n(February)', 'tropics_august': 'Tropics\n(August)',
               'standard': 'standard atmosphere\nwith RH=0%'}
    
    # label for legend with specific times of radiosonde launch: This has to be changed by hand if other data is used!!!
    pam_label_detail = {'central_europe_winter': 'Essen\n(2020-02-02 12)','central_europe_summer': 'Essen\n(2020-08-01 00)', 
                        'arctic_winter': 'Ny-Alesund\n(2020-02-02 12)', 'arctic_summer': 'Ny-Alesund\n(2020-08-01 12)', 
                        'tropics_february': 'Singapore\n(2020-02-01 12)', 'tropics_august': 'Singapore\n(2020-08-01 12)',
                        'standard': 'standard atmosphere\nwith RH=0%'}
    
    #%% plot pamtra simulation
    fig = plt.figure(figsize=(9, 6))
    ax = fig.add_subplot(111)
    ax.set_title('PAMTRA simulation at 833 km nadir view (V-pol) and MWI 183.31 GHz channels\nfor different radiosonde profiles and standard atmosphere (RH=0%)')
    
    for profile in profiles:
        ax.plot(pam_data_df['frequency [GHz]'], pam_data_df[profile], pam_line_fmt[profile], label=pam_label_detail[profile])
    
    # add MWI channels
    for i, channel in enumerate(channels):
        
        # annotate channel name
        ax.annotate(text=freq_txt[i][4:6], xy=[ch_f_arr[i, 0]-0.4, 171], fontsize=7, bbox=dict(boxstyle='square', fc='white', ec='none', pad=0))
        ax.annotate(text=freq_txt[i][4:6], xy=[ch_f_arr[i, 1]-0.4, 171], fontsize=7, bbox=dict(boxstyle='square', fc='white', ec='none', pad=0))
        
        # add vertical lines
        ax.axvline(x=183.31, color='pink', linestyle='-', alpha=0.5)  # mark line center
        ax.axvline(x=ch_f_arr[i, 0], color='gray', linestyle='-', alpha=0.5)  # mark left channel frequency
        ax.axvline(x=ch_f_arr[i, 1], color='gray', linestyle='-', alpha=0.5)  # mark right channel frequency
        
    ax.legend(bbox_to_anchor=(1.05, 0.5), loc='center left', frameon=False)
    ax.grid(axis='y')
    
    ax.set_ylim([170, 290])
    ax.set_xlim([np.min(pam_data_df['frequency [GHz]']), np.max(pam_data_df['frequency [GHz]'])])
    
    ax.set_xlabel('Frequency [GHz]')
    ax.set_ylabel('Brightness temperature [K]')
    
    fig.tight_layout()
    
    plt.savefig(path_fig + 'pamtra_simulation.png', dpi=200)
    
    #%% convert sensitivity to linear unit and normalize
    # two measurements are normalized seperately
    
    # convert from dB to linear units and normalize (sum over columns is zero)
    # row: frequency, column: channel
    mwi_dsb_data_mat = mwi_dsb_data.values[:, 1:]  # get sensitivity in dB from pandas df
    mwi_dsb_data_mat = 10**(0.1 * mwi_dsb_data_mat)  # convert to linear unit
    mwi_dsb_data_mat = mwi_dsb_data_mat / mwi_dsb_data_mat.sum(axis=0)  # normalize columns to 1
    
    mwi_data_mat = mwi_data.values[:, 1:]  # get sensitivity in dB from pandas df
    mwi_data_mat = 10**(0.1 * mwi_data_mat)  # convert to linear unit
    mwi_data_mat = mwi_data_mat / mwi_data_mat.sum(axis=0)  # normalize columns to 1
    
    # add to data frames
    mwi_dsb_data_linear = pd.DataFrame()    
    mwi_dsb_data_linear['frequency [GHz]'] = mwi_dsb_data.values[:, 0]
    mwi_dsb_data_linear['ch14 sensitivity'] = mwi_dsb_data_mat[:, 0]
    mwi_dsb_data_linear['ch15 sensitivity'] = mwi_dsb_data_mat[:, 1]
    mwi_dsb_data_linear['ch16 sensitivity'] = mwi_dsb_data_mat[:, 2]
    mwi_dsb_data_linear['ch17 sensitivity'] = mwi_dsb_data_mat[:, 3]
    mwi_dsb_data_linear['ch18 sensitivity'] = mwi_dsb_data_mat[:, 4]
    
    mwi_data_linear = pd.DataFrame()    
    mwi_data_linear['frequency [GHz]'] = mwi_data.values[:, 0]
    mwi_data_linear['ch14 sensitivity'] = mwi_data_mat[:, 0]
    mwi_data_linear['ch15 sensitivity'] = mwi_data_mat[:, 1]
    mwi_data_linear['ch16 sensitivity'] = mwi_data_mat[:, 2]
    mwi_data_linear['ch17 sensitivity'] = mwi_data_mat[:, 3]
    mwi_data_linear['ch18 sensitivity'] = mwi_data_mat[:, 4]
    
    #%% New: Noise to perturb the spectral response functions (SRF)
    
    # get std of spectral response function of MWI-RX183_DSB_Matlab.xlsx
    for i, channel in enumerate(channels):
        
        f_max_l = ch_f_bw_arr[i, 1]
        f_min_l = ch_f_bw_arr[i, 0]
        f_max_r = ch_f_bw_arr[i, 3]
        f_min_r = ch_f_bw_arr[i, 2]
        
        srf_sd_bw = np.std(mwi_dsb_data_linear['ch'+channel+' sensitivity'][(mwi_dsb_data_linear['frequency [GHz]'] < f_max_l) &
                                                                           (mwi_dsb_data_linear['frequency [GHz]'] > f_min_l) |
                                                                           (mwi_dsb_data_linear['frequency [GHz]'] < f_max_r) &
                                                                           (mwi_dsb_data_linear['frequency [GHz]'] > f_min_r)])
        
        print('Standard dev. of SRF from channel {} at channel bandwidth: {}'.format(channel, srf_sd_bw))
        
        srf_sd_bw = np.std(mwi_dsb_data_linear['ch'+channel+' sensitivity'][~((mwi_dsb_data_linear['frequency [GHz]'] < f_max_l) &
                                                                           (mwi_dsb_data_linear['frequency [GHz]'] > f_min_l) |
                                                                           (mwi_dsb_data_linear['frequency [GHz]'] < f_max_r) &
                                                                           (mwi_dsb_data_linear['frequency [GHz]'] > f_min_r))])
        
        print('Standard dev. of SRF from channel {} apart from channel bandwidth: {}'.format(channel, srf_sd_bw))
        
        srf_sd_total = np.std(mwi_dsb_data_linear['ch'+channel+' sensitivity'])
        
        print('Standard dev. of SRF from channel {}: {}\n'.format(channel, srf_sd_total))
    
    # get std of spectral response function of MWI-RX183_Matlab.xlsx
    for i, channel in enumerate(channels):
        
        f_max_l = ch_f_bw_arr[i, 1]
        f_min_l = ch_f_bw_arr[i, 0]
        f_max_r = ch_f_bw_arr[i, 3]
        f_min_r = ch_f_bw_arr[i, 2]
        
        srf_sd_bw = np.std(mwi_data_linear['ch'+channel+' sensitivity'][(mwi_data_linear['frequency [GHz]'] < f_max_l) &
                                                                           (mwi_data_linear['frequency [GHz]'] > f_min_l) |
                                                                           (mwi_data_linear['frequency [GHz]'] < f_max_r) &
                                                                           (mwi_data_linear['frequency [GHz]'] > f_min_r)])
        
        print('Standard dev. of SRF from channel {} at channel bandwidth: {}'.format(channel, srf_sd_bw))
        
        srf_sd_total = np.std(mwi_data_linear['ch'+channel+' sensitivity'])
        
        print('Standard dev. of SRF from channel {}: {}'.format(channel, srf_sd_total))
    
    # result: std of SRF at bandwidth is between 0.0011 and 0.0022 for the MWI-RX183_DSB_Matlab.xlsx file
    # result: std of SRF apart from bandwidth is between 1e-6 and 1e-4 for the MWI-RX183_DSB_Matlab.xlsx file
    
    #%% create noise values
    
    """
    # noise std is based on considerations above
    srf_std_max = 5e-4  # add gaussian noise of 2 times the std of the measured signal
    srf_std_min = 5e-8
    n_noise = 1000
    n_freq = len(mwi_dsb_data_linear['frequency [GHz]'])
    np.random.seed(0)
    
    noise_max = np.random.normal(loc=0, scale=srf_std_max, size=(n_freq, n_noise))
    noise_min = np.random.normal(loc=0, scale=srf_std_min, size=(n_freq, n_noise))
    
    # add 100 noise realizations to each of the measurements and shiw result as boxplot
    # only add noise at bandwith center for each channel
    srf_plus_noise= np.full(shape=(n_freq, n_noise, len(channels)), fill_value=np.nan)
    
    for i, channel in enumerate(channels):
        
        # create mask
        f_max_l = ch_f_bw_arr[i, 1]-0.2
        f_min_l = ch_f_bw_arr[i, 0]+0.2
        f_max_r = ch_f_bw_arr[i, 3]-0.2
        f_min_r = ch_f_bw_arr[i, 2]+0.2
        mask = ((mwi_dsb_data_linear['frequency [GHz]'] < f_max_l) & (mwi_dsb_data_linear['frequency [GHz]'] > f_min_l) | \
               (mwi_dsb_data_linear['frequency [GHz]'] < f_max_r) & (mwi_dsb_data_linear['frequency [GHz]'] > f_min_r))
        
        noise = noise_max.copy()
        noise[~mask, :] = noise_min[~mask, :]  # different noise apart from 
        
        srf_plus_noise[:, :, i] = noise + np.array(mwi_dsb_data_linear['ch'+channel+' sensitivity'])[:, np.newaxis]
    
        # normalize
        # important: avoid negative values by shifting whole array by the lowest value
        # change in absolute value does not affect the normalized values
        noise_lowest = np.abs(np.min(srf_plus_noise[:, :, i]))*1.1  # a bit higher than overall lowest value for simplification
        srf_plus_noise[:, :, i] = (srf_plus_noise[:, :, i]+noise_lowest)/(srf_plus_noise[:, :, i]+noise_lowest).sum(axis=0)
    """
    
    # in logarithmic plot this amplifies the importance of non-center frequencies os a channel by a few orders
    # instead add noise by multiplying by a values around 1 and normalize

    #%% create noise values
    # noise std is based on considerations above
    srf_std = 0.1  # add gaussian noise of 2 times the std of the measured signal
    n_noise = 1000
    n_freq = len(mwi_dsb_data_linear['frequency [GHz]'])
    np.random.seed(0)
    
    noise = np.random.normal(loc=1, scale=srf_std, size=(n_freq, n_noise))
    
    # add realizations to each of the measurements and shiw result as boxplot
    srf_plus_noise= np.full(shape=(n_freq, n_noise, len(channels)), fill_value=np.nan)
    
    for i, channel in enumerate(channels):

        srf_plus_noise[:, :, i] = noise * np.array(mwi_dsb_data_linear['ch'+channel+' sensitivity'])[:, np.newaxis]
    
        # normalize
        srf_plus_noise[:, :, i] = srf_plus_noise[:, :, i]/srf_plus_noise[:, :, i].sum(axis=0)

    #%% plot normalized sensitivity measurement (same as above but with linear dataframe)
    fig, axes = plt.subplots(5, 1, sharex=True, figsize=(9, 6))
    fig.suptitle('Normalized linear spectral response function of MWI channels 14 to 18 with overlying perturbation')
    axes = axes.flatten(order='F')
    
    channels = [str(x).zfill(2) for x in range(14, 19)]
    
    for i, channel in enumerate(channels):
        
        # MWI-RX183_DSB_Matlab.xlsx dataset
        #axes[i].plot(mwi_dsb_data_linear['frequency [GHz]'], 10*np.log10(mwi_dsb_data_linear['ch'+channel+' sensitivity']), color='k', linewidth=0.9)
        axes[i].plot(mwi_dsb_data_linear['frequency [GHz]'], mwi_dsb_data_linear['ch'+channel+' sensitivity'], color='k', linewidth=0.9,
                     label='MWI-RX183_DSB_Matlab.xlsx')

        # MWI-RX183_DSB_Matlab.xlsx dataset perturbed
        #axes[i].plot(mwi_dsb_data_linear['frequency [GHz]'], 10*np.log10(srf_plus_noise[:, ::50, i]), color='green', linewidth=0.5, alpha=0.5)
        axes[i].plot(mwi_dsb_data_linear['frequency [GHz]'], srf_plus_noise[:, 0, i], color='green', linewidth=1, alpha=0.5,
                     label='MWI-RX183_DSB_Matlab.xlsx\n(perturbed)')
        
        # MWI-RX183_Matlab.xslx
        #axes[i].plot(mwi_data_linear['frequency [GHz]'], 10*np.log10(mwi_data_linear['ch'+channel+' sensitivity']), color='blue', alpha=0.5, linewidth=0.9)
        axes[i].plot(mwi_data_linear['frequency [GHz]'], mwi_data_linear['ch'+channel+' sensitivity'], color='blue', alpha=0.5, linewidth=0.9,
                     label='MWI-RX183_Matlab.xlsx')

        # annotate channel name
        axes[i].annotate(text=freq_txt[i], xy=[197.5, 0.0075], backgroundcolor="w")
        
        # set y ticks
        axes[i].set_yticks(np.arange(0, 0.015, 0.005))
        
        # set ax limits
        axes[i].set_ylim([0, 0.015])
        
        # set ax limits
        axes[i].set_xlim([175, 202])
        
        # add vertical lines
        axes[i].axvline(x=183.31, color='red', linestyle='--')  # mark line center
         
        for j in range(2):  # mark left/right channel frequency
            axes[i].axvline(x=ch_f_arr[i, j], color='gray', linestyle='--') 
        
        for j in range(4):  # mark each bandwidth edge
            axes[i].axvline(x=ch_f_bw_arr[i, j], color='gray', linestyle=':')
        
        # add shade for each channel
        axes[i].axvspan(xmin=ch_f_bw_arr[i, 0], xmax=ch_f_bw_arr[i, 1], ymin=-10e3, ymax=10e3, color='gray', alpha=0.2)
        axes[i].axvspan(xmin=ch_f_bw_arr[i, 2], xmax=ch_f_bw_arr[i, 3], ymin=-10e3, ymax=10e3, color='gray', alpha=0.2)

        # add grid
        axes[i].grid(zorder=2)
        
        # add legend
        if i == 4:
            axes[i].legend(bbox_to_anchor=(0, -1), loc='center left', frameon=False, ncol=3)
    
    axes[2].set_ylabel('Sensitivity [1]')
    axes[-1].set_xlabel('Frequency [GHz]')
    
    fig.tight_layout()
        
    plt.savefig(path_fig + 'sensitivity_measurement_normalized_linear.png', dpi=300)

    #%% plot normalized sensitivity measurement (same as above but with linear dataframe)
    fig, axes = plt.subplots(5, 1, sharex=True, figsize=(9, 6))
    fig.suptitle('Normalized spectral response function of MWI channels 14 to 18 with overlying perturbation')
    axes = axes.flatten(order='F')
    
    channels = [str(x).zfill(2) for x in range(14, 19)]
    
    for i, channel in enumerate(channels):
        
        # MWI-RX183_DSB_Matlab.xlsx dataset
        axes[i].plot(mwi_dsb_data_linear['frequency [GHz]'], 10*np.log10(mwi_dsb_data_linear['ch'+channel+' sensitivity']), color='k', linewidth=0.9,
                     label='MWI-RX183_DSB_Matlab.xlsx')

        # MWI-RX183_DSB_Matlab.xlsx dataset perturbed
        axes[i].plot(mwi_dsb_data_linear['frequency [GHz]'], 10*np.log10(srf_plus_noise[:, 0, i]), color='green', linewidth=1, alpha=0.5,
                     label='MWI-RX183_DSB_Matlab.xlsx\n(perturbed)')

        # MWI-RX183_Matlab.xslx
        axes[i].plot(mwi_data_linear['frequency [GHz]'], 10*np.log10(mwi_data_linear['ch'+channel+' sensitivity']), color='blue', alpha=0.5, linewidth=0.9,
                     label='MWI-RX183_Matlab.xlsx')

        # annotate channel name
        axes[i].annotate(text=freq_txt[i], xy=[197.5, -75], backgroundcolor="w")
        
        # set y ticks
        axes[i].set_yticks(np.arange(-150, 25, 25))
        
        # set ax limits
        axes[i].set_ylim([-140, -15])
        axes[i].set_xlim([175, 202])
        
        # add vertical lines
        axes[i].axvline(x=183.31, color='red', linestyle='--')  # mark line center
         
        for j in range(2):  # mark left/right channel frequency
            axes[i].axvline(x=ch_f_arr[i, j], color='gray', linestyle='--') 
        
        for j in range(4):  # mark each bandwidth edge
            axes[i].axvline(x=ch_f_bw_arr[i, j], color='gray', linestyle=':')
        
        # add shade for each channel
        axes[i].axvspan(xmin=ch_f_bw_arr[i, 0], xmax=ch_f_bw_arr[i, 1], ymin=-10e3, ymax=10e3, color='gray', alpha=0.2)
        axes[i].axvspan(xmin=ch_f_bw_arr[i, 2], xmax=ch_f_bw_arr[i, 3], ymin=-10e3, ymax=10e3, color='gray', alpha=0.2)

        # add grid
        axes[i].grid(zorder=2)
        
        # add legend
        if i == 4:
            axes[i].legend(bbox_to_anchor=(0, -1), loc='center left', frameon=False, ncol=3)
    
    axes[2].set_ylabel('Sensitivity [dB]')
    axes[-1].set_xlabel('Frequency [GHz]')
    
    fig.tight_layout()
    
    plt.savefig(path_fig + 'sensitivity_measurement_normalized_dB.png', dpi=600)

    #%% RESULT 1 (MWI-RX183_DSB_Matlab.xlsx data set - problem for Ch 14)
    # calculate measured brightness temperature
    # run pamtra again: include all DSB frequencies. Problem then for channel 14 where some parts are missing
    # don't forget to include the representative frequencies for each channel to pamtra to compare with the 
    # estimate based on the sensitivity at multiple frequencies
    
    # join brightness temperature to the linear sensitivity dataframe
    # hack: convert frequency to join - float to int and then back int to float
    N = 10000
    pam_data_df['frequency [GHz]'] = np.round(pam_data_df['frequency [GHz]']*N).astype(int) 
    mwi_dsb_data_linear['frequency [GHz]'] = np.round(mwi_dsb_data_linear['frequency [GHz]']*N).astype(int) 
    sens_mwi_dsb = pd.merge(pam_data_df, mwi_dsb_data_linear, on='frequency [GHz]')
    sens_mwi_dsb['frequency [GHz]'] = sens_mwi_dsb['frequency [GHz]'] / N
    pam_data_df['frequency [GHz]'] = pam_data_df['frequency [GHz]'] / N
    mwi_dsb_data_linear['frequency [GHz]'] = mwi_dsb_data_linear['frequency [GHz]'] / N

    # create result for each of the modelled profiles
    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_subplot(111)
    ax.set_title('MWI virtual measurement minus PAMTRA simulation at channel frequencies\nSensitivity data: MWI-RX183_DSB_Matlab.xlsx')
    
    for profile in profiles:
    
        # calculate measured brightness temperature as dot product between 
        # simulated TB and sensitivity for the different channels
        ch_14_tb_meas = np.dot(sens_mwi_dsb[profile].values, sens_mwi_dsb['ch14 sensitivity'].values)
        ch_15_tb_meas = np.dot(sens_mwi_dsb[profile].values, sens_mwi_dsb['ch15 sensitivity'].values)
        ch_16_tb_meas = np.dot(sens_mwi_dsb[profile].values, sens_mwi_dsb['ch16 sensitivity'].values)
        ch_17_tb_meas = np.dot(sens_mwi_dsb[profile].values, sens_mwi_dsb['ch17 sensitivity'].values)
        ch_18_tb_meas = np.dot(sens_mwi_dsb[profile].values, sens_mwi_dsb['ch18 sensitivity'].values)
    
        # compare with actual modelled TB at the frequency belonging to the channel
        # get simulated brightness temperature at the channel frequency
        # calculate mean of upper and lower frequency
        ch_14_tb_pam = pam_data_df.loc[pam_data_df['frequency [GHz]'].isin(ch_14_f)][profile].mean()
        ch_15_tb_pam = pam_data_df.loc[pam_data_df['frequency [GHz]'].isin(ch_15_f)][profile].mean()
        ch_16_tb_pam = pam_data_df.loc[pam_data_df['frequency [GHz]'].isin(ch_16_f)][profile].mean()
        ch_17_tb_pam = pam_data_df.loc[pam_data_df['frequency [GHz]'].isin(ch_17_f)][profile].mean()
        ch_18_tb_pam = pam_data_df.loc[pam_data_df['frequency [GHz]'].isin(ch_18_f)][profile].mean()
    
        # then compare values graphically
        ax.plot(14, ch_14_tb_meas - ch_14_tb_pam, **pam_point_fmt[profile], label=pam_label_detail[profile])
        ax.plot(15, ch_15_tb_meas - ch_15_tb_pam, **pam_point_fmt[profile])
        ax.plot(16, ch_16_tb_meas - ch_16_tb_pam, **pam_point_fmt[profile])
        ax.plot(17, ch_17_tb_meas - ch_17_tb_pam, **pam_point_fmt[profile])
        ax.plot(18, ch_18_tb_meas - ch_18_tb_pam, **pam_point_fmt[profile])
        
    ax.set_ylabel('$\Delta TB = TB_{MWI} - TB_{PAMTRA}$ [K]')
    
    # axis limits
    ax.set_ylim([-0.6, 0.2])
    ax.set_xlim([13.5, 18.5])

    # axis tick settings
    ax.set_xticks(np.arange(14, 19), minor=True)
    ax.set_xticks(np.arange(13.5, 19.5), minor=False)
    ax.set_xticklabels(freq_txt, minor=True)
    ax.set_xticklabels('', minor=False)
    ax.xaxis.grid(True, which='major')
    ax.yaxis.grid(True)
    ax.tick_params('x', length=0, width=0, which='minor')
    
    # add 0-line
    ax.axhline(y=0, color='k', linestyle='--', linewidth=.75)
    
    # legend
    ax.legend(bbox_to_anchor=(1.05, 0.5), loc='center left', frameon=False)
    
    # layout
    fig.tight_layout()
    
    plt.savefig(path_fig + 'result_1_MWI-RX183_DSB_Matlab.png', dpi=200)
    
    #%% RESULT 1B (MWI-RX183_DSB_Matlab.xlsx data set - problem for Ch 14)
    # extended with noise
    
    # calculate measured brightness temperature
    # run pamtra again: include all DSB frequencies. Problem then for channel 14 where some parts are missing
    # don't forget to include the representative frequencies for each channel to pamtra to compare with the 
    # estimate based on the sensitivity at multiple frequencies
    
    # join brightness temperature to the linear sensitivity dataframe
    # hack: convert frequency to join - float to int and then back int to float
    N = 10000
    pam_data_df['frequency [GHz]'] = np.round(pam_data_df['frequency [GHz]']*N).astype(int) 
    mwi_dsb_data_linear['frequency [GHz]'] = np.round(mwi_dsb_data_linear['frequency [GHz]']*N).astype(int) 
    sens_mwi_dsb = pd.merge(pam_data_df, mwi_dsb_data_linear, on='frequency [GHz]')
    sens_mwi_dsb['frequency [GHz]'] = sens_mwi_dsb['frequency [GHz]'] / N
    pam_data_df['frequency [GHz]'] = pam_data_df['frequency [GHz]'] / N
    mwi_dsb_data_linear['frequency [GHz]'] = mwi_dsb_data_linear['frequency [GHz]'] / N

    #srf_plus_noise[:, :, -1] # shape=(n_freq, n_noise, len(channels))

    # create result for each of the modelled profiles
    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_subplot(111)
    ax.set_title('MWI virtual measurement minus PAMTRA simulation at channel frequencies\nSensitivity data: 1000 perturbed measurements (MWI-RX183_DSB_Matlab.xlsx)')
    
    for i, profile in enumerate(profiles):
                    
        # calculate measured brightness temperature as dot product between 
        # simulated TB and sensitivity for the different channels
        ch_14_tb_meas = np.dot(sens_mwi_dsb[profile].values, srf_plus_noise[:, :, 0])
        ch_15_tb_meas = np.dot(sens_mwi_dsb[profile].values, srf_plus_noise[:, :, 1])
        ch_16_tb_meas = np.dot(sens_mwi_dsb[profile].values, srf_plus_noise[:, :, 2])
        ch_17_tb_meas = np.dot(sens_mwi_dsb[profile].values, srf_plus_noise[:, :, 3])
        ch_18_tb_meas = np.dot(sens_mwi_dsb[profile].values, srf_plus_noise[:, :, 4])
    
        # compare with actual modelled TB at the frequency belonging to the channel
        # get simulated brightness temperature at the channel frequency
        # calculate mean of upper and lower frequency
        ch_14_tb_pam = pam_data_df.loc[pam_data_df['frequency [GHz]'].isin(ch_14_f)][profile].mean()
        ch_15_tb_pam = pam_data_df.loc[pam_data_df['frequency [GHz]'].isin(ch_15_f)][profile].mean()
        ch_16_tb_pam = pam_data_df.loc[pam_data_df['frequency [GHz]'].isin(ch_16_f)][profile].mean()
        ch_17_tb_pam = pam_data_df.loc[pam_data_df['frequency [GHz]'].isin(ch_17_f)][profile].mean()
        ch_18_tb_pam = pam_data_df.loc[pam_data_df['frequency [GHz]'].isin(ch_18_f)][profile].mean()
        
        # then compare values graphically
        dx = np.linspace(-0.3, 0.3, 7)
        
        marker_style = dict(fillstyle='none', alpha=0.2)
        
        boxprops = dict(facecolor=pam_colors[profile], color=pam_colors[profile])
        flierprops = dict(markeredgecolor='k', markersize=2)
        medianprops = dict(color='k')
        
        ax.boxplot(x=ch_14_tb_meas - ch_14_tb_pam, notch=True, sym="d", positions=[14+dx[i]], widths=0.075, 
                   boxprops=boxprops, flierprops=flierprops, medianprops=medianprops, patch_artist=True)
        ax.boxplot(x=ch_15_tb_meas - ch_15_tb_pam, notch=True, sym="d", positions=[15+dx[i]], widths=0.075, 
                   boxprops=boxprops, flierprops=flierprops, medianprops=medianprops, patch_artist=True)
        ax.boxplot(x=ch_16_tb_meas - ch_16_tb_pam, notch=True, sym="d", positions=[16+dx[i]], widths=0.075, 
                   boxprops=boxprops, flierprops=flierprops, medianprops=medianprops, patch_artist=True)
        ax.boxplot(x=ch_17_tb_meas - ch_17_tb_pam, notch=True, sym="d", positions=[17+dx[i]], widths=0.075, 
                   boxprops=boxprops, flierprops=flierprops, medianprops=medianprops, patch_artist=True)
        ax.boxplot(x=ch_18_tb_meas - ch_18_tb_pam, notch=True, sym="d", positions=[18+dx[i]], widths=0.075, 
                   boxprops=boxprops, flierprops=flierprops, medianprops=medianprops, patch_artist=True)     
        
    ax.set_ylabel('$\Delta TB = TB_{MWI} - TB_{PAMTRA}$ [K]')
    
    # axis limits
    ax.set_ylim([-0.6, 0.2])
    ax.set_xlim([13.5, 18.5])

    ax.set_xticks(np.arange(14, 19), minor=True)
    ax.set_xticks(np.arange(13.5, 19.5), minor=False)
    ax.set_xticklabels(freq_txt, minor=True)
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
    
    plt.savefig(path_fig + 'result_1B_MWI-RX183_DSB_Matlab.png', dpi=400)
    
    #%% RESULT 2 (sensitivity from MWI-RX183_Matlab.xlsx - only sensitivity above 183.31)
    # calculate measured brightness temperature
    # join brightness temperature to the linear sensitivity dataframe
    # hack: convert frequency to join - float to int and then back int to float
    N = 10000
    pam_data_df['frequency [GHz]'] = np.round(pam_data_df['frequency [GHz]']*N).astype(int) 
    mwi_data_linear['frequency [GHz]'] = np.round(mwi_data_linear['frequency [GHz]']*N).astype(int) 
    sens_mwi = pd.merge(pam_data_df, mwi_data_linear, on='frequency [GHz]')
    sens_mwi['frequency [GHz]'] = sens_mwi['frequency [GHz]'] / N
    pam_data_df['frequency [GHz]'] = pam_data_df['frequency [GHz]'] / N
    mwi_data_linear['frequency [GHz]'] = mwi_data_linear['frequency [GHz]'] / N
    
    # create result for each of the modelled profiles
    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_subplot(111)
    ax.set_title('MWI virtual measurement minus PAMTRA simulation at channel frequencies\nSensitivity data: MWI-RX183_Matlab.xlsx (only > 183.31 GHz)')

    
    for profile in profiles:

        # calculate measured brightness temperature as dot product between 
        # simulated TB and sensitivity for the different channels
        ch_14_tb_meas = np.dot(sens_mwi[profile].values, sens_mwi['ch14 sensitivity'].values)
        ch_15_tb_meas = np.dot(sens_mwi[profile].values, sens_mwi['ch15 sensitivity'].values)
        ch_16_tb_meas = np.dot(sens_mwi[profile].values, sens_mwi['ch16 sensitivity'].values)
        ch_17_tb_meas = np.dot(sens_mwi[profile].values, sens_mwi['ch17 sensitivity'].values)
        ch_18_tb_meas = np.dot(sens_mwi[profile].values, sens_mwi['ch18 sensitivity'].values)
    
        # compare with actual modelled TB at the frequency belonging to the channel
        # get simulated brightness temperature at the channel frequency, here only right value!
        ch_14_tb_pam = pam_data_df.loc[pam_data_df['frequency [GHz]'].isin(ch_14_f)][profile].values[1]
        ch_15_tb_pam = pam_data_df.loc[pam_data_df['frequency [GHz]'].isin(ch_15_f)][profile].values[1]
        ch_16_tb_pam = pam_data_df.loc[pam_data_df['frequency [GHz]'].isin(ch_16_f)][profile].values[1]
        ch_17_tb_pam = pam_data_df.loc[pam_data_df['frequency [GHz]'].isin(ch_17_f)][profile].values[1]
        ch_18_tb_pam = pam_data_df.loc[pam_data_df['frequency [GHz]'].isin(ch_18_f)][profile].values[1]
        
        ax.plot(14, ch_14_tb_meas - ch_14_tb_pam, **pam_point_fmt[profile], label=pam_label_detail[profile])
        ax.plot(15, ch_15_tb_meas - ch_15_tb_pam, **pam_point_fmt[profile])
        ax.plot(16, ch_16_tb_meas - ch_16_tb_pam, **pam_point_fmt[profile])
        ax.plot(17, ch_17_tb_meas - ch_17_tb_pam, **pam_point_fmt[profile])
        ax.plot(18, ch_18_tb_meas - ch_18_tb_pam, **pam_point_fmt[profile])
    
    ax.set_ylabel('$\Delta TB = TB_{MWI} - TB_{PAMTRA}$ [K]')
    
    # axis limits
    ax.set_ylim([-0.5, 0.2])
    ax.set_xlim([13.5, 18.5])

    # axis tick settings
    ax.set_xticks(np.arange(14, 19), minor=True)
    ax.set_xticks(np.arange(13.5, 19.5), minor=False)
    ax.set_xticklabels(freq_txt, minor=True)
    ax.set_xticklabels('', minor=False)
    ax.xaxis.grid(True, which='major')
    ax.yaxis.grid(True)
    ax.tick_params('x', length=0, width=0, which='minor')
    
    # add 0-line
    ax.axhline(y=0, color='k', linestyle='--', linewidth=.75)
    
    # legend
    ax.legend(bbox_to_anchor=(1.05, 0.5), loc='center left', frameon=False)
    
    # layout
    fig.tight_layout()
    
    plt.savefig(path_fig + 'result_2_MWI-RX183_Matlab_above183GHz.png', dpi=200)

    #%% RESULT 3 (sensitivity from MWI-RX183_Matlab.xlsx - measured sensitivity above 183.31 mirrored to the left - upper and lower frequency)
    
    # create dataset with sensitivity measurement mirrored ad 183.31 GHz
    mwi_data_linear_extend = pd.DataFrame() 
    mwi_data_linear_extend['frequency [GHz]'] = np.append(mwi_data_linear['frequency [GHz]'], 2*183.31 - mwi_data_linear['frequency [GHz]'])
    mwi_data_linear_extend['ch14 sensitivity'] = np.append(mwi_data_linear['ch14 sensitivity'], mwi_data_linear['ch14 sensitivity'])
    mwi_data_linear_extend['ch15 sensitivity'] = np.append(mwi_data_linear['ch15 sensitivity'], mwi_data_linear['ch15 sensitivity'])
    mwi_data_linear_extend['ch16 sensitivity'] = np.append(mwi_data_linear['ch16 sensitivity'], mwi_data_linear['ch16 sensitivity'])
    mwi_data_linear_extend['ch17 sensitivity'] = np.append(mwi_data_linear['ch17 sensitivity'], mwi_data_linear['ch17 sensitivity'])
    mwi_data_linear_extend['ch18 sensitivity'] = np.append(mwi_data_linear['ch18 sensitivity'], mwi_data_linear['ch18 sensitivity'])
    
    # normalize linear sensitivity now for the combined dataset
    mwi_data_linear_extend.iloc[:, 1:] = mwi_data_linear_extend.iloc[:, 1:]/mwi_data_linear_extend.iloc[:, 1:].sum(axis=0)
    
    # calculate measured brightness temperature
    # join brightness temperature to the linear sensitivity dataframe
    # hack: convert frequency to join - float to int and then back int to float
    N = 10000
    pam_data_df['frequency [GHz]'] = np.round(pam_data_df['frequency [GHz]']*N).astype(int) 
    mwi_data_linear_extend['frequency [GHz]'] = np.round(mwi_data_linear_extend['frequency [GHz]']*N).astype(int) 
    sens_mwi_extend = pd.merge(pam_data_df, mwi_data_linear_extend, on='frequency [GHz]')
    sens_mwi_extend['frequency [GHz]'] = sens_mwi_extend['frequency [GHz]'] / N
    pam_data_df['frequency [GHz]'] = pam_data_df['frequency [GHz]'] / N
    mwi_data_linear_extend['frequency [GHz]'] = mwi_data_linear_extend['frequency [GHz]'] / N

    # create result for each of the modelled profiles
    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_subplot(111)
    ax.set_title('MWI virtual measurement minus PAMTRA simulation at channel frequencies\nSensitivity data: MWI-RX183_Matlab.xlsx (mirrored at 183.31 GHz)')
    
    for profile in profiles:

        # calculate measured brightness temperature as dot product between 
        # simulated TB and sensitivity for the different channels
        ch_14_tb_meas = np.dot(sens_mwi_extend[profile].values, sens_mwi_extend['ch14 sensitivity'].values)
        ch_15_tb_meas = np.dot(sens_mwi_extend[profile].values, sens_mwi_extend['ch15 sensitivity'].values)
        ch_16_tb_meas = np.dot(sens_mwi_extend[profile].values, sens_mwi_extend['ch16 sensitivity'].values)
        ch_17_tb_meas = np.dot(sens_mwi_extend[profile].values, sens_mwi_extend['ch17 sensitivity'].values)
        ch_18_tb_meas = np.dot(sens_mwi_extend[profile].values, sens_mwi_extend['ch18 sensitivity'].values)
    
        # compare with actual modelled TB at the frequency belonging to the channel
        # get simulated brightness temperature at the channel frequency
        ch_14_tb_pam = pam_data_df.loc[pam_data_df['frequency [GHz]'].isin(ch_14_f)][profile].mean()
        ch_15_tb_pam = pam_data_df.loc[pam_data_df['frequency [GHz]'].isin(ch_15_f)][profile].mean()
        ch_16_tb_pam = pam_data_df.loc[pam_data_df['frequency [GHz]'].isin(ch_16_f)][profile].mean()
        ch_17_tb_pam = pam_data_df.loc[pam_data_df['frequency [GHz]'].isin(ch_17_f)][profile].mean()
        ch_18_tb_pam = pam_data_df.loc[pam_data_df['frequency [GHz]'].isin(ch_18_f)][profile].mean()

        ax.plot(14, ch_14_tb_meas - ch_14_tb_pam, **pam_point_fmt[profile], label=pam_label_detail[profile])
        ax.plot(15, ch_15_tb_meas - ch_15_tb_pam, **pam_point_fmt[profile])
        ax.plot(16, ch_16_tb_meas - ch_16_tb_pam, **pam_point_fmt[profile])
        ax.plot(17, ch_17_tb_meas - ch_17_tb_pam, **pam_point_fmt[profile])
        ax.plot(18, ch_18_tb_meas - ch_18_tb_pam, **pam_point_fmt[profile])
    
    ax.set_ylabel('$\Delta TB = TB_{MWI} - TB_{PAMTRA}$ [K]')
    
    # axis limits
    ax.set_ylim([-0.5, 0.2])
    ax.set_xlim([13.5, 18.5])

    # axis tick settings
    ax.set_xticks(np.arange(14, 19), minor=True)
    ax.set_xticks(np.arange(13.5, 19.5), minor=False)
    ax.set_xticklabels(freq_txt, minor=True)
    ax.set_xticklabels('', minor=False)
    ax.xaxis.grid(True, which='major')
    ax.yaxis.grid(True)
    ax.tick_params('x', length=0, width=0, which='minor')
    
    # add 0-line
    ax.axhline(y=0, color='k', linestyle='--', linewidth=.75)
    
    # legend
    ax.legend(bbox_to_anchor=(1.05, 0.5), loc='center left', frameon=False)
    
    # layout
    fig.tight_layout()
    
    plt.savefig(path_fig + 'result_3_MWI-RX183_Matlab.png', dpi=200)
    
    #%% RESULT 4 (MWI-RX183_DSB_Matlab.xlsx data set - problem for Ch 14)
    # here for the Pamtra simulation the four frequencies at the edge of the bandwidth
    # for each frequency is averaged, instead of the two central frequencies
    
    # calculate virtual measurement of MWI
    # join brightness temperature to the linear sensitivity dataframe
    # hack: convert frequency to join - float to int and then back int to float
    N = 10000
    pam_data_df['frequency [GHz]'] = np.round(pam_data_df['frequency [GHz]']*N).astype(int) 
    mwi_dsb_data_linear['frequency [GHz]'] = np.round(mwi_dsb_data_linear['frequency [GHz]']*N).astype(int) 
    sens_mwi_dsb = pd.merge(pam_data_df, mwi_dsb_data_linear, on='frequency [GHz]')
    sens_mwi_dsb['frequency [GHz]'] = sens_mwi_dsb['frequency [GHz]'] / N
    pam_data_df['frequency [GHz]'] = pam_data_df['frequency [GHz]'] / N
    mwi_dsb_data_linear['frequency [GHz]'] = mwi_dsb_data_linear['frequency [GHz]'] / N

    # create result for each of the modelled profiles
    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_subplot(111)
    ax.set_title('MWI virtual measurement minus PAMTRA simulation at channel bandwith edges\nSensitivity data: MWI-RX183_DSB_Matlab.xlsx')
    
    for i, profile in enumerate(profiles):
    
        # calculate measured brightness temperature as dot product between 
        # simulated TB and sensitivity for the different channels
        ch_14_tb_meas = np.dot(sens_mwi_dsb[profile].values, sens_mwi_dsb['ch14 sensitivity'].values)
        ch_15_tb_meas = np.dot(sens_mwi_dsb[profile].values, sens_mwi_dsb['ch15 sensitivity'].values)
        ch_16_tb_meas = np.dot(sens_mwi_dsb[profile].values, sens_mwi_dsb['ch16 sensitivity'].values)
        ch_17_tb_meas = np.dot(sens_mwi_dsb[profile].values, sens_mwi_dsb['ch17 sensitivity'].values)
        ch_18_tb_meas = np.dot(sens_mwi_dsb[profile].values, sens_mwi_dsb['ch18 sensitivity'].values)
    
        # compare with actual modelled TB at the frequency belonging to the channel
        # get simulated brightness temperature at the channel frequency edges (bandwidth)
        # calculate mean of the four edge frequencies
        ch_14_tb_pam = pam_data_df.loc[pam_data_df['frequency [GHz]'].isin(ch_14_f_bw)][profile].mean()
        ch_15_tb_pam = pam_data_df.loc[pam_data_df['frequency [GHz]'].isin(ch_15_f_bw)][profile].mean()
        ch_16_tb_pam = pam_data_df.loc[pam_data_df['frequency [GHz]'].isin(ch_16_f_bw)][profile].mean()
        ch_17_tb_pam = pam_data_df.loc[pam_data_df['frequency [GHz]'].isin(ch_17_f_bw)][profile].mean()
        ch_18_tb_pam = pam_data_df.loc[pam_data_df['frequency [GHz]'].isin(ch_18_f_bw)][profile].mean()
    
        # then compare values graphically
        ax.plot(14, ch_14_tb_meas - ch_14_tb_pam, label=pam_label_detail[profile], **pam_point_fmt[profile])
        ax.plot(15, ch_15_tb_meas - ch_15_tb_pam, **pam_point_fmt[profile])
        ax.plot(16, ch_16_tb_meas - ch_16_tb_pam, **pam_point_fmt[profile])
        ax.plot(17, ch_17_tb_meas - ch_17_tb_pam, **pam_point_fmt[profile])
        ax.plot(18, ch_18_tb_meas - ch_18_tb_pam, **pam_point_fmt[profile])
        
    ax.set_ylabel('$\Delta TB = TB_{MWI} - TB_{PAMTRA}$ [K]')
    
    # axis labels
    ax.set_ylim([-0.1, 0.8])
    ax.set_xlim([13.5, 18.5])

    # axis tick settings
    ax.set_xticks(np.arange(14, 19), minor=True)
    ax.set_xticks(np.arange(13.5, 19.5), minor=False)
    ax.set_xticklabels(freq_txt, minor=True)
    ax.set_xticklabels('', minor=False)
    ax.xaxis.grid(True, which='major')
    ax.yaxis.grid(True)
    ax.tick_params('x', length=0, width=0, which='minor')
    
    # add 0-line
    ax.axhline(y=0, color='k', linestyle='--', linewidth=.75)
    
    # legend
    ax.legend(bbox_to_anchor=(1.05, 0.5), loc='center left', frameon=False)
    
    # layout
    fig.tight_layout()
    
    plt.savefig(path_fig + 'result_4_MWI-RX183_DSB_Matlab.png', dpi=200)

    #%% RESULT 4B (MWI-RX183_DSB_Matlab.xlsx data set - problem for Ch 14)
    # here for the Pamtra simulation the four frequencies at the edge of the bandwidth
    # for each frequency is averaged, instead of the two central frequencies
    
    # extended with noise
    
    # calculate measured brightness temperature
    # run pamtra again: include all DSB frequencies. Problem then for channel 14 where some parts are missing
    # don't forget to include the representative frequencies for each channel to pamtra to compare with the 
    # estimate based on the sensitivity at multiple frequencies
    
    # join brightness temperature to the linear sensitivity dataframe
    # hack: convert frequency to join - float to int and then back int to float
    N = 10000
    pam_data_df['frequency [GHz]'] = np.round(pam_data_df['frequency [GHz]']*N).astype(int) 
    mwi_dsb_data_linear['frequency [GHz]'] = np.round(mwi_dsb_data_linear['frequency [GHz]']*N).astype(int) 
    sens_mwi_dsb = pd.merge(pam_data_df, mwi_dsb_data_linear, on='frequency [GHz]')
    sens_mwi_dsb['frequency [GHz]'] = sens_mwi_dsb['frequency [GHz]'] / N
    pam_data_df['frequency [GHz]'] = pam_data_df['frequency [GHz]'] / N
    mwi_dsb_data_linear['frequency [GHz]'] = mwi_dsb_data_linear['frequency [GHz]'] / N

    #srf_plus_noise[:, :, -1] # shape=(n_freq, n_noise, len(channels))

    # create result for each of the modelled profiles
    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_subplot(111)
    ax.set_title('MWI virtual measurement minus PAMTRA simulation at channel bandwith edges\nSensitivity data: 1000 perturbed measurements (MWI-RX183_DSB_Matlab.xlsx)')
    
    for i, profile in enumerate(profiles):
                    
        # calculate measured brightness temperature as dot product between 
        # simulated TB and sensitivity for the different channels
        ch_14_tb_meas = np.dot(sens_mwi_dsb[profile].values, srf_plus_noise[:, :, 0])
        ch_15_tb_meas = np.dot(sens_mwi_dsb[profile].values, srf_plus_noise[:, :, 1])
        ch_16_tb_meas = np.dot(sens_mwi_dsb[profile].values, srf_plus_noise[:, :, 2])
        ch_17_tb_meas = np.dot(sens_mwi_dsb[profile].values, srf_plus_noise[:, :, 3])
        ch_18_tb_meas = np.dot(sens_mwi_dsb[profile].values, srf_plus_noise[:, :, 4])
    
        # compare with actual modelled TB at the frequency belonging to the channel
        # get simulated brightness temperature at the channel frequency edges (bandwidth)
        # calculate mean of the four edge frequencies
        ch_14_tb_pam = pam_data_df.loc[pam_data_df['frequency [GHz]'].isin(ch_14_f_bw)][profile].mean()
        ch_15_tb_pam = pam_data_df.loc[pam_data_df['frequency [GHz]'].isin(ch_15_f_bw)][profile].mean()
        ch_16_tb_pam = pam_data_df.loc[pam_data_df['frequency [GHz]'].isin(ch_16_f_bw)][profile].mean()
        ch_17_tb_pam = pam_data_df.loc[pam_data_df['frequency [GHz]'].isin(ch_17_f_bw)][profile].mean()
        ch_18_tb_pam = pam_data_df.loc[pam_data_df['frequency [GHz]'].isin(ch_18_f_bw)][profile].mean()
        
        # then compare values graphically
        dx = np.linspace(-0.3, 0.3, 7)
        
        marker_style = dict(fillstyle='none', alpha=0.2)
        
        boxprops = dict(facecolor=pam_colors[profile], color=pam_colors[profile])
        flierprops = dict(markeredgecolor='k', markersize=2)
        medianprops = dict(color='k')
        
        ax.boxplot(x=ch_14_tb_meas - ch_14_tb_pam, notch=True, sym="d", positions=[14+dx[i]], widths=0.075, 
                   boxprops=boxprops, flierprops=flierprops, medianprops=medianprops, patch_artist=True)
        ax.boxplot(x=ch_15_tb_meas - ch_15_tb_pam, notch=True, sym="d", positions=[15+dx[i]], widths=0.075, 
                   boxprops=boxprops, flierprops=flierprops, medianprops=medianprops, patch_artist=True)
        ax.boxplot(x=ch_16_tb_meas - ch_16_tb_pam, notch=True, sym="d", positions=[16+dx[i]], widths=0.075, 
                   boxprops=boxprops, flierprops=flierprops, medianprops=medianprops, patch_artist=True)
        ax.boxplot(x=ch_17_tb_meas - ch_17_tb_pam, notch=True, sym="d", positions=[17+dx[i]], widths=0.075, 
                   boxprops=boxprops, flierprops=flierprops, medianprops=medianprops, patch_artist=True)
        ax.boxplot(x=ch_18_tb_meas - ch_18_tb_pam, notch=True, sym="d", positions=[18+dx[i]], widths=0.075, 
                   boxprops=boxprops, flierprops=flierprops, medianprops=medianprops, patch_artist=True)     
        
    ax.set_ylabel('$\Delta TB = TB_{MWI} - TB_{PAMTRA}$ [K]')
    
    # ax limits
    ax.set_ylim([-0.1, 0.8])
    ax.set_xlim([13.5, 18.5])

    # axis tick settings
    ax.set_xticks(np.arange(14, 19), minor=True)
    ax.set_xticks(np.arange(13.5, 19.5), minor=False)
    ax.set_xticklabels(freq_txt, minor=True)
    ax.set_xticklabels('', minor=False)
    ax.xaxis.grid(True, which='major')
    ax.yaxis.grid(True)
    ax.tick_params('x', length=0, width=0, which='minor')
    
    # add 0-line
    ax.axhline(y=0, color='k', linestyle='--', linewidth=.75)
    
    # legend settings
    patches = []
    for profile in profiles:
        patches.append(mpatches.Patch(color=pam_colors[profile], label=pam_label_detail[profile]))
    
    ax.legend(handles=patches, bbox_to_anchor=(1.05, 0.5), loc='center left', frameon=False)
    
    fig.tight_layout()
    
    plt.savefig(path_fig + 'result_4B_MWI-RX183_DSB_Matlab.png', dpi=400)

    #%% plot atmospheric profiles
    
    path = path_data + 'atmosphere/'
    
    fig = plt.figure(figsize=(9, 6))
    
    ax1 = fig.add_subplot(121)
    ax1.invert_yaxis()
    ax2 = fig.add_subplot(122, sharey=ax1)
    
    for profile in pam_label_detail.keys():
        
        if profile != 'standard':
        
            rs = np.loadtxt(path+profile+'.txt', usecols=[0, 1, 2, 4])  # pres [hPa], hght [m], temp [C], relh [%]
            
            ax1.plot(rs[:, 2], rs[:, 0], pam_line_fmt[profile], label=pam_label_detail[profile])
            ax2.plot(rs[:, 3], rs[:, 0], pam_line_fmt[profile], label=pam_label_detail[profile])
            
            ax1.set_ylabel('Pressure [hPa]')
            ax1.set_xlabel('Temperature [°C]')
            ax2.set_xlabel('Relative humidity [%]')
            
            for ax in [ax1, ax2]:
                ax.grid(True)
                ax.set_ylim([1040, 0])
            
            ax2.set_xlim([0, 100])
            
    ax2.legend(bbox_to_anchor=(1.05, 0.5), loc='center left', frameon=False)
    fig.tight_layout()
    
    plt.savefig(path_fig + 'radiosonde_profiles.png', dpi=200)
