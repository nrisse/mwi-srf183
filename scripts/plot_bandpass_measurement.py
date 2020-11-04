

import numpy as np
import matplotlib.pyplot as plt

import sys
sys.path.append('/home/nrisse/uniHome/WHK/eumetsat/scripts')
from importer import Sensitivity
from mwi_info import mwi
from path_setter import *


"""
Script to plot bandpass measurements on log scale
"""


if __name__ == '__main__':
    
    #%% read bandpass measurement
    sen_dsb = Sensitivity(path=path_sens, filename='MWI-RX183_DSB_Matlab.xlsx')
    sen = Sensitivity(path=path_sens, filename='MWI-RX183_Matlab.xlsx')
    
    #%% plot sensitivity data (raw, all, log scale)
    fig, axes = plt.subplots(5, 1, sharex='all', figsize=(9, 6))
    axes = axes.flatten(order='F')
    
    fig.suptitle('Bandpass measurements of MWI channels 14 to 18')
    
    for i, channel in enumerate(mwi.channels_str):
        
        # MWI-RX183_DSB_Matlab.xlsx dataset
        axes[i].plot(sen_dsb.data['frequency [GHz]'], sen_dsb.data['ch'+channel+' sensitivity [dB]'],
                     color='k', linewidth=0.9, label='MWI-RX183_DSB_Matlab.xlsx')
        
        # MWI-RX183_Matlab.xslx
        axes[i].plot(sen.data['frequency [GHz]'], sen.data['ch'+channel+' sensitivity [dB]'],
                     color='blue', alpha=0.5, linewidth=0.9, label='MWI-RX183_Matlab.xlsx')
        
        # y axis settings
        axes[i].set_yticks(np.arange(-100, 25, 25))
        axes[i].set_ylim([-110, 5])
                
        # set x-limit
        axes[i].set_xlim([175, 202])
        
        # annotate channel name
        axes[i].annotate(text=mwi.freq_txt[i], xy=(0.99, 0.9), xycoords='axes fraction', backgroundcolor="w",
                         annotation_clip=False, horizontalalignment='right', verticalalignment='top')
        
        # add vertical lines
        axes[i].axvline(x=mwi.absorpt_line, color='red', linestyle='--')  # mark line center
        
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
    axes[2].set_ylabel('Sensitivity [dB]')
    
    axes[-1].set_xlabel('Frequency [GHz]')
    
    fig.tight_layout()
    
    plt.savefig(path_plot + 'bandpass_measurement_all.png', dpi=300)

    #%% plot sensitivity data (raw, dsb, log scale)
    fig, axes = plt.subplots(5, 1, sharex='all', figsize=(6, 6))
    axes = axes.flatten(order='F')
    
    fig.suptitle('Bandpass measurements of MWI channels 14 to 18')
    
    plt.subplots_adjust(#left = 0.1,  # the left side of the subplots of the figure
                        right = 0.8,   # the right side of the subplots of the figure
                        #bottom = 0.1,  # the bottom of the subplots of the figure
                        #top = 0.9,     # the top of the subplots of the figure
                        #wspace = 0.2,  # the amount of width reserved for space between subplots,
                                       # expressed as a fraction of the average axis width
                        #hspace = 0.2  # the amount of height reserved for space between subplots,
                                      # expressed as a fraction of the average axis height
                        )
    
    for i, channel in enumerate(mwi.channels_str):
        
        # MWI-RX183_DSB_Matlab.xlsx dataset
        axes[i].plot(sen_dsb.data['frequency [GHz]'], sen_dsb.data['ch'+channel+' sensitivity [dB]'], color='k', linewidth=1)
        
        # y axis settings
        axes[i].set_yticks(np.arange(-100, 25, 25))
        axes[i].set_ylim([-100, 5])
                
        # set x-limit
        axes[i].set_xlim([np.min(mwi.freq_bw)-0.1, np.max(mwi.freq_bw)+0.1])
        
        # annotate channel name
        axes[i].annotate(text=mwi.freq_txt[i], xy=(1.01, 0.5), xycoords='axes fraction', backgroundcolor="None",
                         annotation_clip=False, horizontalalignment='left', verticalalignment='center')
        
        # add vertical lines
        axes[i].axvline(x=mwi.absorpt_line, color='red', linewidth=0.5)  # mark line center
        
        for j in range(2):  # mark left/right channel frequency
            axes[i].axvline(x=mwi.freq_center[i, j], color='gray', linestyle='--', linewidth=0.75)
        
        for j in range(4):  # mark each bandwidth edge
            axes[i].axvline(x=mwi.freq_bw[i, j], color='gray', linestyle=':', linewidth=0.75)
        
        # add shade for each channel
        axes[i].axvspan(xmin=mwi.freq_bw[i, 0], xmax=mwi.freq_bw[i, 1], ymin=-10e3, ymax=10e3, color='gray',
                        alpha=0.2)
        axes[i].axvspan(xmin=mwi.freq_bw[i, 2], xmax=mwi.freq_bw[i, 3], ymin=-10e3, ymax=10e3, color='gray',
                        alpha=0.2)

        # add grid
        axes[i].grid(zorder=2)
        
    # set axis labels
    axes[2].set_ylabel('Sensitivity [dB]')
    axes[-1].set_xlabel('Frequency [GHz]')
    
    #fig.tight_layout()
    
    plt.savefig(path_plot + 'bandpass_measurement_dsb.png', dpi=300)
    
    #%% linear scale
    
    # set axis labels
    axes[2].set_ylabel('Sensitivity [1]')
    
    #%% noise
        
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