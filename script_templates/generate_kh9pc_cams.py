import subprocess
from pathlib import Path
import geopandas as gpd
from spymicmac import asp, data


prefix = ''
fn_dem = Path('..', '..', '..', 'aux_dems', f"{prefix}_reference_dem_large.tif") # fill in path to optional land mask
fn_footprints = Path('..', 'images_footprint.geojson')

masked_dem = data.crop_mask_dem(fn_dem, fn_footprints, buff=10000)
masked_dem.to_file('dem_cropped.tif')

p = subprocess.Popen(['dem_mosaic', '--dem-blur-sigma', '5', 'dem_cropped.tif', '-o', 'dem_blur.tif'])
p.wait()

footprints = gpd.read_file(fn_footprints)
footprints['ID'] = footprints['Entity ID']

for fn_img in footprints['ID']:
    if asp._isaft(fn_img):
        north_up = False
    else:
        north_up = True

    asp.cam_from_footprint(fn_img + '.tif', 'KH9', scan_res=7e-6, fn_dem='dem_blur.tif', north_up=north_up,
                           footprints=footprints, mean_el=None)

    asp.mapproject(
        fn_dem = 'dem_blur.tif',
        fn_img = fn_img + '.tif',
        fn_cam = fn_img + '.tsai',
        res = 20,
        fn_out = fn_img + '.map-init.tif'
    )
