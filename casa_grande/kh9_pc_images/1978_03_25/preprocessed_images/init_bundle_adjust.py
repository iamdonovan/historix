from pathlib import Path
import subprocess
from glob import glob
import geopandas as gpd
from spymicmac import asp, micmac


min_matches = 20 # minimum number of matches to accept as a valid overlap

footprints = gpd.read_file('Footprints.gpkg')
imlist = sorted(list(footprints['ID']))

# write the initial set of image overlaps, based on the footprints
overlaps = micmac.pairs_from_footprints(imlist, footprints, prefix='')
sorted(set(tuple(sorted(pair)) for pair in overlaps))

with open('overlaps.txt', 'w') as f:
    for pair in overlaps:
        print(' '.join(pair), file=f)


ba_kwargs = {
    'intrinsics-to-float': 'other_intrinsics',
    'intrinsics-to-share': 'none',
    'heights-from-dem': 'dem_blur.tif',
    'heights-from-dem-uncertainty': 10000,
    'ip-per-image': 100000,
    'ip-inlier-factor': 1000,
    'remove-outliers-params': "75 3 1000 1000",
    'overlap-list': 'overlaps.txt'
}

ba_flags = [
    'inline-adjustments',
    'solve-intrinsics'
]

asp.bundle_adjust(
    'D3C*.tif',
    'ba/all',
    map_suffix = 'map-init.tif',
    num_iter = 30,
    num_pass = 3,
    ba_kwargs = ba_kwargs,
    ba_flags = ba_flags
)

matchlist = sorted(glob('all*clean.match', root_dir='ba'))
match_pairs = []

# parse match files to figure out which pairs of images actually overlap
for fn_match in matchlist:
    p = subprocess.Popen(['parse_match_file.py', Path('ba', fn_match), fn_match.replace('.match', '.txt')])
    p.wait()

    left, right = fn_match.split('__')
    left = left.split('all-')[-1] + '.tif'
    right = right.split('-clean.match')[0] + '.tif'

    with open(fn_match.replace('.match', '.txt'), 'r') as f:
        num_matches = int(f.readline().strip().split()[0])
        if num_matches > min_matches:
            match_pairs.append((left, right))

# re-write the overlapping images based on the initial bundle adjustment
with open('overlaps.txt', 'w') as f:
    for pair in match_pairs:
        print(' '.join(pair), file=f)


for fn_img in imlist:
    asp.mapproject(
        fn_dem = 'dem_blur.tif',
        fn_img = fn_img + '.tif',
        fn_cam = Path('ba', f"all-{fn_img}.tsai"),
        res = 10,
        fn_out = fn_img + '.map-ba.tif'
    )
