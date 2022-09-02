
# Environment variables
Path locations for this project are defined by a `.env` file. An example
containing all required path variables is provided in the root directory.
Simply copy the example file `.env.example` to `.env` and assign your paths
like `PATH_SRF=/data/srf`.
Currently, four environment variables are required:
- PATH_SRF: path with SRF files
- PATH_BRT: path with brightness temperature data (i.e. forward simulations)
- PATH_ATM: path with atmopsheric data (radiosondes and ERA-5 fields)
- PATH_PLT: path with plots
