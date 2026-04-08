#!/usr/bin/env python
import argparse
from pathlib import Path
from glob import glob
from spymicmac import micmac


def main():
    parser = argparse.ArgumentParser(description="process DEMs for an orientation directory",
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('ori', action='store', type=str,
                        help='Name of orientation directory (after Ori-).')
    parser.add_argument('globstr', action='store', type=str,
                        help='Matching pattern for images to process (e.g., DZB*.tif).')
    parser.add_argument('local_crs', action='store', type=str,
                        help='EPSG code for the output CRS (e.g., 32627).')
    parser.add_argument('prefix', action='store', type=str,
                        help='Prefix for the HISTORIX test cite (should be either CG or IL).')
    parser.add_argument('out_dir', action='store', type=str,
                        help='Output directory for results.')
    parser.add_argument('--do_ortho', action='store_true',
                        help='Process ortho images as part of Malt (default: False).')
    parser.add_argument('--as_block', action='store_true',
                        help='Process using spymicmac.block_malt (default: False).')

    args = parser.parse_args()
    print(args)

    malt_kwargs = {
        'dirmec': f"MEC-{args.ori}",
        'zoomf': 1,
        'cost_trans': 4,
        'szw': 3,
        'regul': 0.1,
        'do_ortho': args.do_ortho,
        'clean': True
    }

    # create the absolute dem/orthophotos
    if args.as_block:
        imlist = sorted(glob(args.globstr))
        micmac.block_malt(
            imlist,
            f"Terrain{args.ori}",
            nimg=2,
            malt_kwargs=malt_kwargs
        )
        for ind, block in enumerate(glob(f"MEC-{args.ori}_block*/")):
            # create the orthomosaic
            if args.do_ortho:
                micmac.tawny(block)

            # clean up the outputs
            micmac.post_process(
                out_dir=Path(args.out_dir, 'post_processed'),
                projstr=args.local_crs,
                out_name=f"Terrain{args.ori}_block{ind}",
                dirmec=block,
                do_ortho=args.do_ortho,
                ind_ortho=False,
                do_ply=True
            )

    else:
        micmac.malt(
            args.globstr.replace('*.', '.*'),
            f"Terrain{args.ori}",
            **malt_kwargs
        )

    if args.do_ortho:
        micmac.tawny(f"MEC-{args.ori}")

    # clean up the outputs
    micmac.post_process(
        out_dir=Path(args.out_dir, 'post_processed'),
        projstr=args.local_crs,
        out_name=f"Terrain{args.ori}",
        dirmec=f"MEC-{args.ori}",
        do_ortho=args.do_ortho,
        ind_ortho=False,
        do_ply=True
    )


if __name__ == "__main__":
    main()
