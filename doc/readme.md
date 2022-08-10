# Workflow to reproduce study results
## Programming environment and input data
- setup python environment as specified in the yml file (for analysis)
- setup python environment for PAMTRA simulation
- retrieve the required data: radiosondes (see report), ERA-5 (see report), SRF (two .xlsx files from ESA)

## PAMTRA simulations
- create file with frequencies used for PAMTRA simulations (frequencies.txt) using write_frequencies_to_file.txt
- install PAMTRA from github repository and follow the instructions
- run pamtra_simulation_era.py with python3 (needs read_era5.py and a tool to write pamtra output to netcdf which is in another directory). This script is equivalent to the pamtra_simulation_era5.ipynb. Run once with and once without hydrometeors and adapt the file name of the output file manually.
- run pamtra_simulation_radiosondes.ipynb (needs a tool to write pamtra output to netcdf, which is in another directory). A dimension for the radiosonde profile is created already, and will be in the next step completed by extracting the date and station name
- finally, two files are written for each simulation. One file contains many variables provided by PAMTRA, the other file is reduced for the downstream analysis. All files are initially written to work directory. The two reduced files need to be copied to data/brightness_temperature (TB_era5.nc - ERA-5 clear-sky, TB_era5_hyd.nc - ERA-5 all-sky, TB_era5.nc - radiosondes)

## Bandpass effect calculation
- run tb_mwi_calculation.py. Here, all the different SRF are defined and the MWI observations are calculated as well as respective differences to the observation based on the original SRF. All variables from the PAMTRA simulation are kept in the same dataset for the analysis later.
- output files have the same name as the PAMTRA simulations with the additional extension '_MWI'
- now, all the data is ready for the analysis and contained in these nc files in a consistent way:
  - integrated hydrometeors (hydro_wp)
  - integrated iwv (iwv)
  - spectral tb variation
  - original SRF
  - reduced SRF
  - perturbed SRF (offset in dB, dB, linear)
  - estimation types SRFs (tophat, selected frequencies)
  - tb based on the different SRF
  - difference of tb based on different SRF to the TB from original SRF (two make no sense: tb_mwi_err_offset_dB, tb_mwi_err_dB!)
  - PAMTRA model settings (sfc_type, sfc_model, sfc_refl, emissivity, obs_height, ...)

# Reproduce the figures
## Figure 1

## Figure 2

## Figure 3

## Figure 4

## Figure 5

## Figure 6

## Figure 7

## Figure 8

## Figure 9