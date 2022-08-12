# Introduction
This document describes the required steps to reproduce the results presented in 
the report

        Bandpass effects of the MetOp-SG Microwave Imager
                        (MWI) at 183 GHz                

by Nils Risse, Mario Mech, and Susanne Crewell (2022) for EUMETSAT. The study 
design was setup in close collaboration with Christophe Accadia, Vinia Mattioli, 
Francesco De Angelis (EUMETSAT) and Ulf Klein (ESA).

# Study approach
The general approach for the study is to simulate the brightness temperature 
(TB) with high spectral resolution under MWI observing conditions (altitude, 
incidence angle, polarization) of different atmospheric conditions. This 
spectral TB is then weighted with the measured spectral response function (SRF), 
which corresponds to the virtual MWI observation. If one would not have access 
to the SRF, the MWI observation gets estimated either using a tophat function 
over the bandpass or by averaging the TB at two center frequencies of every 
channel. This was done in the study as well, and the deviation from the virtual 
observation based on the SRF was analyzed. Different scenarios are compared in 
the end under clear-sky and cloudy conditions. In addition, the measured SRF 
was perturbed or reduced in the sampling interval to find out, how much the 
virtual observation changes if the SRF changes.

In the beginning of the study, a decision had to be made which SRF data would be 
best to use. Finally the measurement along both bandpasses was chosen. It would 
be also an option to mirror the one-sided SRF measurement at 183 GHz, which 
would neglect channel imbalances.

# Study history
## Major changes in the study design
The first study idea was to simulate three regions (polar, mid-latitude, 
tropical) under clear-sky and cloudy conditions. The surface emissivity was set 
to 0.6. Hydrometeors would get extracted from a model. Another idea was to use 
idealized profiles to test the effect of hydrometeors. This was not done later 
on. (2020-07-08)

After a meeting with Susanne Crewell, Christophe Accadia, Vinia Mattioli, and 
Francesco De Angelis, the study design was further refined. Main focus was put 
on three points: vary the noise error, add third estimate of MWI TB (center+
cutoff together), analyze cloud interaction (ERA-5). Minor docus on four points: 
reduce number of SRF measurements, compare different idealized RH levels using 
the standard atmosphere, analyze more profiles, visualize bandpass effect as 
function of IWV.

After the first presentation at the SAG meeting, it was decided that the 
Gaussian noise perturbation on the SRF is not easy to interpret and offsets
mostly cancel out. It was decided to aim for worst-case scenarios, e.g. 
correlated errors. Results of the updates perturbation study will be presented 
at the next SAG meeting.

After a discussion with Susanne Crewell and Ulf Klein (2020-12-02), it was 
decided to improve the estimation of SRF uncertainties by introducing ripples, 
slopes, and imbalances.

Gaussian noise is completely removed in the final report, as it has a limited 
effect on the TB and is hard to interpret.

In the presentations, the radiosonde profiles were simulated with a surface 
emissivity of 0.6. This was changed to 0.9 in the final report, since this value 
is more realistic for water surfaces. This change had an effect only at low IWV 
and caused a larger bandpass effect.

## Reports and presentations
### 2020-09-22: Short summary of work
- many things changed from this report until the first presentation at SAG 
  meeting.

### 2020-11-12: Presentation at MWI-ICI SAG meeting
- for this presentation, an emissivity of 0.6 was used for the radiosonde 
  forward simulations, which caused offsets to the ERA-5 simulation. To be more
  consistent, the report uses an emissivity of 0.9. This changed the bandpass 
  effect for low IWV (generally lower bandpass effect!).
- SRF perturbations were Gaussian noise, which mostly cancels out.
- increase of SRF sampling interval was presented and is also in final report.
- IWV-dependence was presented.

### 2021-01-12: Short summary of work
- focus is on the SRF perturbations as discussed with Ulf Klein.
- these are the basis for the final report and the second presentation at the 
  SAG meeting.

### 2021-02-02: Presentation to AWARES seminar
- summary of previous report
- additionally, varying magnitude of perturbations

### 2021-04-23: Presentation at MWI-ICI SAG meeting
- follow-up from first presentation
- focus on the systematic SRF perturbations instead of Gaussian noise as was 
  presented the last time
- same data is in the last presentation, and same PAMTRA simulations
- after this meeting, it was suggested to write a publication about the two 
  presentations as reference for EUMETSAT.

### 2022-08-12: Written report
- based on presentations during SAG meeting and discussions in before the first 
  meeting and between the first and second meeting.
- changes were made also after the second presentation (see major changes in the 
  study design).

# Reproduction of study results
## Programming environment
- setup python environment for the analysis as specified in the environment.yml 
  or spec-file.txt
- setup python environment for PAMTRA simulation (python3)
- set environment variable which defines the base directory (currently PATH_PHD 
  variable)

## Data
### Radiosondes
- source: http://weather.uwyo.edu/upperair/sounding.html
- download data from 2019 for the four stations
- check .xls file for station list

### ERA-5
- single levels (era5-single-levels_20150331_1200.nc) and pressure levels 
  (era5-pressure-levels_20150331_1200.nc)

### SRF
- two excel files provided by esa
  - MWI-RX183_DSB_Matlab.xlsx: original measured SRF in dB, maximum value is 
    0 dB for every channel. Frequency range for channel 14 likely too short!
  - MWI-RX183_Matlab.xlsx: original measured SRF in dB. Only frequencies above 
    183 GHz (not used in final report, but interesting for comparison)

## PAMTRA simulations
- create file with frequencies used for PAMTRA simulations (frequencies.txt) 
  using write_frequencies_to_file.txt
- install PAMTRA from github repository and follow the instructions
- run pamtra_simulation_era.py with python3 (needs read_era5.py and a tool to 
  write pamtra output to netcdf which is in pamtra_model/tools directory). This 
  script is equivalent to the pamtra_simulation_era5.ipynb. Run once with and 
  once without hydrometeors and adapt the file name of the output file manually.
- run pamtra_simulation_radiosondes.ipynb (needs a tool to write pamtra output 
  to netcdf, which is in pamtra_model/tools directory). A dimension for the 
  radiosonde profile is created already, and will be in the next step completed 
  by extracting the date and station name
- finally, two files are written for each simulation. One file contains many 
  variables provided by PAMTRA, the other file is reduced for the downstream 
  analysis. All files are initially written to work directory. The two reduced 
  files need to be copied to data/brightness_temperature (TB_era5.nc - ERA-5 
  clear-sky, TB_era5_hyd.nc - ERA-5 all-sky, TB_era5.nc - radiosondes)

## Bandpass effect calculation
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

# Reproduce the figures
## Basic scripts needed for all figures
- mwi_info/mwi_183.py: contains MWI channel specifications and labels (mwi)
- path_setter/path.py: defines paths where data and figures are stored 
  (path_data, path_plot)

## Figure 1: bandpass data
- script to read sensitivity data: importer/read_sensitivity.py --> read 
  sensitivity to xarray.Dataset from one of the two .xlsx files. Raw and 
  linearized and normalized SRF is written to xarray.Dataset

## Figure 2: era-5 integrated hydrometeors
- data_viewer_era5.py

## Figure 3: tb spectra
- tb_spectra.py
- basic scripts are imported
- only parts of the script are needed

## Figure 4: systematic srf errors
- bandpass_measurements/plot_perturbations.py
- only parts of the script are needed

## Figure 5: bandpass effect clear-sky as a function of TBobs
- evaluation_dtb_mwi_est.py
- run only some parts of the script

## Figure 6: bandpass effect clear-sky as a function of IWV
- evaluation_dtb_mwi_est.py
- run only some parts of the script

## Figure 7: influence of hydrometeors on bandpass effect
- evaluation_dtb_mwi_est_era5_grid.py
- only some parts of the script

## Figure 8: effect of systematic perturbations
- evaluation_srf_perturbation.py

## Figure 9: effect of sampling interval reduction
- evaluation_srf_reduced_sampling.py

# Additional scripts used for written information
- spectral TB gradients and differences described in forward simulation chapter 
  come from: tb_mwi_cumulative_visualization.py
- SRF out-of-band sensitivity: plot_bandpass_measurement.py
- SRF imbalance: plot_bandpass_measurement.py


# Overview of scripts
├── bandpass_measurement
│   ├── __init__.py
│   ├── plot_bandpass_measurement.py

various plots and statistics of srf

│   ├── plot_frequencies.py

helper script to quickly check where frequencies are located of the two 
sensitivity datasets and for the PAMTRA simulation

│   ├── plot_perturbations.py

plots systematic perturbations

│   ├── plot_reference_tb_overview.py

makes small figures for presentation showing reference frequency

│   └── srf_analysis.py

some analysis on the srf measurements (not needed for report)

├── data_viewer_era5.py

plot atmospheric data from era-5 (hydrometeors) and emissivity on map

├── evaluation_dtb_mwi_est_era5_grid.py

evaluation of bandpass effect from era-5 (map)

├── evaluation_dtb_mwi_est.py

evaluation of bandpass effect from radiosondes and era-5 together or just 
radiosondes

├── evaluation_srf_perturbation.py

evaluation of perturbations on bandpass effect

├── evaluation_srf_reduced_sampling.py

evaluation of reduced srf sampling on bandpass effect

├── importer
│   ├── __init__.py
│   └── read_sensitivity.py

read srf from excel files to xarray.Dataset

├── __init__.py
├── mwi_info
│   ├── __init__.py
│   ├── mwi_183.py

mwi channel specification as numpy arrays

├── pamtra
│   ├── __init__.py
│   ├── pamtra_simulation_era5.py

pamtra simulation for era-5

│   ├── pamtra_simulation_era5.ipynb

pamtra simulation for era-5 (same as .py script)

│   └── pamtra_simulation_radiosondes.ipynb

pamtra simulation for radiosondes

│   └── write_frequencies_to_file.py

writes frequencies for PAMTRA simulation into textfile

├── path_setter
│   ├── __init__.py
│   ├── path.py

defines directories for plot and data

├── radiosonde
│   ├── __init__.py
│   ├── plot_radiosonde_iwv.py

plot monthly mean+std IWV of radiosondes

│   ├── plot_radiosonde_t_rh.py

plot mean temperature and rh of radiosondes

│   ├── radiosonde_data_availability.py

plot data availability of radiosonde data

│   ├── radiosondes_download_wyo.py

download radiosonde data

│   └── stations_on_map.py

plot location of radiosondes and era-5 scene on globe

├── tb_mwi_calculation.py

calculation of mwi tb from pamtra simulation, and definition of other 
srfs/estimates

├── tb_mwi_cumulative_visualization.py

some visualization of why some profiles deviate more, and of the tb gradients of 
the pamtra simulation

└── tb_spectra.py

plots tb spectra from pamtra simulations
