# spymicmac scripts and outputs for historix experiment

This repository contains scripts and (text-based) outputs for the Historical Images for Surface Topography Reconstruction
Intercomparison eXperiment (HISTORIX).

## scripts

The `script_templates/` folder contains the following scripts, adapted for each study site and image set:

- `convert_gcps.py` - for converting the provided intrinsics and GCP measurements into the MicMac xml format
- `calibrate_cams.py` - for creating tie points and an initial camera calibration (`Tapioca` and `Tapas`) 
- `bundle_adjust.py` - for running the bundle block adjustment (`GCPBascule` and `Campari`) using the provided
  GCP measurements
- `process_dems.py` - for doing the dense matching (`Malt`) and various post-processing steps
- `prepare_submissions.py` - for compiling the various outputs into the format required for submitting to HISTORIX
- `register_preproc.py` - for running the bundle block adjustment on the pre-processed images by automatically finding
  GCPs in the reference DEM or Orthoimage
- `one_big_script.py` - for processing the raw KH-9 MC images

Each image dataset directory has the adapted/adjusted versions of these scripts, along with an `experiments.csv` file
that provides additional information about the processing, along with the prefix code for submitting to HISTORIX.

## setup

Use the provided `environment.yml` file to create a conda environment with the necessary python packages. Once the
environment is created, I recommend cloning + installing the latest version of [spymicmac](https://spymicmac.readthedocs.io)
using pip:

```text
git clone https://github.com/iamdonovan/spymicmac.git
pip install -e spymicmac
```

Additionally, you will need a working version of MicMac installed on your machine. For more information about setting
this up, see [these instructions](https://spymicmac.readthedocs.io/en/latest/setup.html#installing-micmac). Note that
the processing should work by compiling either the *IncludeALGLIB* branch recommended there, or the *main* branch. I
cannot speak for the other branches, as I have not tested them.
