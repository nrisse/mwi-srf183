from __future__ import division
import sys
import numpy as np
import os
import pandas as pd
from glob import glob
from netCDF4 import Dataset
import datetime

os.environ['OPENBLAS_NUM_THREADS'] = "1"
os.environ['PAMTRA_DATADIR'] = ""

sys.path.append('/home/mech/lib/python/')

import pyPamtra


def run_pamtra(freqs, atmosphere='standard'):
    """
    Run Pamtra and calculate brightness temperature

    Pamtra output
    ['gridx', 'gridy', 'outlevels', 'angles', 'frequency', 'passive_npol']
    (1, 1, 2, 32, 1, 2)

    observation height: 833000, 0 (pam.p['obs_height'])
    angles: index0; 180deg (nadir upwelling), index31; 0deg (zenith downwelling)
    passive_npol: 'V' and 'H'
    """

    pam = pyPamtra.pyPamtra()
    
    # todo: specifiy six profiles
    # add atleast one hydrometeor
    pam.df.addHydrometeor(("ice", -99., -1, 917., 130., 3.0, 0.684, 2., 3, 1, 
                           "mono_cosmo_ice", -99., -99., -99., -99., -99., -99., 
                           "mie-sphere", "heymsfield10_particles", 0.0))
    
    if atmosphere == 'standard':
        
        # fill atmoshere based on standard atmosphere
        heights = np.logspace(np.log10(0.1), np.log10(33000), 200, base=10)
        pam = pyPamtra.importer.createUsStandardProfile(pam=pam, hgt_lev=heights)
        
    else:
        
        # read atmosphere from txt file (downloaded and formatted from http://weather.uwyo.edu/upperair/sounding.html)
        #rs = np.loadtxt(atmosphere, usecols=[0, 1, 2, 4])  # pres [hPa], hght [m], temp [C], relh [%]
        #rs[:, 2] += 273.15  # temp from C to K
        #rs[:, 0] = rs[:, 0] * 100  # press from hPa to Pa
        
        rs = pd.read_csv(atmosphere, comment='#')
        rs.drop(rs[rs['z [m]'] < 0].index , inplace=True)  # remove entries with negative height
        rs.dropna(axis='index', subset=['p [hPa]', 'z [m]', 'T [C]', 'RH [%]'], inplace=True)
        
        # write profile to dictionary
        pamData = dict()
        pamData["press"] = rs['p [hPa]'] * 100
        pamData["hgt"] = rs['z [m]']
        pamData["temp"] = rs['T [C]'] + 273.15
        pamData["relhum"] = rs['RH [%]']
        
        # write profile from dictionary
        pam.createProfile(**pamData)

    # turn active off
    pam.nmlSet['active'] = False

    # run pamtra
    pam.runParallelPamtra(freqs, pp_deltaX=1, pp_deltaY=1, pp_deltaF=1, pp_local_workers="auto")

    # mean over both polarizations
    TB_mod = pam.r['tb'][0, 0, 0, :, :, 0]  # only vertical polarization, height 833 km

    return TB_mod, pam


def calculate_iwv(file):
    """
    Calculate integrated water vapor content from radiosonde profiles
    """
    
    pam = pyPamtra.pyPamtra()
    
    # read radiosonde profile
    rs = pd.read_csv(file, comment='#')
    rs.drop(rs[rs['z [m]'] < 0].index , inplace=True)  # remove entries with negative height
    rs.dropna(axis='index', subset=['p [hPa]', 'z [m]', 'T [C]', 'RH [%]'], inplace=True)
    
    # write profile to dictionary
    pamData = dict()
    pamData["press"] = rs['p [hPa]'] * 100
    pamData["hgt"] = rs['z [m]']
    pamData["temp"] = rs['T [C]'] + 273.15
    pamData["relhum"] = rs['RH [%]']
    
    # write profile from dictionary
    pam.createProfile(**pamData)
    
    # calculate iwv
    pam.addIntegratedValues()
    iwv = pam.p['iwv']
    
    return iwv



def main():

    # todo: reselect atmosphere files and adapt read function above    

    outfile = '/home/nrisse/WHK/eumetsat/data/mwi_pamtra_tb.txt'
    
    # path of radiosondes or definition of other types of profiles
    atmos_dict = {'arctic_winter': '/home/nrisse/WHK/eumetsat/data/atmosphere/arctic_winter.txt',
                 'arctic_summer': '/home/nrisse/WHK/eumetsat/data/atmosphere/arctic_summer.txt',
                 'central_europe_winter': '/home/nrisse/WHK/eumetsat/data/atmosphere/central_europe_winter.txt',
                 'central_europe_summer': '/home/nrisse/WHK/eumetsat/data/atmosphere/central_europe_summer.txt',
                 'tropics_february': '/home/nrisse/WHK/eumetsat/data/atmosphere/tropics_february.txt',
                 'tropics_august': '/home/nrisse/WHK/eumetsat/data/atmosphere/tropics_august.txt',
                 'standard': 'standard',
                 }
    atmos_names = list(atmos_dict.keys())

    # import frequencies
    freqs_pamtra = np.loadtxt('/home/nrisse/WHK/eumetsat/data/frequencies.txt')
    
    # result matrix: frequency in first column, other columns are profiles
    pam_result = np.full(shape=(len(freqs_pamtra), len(atmos_dict)+1), fill_value=np.nan)
    pam_result[:, 0] = freqs_pamtra
    
    # simulate each of the atmospheric profiles
    for i_atm, atmosphere in enumerate(atmos_names):
        
        print('Simulating with the atmosphere {}/{}: {}'.format(i_atm+1, len(atmos_dict), atmosphere))
    
        # model always a selection of frequencies
        n_split = 10  # number of splits of whole frequency array
        f_arr = np.array([])  # current frequencies
        tb_arr = np.array([])  # resulting TB from Pamtra
        
        for i_split in range(0, n_split):
            
            print('Simulating section of frequency range: {}/{}'.format(i_split+1, n_split))
            
            # divide freqs into smaller arrays and get the current subsection
            f = np.array_split(freqs_pamtra, n_split)[i_split]
        
            # run pamtra
            tb = run_pamtra(freqs=f, atmosphere=atmos_dict[atmosphere])
            
            tb_arr = np.append(tb_arr, tb)
            f_arr = np.append(f_arr, f)
        
        # write result of profile to array
        pam_result[:, i_atm+1] = tb_arr
    
    # write array to file
    header = ','.join(atmos_names)
    np.savetxt(outfile, pam_result, header='frequency_GHz,'+header, delimiter=',', comments='')
    
    
def main_all_data():

    file_out = '/home/nrisse/WHK/eumetsat/data/brightness_temperature/TB_radiosondes_2019.nc'
    
    # read data
    folder_atmos = '/home/nrisse/WHK/eumetsat/data/atmosphere/'
    files = glob(folder_atmos+'2019/*/*/*.txt')
    
    print(files)
    
    profile_names = np.array([x[-25:-4] for x in files])
    
    # read frequencies
    freqs_pamtra = np.loadtxt('/home/nrisse/WHK/eumetsat/data/frequencies.txt')
    
    # resulting tb
    n_angles = 32
    n_profiles = len(profile_names)
    tb = np.zeros(shape=(n_profiles, n_angles, len(freqs_pamtra)))  # resulting TB from Pamtra
    
    n_split = 5
    
    # simulate each of the atmospheric profiles
    for i_atm, atmosphere in enumerate(files):
        
        print('Simulating with the atmosphere {}/{}: {}'.format(i_atm+1, len(files), atmosphere))
        
        j = 0
        
        for i_split in range(0, n_split):
            
            print('Simulating section of frequency range: {}/{}'.format(i_split+1, n_split))
            
            # divide freqs into smaller arrays and get the current subsection
            f = np.array_split(freqs_pamtra, n_split)[i_split]
            
            i = j
            j += len(f)
            
            # run pamtra
            tb[i_atm, :,  i:j], pam = run_pamtra(freqs=f, atmosphere=atmosphere)

    with Dataset(file_out, 'w', format='NETCDF4') as rootgrp:
        
        # global attributes
        rootgrp.author = "Nils Risse"
        rootgrp.history = "created: {}".format(datetime.datetime.now().date().strftime('%Y-%m-%d'))
        
        # create dimension
        rootgrp.createDimension(dimname='profile', size=tb.shape[0])
        rootgrp.createDimension(dimname='angle', size=tb.shape[1])
        rootgrp.createDimension(dimname='frequency', size=tb.shape[2])
        
        # write variables
        var_profile = rootgrp.createVariable(varname='profile', datatype=np.str, dimensions=('profile',))
        var_profile[:] = profile_names
        
        var_angle = rootgrp.createVariable(varname='angle', datatype='f', dimensions=('angle',))
        var_angle[:] = pam.r['angles_deg']
        
        var_frequency = rootgrp.createVariable(varname='frequency', datatype='f', dimensions=('frequency',))
        var_frequency[:] = freqs_pamtra
        
        var_tb = rootgrp.createVariable(varname='tb', datatype='f', dimensions=('profile', 'angle', 'frequency',))
        var_tb[:] = tb


def main_standard_atmosphere():

    base_dir_out = '/home/nrisse/WHK/eumetsat/data/brightness_temperature/'

    # read frequencies
    freqs_pamtra = np.loadtxt('/home/nrisse/WHK/eumetsat/data/frequencies.txt')
    
    # model always a selection of frequencies
    n_split = 6  # number of splits of whole frequency array
    f_arr = np.array([])  # current frequencies
    tb_arr = np.array([])  # resulting TB from Pamtra
    
    for i_split in range(0, n_split):
        
        print('Simulating section of frequency range: {}/{}'.format(i_split+1, n_split))
        
        # divide freqs into smaller arrays and get the current subsection
        f = np.array_split(freqs_pamtra, n_split)[i_split]
        
        # run pamtra
        tb = run_pamtra(freqs=f, atmosphere='standard')
        
        tb_arr = np.append(tb_arr, tb)
        f_arr = np.append(f_arr, f)
    
    # create pandas data frame of result
    data = pd.DataFrame(columns=['Frequency [GHz]', 'TB'], data=np.array([f_arr, tb_arr]).T)
    
    # write result of profile to file
    file = 'TB_PAMTRA_standard_atmosphere.txt'
    header = '# Standard atmosphere as implemented in PAMTRA (RH: 0%)\n'

    print('Writing file: {}'.format(base_dir_out+file))
    
    with open(base_dir_out+file, 'w') as f:
        f.write(header)
        data.to_csv(f, index=False)


def iwv_of_all_profiles():
    
    base_dir_out = '/home/nrisse/WHK/eumetsat/data/brightness_temperature/'
    
    # read data
    folder_atmos = '/home/nrisse/WHK/eumetsat/data/atmosphere/'
    files = []
    for month in range(1, 13):
        mm = str(month).zfill(2)
        files.append(glob(folder_atmos+'2019/'+mm+'/*/*.txt'))
    
    files = [f for sublist in files for f in sublist]
    filenames = [f[-25:-4] for f in files]
    
    iwv_df = pd.DataFrame(columns=filenames, index=['iwv'], data=np.nan)
    
    for i, file in enumerate(files):
        
        print('{}/{}'.format(i, len(files)))
        
        iwv_df.loc['iwv', filenames[i]] = calculate_iwv(file)
    
    outfile = '/home/nrisse/WHK/eumetsat/data/iwv/iwv_pamtra.txt'
    with open(outfile, 'w') as f:
        f.write('# Integrated water vaport calculated with PAMTRA\n')
        iwv_df.to_csv(f)
    
    
if __name__ == '__main__':

    main_all_data()
    #main_standard_atmosphere()
    
    # calculate iwv of all files
    #iwv_of_all_profiles()
    
