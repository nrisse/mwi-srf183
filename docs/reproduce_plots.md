# Reproduce plots in study
This list summarizes the required steps to reproduce the results presented in 
the report. Most script use helper functions defined in `src/helpers`. These
provide the MWI channel specifications at 183 GHz ([`mwi_183.py`](../src/helpers/mwi_183.py))
and a function to read the SRF data ([`srf_reader.py`](../src/helpers/srf_reader.py))
as well as color settings for plots.

- Figure 1: **SRF measurements**
  - [`srf_viewer.py`](../src/srf_analysis/srf_viewer.py)
- Figure 2: **ERA-5 integrated hydrometeors**
  - [`era5.py`](src/atmos_viewer/era5.py)
- Figure 3: **TB spectra**
  - [`tb_spectra.py`](src/evaluation/tb_spectra.py)
- Figure 4: **Difference between SRFs**
  - [`srf_comparison.py`](src/srf_analysis/srf_comparison.py)
- Figure 5: **Systematic SRF perturbations**
  - Defined in [`tb_mwi_calculation.py`](src/tb_mwi_calculation/tb_mwi_calculation.py) 
    and plotted in [`view_srf_perturbations.py`](src/tb_mwi_calculation/view_srf_perturbations.py) 
- Figure 6: **Effect of systematic perturbations**
  - [`srf_perturbation.py`](src/evaluation/srf_perturbation.py)
- Figure 7: **Effect of sampling interval reduction**
  - [`srf_reduced_sampling.py`](src/evaluation/srf_reduced_sampling.py)
- Figure 8: **Differences between MWI estimates and observation (clear-sky)**
  - [`dtb_mwi_est.py`](src/evaluation/dtb_mwi_est.py)
- Figure 9: **Differences between MWI estimates and observation (hydrometeor effect)**
  - [`dtb_mwi_est_era5_grid.py`](src/evaluation/dtb_mwi_est_era5_grid.py)
