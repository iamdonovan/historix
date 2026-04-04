import subprocess
from pathlib import Path
from spymicmac import asp


do_corr = True

p = subprocess.Popen(['gdaldem', 'hillshade', '-multidirectional', '-compute_edges',
                      'dem_blur.tif', 'dem_blur_hs.tif'])
p.wait()

# read the pairs file
with open('overlaps.txt', 'r') as f:
    pairs = [l.strip() for l in f.readlines()]

for nn, pair in enumerate(pairs, start=1):
    left, right = pair.split()

    p = subprocess.Popen(['dem_mosaic', '--dem-blur-sigma', '5', f"st_small/pair{nn}-DEM.tif",
                          '-o', f"dem_lowres_pair{nn}.tif"])
    p.wait()

    p = subprocess.Popen(['gdaldem', 'hillshade', '-multidirectional', '-compute_edges',
                          f"dem_lowres_pair{nn}.tif", f"dem_lowres_pair{nn}_hs.tif"])
    p.wait()

    if do_corr:
        p = subprocess.Popen(['parallel_stereo', '--correlator-mode', '--stereo-algorithm', 'asp_mgm',
                              '--subpixel-mode', '9', '--ip-per-tile', '1000',
                              f"dem_lowres_pair{nn}_hs.tif", 'dem_blur_hs.tif', f"warp/run{nn}"])
        p.wait()


    p = subprocess.Popen(['dem2gcp', '--warped-dem', f"dem_lowres_pair{nn}.tif", '--ref-dem', 'dem_blur.tif',
                          '--warped-to-ref-disparity', f"warp/run{nn}-F.tif",
                          '--left-image', left,
                          '--right-image', right,
                          '--left-camera', f"ba/all-{left.replace('.tif', '')}.tsai",
                          '--right-camera', f"ba/all-{right.replace('.tif', '')}.tsai",
                          '--match-file', f"ba/all-{left.replace('.tif', '')}__{right.replace('.tif','')}-clean.match",
                          '--gcp-sigma', '1.0',
                          '--max-num-gcp', '20000',
                          '--output-gcp', f"pair{nn}_dem.gcp"
                          ])
    p.wait()


ba_kwargs = {
    'intrinsics-to-float': 'all',
    'intrinsics-to-share': 'focal_length',
    'heights-from-dem': 'dem_blur.tif',
    'heights-from-dem-uncertainty': 10000,
    'ip-per-image': 100000,
    'ip-inlier-factor': 1000,
    'remove-outliers-params': "75.0 3.0 10 20",
    'overlap-list': 'overlaps.txt',
    'match-files-prefix': 'ba/all',
}

ba_flags = [
    'inline-adjustments',
    'solve-intrinsics'
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
        res = 10,
        fn_out = fn_img + '.map-ba.tif'
    )
