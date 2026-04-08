#!/usr/bin/env python
from spymicmac import micmac


globstr = 'F-*.tif' # fill in image pattern
local_crs = 32627 # need to fill in the crs to use
do_ortho = True # whether to make the ortho images

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
