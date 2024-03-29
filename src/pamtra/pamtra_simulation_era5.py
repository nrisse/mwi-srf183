"""
PAMTRA simulations based on ERA-5 with or without hydrometeor scattering.
"""


from __future__ import division
import pyPamtra
import os
import numpy as np
import datetime
from dotenv import load_dotenv
import netCDF4
from pamtra.pamtra_tools import pam_to_xarray

load_dotenv()


def readERA5press(fname2d,
                  fname3d,
                  descriptorFile,
                  grid,
                  timeidx=None,
                  rmHyds=False):
    """
    Create pamtra object from an era-5 file.

    Parameters
    ----------
    fname2d :
        File name of single level file.
    fname3d :
        File name of pressure level file.
    descriptorFile :
        File name of descriptor file.
    grid :
        Indices of the extent of the ERA-5 field to be read [x0, x1, y0, y1].
    timeidx : optional
        Time index. The default is None.
    rmHyds : optional
        Whether to remove hydrometeors. The default is False.

    Returns
    -------
    pam :
        Pamtra object.
    """

    variables1D = ['longitude', 'latitude']
    variables2D = ['skt', 'sst', 'msl', 'sp', 'u10', 'v10', 'lsm', 'siconc']
    variables3D = ['z', 't', 'q', 'clwc', 'ciwc', 'crwc', 'cswc']

    c, d, a, b = grid

    ERA5_file2D = netCDF4.Dataset(fname2d, mode='r')
    ERA5_file3D = netCDF4.Dataset(fname3d, mode='r')

    vals2D = ERA5_file2D.variables
    vals3D = ERA5_file3D.variables

    for val in variables1D:
        if val not in vals2D: raise AttributeError(val + ' not in vals2D')
    
    for val in variables2D:
        if val not in vals2D: raise AttributeError(val + ' not in vals2D')
    
    for val in variables3D:
        if val not in vals3D: raise AttributeError(val + ' not in vals3D')

    Nx = len(vals2D['longitude'][a:b])
    Ny = len(vals2D['latitude'][c:d])
    Nh = len(vals3D['level'])
    nHydro = 4

    shape2D = (Nx,Ny)
    shape3D = (Nx,Ny,Nh)
    shape3Dplus = (Nx,Ny,Nh+1)
    shape4D = (Nx,Ny,Nh,nHydro)
    
    # if timeidx is not defined take the first one 
    if timeidx is None:
        timeidx = 0

    unixtime = np.zeros(shape2D)+(datetime.datetime(
        year=1900, month=1, day=1, hour=0, minute=0, second=0) +\
            datetime.timedelta(hours=int(vals2D['time'][timeidx])) -\
                datetime.datetime(1970,1,1)).total_seconds()

    pam_profile = dict()  # empty dictionary to store pamtra data

    pam_profile['timestamp'] = unixtime

    # create latitude and longitude grid
    pam_profile['lat'], pam_profile['lon'] = np.meshgrid(
            vals2D['latitude'][c:d],
            vals2D['longitude'][a:b])

    pam_profile['temp_lev'] = np.empty(shape3Dplus)
    pam_profile['temp'] = np.swapaxes(vals3D['t'][timeidx,::-1,c:d,a:b],0,2)
    pam_profile['temp_lev'][...,1:-1] = (pam_profile['temp'][...,1:] +\
                                         pam_profile['temp'][...,0:-1])*0.5
    pam_profile['temp_lev'][...,-1] = pam_profile['temp_lev'][...,-2]
    pam_profile['temp_lev'][...,0] = np.swapaxes(
        vals2D['skt'][timeidx,c:d,a:b],0,1)

    z = np.swapaxes(vals3D['z'][timeidx,::-1,c:d,a:b],0,2)
    z_sfc = np.swapaxes(vals2D['z'][timeidx,c:d,a:b],0,1)

    pam_profile['hgt_lev'] = np.empty(shape3Dplus)
    pam_profile['hgt'] = np.empty(shape3D)
    pam_profile['press_lev'] = np.empty(shape3Dplus)
    pam_profile['press'] = np.empty(shape3D)

    sfc_press = np.swapaxes(vals2D['sp'][timeidx,c:d,a:b],0,1)
    msl_press = np.swapaxes(vals2D['msl'][timeidx,c:d,a:b],0,1)

    g = 9.80665  # gravity
    Re = 6356766  # earth radius

    pam_profile['hgt'] = np.abs(z/g)*Re/(Re-(z/g))
    pam_profile['hgt_lev'][...,0] = np.abs(z_sfc/g)*Re/(Re-(z_sfc/g))
    pam_profile['hgt_lev'][...,1:-1] = (pam_profile['hgt'][...,1:] +\
                                        pam_profile['hgt'][...,0:-1])*0.5
    pam_profile['hgt_lev'][...,-1] = pam_profile['hgt'][...,-1]+\
        (pam_profile['hgt'][...,-1]-pam_profile['hgt_lev'][...,-2])

    # calculate pressure according to barometric formular
    M = 0.02896  # molar mass in kg mol-1
    R = 8.314  # molar gas constant in J K-1 mol-1

    for i in range(shape2D[0]):
        for j in range(shape2D[1]):
            pam_profile['press'][i,j,:] = msl_press[i,j]*\
                np.exp(-M*g*pam_profile['hgt'][i,j,:]/(R*288.15))
            pam_profile['press_lev'][i,j,:] = msl_press[i,j]*\
                np.exp(-M*g*pam_profile['hgt_lev'][i,j,:]/(R*288.15))

    pam_profile['press_lev'][...,0] = sfc_press


    pam_profile['relhum'] = np.empty(shape3D)
    pam_profile['relhum'][:,:,:] = (pyPamtra.meteoSI.q2rh(
        np.swapaxes(vals3D['q'][timeidx,::-1,c:d,a:b],0,2),
        pam_profile['temp'][:,:,:],pam_profile['press'][:,:,:]) * 100.
        )

    pam_profile['hydro_q'] = np.zeros(shape4D) + np.nan
    pam_profile['hydro_q'][:,:,:,0] = np.swapaxes(vals3D['clwc']
                                                  [timeidx,::-1,c:d,a:b],0,2)
    pam_profile['hydro_q'][:,:,:,1] = np.swapaxes(vals3D['ciwc']
                                                  [timeidx,::-1,c:d,a:b],0,2)
    pam_profile['hydro_q'][:,:,:,2] = np.swapaxes(vals3D['crwc']
                                                  [timeidx,::-1,c:d,a:b],0,2)
    pam_profile['hydro_q'][:,:,:,3] = np.swapaxes(vals3D['cswc']
                                                  [timeidx,::-1,c:d,a:b],0,2)

    # mass mixing ratios can be smaller than 0
    pam_profile['hydro_q'][pam_profile['hydro_q'] < 0.] = 0.

    # to set specific hydrometeors to 0
    if rmHyds:
        pam_profile['hydro_q'][:,:,:,0] = 0.  # cloud water
        pam_profile['hydro_q'][:,:,:,1] = 0.  # cloud ice
        pam_profile['hydro_q'][:,:,:,2] = 0.  # rain 
        pam_profile['hydro_q'][:,:,:,3] = 0.  # snow

    varPairs = [['u10','wind10u'],
                ['v10','wind10v'],
                ['skt','groundtemp'],
                ['lsm','sfc_slf'],
                ['siconc','sfc_sif']]
    for era5Var, pamVar in varPairs:
        pam_profile[pamVar] = np.swapaxes(vals2D[era5Var][timeidx,c:d,a:b],0,1)
    
    # surface properties
    pam_profile['sfc_type'] = np.around(pam_profile['sfc_slf'])
    pam_profile['sfc_type'][(pam_profile['sfc_type'] == 0) &
                            (pam_profile['sfc_sif'] > 0)] = 2
    pam_profile['sfc_model'] = np.zeros(shape2D)
    pam_profile['sfc_refl'] = np.chararray(shape2D)
    pam_profile['sfc_refl'][:] = 'F'
    pam_profile['sfc_refl'][pam_profile['sfc_type'] > 0] = 'S'
    
    # observation height
    pam_profile['obs_height'] = np.full((Nx, Ny, 1), fill_value=833000, 
                                        dtype='int')
    
    # create pamtra object
    pam = pyPamtra.pyPamtra()

    if isinstance(descriptorFile, str):
        pam.df.readFile(descriptorFile)
    else:
        for df in descriptorFile:
            pam.df.addHydrometeor(df)
    
    pam.createProfile(**pam_profile)
    
    return pam


if __name__ == '__main__':
    
    # choose, if hydrometeor scattering is omitted
    rmHyds = False
    
    # read era5 data
    fname2d = os.path.join(
        os.environ['PATH_ATM'], 'era5-single-levels_20150331_1200.nc')
    fname3d = os.path.join(
        os.environ['PATH_ATM'], 'era5-pressure-levels_20150331_1200.nc')
    descriptorFile = './pamtra/descriptor_file_ecmwf.txt'
    grid = [141, 180, 181, 200]  # grid to simulate
    
    pam = readERA5press(fname2d=fname2d,
                        fname3d=fname3d,
                        descriptorFile=descriptorFile,
                        grid=grid,
                        rmHyds=rmHyds)
    
    assert np.all(pam.p['sfc_type'] == 0)  # ocean
    assert np.all(pam.p['sfc_model'] == 0)  # TESSEM2
    assert np.all(pam.p['sfc_refl'] == b'F')  # Fresnel (= specular)
    
    pam.nmlSet['creator'] = 'Nils Risse'
    
    pam.nmlSet['active'] = False
    pam.nmlSet['passive'] = True
    pam.nmlSet['outpol'] = 'VH'
    pam.set['freqs'] = np.loadtxt(os.path.join(
        os.environ['PATH_BRT'], 'frequencies.txt'))
    
    pam.nmlSet['add_obs_height_to_layer'] = False
    
    pam.nmlSet['gas_mod'] = 'R98'
    pam.nmlSet['emissivity'] = 0.9  # will not be used here
    
    pam.runParallelPamtra(pam.set['freqs'],
                          pp_deltaX=1, 
                          pp_deltaY=1, 
                          pp_deltaF=10, 
                          pp_local_workers="auto")
    pam.addIntegratedValues()
    
    ds_pam = pam_to_xarray(pam)
    ds_pam['hydro_class'] = np.array(['cwc', 'iwc', 'rwc', 'swc'])
    
    # write result to file
    if rmHyds:
        basename = 'TB_era5'
    else:
        basename = 'TB_era5_hyd'
    
    ds_pam.to_netcdf(os.path.join(
            os.environ['PATH_SEC'],
            f'data/mwi_bandpass_effects/{basename}_complete.nc',
            ))
    
    # write result with reduced variables to file
    ds_pam_red = ds_pam.sel(direction='up', outlevel=0, polarization='V')
    ds_pam_red.to_netcdf(os.path.join(
            os.environ['PATH_BRT'], 
            f'{basename}.nc'))
    