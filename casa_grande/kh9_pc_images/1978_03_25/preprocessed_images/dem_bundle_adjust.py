import os
import subprocess
from pathlib import Path
from spymicmac import asp, data


map_res = 12 # resolution to project images to

# read the pairs file
with open('overlaps.txt', 'r') as f:
    pairs = [l.strip() for l in f.readlines()]

for nn, pair in enumerate(pairs, start=1):
    if not Path('st_small', f"pair{nn}-DEM.tif").exists():
        print(f"No DEM found for pair {nn}, skipping.")
        continue
    else:
        left, right = pair.split()
        asp.gcps_from_dem(
            (left, right),
            fn_dem = f"st_small/pair{nn}-DEM.tif",
            fn_ref = 'dem_cropped.tif',
            camera_prefix = 'ba/all',
            fn_gcp = f"pair{nn}_dem.gcp",
            warp_prefix = f"warp/run{nn}"
        )


ba_kwargs = {
    'intrinsics-to-float': 'all',
    'intrinsics-to-share': 'focal_length',
    'heights-from-dem': 'dem_cropped.tif',
    'heights-from-dem-uncertainty': 10000,
    'ip-per-image': 100000,
    'ip-inlier-factor': 1000,
    'remove-outliers-params': "75.0 3.0 3 5",
    'overlap-list': 'overlaps.txt',
    #'match-files-prefix': 'ba/all',
}

ba_flags = [
    'inline-adjustments',
    'solve-intrinsics',
    'use-lon-lat-height-gcp-error'
]

asp.bundle_adjust(
    'D3C*.tif',
    'ba_gcp/all',
    gcp_patt = 'pair*_dem.gcp',
    session_type = 'opticalbar',
    num_iter = 20,
    num_pass = 3,
    ba_kwargs = ba_kwargs,
    ba_flags = ba_flags
)

imlist = sorted(set([pp for pair in pairs for pp in pair.split(' ')]))
for fn_img in imlist:
    asp.mapproject(
        fn_dem = 'dem_blur.tif',
        fn_img = fn_img + '.tif',
        fn_cam = Path('ba', f"all-{fn_img}.tsai"),
        res = map_res,
        fn_out = fn_img + '.map-ba.tif'
    )
