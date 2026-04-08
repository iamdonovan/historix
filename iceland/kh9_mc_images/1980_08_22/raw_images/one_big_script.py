#!/usr/bin/env python
from pathlib import Path
from glob import glob
from spymicmac import preprocessing, micmac, register


local_crs = 32627 # need to fill in the crs to use
out_name = 'Final_FraserExtended' # fill in prefix for final files
prefix = 'IL'

glacmask = None # fill in path to optional glacier mask
landmask = Path('..', '..', '..', 'aux_dems', f"{prefix}_reference_dem_large_mask.tif") # fill in path to optional land mask
fn_dem = Path('..', '..', '..', 'aux_dems', f"{prefix}_reference_dem_large.tif") # fill in path to reference dem
fn_ref = Path('..', '..', '..', 'aux_orthos', f"{prefix}_orthomosaic_large.tif") # fill in path to reference ortho
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

micmac.tawny('Ortho-MEC-Relative')

micmac.mosaic_micmac_tiles(
    filename='Orthophotomosaic',
    dirname='Ortho-MEC-Relative',
)

micmac.mosaic_micmac_tiles(
    filename='Z_Num8_DeZoom2_STD-MALT',
    dirname='MEC-Relative',
)

# register the images to the reference DEM
register.register_relative(
    'MEC-Relative',
    fn_dem,
    glacmask=glacmask,
    landmask=landmask,
    density=400,
    strategy='peaks',
    use_hillshade=True,
    subscript='dem'
)

register.register_relative(
    'MEC-Relative',
    fn_dem,
    fn_ref=fn_ref,
    useortho=True,
    glacmask=glacmask,
    landmask=landmask,
    density=400,
    strategy='peaks',
    subscript='ortho'
)

malt_args = {
    'zoomf': 1,
    'cost_trans': 4,
    'szw': 3,
    'regul': 0.1,
    'do_ortho': do_ortho,
    'clean': True
}

# create the absolute dem/orthophotos
# TODO: check if this is too big and iterate if needed
imlist = sorted(glob('OIS*.tif'))

for ref in ['dem', 'ortho']:
    malt_args['dirmec'] = f"MEC-Malt_{ref}"

    micmac.block_malt(
        imlist,
        ori=f"TerrainFinal_{ref}",
        nimg=2,
        malt_kwargs=malt_args
    )

    # clean up the outputs
    for ind, block in enumerate(glob(f"MEC-Malt_{ref}_block*/")):
        # create the orthomosaic
        if do_ortho:
            micmac.tawny(block)

        # clean up the outputs
        micmac.post_process(
            projstr=local_crs,
            out_name=f"{out_name}_{ref}_block{ind}",
            dirmec=block,
            do_ortho=do_ortho,
            ind_ortho=False,
            do_ply=True
        )
