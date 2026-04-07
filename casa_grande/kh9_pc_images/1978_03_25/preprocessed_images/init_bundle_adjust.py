import os
from pathlib import Path
import subprocess
from glob import glob
import pandas as pd
import geopandas as gpd
import geoutils as gu
from spymicmac import asp, micmac


def drop_low_overlaps(footprints, thresh=0.1):
    imlist = sorted(list(footprints['ID']))
    overlaps, pct_overlaps = micmac.pairs_from_footprints(imlist, footprints, prefix='', return_overlap=True)

    overlap_df = pd.DataFrame(data={'pair': overlaps,
                                    'pct_overlap': pct_overlaps,
                                    'sorted': [sorted(pair) for pair in overlaps]})
    overlap_df.drop_duplicates(subset='sorted', inplace=True)
    return overlap_df.loc[overlap_df['pct_overlap'] > thresh]


min_matches = 20 # minimum number of matches to accept as a valid overlap
map_res = 30 # resolution to project images to

footprints = gpd.read_file('Footprints.gpkg')
imlist = sorted(list(footprints['ID']))

# get images that overlap by at least 5%
overlap_df = drop_low_overlaps(footprints, thresh=0.05)

with open('overlaps.txt', 'w') as f:
    for pair in overlap_df['pair']:
        left, right = sorted(pair, reverse=True)
        if any([asp._isaft(left), asp._isaft(right)]) and not all([asp._isaft(left), asp._isaft(right)]):
            print(' '.join([left, right]), file=f)


ba_kwargs = {
    'intrinsics-to-float': 'other_intrinsics',
    'intrinsics-to-share': 'none',
    'heights-from-dem': 'dem_cropped.tif',
    'heights-from-dem-uncertainty': 1000,
    'ip-per-image': 100000,
    #'ip-inlier-factor': 100,
    'remove-outliers-params': "75 3 100 100",
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
    num_pass = 2,
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

    os.remove(fn_match.replace('.match', '.txt'))

footprints = []
for fn_img in imlist:
    asp.mapproject(
        fn_dem = 'dem_blur.tif',
        fn_img = fn_img + '.tif',
        fn_cam = Path('ba', f"all-{fn_img}.tsai"),
        res = map_res,
        fn_out = fn_img + '.map-ba.tif'
    )

#    gdf = asp.mapprojected_footprint(fn_img + '.map-ba.tif')
#    gdf['ID'] = fn_img
#    footprints.append(gdf)

#overlap_df = drop_low_overlaps(gpd.GeoDataFrame(pd.concat(footprints)), thresh=0.1)

with open('overlaps.txt', 'w') as f:
    #for pair in overlap_df['pair']:
    for pair in match_pairs:
        left, right = pair
        if any([asp._isaft(left), asp._isaft(right)]) and not all([asp._isaft(left), asp._isaft(right)]):
            print(' '.join([left, right]), file=f)
