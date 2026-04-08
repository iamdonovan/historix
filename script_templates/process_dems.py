#!/usr/bin/env python
from glob import glob
from spymicmac import micmac


globstr = '' # fill in image pattern
local_crs = '' # need to fill in the crs to use
prefix = '' # fill in prefix for study site
do_ortho = False # whether to make the ortho images

# update orientation names as needed
for ori in ['RadialBasic', 'RadialExtended', 'FraserBasic', 'FraserExtended', 'Final_FraserExtended']:

    malt_kwargs = {
        'dirmec': f"MEC-{ori}",
        'zoomf': 1,
        'cost_trans': 4,
        'szw': 3,
        'regul': 0.1,
        'do_ortho': do_ortho,
        'clean': True
    }

    # create the absolute dem/orthophotos
    imlist = sorted(glob(globstr))
    micmac.block_malt(
        imlist,
        ori,
        nimg=2,
        malt_kwargs=malt_kwargs
    )

    for ind, block in enumerate(glob(f"MEC-{ori}_block*/")):
        # create the orthomosaic
        if do_ortho:
            micmac.tawny(block)

        # clean up the outputs
        micmac.post_process(
            projstr=local_crs,
            out_name=f"Terrain{ori}_block{ind}",
            dirmec=block,
            do_ortho=do_ortho,
            ind_ortho=False,
            do_ply=True
        )
