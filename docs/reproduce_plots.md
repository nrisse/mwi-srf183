# Reproduce plots from study
This list summarizes the required steps to reproduce the results presented in 
the report. Most script use helper functions defined in `src/helpers`.

- Figure 1: **SRF measurements**
  - [`srf_viewer.py`](../src/srf_analysis/srf_viewer.py)
- Figure 2: **ERA-5 integrated hydrometeors**
  - `src/atmos_viewer/era5.py`
- Figure 3: **TB spectra**
  - `src/evaluation/tb_spectra.py
- Figure 4: **Difference between SRFs**
  - `src/srf_analysis/srf_comparison.py`
- Figure 5: ****
  - `src/`
- Figure 6: ****
  - `src/`
- Figure 7: ****
  - `src/`
- Figure 8: ****
  - `src/`
- Figure 9: ****
  - `src/`


## Figure 4: systematic srf errors
- bandpass_measurements/plot_perturbations.py
- line 147

## Figure 5: bandpass effect clear-sky as a function of TBobs
- evaluation_dtb_mwi_est.py, line 101

## Figure 6: bandpass effect clear-sky as a function of IWV
- evaluation_dtb_mwi_est.py, line 214

## Figure 7: influence of hydrometeors on bandpass effect
- evaluation_dtb_mwi_est_era5_grid.py, line 119

## Figure 8: effect of systematic perturbations
- evaluation_srf_perturbation.py, entire script

## Figure 9: effect of sampling interval reduction
- evaluation_srf_reduced_sampling.py, entire script

## Basic scripts needed for multiple figures
- script to read sensitivity data: importer/read_sensitivity.py --> read 
  sensitivity to xarray.Dataset from one of the two .xlsx files. Raw and 
  linearized and normalized SRF is written to xarray.Dataset
- mwi_info/mwi_183.py: contains MWI channel specifications and labels (mwi)
- path_setter/path.py: defines paths where data and figures are stored 
  (path_data, path_plot)

# Additional scripts used for written information
- spectral TB gradients and differences described in forward simulation chapter 
  come from tb_mwi_cumulative_visualization.py
- SRF out-of-band sensitivity: plot_bandpass_measurement.py
- SRF imbalance: plot_bandpass_measurement.py
