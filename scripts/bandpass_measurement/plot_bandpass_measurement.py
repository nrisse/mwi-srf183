"""
Script to plot bandpass measurements in various forms
"""


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
import os
import sys
sys.path.append(f'{os.environ["PATH_PHD"]}/projects/mwi_bandpass_effects/scripts')
from importer import Sensitivity, Sensitivity_Pandas
from mwi_info import mwi
from path_setter import path_plot
from calc_delta_tb import create_noise_values


if __name__ == '__main__':
    
    #%% read bandpass measurement
    print(Sensitivity.files)
    sen_dsb = Sensitivity_Pandas(filename=Sensitivity.files[0])
    sen = Sensitivity_Pandas(filename=Sensitivity.files[1])
    sen_dsb_pert_values = create_noise_values(data_lino=sen_dsb.data_lino, std=0.05, n=1).reshape((1060, 5))
    sen_dsb_pert_df = pd.DataFrame(columns=sen_dsb.data_lino.columns, 
                                   data=np.concatenate((sen_dsb.data_lino['frequency [GHz]'].values.reshape(1060, 1), sen_dsb_pert_values), axis=1))
    
    #%% PROOF plot sensitivity data (raw, all, log scale)
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
        axes[i].set_ylim([-100, 5])
                
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
    axes[2].set_ylabel('Sensitivity [%]')
    
    axes[-1].set_xlabel('Frequency [GHz]')
    
    fig.tight_layout()
    
    plt.savefig(path_plot + 'bandpass_measurement/bandpass_measurement_all.png', dpi=300)
    
    #%% PROOF plot sensitivity data lino (raw, all, lin scale)
    fig, axes = plt.subplots(5, 1, sharex='all', figsize=(9, 6))
    axes = axes.flatten(order='F')
    
    fig.suptitle('Bandpass measurements of MWI channels 14 to 18')
    
    for i, channel in enumerate(mwi.channels_str):
        
        # MWI-RX183_DSB_Matlab.xlsx dataset
        axes[i].plot(sen_dsb.data_lino['frequency [GHz]'], sen_dsb.data_lino['ch'+channel+' sensitivity']*100,
                     color='k', linewidth=0.9, label='MWI-RX183_DSB_Matlab.xlsx')
        
        # MWI-RX183_Matlab.xslx
        axes[i].plot(sen.data_lino['frequency [GHz]'], sen.data_lino['ch'+channel+' sensitivity']*100,
                     color='blue', alpha=0.5, linewidth=0.9, label='MWI-RX183_Matlab.xlsx')
        
        # y axis settings
        axes[i].set_yticks([0, 0.5, 1, 1.5])
        axes[i].set_ylim([0, 1.5])
                
        # set x-limit
        axes[i].set_xlim([175, 202])
        
        # annotate channel name
        axes[i].annotate(text=mwi.freq_txt[i], xy=(0.99, 0.88), xycoords='axes fraction', backgroundcolor="w",
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
    axes[2].set_ylabel('Sensitivity [%]')
    
    axes[-1].set_xlabel('Frequency [GHz]')
    
    fig.tight_layout()
    
    plt.savefig(path_plot + 'bandpass_measurement/bandpass_measurement_all_lino.png', dpi=300)

    #%% PROOF plot sensitivity data lino (raw, all, lin scale)
    fig, axes = plt.subplots(5, 1, sharex='all', figsize=(9, 6))
    axes = axes.flatten(order='F')
    
    fig.suptitle('Bandpass measurements of MWI channels 14 to 18')
    
    for i, channel in enumerate(mwi.channels_str):
        
        # MWI-RX183_DSB_Matlab.xlsx dataset
        axes[i].plot(sen_dsb.data_lino['frequency [GHz]'], sen_dsb.data_lino['ch'+channel+' sensitivity']*100,
                     color='k', linewidth=0.9, label='MWI-RX183_DSB_Matlab.xlsx')
        
        # MWI-RX183_Matlab.xslx
        axes[i].plot(sen.data_lino['frequency [GHz]'], sen.data_lino['ch'+channel+' sensitivity']*100/2,
                     color='blue', alpha=0.5, linewidth=0.9, label='MWI-RX183_Matlab.xlsx')
        
        # y axis settings
        axes[i].set_yticks([0, 0.5])
        axes[i].set_ylim([0, 0.85])
                
        # set x-limit
        axes[i].set_xlim([mwi.absorpt_line-0.1, np.max(mwi.freq_bw)+0.1])
        
        # annotate channel name
        axes[i].annotate(text=mwi.freq_txt[i], xy=(1.01, 0.5), xycoords='axes fraction', backgroundcolor="None",
                         annotation_clip=False, horizontalalignment='left', verticalalignment='center')
        
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
    axes[2].set_ylabel('Sensitivity [%]')
    
    axes[-1].set_xlabel('Frequency [GHz]')
    
    fig.tight_layout()
    
    plt.savefig(path_plot + 'bandpass_measurement/bandpass_measurement_all_lino_zoom.png', dpi=300)

    #%% PROOF plot sensitivity data (raw, dsb, log scale)
    fig, axes = plt.subplots(5, 1, sharex='all', figsize=(6, 6))
    axes = axes.flatten(order='F')
    
    fig.suptitle('Bandpass measurements of MWI channels 14 to 18')
    
    plt.subplots_adjust(#left = 0.1,  # the left side of the subplots of the figure
                        right = 0.8,   # the right side of the subplots of the figure
                        #bottom = 0.1,  # the bottom of the subplots of the figure
                        top = 0.925,     # the top of the subplots of the figure
                        #wspace = 0.2,  # the amount of width reserved for space between subplots,
                                       # expressed as a fraction of the average axis width
                        #hspace = 0.2  # the amount of height reserved for space between subplots,
                                      # expressed as a fraction of the average axis height
                        )
    
    for i, channel in enumerate(mwi.channels_str):
        
        # MWI-RX183_DSB_Matlab.xlsx dataset
        axes[i].plot(sen_dsb.data['frequency [GHz]'], sen_dsb.data['ch'+channel+' sensitivity [dB]'], color='k', linewidth=1, zorder=2)
        
        # y axis settings
        axes[i].set_yticks(np.arange(-100, 25, 25))
        axes[i].set_ylim([-100, 5])
                
        # set x-limit
        axes[i].set_xlim([np.min(mwi.freq_bw)-0.1, np.max(mwi.freq_bw)+0.1])
        
        # annotate channel name
        axes[i].annotate(text=mwi.freq_txt[i], xy=(1.01, 0.5), xycoords='axes fraction', backgroundcolor="None",
                         annotation_clip=False, horizontalalignment='left', verticalalignment='center')
        
        # add vertical lines
        axes[i].axvline(x=mwi.absorpt_line, color='red', linewidth=0.5, zorder=0)  # mark line center
        
        for j in range(2):  # mark left/right channel frequency
            axes[i].axvline(x=mwi.freq_center[i, j], color='gray', linestyle='--', linewidth=0.75, zorder=0)
        
        for j in range(4):  # mark each bandwidth edge
            axes[i].axvline(x=mwi.freq_bw[i, j], color='gray', linestyle=':', linewidth=0.75, zorder=0)
        
        # add shade for each channel
        axes[i].axvspan(xmin=mwi.freq_bw[i, 0], xmax=mwi.freq_bw[i, 1], ymin=-10e3, ymax=10e3, color='gray',
                        alpha=0.2)
        axes[i].axvspan(xmin=mwi.freq_bw[i, 2], xmax=mwi.freq_bw[i, 3], ymin=-10e3, ymax=10e3, color='gray',
                        alpha=0.2)

        # add grid
        axes[i].grid(zorder=-1)
        
    # set axis labels
    axes[2].set_ylabel('Sensitivity [dB]')
    axes[-1].set_xlabel('Frequency [GHz]')
        
    plt.savefig(path_plot + 'bandpass_measurement/bandpass_measurement_dsb.png', dpi=300)
    
    #%% PROOF plot sensitivity data (lino, dsb, lin scale)
    fig, axes = plt.subplots(5, 1, sharex='all', figsize=(6, 6))
    axes = axes.flatten(order='F')
    
    fig.suptitle('Linearized and normalized SRF')
    
    plt.subplots_adjust(#left = 0.1,  # the left side of the subplots of the figure
                        right = 0.8,   # the right side of the subplots of the figure
                        #bottom = 0.1,  # the bottom of the subplots of the figure
                        top = 0.925,     # the top of the subplots of the figure
                        #wspace = 0.2,  # the amount of width reserved for space between subplots,
                                       # expressed as a fraction of the average axis width
                        #hspace = 0.2  # the amount of height reserved for space between subplots,
                                      # expressed as a fraction of the average axis height
                        )
    
    for i, channel in enumerate(mwi.channels_str):
        
        # MWI-RX183_DSB_Matlab.xlsx dataset
        axes[i].plot(sen_dsb.data_lino['frequency [GHz]'], sen_dsb.data_lino['ch'+channel+' sensitivity']*100, color='k', linewidth=1,
                     zorder=2)
        
        # y axis settings
        axes[i].set_yticks([0, 0.5])
        axes[i].set_ylim([0, 0.85])
                
        # set x-limit
        axes[i].set_xlim([np.min(mwi.freq_bw)-0.1, np.max(mwi.freq_bw)+0.1])
        
        # annotate channel name
        axes[i].annotate(text=mwi.freq_txt[i], xy=(1.01, 0.5), xycoords='axes fraction', backgroundcolor="None",
                         annotation_clip=False, horizontalalignment='left', verticalalignment='center')
        
        # add vertical lines
        axes[i].axvline(x=mwi.absorpt_line, color='red', linewidth=0.5, zorder=0)  # mark line center
        
        for j in range(2):  # mark left/right channel frequency
            axes[i].axvline(x=mwi.freq_center[i, j], color='gray', linestyle='--', linewidth=0.75, zorder=0)
        
        for j in range(4):  # mark each bandwidth edge
            axes[i].axvline(x=mwi.freq_bw[i, j], color='gray', linestyle=':', linewidth=0.75, zorder=0)
        
        # add shade for each channel
        axes[i].axvspan(xmin=mwi.freq_bw[i, 0], xmax=mwi.freq_bw[i, 1], ymin=-10e3, ymax=10e3, color='gray',
                        alpha=0.2)
        axes[i].axvspan(xmin=mwi.freq_bw[i, 2], xmax=mwi.freq_bw[i, 3], ymin=-10e3, ymax=10e3, color='gray',
                        alpha=0.2)

        # add grid
        axes[i].grid(zorder=-1)

    # set axis labels
    axes[2].set_ylabel('Sensitivity [%]')
    axes[-1].set_xlabel('Frequency [GHz]')
        
    plt.savefig(path_plot + 'bandpass_measurement/bandpass_measurement_dsb_lino.png', dpi=300)
    
    #%% PROOF plot sensitivity data (lino, dsb, lin scale) with a perturbation
    fig, axes = plt.subplots(5, 1, sharex='all', figsize=(6, 6))
    axes = axes.flatten(order='F')
    
    fig.suptitle('Linearized and normalized SRF')
    
    plt.subplots_adjust(#left = 0.1,  # the left side of the subplots of the figure
                        right = 0.8,   # the right side of the subplots of the figure
                        #bottom = 0.1,  # the bottom of the subplots of the figure
                        top = 0.925,     # the top of the subplots of the figure
                        #wspace = 0.2,  # the amount of width reserved for space between subplots,
                                       # expressed as a fraction of the average axis width
                        #hspace = 0.2  # the amount of height reserved for space between subplots,
                                      # expressed as a fraction of the average axis height
                        )
    
    for i, channel in enumerate(mwi.channels_str):
        
        # with noise
        axes[i].plot(sen_dsb_pert_df['frequency [GHz]'], sen_dsb_pert_df['ch'+channel+' sensitivity']*100, color='#12A2FF', linewidth=0.75,
                     zorder=1, label='perturbed SRF')
        
        # MWI-RX183_DSB_Matlab.xlsx dataset
        axes[i].plot(sen_dsb.data_lino['frequency [GHz]'], sen_dsb.data_lino['ch'+channel+' sensitivity']*100, color='k', linewidth=1,
                     zorder=2, label='SRF')
        
        # y axis settings
        axes[i].set_yticks([0, 0.5])
        axes[i].set_ylim([0, 0.85])
                
        # set x-limit
        axes[i].set_xlim([np.min(mwi.freq_bw)-0.1, np.max(mwi.freq_bw)+0.1])
        
        # annotate channel name
        axes[i].annotate(text=mwi.freq_txt[i], xy=(1.01, 0.5), xycoords='axes fraction', backgroundcolor="None",
                         annotation_clip=False, horizontalalignment='left', verticalalignment='center')
        
        # add vertical lines
        axes[i].axvline(x=mwi.absorpt_line, color='red', linewidth=0.5, zorder=0)  # mark line center
        
        for j in range(2):  # mark left/right channel frequency
            axes[i].axvline(x=mwi.freq_center[i, j], color='gray', linestyle='--', linewidth=0.75, zorder=0)
        
        for j in range(4):  # mark each bandwidth edge
            axes[i].axvline(x=mwi.freq_bw[i, j], color='gray', linestyle=':', linewidth=0.75, zorder=0)
        
        # add shade for each channel
        axes[i].axvspan(xmin=mwi.freq_bw[i, 0], xmax=mwi.freq_bw[i, 1], ymin=-10e3, ymax=10e3, color='gray',
                        alpha=0.2)
        axes[i].axvspan(xmin=mwi.freq_bw[i, 2], xmax=mwi.freq_bw[i, 3], ymin=-10e3, ymax=10e3, color='gray',
                        alpha=0.2)

        # add grid
        axes[i].grid(zorder=-1)
    
    # add legend below
    axes[-1].legend(bbox_to_anchor=(0.97, -0.2), ncol=1, loc='upper left', frameon=True, fontsize=8)

    # set axis labels
    axes[2].set_ylabel('Sensitivity [%]')
    axes[-1].set_xlabel('Frequency [GHz]')
        
    plt.savefig(path_plot + 'bandpass_measurement/bandpass_measurement_dsb_lino_noise.png', dpi=300)

    #%% PROOF plot all linearized SRF with reduction of measurement points
    pd.options.mode.chained_assignment = None 
    reduction_levels = np.arange(1, 6, 1)
    
    n_orig = 1060
    reduction_levels = np.arange(1, 6)  # how it was specified in delta_tb.nc
    number_meas = np.floor(n_orig/reduction_levels)
    sample_width =  191.302 - 175.322
    x = sample_width/number_meas*1000
    x = [int(a) for a in x]
    
    colors = cm.get_cmap('viridis', len(reduction_levels)).colors
    
    fig, axes = plt.subplots(5, 1, sharex='all', figsize=(6, 6))
    axes = axes.flatten(order='F')
    
    fig.suptitle('Data reduction of SRF (not normalized)')
    
    plt.subplots_adjust(#left = 0.1,  # the left side of the subplots of the figure
                        right = 0.8,   # the right side of the subplots of the figure
                        bottom = 0.25,  # the bottom of the subplots of the figure
                        top = 0.925,     # the top of the subplots of the figure
                        #wspace = 0.2,  # the amount of width reserved for space between subplots,
                                       # expressed as a fraction of the average axis width
                        #hspace = 0.2  # the amount of height reserved for space between subplots,
                                      # expressed as a fraction of the average axis height
                        )
    
    for i, channel in enumerate(mwi.channels_str):
        
        # MWI-RX183_DSB_Matlab.xlsx dataset
        for j, reduction_level in enumerate(reduction_levels):
            
            srf_red = sen_dsb.data_lino.iloc[::reduction_level, :]
            #srf_values = srf_red.iloc[:, 1:].values.copy()
            #srf_red.iloc[:, 1:] = Sensitivity.normalize_srf(srf_values)
            
            axes[i].plot(srf_red['frequency [GHz]'], srf_red['ch'+channel+' sensitivity']*100, color=colors[j], linewidth=1,
                         zorder=2, label=x[j])
        
        # y axis settings
        axes[i].set_yticks([0, 0.5])
        axes[i].set_ylim([0, 0.85])
                
        # set x-limit
        axes[i].set_xlim([np.min(mwi.freq_bw)-0.1, np.max(mwi.freq_bw)+0.1])
        
        # annotate channel name
        axes[i].annotate(text=mwi.freq_txt[i], xy=(1.01, 0.5), xycoords='axes fraction', backgroundcolor="None",
                         annotation_clip=False, horizontalalignment='left', verticalalignment='center')
        
        # add vertical lines
        axes[i].axvline(x=mwi.absorpt_line, color='red', linewidth=0.5, zorder=0)  # mark line center
        
        for j in range(2):  # mark left/right channel frequency
            axes[i].axvline(x=mwi.freq_center[i, j], color='gray', linestyle='--', linewidth=0.75, zorder=0)
        
        for j in range(4):  # mark each bandwidth edge
            axes[i].axvline(x=mwi.freq_bw[i, j], color='gray', linestyle=':', linewidth=0.75, zorder=0)
        
        # add shade for each channel
        axes[i].axvspan(xmin=mwi.freq_bw[i, 0], xmax=mwi.freq_bw[i, 1], ymin=-10e3, ymax=10e3, color='gray',
                        alpha=0.2)
        axes[i].axvspan(xmin=mwi.freq_bw[i, 2], xmax=mwi.freq_bw[i, 3], ymin=-10e3, ymax=10e3, color='gray',
                        alpha=0.2)

        # add grid
        axes[i].grid(zorder=-1)
    
    # add legend below
    axes[-1].legend(bbox_to_anchor=(0.5, -1), ncol=5, loc='upper center', frameon=True, fontsize=8, title='Sampling interval [MHz]')

    # set axis labels
    axes[2].set_ylabel('Sensitivity')
    axes[-1].set_xlabel('Frequency [GHz]')
        
    plt.savefig(path_plot + 'bandpass_measurement/bandpass_measurement_dsb_lino_data_reduction.png', dpi=300)
