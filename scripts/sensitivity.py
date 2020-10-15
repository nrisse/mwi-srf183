

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import sys
sys.path.append('/home/nrisse/uniHome/WHK/eumetsat/scripts')
from mwi_183 import MWI183GHz as mwi


"""
Description

Analyze seasonal and regional dependency of the difference between the virtual
MWI measurement and the TB calculated with PAMTRA.

Requires:
    - seven radiosonde profiles
    
Caution: no clouds included
"""



profile_prop = {'arctic_winter': {'file_profile':  'atmosphere/2020/02/01/ID_01004_202002011200.txt',
                                  'file_tb':       'brightness_temperature/2020/02/01/TB_PAMTRA_ID_01004_202002011200.txt',
                                  'boxplot_color': '#002375',
                                  'line_format':   'b:',
                                  'point_format':  dict(marker='*', fillstyle='none', markersize=7, markeredgecolor='b', linestyle='None'),
                                  'label':         'Ny-Alesund\n(2020-02-01 12)'
                                  },
                'arctic_summer': {'file_profile':  'atmosphere/2020/08/01/ID_01004_202008011200.txt',
                                  'file_tb':       'brightness_temperature/2020/08/01/TB_PAMTRA_ID_01004_202008011200.txt',
                                  'boxplot_color': '#6594FF',
                                  'line_format':   'b-',
                                  'point_format':  dict(marker='o', fillstyle='none', markersize=7, markeredgecolor='b', linestyle='None'),
                                  'label':         'Ny-Alesund\n(2020-08-01 12)'
                                  },
                'central_europe_winter': {'file_profile':  'atmosphere/2020/02/01/ID_10410_202002011200.txt',
                                          'file_tb':       'brightness_temperature/2020/02/01/TB_PAMTRA_ID_10410_202002011200.txt',
                                          'boxplot_color': '#008B00',
                                          'line_format':   'g:',
                                          'point_format':  dict(marker='*', fillstyle='none', markersize=7, markeredgecolor='g', linestyle='None'),
                                          'label':         'Essen\n(2020-02-01 12)'
                                          }, 
                'central_europe_summer': {'file_profile':  'atmosphere/2020/08/01/ID_10410_202008011200.txt',
                                          'file_tb':       'brightness_temperature/2020/08/01/TB_PAMTRA_ID_10410_202008011200.txt',
                                          'boxplot_color': '#51FF51',
                                          'line_format':   'g-',
                                          'point_format':  dict(marker='o', fillstyle='none', markersize=7, markeredgecolor='g', linestyle='None'),
                                          'label':         'Essen\n(2020-08-01 12)'
                                          },
                'tropics_february': {'file_profile':  'atmosphere/2020/02/01/ID_48698_202002011200.txt',
                                     'file_tb':       'brightness_temperature/2020/02/01/TB_PAMTRA_ID_48698_202002011200.txt',
                                     'boxplot_color': '#AE0000',
                                     'line_format':   'r:',
                                     'point_format':  dict(marker='*', fillstyle='none', markersize=7, markeredgecolor='r', linestyle='None'),
                                     'label':         'Singapore\n(2020-02-01 12)'
                                     },
                'tropics_august': {'file_profile':  'atmosphere/2020/08/01/ID_48698_202008011200.txt',
                                   'file_tb':       'brightness_temperature/2020/08/01/TB_PAMTRA_ID_48698_202008011200.txt',
                                   'boxplot_color': '#FF5555',
                                   'line_format':   'r-',
                                   'point_format':  dict(marker='o', fillstyle='none', markersize=7, markeredgecolor='r', linestyle='None'),
                                   'label':         'Singapore\n(2020-08-01 12)'
                                   },
                'standard': {'file_profile':  None,
                             'file_tb':       'brightness_temperature/TB_PAMTRA_standard_atmosphere.txt',
                             'boxplot_color': '#000000',
                             'line_format':   'k-',
                             'point_format':  dict(marker='o', fillstyle='none', markersize=7, markeredgecolor='k', linestyle='None'),
                             'label':         'Standard atmosphere\nwith RH=0%'
                             }
                }



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
        #self.mwi_data = self.get_data(file='MWI-RX183_Matlab.xlsx')
        
        # linearize and normalize sensitivity data
        self.mwi_dsb_data_lino = self.prepare_data(dataframe=self.mwi_dsb_data)
        #self.mwi_data_lino = self.prepare_data(dataframe=self.mwi_data)
        
        # read pamtra simulation
        self.pam_data_df = self.read_pamtra_simulation()

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
        freqs_pamtra = np.append(freqs_pamtra, mwi.freq_bw_center.flatten())  # channel frequencies
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
    
    @staticmethod
    def join_pam_on_srf(pam, srf):
        """
        Combine PAMTRA brightness temperature dataframe and linearized and normalized sensitivity
        data at matching frequencies.
        
        here: convert frequency to join - float to int and then back int to float
        """

        N = 10000
        
        # make copy of data 
        pam = pam.copy(deep=True)
        srf = srf.copy(deep=True)
        
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

    def calculate_tb_pamtra(tb, avg_freq, profile):
        """
        Calculate TB from PAMTRA at frequencies for a specific profile
        
        tb:  pandas dataframe with TB of profile
        """
        
        tb_pam = tb.loc[tb['frequency [GHz]'].isin(avg_freq)][profile].mean()
        
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

    def plot_result_noise(self, frequencies, std, filename, title, ylim):
        """
        Plot result with noise as boxplot

        frequencies     frequencies that are used to calculat TB pamtra of shape (n_channels, n_frequencies)
        filename        filename of the plot that is saved
        title           title of the plot
        ylim            y-limit to use
        """

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
