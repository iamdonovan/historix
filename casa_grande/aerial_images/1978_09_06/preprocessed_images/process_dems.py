#!/usr/bin/env python
from spymicmac import micmac


globstr = 'ARBC*.tif' # fill in image pattern
local_crs = 6341 # need to fill in the crs to use
prefix = 'CG' # fill in prefix for study site
do_ortho = False # whether to make the ortho images

# update orientation names as needed
for ori in ['RadialBasic', 'RadialExtended', 'FraserBasic', 'FraserExtended', 'Final_FraserExtended']:

    # create the absolute dem/orthophotos
    micmac.malt(
        globstr.replace('*.', '.*'),
        f"Terrain{ori}",
        dirmec=f"MEC-{ori}",
        zoomf=1,
        cost_trans=4,
        szw=3,
        regul=0.1,
        clean=True
    )

    # create the orthomosaic
    if do_ortho:
        micmac.tawny(f"MEC-{ori}")

    # clean up the outputs
    micmac.post_process(
        projstr=local_crs,
        out_name=f"Terrain{ori}",
        dirmec=f"MEC-{ori}",
        do_ortho=True,
        ind_ortho=False,
        do_ply=True
    )
