from __future__ import division
import sys
import numpy as np
import os

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
        rs = np.loadtxt(atmosphere, usecols=[0, 1, 2, 4])  # pres [hPa], hght [m], temp [C], relh [%]
        rs[:, 2] += 273.15  # temp from C to K
        rs[:, 0] = rs[:, 0] * 100  # press from hPa to Pa
        
        # write profile to dictionary
        pamData = dict()
        pamData["press"] = rs[:, 0]
        pamData["hgt"] = rs[:, 1]
        pamData["temp"] = rs[:, 2]
        pamData["relhum"] = rs[:, 3]
        
        # write profile from dictionary
        pam.createProfile(**pamData)

    # turn active off
    pam.nmlSet['active'] = False

    # run pamtra
    pam.runParallelPamtra(freqs, pp_deltaX=1, pp_deltaY=1, pp_deltaF=1, pp_local_workers="auto")

    # mean over both polarizations
    TB_mod = pam.r['tb'][0, 0, 0, 0, :, 0]  # only vertical polarization, height 833 km

    return TB_mod


def main():

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
        
        
if __name__ == '__main__':

    main()
