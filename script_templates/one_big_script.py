#!/usr/bin/env python
from pathlib import Path
from glob import glob
from spymicmac import preprocessing, micmac, register


local_crs = '' # need to fill in the crs to use
out_name = '' # fill in prefix for final files
prefix = ''

glacmask = None # fill in path to optional glacier mask
landmask = Path('..', '..', '..', 'aux_dems', f"{prefix}_reference_dem_large_mask.tif") # fill in path to optional land mask
fn_ref = Path('..', '..', '..', 'aux_dems', f"{prefix}_reference_dem_large.tif") # fill in path to optional land mask
do_ortho = False

# preprocess images
preprocessing.preprocess_kh9_mc(
    option=['balance'],
    nproc='max',
    scale=140,
    blend=True,
    add_sfs=True,
    res_low=400,
    res_high=8000,
    add_params=True
)

# create the relative dem/orthophoto
micmac.malt(
    'OIS.*tif',
    'Relative',
    dirmec='MEC-Relative',
    zoomf=2,
    cost_trans=4,
    szw=3,
    regul=0.1
)

imlist = sorted(glob('OIS*.tif'))
for fn in imlist:
    micmac.mosaic_micmac_tiles(
        filename=f"Ort_{fn.replace('.tif', '')}",
        dirname='Ortho-MEC-Relative',
    )

micmac.mosaic_micmac_tiles(
    filename='Z_Num8_DeZoom2_STD-MALT',
    dirname='MEC-Relative',
)

# register the images to the reference DEM
register.register_relative(
    'MEC-Relative',
    fn_ref,
    glacmask=glacmask,
    landmask=landmask,
    density=400,
    strategy='peaks',
    use_hillshade=True
)

malt_args = {
    'dirmec': 'MEC-Malt',
    'zoomf': 1,
    'cost_trans': 4,
    'szw': 3,
    'regul': 0.1,
    'do_ortho': do_ortho
}

# create the absolute dem/orthophotos
# TODO: check if this is too big and iterate if needed
imlist = sorted(glob('OIS*.tif'))
micmac.block_malt(
    imlist,
    ori='TerrainFinal',
    nimg=2,
    malt_args=malt_args
)

# clean up the outputs
for block in len(glob('MEC-Malt*block*/')):
    # create the orthomosaic
    if do_ortho:
        micmac.tawny(f"MEC-Malt_block{block}")

    micmac.post_process(
        projstr=local_crs,
        out_name=out_name,
        dirmec=f"MEC-Malt_block{block}",
        do_ortho=do_ortho,
        ind_ortho=False
    )
