# Getting started
The following provides an overview of the steps to reproduce the study results.

## Python environment
The scripts were developed under python 3.10.5 and require basic functionalities 
from 
- numpy (1.21.0)
- xarray (0.20.1), 
- pandas (1.4.2), 
- matplotlib-base (3.5.2), 
- cartopy (0.20.2), 
- requests (2.28.0), and 
- python-dotenv (0.20.0). 

However, also other versions are expected to work.

The python environment required for PAMTRA simulations is described
[here](https://pamtra.readthedocs.io/en/latest/installation.html). 
A separate python 3.8.10 environment was created as described in the 
documentation with the additional modules xarray (0.19.0) and python-dotenv 
(0.20.0).

## Environment variables
Path locations for this project are defined by a `.env` file. An example
containing all required path variables is provided in the root directory.
Simply copy the example file [`.env.example`](../.env.example) to `.env` and 
assign your paths like `PATH_SRF=/data/srf`. These environment variables are 
required:
- `PATH_SRF`: path with SRF files.
- `PATH_BRT`: path with brightness temperature data (i.e. forward simulations).
- `PATH_ATM`: path with atmopsheric data (radiosondes and ERA-5 fields).
- `PATH_PLT`: path with plots.
- `PATH_SIM`: path with complete output of PAMTRA simulation.

## Data
### Input
Download the data as described in the publication. For the radiosonde data, a
download script is provided [here](../src/helpers/download_radiosondes.py).
The following lists the files and their expected location:
- Spectral response functions
    - `PATH_SRF`: `MWI-RX183_DSB_Matlab.xlsx`
    - `PATH_SRF`: `MWI-RX183_Matlab.xlsx`
    - `PATH_SRF`: `rtcoef_gpm_1_gmi_srf_srf_ch12.txt`
    - `PATH_SRF`: `rtcoef_gpm_1_gmi_srf_srf_ch13.txt`
- Atmospheric data
    - `PATH_ATM`: `era5-pressure-levels_20150331_1200.nc`
    - `PATH_ATM`: `era5-single-levels_20150331_1200.nc`
    - `PATH_ATM`: `yyyy/mm/dd/ID_?????_yyyymmddhhmm.txt`

### Output
The following files will be created:
- PAMTRA simulation
    - `PATH_BRT`: `frequencies.txt`
    - `PATH_BRT`: `TB_era5.nc`
    - `PATH_BRT`: `TB_era5_hyd.nc`
    - `PATH_BRT`: `TB_radiosondes_2019.nc`
    - `PATH_SIM`: `TB_era5_complete.nc`
    - `PATH_SIM`: `TB_era5_hyd_complete.nc`
    - `PATH_SIM`: `TB_radiosondes_2019_complete.nc`
- MWI observations
    - `PATH_BRT`: `TB_era5_MWI.nc`
    - `PATH_BRT`: `TB_era5_hyd_MWI.nc`
    - `PATH_BRT`: `TB_radiosondes_2019_MWI.nc`
- Figures
    - `PATH_PLT`: several plots are saved here.

# PAMTRA simulations
The following provides a step-by-step description on how to run the PAMRA
simulation after the environment was created.
1. Create file with frequencies (`frequencies.txt` in `PATH_BRT`) using 
   [write_frequencies_to_file.py](../src/pamtra/write_frequencies_to_file.py)
2. Run 
   [pamtra_simulation_era5.py](../src/pamtra/pamtra_simulation_era5.py) once with
   and once without hydrometeors by setting the flag parameter in the script.
   For each run, two output files are created in `PATH_BRT` (smaller file) and 
   `PATH_SIM` (larger file).
3. Run 
   [pamtra_simulation_radiosondes.py](../src/pamtra/pamtra_simulation_radiosondes.py).
   A dimension for the radiosonde profile is created.
   Two output files are created in `PATH_BRT` (smaller file) and 
   `PATH_SIM` (larger file).

The larger files can be deleted, as they are not required for further analysis.

# MWI observation calculation
Finally, three files containting the MWI brightness temperatures are created and
written to `PATH_BRT` with
[tb_mwi_calculation.py](../src/tb_mwi_calculation/tb_mwi_calculation.py).
Here, all the different SRF are defined and the MWI 
observations are calculated as well as respective differences to the 
observation based on the original SRF. All variables from the PAMTRA 
simulation are kept in the same dataset for the analysis later. 

# Data analysis
The data analysis is based on all other scripts. 
[This list](../docs/reproduce_plots.md) contains all the
scripts required to create the plots of the final report after the output data
was created.
