#!/usr/bin/env python
from pathlib import Path
from glob import glob
from spymicmac import micmac, register


globstr = 'F-*.tif' # fill in image pattern
local_crs = 32627 # need to fill in the crs to use
prefix = 'IL' # fill in prefix for study site
do_ortho = True # whether to make the ortho images
ori = 'FraserExtended' # change orientation directory if needed

glacmask = None # fill in path to optional glacier mask
fn_ref_pre = Path('..', '..', '..', 'aux_orthos') # fill in path to optional land mask
fn_dem_pre = Path('..', '..', '..', 'aux_dems') # fill in path to optional land mask

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

        micmac.tawny(f"Ortho-MEC-Rel{ori}")
        micmac.mosaic_micmac_tiles(
            filename = 'Orthophotomosaic',
            dirname=f"Ortho-MEC-Rel{ori}",
        )

    micmac.mosaic_micmac_tiles(
        filename='Z_Num8_DeZoom2_STD-MALT',
        dirname=f"MEC-Rel{ori}"
    )

for zoom in ['large', 'zoom']:
    fn_dem = fn_dem_pre / f"{prefix}_reference_dem_{zoom}.tif"
    landmask = fn_dem_pre / f"{prefix}_reference_dem_{zoom}_mask.tif"

    # register the images to the reference DEM
    register.register_relative(
        f"MEC-Rel{ori}",
        fn_dem,
        useortho = True,
        globstr = globstr,
        glacmask = glacmask,
        landmask = landmask,
        ori = ori,
        density = 200,
        strategy = 'peaks',
        use_hillshade = True,
        subscript = f"{ori}_{zoom}_dem",
        rap_txt = f"TerrainFinal_{ori}_{zoom}_dem_rapport.txt"
    )
