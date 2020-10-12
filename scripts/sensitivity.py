

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import sys

sys.path.append('/home/nrisse/uniHome/WHK/eumetsat/scripts')
from mwi_183 import MWI183GHz as mwi


# list of atmospheric profiles
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
pam_point_fmt = {'central_europe_winter': dict(marker='*', fillstyle='none', markersize=7, markeredgecolor='g', linestyle='None'),
                 'central_europe_summer': dict(marker='o', fillstyle='none', markersize=7, markeredgecolor='g', linestyle='None'),
                 'arctic_winter': dict(marker='*', fillstyle='none', markersize=7, markeredgecolor='b', linestyle='None'),
                 'arctic_summer': dict(marker='o', fillstyle='none', markersize=7, markeredgecolor='b', linestyle='None'),
                 'tropics_february': dict(marker='*', fillstyle='none', markersize=7, markeredgecolor='r', linestyle='None'),
                 'tropics_august': dict(marker='o', fillstyle='none', markersize=7, markeredgecolor='r', linestyle='None'),
                 'standard': dict(marker='o', fillstyle='none', markersize=7, markeredgecolor='k', linestyle='None')}

# label for legend
pam_label = {'central_europe_winter': 'Central Europe\n(Winter)', 'central_europe_summer': 'Central Europe\n(Summer)',
             'arctic_winter': 'Arctic\n(Winter)', 'arctic_summer': 'Arctic\n(Summer)',
             'tropics_february': 'Tropics\n(February)', 'tropics_august': 'Tropics\n(August)',
             'standard': 'standard atmosphere\nwith RH=0%'}

# label for legend with specific times of radiosonde launch: This has to be changed by hand if other data is used!!!
pam_label_detail = {'central_europe_winter': 'Essen\n(2020-02-02 12)', 'central_europe_summer': 'Essen\n(2020-08-01 00)',
                    'arctic_winter': 'Ny-Alesund\n(2020-02-02 12)', 'arctic_summer': 'Ny-Alesund\n(2020-08-01 12)',
                    'tropics_february': 'Singapore\n(2020-02-01 12)', 'tropics_august': 'Singapore\n(2020-08-01 12)',
                    'standard': 'standard atmosphere\nwith RH=0%'}


class RadiosondeMWI:

    def __init__(self, path_data, path_fig):
        """
        Class to display radiosonde profiles that are used for MWI analysis
        """

        self._path_data = path_data
        self._path_fig = path_fig

        # profiles (without standard atmosphere)
        # todo: add profile of standard atmosphere
        self.profiles = np.array(['arctic_winter', 'arctic_summer',
                                  'central_europe_winter', 'central_europe_summer',
                                  'tropics_february', 'tropics_august'])

        # IWV
        self.IWV = pd.DataFrame(data=np.nan, index=['IWV'], columns=profiles)

    def read_profile(self, profile):
        """
        Read radiosonde profiles
        """

        path = self._path_data + 'atmosphere/'

        rs_df = pd.read_csv(path + profile + '.txt', comment='#', delim_whitespace=True,
                            names=['p [hPa]', 'z [m]', 'T [C]', 'T_dew [C]', 'RH [%]', 'r [g/kg]', 'wdir [deg]',
                                   'SKNT [knot]', 'THTA [K]', 'THTE [K]', 'THTV [K]'])

        return rs_df

    def calculate_iwv(self):
        """
        Calculate IWV of profile
        """

        Rd = 287  # J / kg K

        for profile in self.profiles:

            rs_df = self.read_profile(profile)

            z = rs_df['z [m]'].values
            T = rs_df['T [C]'].values + 273.15  # K
            p = rs_df['p [hPa]'].values * 100  # Pa
            r = rs_df['r [g/kg]'].values * 1e-3  # kg/kg

            # density of water vapor [kg/m3]
            rho_v = p / (Rd * T) * r / (1 - 1.608 * r)

            # integrated water vapor [kg/m2]
            dz = z[1:] - z[:-1]
            self.IWV[profile] = np.nansum(rho_v[:-1] * dz)

    def plot_atmosphere(self):
        """
        Plot dropsonde profile
        """

        fig = plt.figure(figsize=(9, 6))

        ax1 = fig.add_subplot(121)
        ax1.invert_yaxis()
        ax2 = fig.add_subplot(122, sharey=ax1)

        for profile in self.profiles:

            rs_df = self.read_profile(profile)

            ax1.plot(rs_df['T [C]'], rs_df['p [hPa]'], pam_line_fmt[profile], label=pam_label_detail[profile])
            ax2.plot(rs_df['RH [%]'], rs_df['p [hPa]'], pam_line_fmt[profile], label=pam_label_detail[profile])

            ax1.set_ylabel('Pressure [hPa]')
            ax1.set_xlabel('Temperature [°C]')
            ax2.set_xlabel('Relative humidity [%]')

            for ax in [ax1, ax2]:
                ax.grid(True)
                ax.set_ylim([1040, 0])

            ax2.set_xlim([0, 100])

        ax2.legend(bbox_to_anchor=(1.05, 0.5), loc='center left', frameon=False)
        fig.tight_layout()

        plt.savefig(self._path_fig + 'radiosonde_profiles.png', dpi=200)


class MicrowaveImager:
    
    def __init__(self, path_sensitivity, path_fig, path_data):
        """
        Initialize paramters
        """
        
        # paths
        self._path_sensitivity = path_sensitivity
        self._path_fig = path_fig
        self._path_data = path_data
        
        # read sensitivity data
        self.mwi_dsb_data = self.get_data(file='MWI-RX183_DSB_Matlab.xlsx')
        self.mwi_data = self.get_data(file='MWI-RX183_Matlab.xlsx')
        
        # linearize and normalize sensitivity data
        self.mwi_dsb_data_lino = self.get_data_lino(dataframe=self.mwi_dsb_data)
        self.mwi_data_lino = self.get_data_lino(dataframe=self.mwi_data)

        # read pamtra simulation
        self.pam_data_df = self.read_pamtra_simulation()

    def get_data(self, file):
        """
        Read sensitivity measurement from excel file
        """
        
        # read data from excel sheet
        data_ch14 = pd.read_excel(self._path_sensitivity+file, sheet_name='Ch14', usecols=[0, 1],
                                  names=['frequency [GHz]', 'sensitivity [dB]'], header=None)
        data_ch15 = pd.read_excel(self._path_sensitivity+file, sheet_name='Ch15', usecols=[0, 1],
                                  names=['frequency [GHz]', 'sensitivity [dB]'], header=None)
        data_ch16 = pd.read_excel(self._path_sensitivity+file, sheet_name='Ch16', usecols=[0, 1],
                                  names=['frequency [GHz]', 'sensitivity [dB]'], header=None)
        data_ch17 = pd.read_excel(self._path_sensitivity+file, sheet_name='Ch17', usecols=[0, 1],
                                  names=['frequency [GHz]', 'sensitivity [dB]'], header=None)
        data_ch18 = pd.read_excel(self._path_sensitivity+file, sheet_name='Ch18', usecols=[0, 1],
                                  names=['frequency [GHz]', 'sensitivity [dB]'], header=None)
        
        # check if frequencies are the same
        assert np.sum(data_ch14.iloc[:, 0] != data_ch15.iloc[:, 0]) == 0
        assert np.sum(data_ch14.iloc[:, 0] != data_ch16.iloc[:, 0]) == 0
        assert np.sum(data_ch14.iloc[:, 0] != data_ch17.iloc[:, 0]) == 0
        assert np.sum(data_ch14.iloc[:, 0] != data_ch18.iloc[:, 0]) == 0
        
        # write data into single dataframe
        data = pd.DataFrame()
        data['frequency [GHz]'] = data_ch14.iloc[:, 0]  # use frequency from channel 14
        data['ch14 sensitivity [dB]'] = data_ch14.iloc[:, 1]
        data['ch15 sensitivity [dB]'] = data_ch15.iloc[:, 1]
        data['ch16 sensitivity [dB]'] = data_ch16.iloc[:, 1]
        data['ch17 sensitivity [dB]'] = data_ch17.iloc[:, 1]
        data['ch18 sensitivity [dB]'] = data_ch18.iloc[:, 1]
                
        return data
    
    @staticmethod
    def linearize_srf(values):
        """
        Convert spectral response function from dB to linear units
        number of rows:    number of frequencies
        number of columns: number of channel
        """
        
        values_lin = 10**(0.1 * values)
        
        return values_lin
    
    @staticmethod
    def normalize_srf(values_lin):
        """
        Normalize linear spectral response function to a sum along each column of 1
        number of rows:    number of frequencies
        number of columns: number of channel
        """
        
        values_norm = values_lin / values_lin.sum(axis=0)
    
        return values_norm
    
    def get_data_lino(self, dataframe):
        """
        Linearize and normalize measured spectral response functions
        """
        
        freqs = dataframe.values[:, 0]  # get frequencies
        values = dataframe.values[:, 1:]  # get sensitivity in dB
        
        values_lino = self.normalize_srf(values_lin=self.linearize_srf(values))
        
        # add to data frames
        data_lino = pd.DataFrame()    
        data_lino['frequency [GHz]'] = freqs
        data_lino['ch14 sensitivity'] = values_lino[:, 0]
        data_lino['ch15 sensitivity'] = values_lino[:, 1]
        data_lino['ch16 sensitivity'] = values_lino[:, 2]
        data_lino['ch17 sensitivity'] = values_lino[:, 3]
        data_lino['ch18 sensitivity'] = values_lino[:, 4]
        
        return data_lino
        
    def find_matching_frequency(self):
        """
        UPDATE: not necessary. Frequencies for Pamtra are set identical to the measurements.
        
        comment: df_mwi_dsb has jump in frequency between 183.257 GHz (index 529) and 183.367 GHz (index 530)
        (difference is 0.11)
        comment: df_mwi step in frequency is always 0.015
        comment: the frequencies from both files do not overlap, the values are shiftet by 0.005 GHz 
        comment: however, this can be corrected by interpolating the modelled brightness temperatures to the used
        frequencies
        comment: a regular grid of modelled brightness temperatures is defined with step width 0.
        """
        
        df_mwi_dsb = self.mwi_dsb_data['frequency [GHz]'].values[1:] - self.mwi_dsb_data['frequency [GHz]'].values[:-1]
        df_mwi = self.mwi_data['frequency [GHz]'].values[1:] - self.mwi_data['frequency [GHz]'].values[:-1]
    
        print(np.max(df_mwi_dsb))
        ix = np.where(df_mwi_dsb == np.max(df_mwi_dsb))[0][0]
        print(self.mwi_dsb_data['frequency [GHz]'].values[ix])
        print(self.mwi_dsb_data['frequency [GHz]'].values[ix+1])
        
        print(np.max(df_mwi))  # constant
        
        # min always constant 0.015
        print(np.min(df_mwi_dsb))
        print(np.min(df_mwi))
        
        # do the frequencies overlap?
        print(self.mwi_dsb_data['frequency [GHz]'].values[ix:ix+10])
        print(self.mwi_data['frequency [GHz]'].values[:10])
    
    def save_sensitivity_plot(self, fig, axes, filename, linear=True):
        """
        Plot sensitivity measurement
        In order to plot different things, return ax and save different data in the base plot
        """
   
        for i, channel in enumerate(mwi.channels_str):
            
            # set x-limit
            axes[i].set_xlim([175, 202])
            
            # annotate channel name
            axes[i].annotate(text=mwi.freq_txt[i], xy=(0.99, 0.9), xycoords='axes fraction', backgroundcolor="w",
                             annotation_clip=False, horizontalalignment='right', verticalalignment='top')
            
            # add vertical lines
            axes[i].axvline(x=183.31, color='red', linestyle='--')  # mark line center
             
            for j in range(2):  # mark left/right channel frequency
                axes[i].axvline(x=mwi.freq_center[i, j], color='gray', linestyle='--')
            
            for j in range(4):  # mark each bandwidth edge
                axes[i].axvline(x=mwi.freq_bw[i, j], color='gray', linestyle=':')
            
            # add shade for each channel
            axes[i].axvspan(xmin=mwi.freq_bw[i, 0], xmax=mwi.freq_bw[i, 1], ymin=-10e3, ymax=10e3, color='gray',
                            alpha=0.2)
            axes[i].axvspan(xmin=mwi.freq_bw[i, 2], xmax=mwi.freq_bw[i, 3], ymin=-10e3, ymax=10e3, color='gray',
                            alpha=0.2)
    
            # add grid
            axes[i].grid(zorder=2)
            
        # add legend
        axes[4].legend(bbox_to_anchor=(0, -1), loc='center left', frameon=False, ncol=3)
        
        # set axis labels
        if linear:
            axes[2].set_ylabel('Sensitivity [1]')
        else:
            axes[2].set_ylabel('Sensitivity [dB]')
        
        axes[-1].set_xlabel('Frequency [GHz]')
        
        fig.tight_layout()
        
        plt.savefig(self._path_fig+filename, dpi=300)
        
    def plot_sensitivity_data(self):
        """
        Plot sensitivity data 
        """
        
        fig, axes = plt.subplots(5, 1, sharex='all', figsize=(9, 6))
        axes = axes.flatten(order='F')
        
        fig.suptitle('Bandpass measurements of MWI channels 14 to 18')
        
        for i, channel in enumerate(mwi.channels_str):
            
            # MWI-RX183_DSB_Matlab.xlsx dataset
            axes[i].plot(self.mwi_dsb_data['frequency [GHz]'], self.mwi_dsb_data['ch'+channel+' sensitivity [dB]'],
                         color='k', linewidth=0.9, label='MWI-RX183_DSB_Matlab.xlsx')
        
            # MWI-RX183_Matlab.xslx
            axes[i].plot(self.mwi_data['frequency [GHz]'], self.mwi_data['ch'+channel+' sensitivity [dB]'],
                         color='blue', alpha=0.5, linewidth=0.9, label='MWI-RX183_Matlab.xlsx')
            
            # y axis settings
            axes[i].set_yticks(np.arange(-100, 25, 25))
            axes[i].set_ylim([-110, 5])
        
        self.save_sensitivity_plot(fig=fig, axes=axes, filename='sensitivity_measurement.png', linear=False)
        
    def plot_sensitivity_data_noise(self):
        """
        Plot linearized and normalized sensitivity data with noise on top (also with dB unit)
        """
        
        # linear unit
        fig, axes = plt.subplots(5, 1, sharex='all', figsize=(9, 6))
        axes = axes.flatten(order='F')
        
        fig.suptitle('Normalized linear spectral response function of MWI channels 14 to 18 with overlying ' +
                     'perturbation')
        
        for i, channel in enumerate(mwi.channels_str):
            
            # MWI-RX183_DSB_Matlab.xlsx dataset
            axes[i].plot(self.mwi_dsb_data_lino['frequency [GHz]'], self.mwi_dsb_data_lino['ch'+channel+' sensitivity'],
                         color='k', linewidth=0.9,
                         label='MWI-RX183_DSB_Matlab.xlsx')
    
            # MWI-RX183_DSB_Matlab.xlsx dataset perturbed
            axes[i].plot(self.mwi_dsb_data_lino['frequency [GHz]'], srf_plus_noise[:, 0, i], color='green', linewidth=1,
                         alpha=0.5,
                         label='MWI-RX183_DSB_Matlab.xlsx\n(perturbed)')
            
            # MWI-RX183_Matlab.xslx
            axes[i].plot(self.mwi_data_lino['frequency [GHz]'], self. mwi_data_lino['ch'+channel+' sensitivity'],
                         color='blue', alpha=0.5, linewidth=0.9,
                         label='MWI-RX183_Matlab.xlsx')
            
            # y axis settings
            axes[i].set_yticks(np.arange(0, 0.015, 0.005))
            axes[i].set_ylim([0, 0.015])
        
        self.save_sensitivity_plot(fig=fig, axes=axes, filename='sensitivity_measurement_normalized_linear.png',
                                   linear=True)
        
        # log unit
        fig, axes = plt.subplots(5, 1, sharex='all', figsize=(9, 6))
        axes = axes.flatten(order='F')
        
        fig.suptitle('Normalized spectral response function of MWI channels 14 to 18 with overlying perturbation')
        
        for i, channel in enumerate(mwi.channels_str):
            
            # MWI-RX183_DSB_Matlab.xlsx dataset
            axes[i].plot(self.mwi_dsb_data_lino['frequency [GHz]'],
                         10*np.log10(self.mwi_dsb_data_lino['ch'+channel+' sensitivity']), color='k', linewidth=0.9,
                         label='MWI-RX183_DSB_Matlab.xlsx')
    
            # MWI-RX183_DSB_Matlab.xlsx dataset perturbed
            axes[i].plot(self.mwi_dsb_data_lino['frequency [GHz]'], 10*np.log10(srf_plus_noise[:, 0, i]), color='green',
                         linewidth=1, alpha=0.5, label='MWI-RX183_DSB_Matlab.xlsx\n(perturbed)')
    
            # MWI-RX183_Matlab.xslx
            axes[i].plot(self.mwi_data_lino['frequency [GHz]'],
                         10*np.log10(self.mwi_data_lino['ch'+channel+' sensitivity']), color='blue', alpha=0.5,
                         linewidth=0.9, label='MWI-RX183_Matlab.xlsx')
            
            # y axis settings
            axes[i].set_yticks(np.arange(-150, 25, 25))
            axes[i].set_ylim([-140, -15])
        
        self.save_sensitivity_plot(fig=fig, axes=axes, filename='sensitivity_measurement_normalized_dB.png',
                                   linear=False)

    def set_freqs_pamtra(self):
        """
        Create frequency array based on where measurements are taken (including actual channel frequencies) and save to
        file.
        
        Frequencies from MWI-RX183_Matlab.xlsx are not considered
        """
        
        freqs_pamtra = self.mwi_dsb_data['frequency [GHz]'].values  # frequencies from dsb file
        freqs_pamtra = np.append(freqs_pamtra, mwi.freq_bw_center.flatten())  # chennel frequencies
        freqs_pamtra = np.unique(np.sort(freqs_pamtra))  # sort and remove duplicates
        
        # write frequencies to file
        np.savetxt(self._path_data + 'frequencies.txt', freqs_pamtra)
        
    def plot_frequencies(self):
        """
        Compare defined frequency grid and frequency grid from measurement files
        """
        
        # read pamtra frequencies
        freqs_pamtra = np.loadtxt(self._path_data + 'frequencies.txt')
        
        plt.figure(figsize=(6, 2))
        
        plt.plot(freqs_pamtra, [1]*len(freqs_pamtra), 'xk', label='pamtra frequencies', alpha=0.6, markeredgecolor=None)
        plt.plot(self.mwi_dsb_data['frequency [GHz]'], [1]*len(self.mwi_dsb_data['frequency [GHz]']), '.r',
                 label='MWI-RX183_DSB_Matlab.xlsx', alpha=0.6, markeredgecolor=None)
        plt.plot(self.mwi_data['frequency [GHz]'], [1]*len(self.mwi_data['frequency [GHz]']), '.b',
                 label='MWI-RX183_Matlab.xlsx', alpha=0.6, markeredgecolor=None)
        
        plt.axvline(x=183.31, color='gray')
        plt.legend()
        plt.grid()
        
        plt.savefig(self._path_fig + 'frequencies.png', dpi=400)
    
    def read_pamtra_simulation(self):
        """
        read data from pamtra simulation
        """
        
        pam_data_df = pd.read_csv(self._path_data + 'mwi_pamtra_tb.txt', delimiter=',')
        pam_data_df.rename(columns={'frequency_GHz': 'frequency [GHz]'}, inplace=True)  # for the join later
        
        return pam_data_df
    
    def plot_pamtra_simulation(self):
        """
        plot pamtra simulation
        """

        fig = plt.figure(figsize=(9, 6))
        ax = fig.add_subplot(111)
        ax.set_title('PAMTRA simulation at 833 km nadir view (V-pol) and MWI 183.31 GHz channels\nfor different ' +
                     'radiosonde profiles and standard atmosphere (RH=0%)')
        
        for profile in profiles:
            ax.plot(self.pam_data_df['frequency [GHz]'], self.pam_data_df[profile], pam_line_fmt[profile],
                    label=pam_label_detail[profile])
        
        # add MWI channels
        for i, channel in enumerate(mwi.channels_str):
            
            # annotate channel name
            ax.annotate(text=mwi.freq_txt[i][4:6], xy=[mwi.freq_center[i, 0]-0.4, 171], fontsize=7,
                        bbox=dict(boxstyle='square', fc='white', ec='none', pad=0))
            ax.annotate(text=mwi.freq_txt[i][4:6], xy=[mwi.freq_center[i, 1]-0.4, 171], fontsize=7,
                        bbox=dict(boxstyle='square', fc='white', ec='none', pad=0))
            
            # add vertical lines
            ax.axvline(x=183.31, color='pink', linestyle='-', alpha=0.5)  # mark line center
            ax.axvline(x=mwi.freq_center[i, 0], color='gray', linestyle='-', alpha=0.5)  # mark left channel frequency
            ax.axvline(x=mwi.freq_center[i, 1], color='gray', linestyle='-', alpha=0.5)  # mark right channel frequency
            
        ax.legend(bbox_to_anchor=(1.05, 0.5), loc='center left', frameon=False)
        ax.grid(axis='y')
        
        ax.set_ylim([170, 290])
        ax.set_xlim([np.min(self.pam_data_df['frequency [GHz]']), np.max(self.pam_data_df['frequency [GHz]'])])
        
        ax.set_xlabel('Frequency [GHz]')
        ax.set_ylabel('Brightness temperature [K]')
        
        fig.tight_layout()
        
        plt.savefig(self._path_fig + 'pamtra_simulation.png', dpi=200)

    def create_noise_values(self, dataframe, std=0.1, n_noise=1000):
        """
        Create gaussian perturbation of the spectral response function
        """
        
        np.random.seed(0)

        n_freq = len(dataframe['frequency [GHz]'])
        
        noise = np.random.normal(loc=1, scale=std, size=(n_freq, n_noise))
        
        # add realizations to each of the measurements and shiw result as boxplot
        srf_plus_noise = np.full(shape=(n_freq, n_noise, len(mwi.channels_str)), fill_value=np.nan)
        
        for i, channel in enumerate(mwi.channels_str):
    
            srf_plus_noise[:, :, i] = noise * np.array(dataframe['ch'+channel+' sensitivity'])[:, np.newaxis]
            srf_plus_noise[:, :, i] = self.normalize_srf(srf_plus_noise[:, :, i])

        return srf_plus_noise
    
    def join_pam_on_sensitivity(self, dataframe):
        """
        Combine PAMTRA brightness temperature dataframe and linearized and normalized sensitivity
        data at matching frequencies.
        
        here: convert frequency to join - float to int and then back int to float
        """

        N = 10000
        
        # make copy of data 
        pam = self.pam_data_df.copy(deep=True)
        srf = dataframe.copy(deep=True)
        
        # convert frequency to integer and use as join
        pam['frequency [GHz]'] = np.round(pam['frequency [GHz]']*N).astype(int)
        srf['frequency [GHz]'] = np.round(srf['frequency [GHz]']*N).astype(int)
        
        # merge the data on the matching frequencies and convert frequency to float again
        srf_pam = pd.merge(pam, srf, on='frequency [GHz]')
        srf_pam['frequency [GHz]'] = srf_pam['frequency [GHz]'] / N

        return srf_pam

    @staticmethod
    def calculate_tb_mwi(tb, srf):
        """
        Calculate virtual MWI temperature
        """
        
        tb_mwi = np.dot(tb, srf)
        
        return tb_mwi

    def calculate_tb_pamtra(self, freqs, profile):
        """
        Calculate TB from PAMTRA at frequencies for a specific profile
        """
        
        tb_pam = self.pam_data_df.loc[self.pam_data_df['frequency [GHz]'].isin(freqs)][profile].mean()
        
        return tb_pam
    
    def plot_result(self, frequencies, filename, title, ylim):
        """
        Plot result without noise

        frequencies     frequencies that are used to calculat TB pamtra of shape (n_channels, n_frequencies)
        filename        filename of the plot that is saved
        title           title of the plot
        ylim            y-limit to use
        """

        # join brightness temperature to the linear sensitivity dataframe
        sens_mwi_dsb = self.join_pam_on_sensitivity(dataframe=self.mwi_dsb_data_lino)

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

    def plot_result_noise(self, frequencies, std, filename, title, ylim):
        """
        Plot result with noise as boxplot

        frequencies     frequencies that are used to calculat TB pamtra of shape (n_channels, n_frequencies)
        filename        filename of the plot that is saved
        title           title of the plot
        ylim            y-limit to use
        """

        # join brightness temperature to the linear sensitivity dataframe
        sens_mwi_dsb = self.join_pam_on_sensitivity(dataframe=self.mwi_dsb_data_lino)

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

    def run(self):
        """
        Main routine

        All results with MWI-RX183_DSB_Matlab.xlsx file
        """

        # reduce number of data points
        # .iloc[::2, :]
        
        mwi.print_info()  # print MWI specifications
        self.plot_sensitivity_data()  # plot sensitivity measurement
        self.set_freqs_pamtra()
        self.plot_frequencies()
        self.plot_pamtra_simulation()

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


if __name__ == '__main__':

    MWI = MicrowaveImager(path_sensitivity='/home/nrisse/uniHome/WHK/eumetsat/sensitivity/', 
                          path_fig='/home/nrisse/uniHome/WHK/eumetsat/plots/', 
                          path_data='/home/nrisse/uniHome/WHK/eumetsat/data/')
    MWI.set_freqs_pamtra()
    #MWI.run()

    #plt.close('all')

    # plot radiosondes
    RS = RadiosondeMWI(path_data='/home/nrisse/uniHome/WHK/eumetsat/data/',
                       path_fig='/home/nrisse/uniHome/WHK/eumetsat/plots/')
    RS.calculate_iwv()

    for profile in profiles:
        print('IWV of {}: {} kg m-2'.format(profile, np.round(RS.IWV.loc['IWV', profile], 2)))
