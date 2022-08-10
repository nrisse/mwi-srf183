

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import xarray as xr
from string import ascii_lowercase as abc
import os
import sys
sys.path.append(f'{os.environ["PATH_PHD"]}/projects/mwi_bandpass_effects/scripts')
from mwi_info import mwi
from radiosonde import wyo
from path_setter import path_plot, path_data


plt.ion()


if __name__ == '__main__':
    
    # read data
    ds_com_rsd = xr.open_dataset(
        path_data+'brightness_temperature/TB_radiosondes_2019_MWI.nc')
    
    #%% calculate cumulative TB mwi for tophat and for orig srf
    ds_com_rsd['tb_mwi_cum_orig'] = (ds_com_rsd.srf_orig * ds_com_rsd['tb'].isel(angle=9)).cumsum('frequency')
    ds_com_rsd['tb_mwi_cum_est'] = (ds_com_rsd.srf_est * ds_com_rsd['tb'].isel(angle=9)).cumsum('frequency')
    
    #%% plot together
    fig, ax = plt.subplots(1, 1, figsize=(6, 4))
    
    ax.plot(ds_com_rsd.frequency*1e-3,
            ds_com_rsd.tb.isel(angle=9, profile=0))
    
    ax.plot(ds_com_rsd.frequency*1e-3,
            ds_com_rsd.tb_mwi_cum_orig.sel(channel=17, 
                                           profile='ID_01004_201901011200'),
            marker='.')
    
    ax.plot(ds_com_rsd.frequency*1e-3,
            ds_com_rsd.tb_mwi_cum_est.sel(channel=17, 
                                          profile='ID_01004_201901011200',
                                          est_type='tophat'),
            marker='.')