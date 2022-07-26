from __future__ import division
import sys
import numpy as np
from netCDF4 import Dataset
import os
import pandas as pd
from glob import glob
import datetime
from readERA5 import readERA5press

os.environ['OPENBLAS_NUM_THREADS'] = "1"
os.environ['PAMTRA_DATADIR'] = ""

sys.path.append('/home/mech/lib/python/')

import pyPamtra


def run_pamtra(freqs, pam):
    """
    Run Pamtra and calculate brightness temperature

    Pamtra output
    ['gridx', 'gridy', 'outlevels', 'angles', 'frequency', 'passive_npol']
    (1, 1, 2, 32, 1, 2)

    observation height: 833000, 0 (pam.p['obs_height'])
    angles: index0; 180deg (nadir upwelling), index31; 0deg (zenith downwelling)
    passive_npol: 'V' and 'H'
    """
    
    # turn active off
    pam.nmlSet['active'] = False

    # run pamtra (parallel: 10 freq per prozessor)
    pam.runParallelPamtra(freqs, pp_deltaX=1, pp_deltaY=1, pp_deltaF=10, pp_local_workers="auto")

    # mean over both polarizations
    TB_mod = pam.r['tb'][0, 0, 0, 0, :, 0]  # only vertical polarization, height 833 km

    return TB_mod


def run_pamtra_grid(freqs, pam):
    """
    Run Pamtra and calculate brightness temperature

    Pamtra output
    ['gridx', 'gridy', 'outlevels', 'angles', 'frequency', 'passive_npol']
    (1, 1, 2, 32, 1, 2)

    observation height: 833000, 0 (pam.p['obs_height'])
    angles: index0; 180deg (nadir upwelling), index31; 0deg (zenith downwelling)
    passive_npol: 'V' and 'H'
    """
    
    # turn active off
    pam.nmlSet['active'] = False

    # run pamtra (parallel: 10 freq per prozessor)
    pam.runParallelPamtra(freqs, pp_deltaX=1, pp_deltaY=1, pp_deltaF=10, pp_local_workers="auto")

    # mean over both polarizations (output all angles)
    TB_mod = pam.r['tb'][:, :, 0, :, :, 0]  # only vertical polarization, height 833 km

    return TB_mod


def calculate_iwv(pam):
    """
    Calculate integrated water vapor content from era5 data
    """
    
    # calculate iwv
    pam.addIntegratedValues()
    iwv = pam.p['iwv']
    
    return iwv


def calculate_integrated_hydrometeors(pam):
    """
    Calculate integrated hydrometeors from era5 data
    """
    
    hydro = pam.p['hydro_wp'][:,:,0:4]  #[xx,yy,ihyd]
    return hydro


def main_point():
    """
    Main routine calculating TB and IWV of ERA5 profiles
    """
    
    # read frequencies
    freqs_pamtra = np.loadtxt('/home/nrisse/WHK/eumetsat/data/frequencies.txt')
    
    # save iwv and integrated hydrometeors
    iwv_df = pd.DataFrame(index=['iwv'])
    ihyd_df = pd.DataFrame(index=['cloud', 'ice', 'rain', 'snow'])  # same order as in descriptor file
    
    base_dir_out = '/home/nrisse/WHK/eumetsat/data/brightness_temperature/era5/'
    base_dir_out_iwv = '/home/nrisse/WHK/eumetsat/data/iwv/'
    
    # era5 setting
    date = '20150331_1200'
    
    grids = {'arctic': [67, 68, 314, 315],     # Arctic at 73.25 deg N 11.5 deg W
             'mid_lat': [152, 153, 184, 185],  # MidLat at 52 deg N 44 deg W 
             'tropics': [351, 352, 344, 345],  # Tropical 2.25 deg N 4 deg E
             }
    
    hydro_state = {'hydro_on': False,
                   'hydro_off': True,
                   }
    
    for loc in list(grids.keys()):
        
        for hyd in list(hydro_state.keys()):
            
            print('Simulating {} atmosphere (hydro: {}) from date: {}'.format(loc, hyd, date))
            
            # create pamtra object of ERA5 profile
            pam = readERA5press(fname2d='/work/mech/data/era5-single-levels_'+date+'.nc', 
                                fname3d='/work/mech/data/era5-pressure-levels_'+date+'.nc', 
                                descriptorFile='/home/mech/workspace/pamtra/descriptorfiles/descriptor_file_ecmwf.txt', 
                                timeidx=None, 
                                debug=False, 
                                verbosity=0, 
                                grid=grids[loc], 
                                rmHyds=hydro_state[hyd])
            
            # model always a selection of frequencies
            n_split = 5  # number of splits of whole frequency array
            f_arr = np.array([])  # current frequencies
            tb_arr = np.array([])  # resulting TB from Pamtra
            
            for i_split in range(0, n_split):
                
                print('Simulating section of frequency range: {}/{}'.format(i_split+1, n_split))
                
                # divide freqs into smaller arrays and get the current subsection
                f = np.array_split(freqs_pamtra, n_split)[i_split]
                
                # run pamtra
                tb = run_pamtra(freqs=f, pam=pam)
                
                tb_arr = np.append(tb_arr, tb)
                f_arr = np.append(f_arr, f)
            
            # create pandas data frame of result
            data = pd.DataFrame(columns=['Frequency [GHz]', 'TB'], data=np.array([f_arr, tb_arr]).T)
            
            # write result of profile to file
            header = '# Date: {}, Location: {}, Hydrometeor setting: {}\n'.format(date, loc, hyd)
            
            path_structure = date[:4]+'/'+date[4:6]+'/'+date[6:8]+'/'  # YYYY/MM/DD/
            folder = base_dir_out + path_structure
            
            if not os.path.exists(folder):
                os.makedirs(folder)
            
            file = 'TB_PAMTRA_ERA5_' + loc + '_' + hyd + '.txt'
            
            print('Writing file: {}'.format(folder+file))
            
            with open(folder+file, 'w') as f:
                f.write(header)
                data.to_csv(f, index=False)
                
            # calculate iwv and save to file           
            colname = date + '_' + loc + '_' + hyd
            iwv_df.loc['iwv', colname] = calculate_iwv(pam)
            
            # calculate integrated hydrometeord and save to file
            ihyd_df.loc[:, colname] = calculate_integrated_hydrometeors(pam).flatten()
        
        # iwv to file
        outfile = '/home/nrisse/WHK/eumetsat/data/iwv/iwv_pamtra_era5.txt'
        with open(outfile, 'w') as f:
            f.write('# Integrated water vapor calculated with PAMTRA (kg/m**2)\n')
            iwv_df.to_csv(f)
            
        # ihyd to file
        outfile = '/home/nrisse/WHK/eumetsat/data/integrated_hydrometeors/ihyd_pamtra_era5.txt'
        with open(outfile, 'w') as f:
            f.write('# Integrated hydrometeors calculated with PAMTRA (kg/m**2)\n')
            ihyd_df.to_csv(f)


def main_grid():
    """
    Main routine calculating TB and IWV of ERA5 profiles
    Here: choose an area for a single day
    """
    
    # read frequencies
    freqs_pamtra = np.loadtxt('/home/nrisse/WHK/eumetsat/data/frequencies.txt')
    
    # NOW WITH RM HYD
        
    # filenames
    dir_tb = '/home/nrisse/WHK/eumetsat/data/brightness_temperature/era5/'
    dir_iwv = '/home/nrisse/WHK/eumetsat/data/iwv/'
    dir_hydro = '/home/nrisse/WHK/eumetsat/data/integrated_hydrometeors/'
    
    filename_tb = 'TB_PAMTRA_ERA5_all_angles_rmHyd.nc'
    filename_iwv = 'IWV_PAMTRA_ERA5_rmHyd.nc'
    filename_hydro = 'HYDRO_PAMTRA_ERA5_rmHyd.nc'
    
    # era5 setting
    date = '20150331_1200'
    grid = [141, 180, 181, 200]
    
    # create pamtra object of ERA5 profile
    pam = readERA5press(fname2d='/work/mech/data/era5-single-levels_'+date+'.nc', 
                        fname3d='/work/mech/data/era5-pressure-levels_'+date+'.nc', 
                        descriptorFile='/home/mech/workspace/pamtra/descriptorfiles/descriptor_file_ecmwf.txt', 
                        timeidx=None, 
                        debug=False, 
                        verbosity=0, 
                        grid=grid, 
                        rmHyds=True)
    
    # model always a selection of frequencies
    n_split = 25  # number of splits of whole frequency array
    n_angles = 32
    tb = np.zeros(shape=(len(pam.p['lon'][:, 0]), len(pam.p['lat'][0, :]), n_angles, len(freqs_pamtra)))  # resulting TB from Pamtra
    
    j = 0
    for i_split in range(0, n_split):
        
        print('Simulating section of frequency range: {}/{}'.format(i_split+1, n_split))
        
        # divide freqs into smaller arrays and get the current subsection
        f = np.array_split(freqs_pamtra, n_split)[i_split]
        
        i = j
        j += len(f)
        
        # run pamtra
        tb[:, :, :, i:j] = run_pamtra_grid(freqs=f, pam=pam)
    
    # calculate integrated values
    iwv = calculate_iwv(pam)
    hydro = calculate_integrated_hydrometeors(pam)
    
    # write to file
    path_tb = dir_tb + date[:4]+'/'+date[4:6]+'/'+date[6:8]+'/'  # YYYY/MM/DD/
    if not os.path.exists(path_tb):
        os.makedirs(path_tb)
        
    f_tb = path_tb+filename_tb
    f_iwv = dir_iwv+filename_iwv
    f_hydro = dir_hydro+filename_hydro
    
    with Dataset(f_tb, 'w', format='NETCDF4') as rootgrp:
        
        # global attributes
        rootgrp.author = "Nils Risse"
        rootgrp.history = "created: {}".format(datetime.datetime.now().date().strftime('%Y-%m-%d'))
        
        # create dimension
        rootgrp.createDimension(dimname='lon', size=tb.shape[0])
        rootgrp.createDimension(dimname='lat', size=tb.shape[1])
        rootgrp.createDimension(dimname='angle', size=tb.shape[2])
        rootgrp.createDimension(dimname='frequency', size=tb.shape[3])
        
        # write variables
        var_lon = rootgrp.createVariable(varname='lon', datatype='f', dimensions=('lon',))
        var_lon[:] = pam.p['lon'][:, 0]
        
        var_lat = rootgrp.createVariable(varname='lat', datatype='f', dimensions=('lat',))
        var_lat[:] = pam.p['lat'][0, :]
        
        var_angle = rootgrp.createVariable(varname='angle', datatype='f', dimensions=('angle',))
        var_angle[:] = pam.r['angles_deg']
        
        var_frequency = rootgrp.createVariable(varname='frequency', datatype='f', dimensions=('frequency',))
        var_frequency[:] = freqs_pamtra
        
        var_tb = rootgrp.createVariable(varname='tb', datatype='f', dimensions=('lon', 'lat', 'angle', 'frequency',))
        var_tb[:] = tb
    
    with Dataset(f_iwv, 'w', format='NETCDF4') as rootgrp:
        
        # global attributes
        rootgrp.author = "Nils Risse"
        rootgrp.history = "created: {}".format(datetime.datetime.now().date().strftime('%Y-%m-%d'))
        
        # create dimension
        rootgrp.createDimension(dimname='lon', size=tb.shape[0])
        rootgrp.createDimension(dimname='lat', size=tb.shape[1])
        
        # write variables
        var_lon = rootgrp.createVariable(varname='lon', datatype='f', dimensions=('lon',))
        var_lon[:] = pam.p['lon'][:, 0]
        
        var_lat = rootgrp.createVariable(varname='lat', datatype='f', dimensions=('lat',))
        var_lat[:] = pam.p['lat'][0, :]
        
        var_iwv = rootgrp.createVariable(varname='iwv', datatype='f', dimensions=('lon', 'lat',))
        var_iwv[:] = iwv
    
    with Dataset(f_hydro, 'w', format='NETCDF4') as rootgrp:
        
        # global attributes
        rootgrp.author = "Nils Risse"
        rootgrp.history = "created: {}".format(datetime.datetime.now().date().strftime('%Y-%m-%d'))
        
        # create dimension
        rootgrp.createDimension(dimname='lon', size=tb.shape[0])
        rootgrp.createDimension(dimname='lat', size=tb.shape[1])
        rootgrp.createDimension(dimname='class', size=hydro.shape[2])
        
        # write variables
        var_lon = rootgrp.createVariable(varname='lon', datatype='f', dimensions=('lon',))
        var_lon[:] = pam.p['lon'][:, 0]
        
        var_lat = rootgrp.createVariable(varname='lat', datatype='f', dimensions=('lat',))
        var_lat[:] = pam.p['lat'][0, :]
        
        var_hclass = rootgrp.createVariable(varname='hydrometeor_class', datatype='f', dimensions=('class',))
        var_hclass.names = '0: cloud, 1: ice, 2: rain, 3: snow'
        var_hclass[:] = np.array([0, 1, 2, 3])
        
        var_hydro = rootgrp.createVariable(varname='ihydro', datatype='f', dimensions=('lon', 'lat', 'class',))
        var_hydro[:] = hydro



if __name__ == '__main__':

    main_grid()
    