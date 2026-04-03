#!/usr/bin/env python
from pathlib import Path
from glob import glob
from spymicmac import micmac, register


globstr = 'DZB*.tif' # fill in image pattern
local_crs = 6341 # need to fill in the crs to use
prefix = 'CG' # fill in prefix for study site
do_ortho = False # whether to make the ortho images
ori = 'FraserExtended' # change orientation directory if needed

glacmask = None # fill in path to optional glacier mask
landmask = Path('..', '..', '..', 'aux_dems', f"{prefix}_reference_dem_large_mask.tif") # fill in path to optional land mask
fn_ref = Path('..', '..', '..', 'aux_dems', f"{prefix}_reference_dem_large.tif") # fill in path to optional land mask

# create the relative dem/orthophoto
if not Path(f"MEC-Rel{ori}").exists():

    micmac.malt(
        globstr.replace('*.', '.*'),
        ori,
        dirmec=f"MEC-Rel{ori}",
        zoomf=2,
        cost_trans=4,
        szw=3,
        regul=0.1,
        do_ortho=do_ortho
    )

    if do_ortho:
        imlist = sorted(glob(globstr))
        for fn in imlist:
            micmac.mosaic_micmac_tiles(
                filename=fn,
                dirname=f"Ortho-MEC-Rel{ori}",
            )

    micmac.mosaic_micmac_tiles(
        filename='Z_Num8_DeZoom2_STD-MALT',
        dirname=f"MEC-Rel{ori}"
    )

# register the images to the reference DEM
register.register_relative(
    f"MEC-Rel{ori}",
    fn_ref,
    globstr=globstr,
    glacmask=glacmask,
    landmask=landmask,
    ori=ori,
    density=200,
    strategy='peaks',
    use_hillshade=True,
    subscript=ori
)
