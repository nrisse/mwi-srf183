# Getting started
The following provides an overview of the steps to reproduce the study results. 

## Environment variables
Path locations for this project are defined by a `.env` file. An example
containing all required path variables is provided in the root directory.
Simply copy the example file `.env.example` to `.env` and assign your paths
like `PATH_SRF=/data/srf`. Four environment variables are required:
- `PATH_SRF`: path with SRF files.
- `PATH_BRT`: path with brightness temperature data (i.e. forward simulations).
- `PATH_ATM`: path with atmopsheric data (radiosondes and ERA-5 fields).
- `PATH_PLT`: path with plots.
- `PATH_SIM`: path with complete output of PAMTRA simulation

## Get input data
Download the data as described in the publication. The following lists the files and their expected location:
- Spectral response functions
    - PATH_SRF: MWI-RX183_DSB_Matlab.xlsx
    - PATH_SRF: MWI-RX183_Matlab.xlsx
    - PATH_SRF: rtcoef_gpm_1_gmi_srf_srf_ch12.txt
    - PATH_SRF: rtcoef_gpm_1_gmi_srf_srf_ch13.txt
- Atmospheric data
    - PATH_ATM: era5-pressure-levels_20150331_1200.nc
    - PATH_ATM: era5-single-levels_20150331_1200.nc
    - PATH_ATM: yyyy/mm/dd/ID_?????_yyyymmddhhmm.txt

## Python environment
- setup python environment for the analysis as specified in the environment.yml 
  or spec-file.txt
- setup python environment for PAMTRA simulation (python3)
- set environment variable which defines the base directory (currently PATH_PHD 
  variable, also used in PAMTRA simulations directly)

## Overview of output data
The following files will be created:
- PAMTRA simulation
    - PATH_BRT: frequencies.txt
    - PATH_BRT: TB_era5.nc
    - PATH_BRT: TB_era5_hyd.nc
    - PATH_BRT: TB_radiosondes_2019.nc
    - PATH_SIM: TB_era5_complete.nc
    - PATH_SIM: TB_era5_hyd_complete.nc
    - PATH_SIM: TB_radiosondes_2019_complete.nc
- MWI observations
    - PATH_BRT: TB_era5_MWI.nc
    - PATH_BRT: TB_era5_hyd_MWI.nc
    - PATH_BRT: TB_radiosondes_2019_MWI.nc
- Figures
    - PATH_PLT: several figures in sub-directories

# PAMTRA simulations
- create file with frequencies used for PAMTRA simulations (frequencies.txt) 
  using ./scripts/pamtra/write_frequencies_to_file.py
- install PAMTRA from github repository and follow the instructions
- run pamtra_simulation_era.py with python3 (tool in ./scripts/pamtra/tools to
  write pamtra output to netcdf). This 
  script is equivalent to the pamtra_simulation_era5.ipynb. Run once with and 
  once without hydrometeors and adapt the file name of the output file manually.
- run pamtra_simulation_radiosondes.ipynb (tool in ./scripts/pamtra/tools to
  write pamtra output to netcdf). A dimension for the 
  radiosonde profile is created already, and will be in the next step completed 
  by extracting the date and station name.
- finally, two files are written for each simulation. One file contains many 
  variables provided by PAMTRA, the other file is reduced for the downstream 
  analysis. All files are initially written to work directory. The two reduced 
  files need to be copied to data/brightness_temperature (TB_era5.nc - ERA-5 
  clear-sky, TB_era5_hyd.nc - ERA-5 all-sky, TB_era5.nc - radiosondes)

# MWI observation calculation
- run tb_mwi_calculation.py. Here, all the different SRF are defined and the MWI 
  observations are calculated as well as respective differences to the 
  observation based on the original SRF. All variables from the PAMTRA 
  simulation are kept in the same dataset for the analysis later.
- output files have the same name as the PAMTRA simulations with the additional 
  extension '_MWI'
- now, all the data is ready for the analysis and contained in these nc files in 
  a consistent way:
  - integrated hydrometeors (hydro_wp)
  - integrated iwv (iwv)
  - spectral tb variation
  - original SRF
  - reduced SRF
  - perturbed SRF (offset in dB, dB, linear)
  - estimation types SRFs (tophat, selected frequencies)
  - tb based on the different SRF
  - difference of tb based on different SRF to the TB from original SRF
  - PAMTRA model settings (sfc_type, sfc_model, sfc_refl, emissivity, 
    obs_height, ...)
