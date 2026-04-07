import subprocess
from pathlib import Path
import re
import geopandas as gpd
from spymicmac import asp, data


prefix = 'CG'
map_res = 12 # resolution to project images to

fn_dem = Path('..', '..', '..', 'aux_dems', f"{prefix}_reference_dem_large.tif") # fill in path to optional land mask
fn_footprints = Path('..', 'images_footprint.geojson')

masked_dem = data.crop_mask_dem(fn_dem, fn_footprints, buff=10000)
masked_dem.to_file('dem_cropped.tif')

p = subprocess.Popen(['dem_mosaic', '--dem-blur-sigma', '5', 'dem_cropped.tif', '-o', 'dem_blur.tif'])
p.wait()

footprints = gpd.read_file(Path('..', 'images_footprint.geojson'))
cols = footprints.columns
new_cols = [re.sub(' +', ' ', col) for col in cols] # remove extra spaces in column names
footprints.rename(columns=dict(zip(cols, new_cols)), inplace=True)

footprints['ID'] = footprints['Entity ID']
footprints.to_file('Footprints.gpkg')


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
        res = map_res,
        fn_out = fn_img + '.map-init.tif'
    )
