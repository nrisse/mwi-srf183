"""
Read spectral responds function from excel files to xarray Dataset
"""


import numpy as np
import pandas as pd
import xarray as xr
import os
import sys
sys.path.append(f'{os.environ["PATH_PHD"]}/projects/mwi_bandpass_effects/scripts')
from path_setter import path_data
from mwi_info import mwi


class Sensitivity:
    
    files = ['MWI-RX183_DSB_Matlab.xlsx', 'MWI-RX183_Matlab.xlsx']
    
    def __init__(self, filename='MWI-RX183_DSB_Matlab.xlsx'):
        """
        Read sensitivity data and prepare (linearize and normalize)
        """
        
        self.data = self.get_data(filename)

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
        Normalize linear spectral response function to a sum along each 
        column of 1
        number of rows:    number of frequencies
        number of columns: number of channel
        """
        
        values_norm = values_lin / values_lin.sum(axis=0, keepdims=True)
        
        return values_norm
        
    def get_data(self, filename):
        """
        Read sensitivity measurement from excel file
        """
        
        # read data from excel sheet
        file = path_data + 'sensitivity/' + filename
        data_ch14 = pd.read_excel(file, sheet_name='Ch14', usecols=[0, 1],
                                  names=['frequency [GHz]', 'sensitivity [dB]'], 
                                  header=None)
        data_ch15 = pd.read_excel(file, sheet_name='Ch15', usecols=[0, 1],
                                  names=['frequency [GHz]', 'sensitivity [dB]'],
                                  header=None)
        data_ch16 = pd.read_excel(file, sheet_name='Ch16', usecols=[0, 1],
                                  names=['frequency [GHz]', 'sensitivity [dB]'], 
                                  header=None)
        data_ch17 = pd.read_excel(file, sheet_name='Ch17', usecols=[0, 1],
                                  names=['frequency [GHz]', 'sensitivity [dB]'],
                                  header=None)
        data_ch18 = pd.read_excel(file, sheet_name='Ch18', usecols=[0, 1],
                                  names=['frequency [GHz]', 'sensitivity [dB]'],
                                  header=None)
        
        # check if frequencies are the same
        assert np.sum(data_ch14.iloc[:, 0] != data_ch15.iloc[:, 0]) == 0
        assert np.sum(data_ch14.iloc[:, 0] != data_ch16.iloc[:, 0]) == 0
        assert np.sum(data_ch14.iloc[:, 0] != data_ch17.iloc[:, 0]) == 0
        assert np.sum(data_ch14.iloc[:, 0] != data_ch18.iloc[:, 0]) == 0
        
        # combine data to numpy array
        sens_data = np.array([data_ch14.iloc[:, 1],
                              data_ch15.iloc[:, 1],
                              data_ch16.iloc[:, 1],
                              data_ch17.iloc[:, 1],
                              data_ch18.iloc[:, 1]
                              ]).T
        
        # linearized and normalized
        sens_data_lino = self.normalize_srf(
            values_lin=self.linearize_srf(sens_data))
        
        # write data to xarray
        data = xr.Dataset(
            data_vars=dict(raw=(('frequency', 'channel'), 
                                sens_data, 
                                dict(units='dB')),
                           lino=(('frequency', 'channel'), 
                                 sens_data_lino,
                                 dict(unit='-')),
                           ),
            coords=dict(frequency=(('frequency'),
                                   (data_ch14.iloc[:, 0].values*1e3).astype(
                                       'int'), 
                                   dict(unit='MHz')),
                        channel=(('channel'), 
                                 mwi.channels_int, 
                                 dict(unit='-'))),
            attrs=dict(source='European Space Agency',
                       file=file,
                       comment='Spectral response function of MWI channels')
                          )
        
        return data


if __name__ == '__main__':
    
    sen1 = Sensitivity(filename=Sensitivity.files[0]).data
    sen2 = Sensitivity(filename=Sensitivity.files[1]).data
    
    # calculate sen2 from sen1
    # sen2 is the combination between the left and right of the double side band measurement DSB
    # both sides are nearly weighted the same (average), but one side can also be weighted more then the other side
    # here: mirror sen1 at channel center and average
    freq_center = 183312
    
    # divide DSB dataset in left and right and reverse left side (both aligned towards line wing)
    sen1_left = sen1.lino.sel(frequency=(sen1.frequency < freq_center)).sortby('frequency', ascending=False)
    sen1_right = sen1.lino.sel(frequency=(sen1.frequency > freq_center))
    
    # check if frequencies match exactly
    assert (freq_center - sen1_left.frequency.values == sen1_right.frequency.values - freq_center).all()
    
    # add both sides and normalize to a sum of 1
    sen1_comb = sen1_left.values + sen1_right.values
    sen1_comb = Sensitivity.normalize_srf(sen1_comb)  # normalize to 1
        
    # write to dataset with the calculated and measured values
    sen2_cal = xr.DataArray(sen1_comb, dims=('frequency', 'channel'), coords=dict(frequency=sen1_right.frequency,
                                                                                  channel=mwi.channels_int))
    
    # caution: DSB and other dataset not at exactly same frequency!
    # solution: linearly interpolate calculated sen2 on sen2 frequencies and calculate difference
    from scipy.interpolate import interp1d as interpolate
    
    f_min = np.min(sen2_cal.frequency.values)
    f_max = np.max(sen2_cal.frequency.values)
    freqs_target = sen2.frequency.sel(frequency=((f_min < sen2.frequency) & (sen2.frequency < f_max))).values
    
    sen2_interp = np.zeros(shape=(len(freqs_target), len(mwi.channels_int)))
    for i, channel in enumerate(mwi.channels_int):
        f = interpolate(x=sen2_cal.frequency.values, 
                        y=sen2_cal.sel(channel=channel).values)
        
        sen2_interp[:, i] = f(freqs_target)
    
    # combine measurement and calculation in dataset
    sen2_compare = xr.Dataset()
    sen2_compare.coords['frequency'] = (('frequency'), freqs_target)
    sen2_compare.coords['channel'] = (('channel'), mwi.channels_int)
    sen2_compare['measured'] = (('frequency', 'channel'), Sensitivity.normalize_srf(sen2.lino.sel(frequency=freqs_target).values))
    sen2_compare['calculated'] = (('frequency', 'channel'), Sensitivity.normalize_srf(sen2_interp))
    diff = sen2_compare['measured'] - sen2_compare['calculated']
    diff_norm = diff/sen2_compare['measured']
    diff_norm_low = diff_norm.values.copy()
    diff_norm_low[np.abs(diff_norm_low)>0.5] = np.nan
    
    # compare with measurement
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors
    
    # linear: just compare two graphs
    fig, axes = plt.subplots(5, 1, figsize=(5, 7), sharex=True, sharey=True)
    for i, ax in enumerate(axes):
        channel = mwi.channels_int[i]
        ax.plot(sen2_compare.frequency*1e-3, sen2_compare.measured.isel(channel=i), marker='o', markersize=2, label='measured')
        ax.plot(sen2_compare.frequency*1e-3, sen2_compare.calculated.isel(channel=i), marker='o', markersize=2, label='calculated from DSB')
    axes[0].legend()
    axes[-1].set_xlabel('Frequency [GHz]')
    axes[2].set_ylabel('Sensitivity')
    fig.tight_layout()
    
    # logarithmic: just compare two graphs
    fig, axes = plt.subplots(5, 1, figsize=(5, 7), sharex=True, sharey=True)
    for i, ax in enumerate(axes):
        channel = mwi.channels_int[i]
        ax.plot(sen2_compare.frequency*1e-3, 10*np.log10(sen2_compare.measured.isel(channel=i)), marker='o', markersize=2, label='measured')
        ax.plot(sen2_compare.frequency*1e-3, 10*np.log10(sen2_compare.calculated.isel(channel=i)), marker='o', markersize=2, label='calculated from DSB')
    axes[0].legend()
    axes[-1].set_xlabel('Frequency [GHz]')
    axes[2].set_ylabel('Sensitivity')
    fig.tight_layout()
    
    # plot differences
    fig, axes = plt.subplots(5, 1, figsize=(5, 7), sharex=True, sharey=True)
    for i, ax in enumerate(axes):
        channel = mwi.channels_int[i]
        ax.plot(sen2_compare.frequency*1e-3, diff.isel(channel=i), marker='o', markersize=2)
    axes[-1].set_xlabel('Frequency [GHz]')
    axes[2].set_ylabel('Sensitivity: meas - calc(DSB)')
    fig.tight_layout()
    
    # absolute differences in log
    fig, axes = plt.subplots(5, 1, figsize=(5, 7), sharex=True, sharey=True)
    for i, ax in enumerate(axes):
        channel = mwi.channels_int[i]
        ax.plot(sen2_compare.frequency*1e-3, 10*np.log10(np.abs(diff.isel(channel=i))), marker='o', markersize=2)
    axes[-1].set_xlabel('Frequency [GHz]')
    axes[2].set_ylabel('Sensitivity: meas - calc(DSB) [dB]')
    fig.tight_layout()

    fig, axes = plt.subplots(5, 1, figsize=(5, 7), sharex=True, sharey=True)
    for i, ax in enumerate(axes):
        channel = mwi.channels_int[i]
        ax.plot(sen2_compare.frequency*1e-3, diff_norm.isel(channel=i), marker='o', markersize=2)
    axes[-1].set_xlabel('Frequency [GHz]')
    axes[2].set_ylabel('Sensitivity: [meas - calc(DSB)]/meas')
    axes[0].set_ylim([-1, 1])
    fig.tight_layout()
    
    fig, axes = plt.subplots(5, 1, figsize=(5, 7), sharex=True, sharey=True)
    for i, ax in enumerate(axes):
        channel = mwi.channels_int[i]
        ax.plot(sen2_compare.frequency*1e-3, diff_norm_low[:, i], marker='o', markersize=2)
    axes[-1].set_xlabel('Frequency [GHz]')
    axes[2].set_ylabel('Sensitivity: [meas - calc(DSB)]/meas')
    axes[0].set_ylim([-1, 1])
    fig.tight_layout()
    
    # comment: looking at the difference between measured and calculated:
    # difference seems to be correlated between channels in overlapping frequencies
    # i.e. channels 14 and 15, 15 and 16
    
    def correlation(a):
            
        df = pd.DataFrame(a)        
        corr = df.corr()
        
        return corr
    
    corr_name = ['meas - calc(DSB)', '[meas - calc(DSB)]/meas', '[meas - calc(DSB)]/meas\noutliers removed (abs > 0.5)']
    corrs = np.zeros(shape=(5, 5, 3))
    for i, a in enumerate([diff.values, diff_norm.values, diff_norm_low]):
        corrs[:, :, i] = correlation(a)
    
    fig, axes = plt.subplots(1, 3, figsize=(8, 4))
    fig.suptitle('Correlation patterns of differences')
    norm = mcolors.TwoSlopeNorm(vmin=-1, vcenter=0, vmax=1)
    
    for i, ax in enumerate(axes):
        im = ax.pcolormesh(mwi.channels_int, mwi.channels_int, corrs[:, :, i], cmap='RdBu_r', shading='nearest', norm=norm)
        ax.set_title(corr_name[i])
        
        for (i, j), z in np.ndenumerate(corrs[:, :, i]):
            ax.annotate(text='{:0.1f}'.format(np.round(z,1)), xy=(14+j, 14+i), xycoords='data', ha='center', va='center',
                        color='gray')
    
    cax = fig.add_axes([0.3, 0.1, 0.4, 0.02])
    fig.colorbar(im, cax=cax, orientation='horizontal')
    
    fig.tight_layout()
    plt.subplots_adjust(bottom=0.2)
    
    # scatterplots
    fig, axes = plt.subplots(5, 5, sharex=True, sharey=True)
    for (i, j), ax in np.ndenumerate(axes):
        ax.scatter(diff_norm.isel(channel=i), diff_norm.isel(channel=j), s=2, c='k', alpha=0.5)
    ax.set_xlim([-0.5, 0.5])
    ax.set_ylim([-0.5, 0.5])
    
    # comment: generate some mocing average errors
    # std dev depends on absolute value(!)
    