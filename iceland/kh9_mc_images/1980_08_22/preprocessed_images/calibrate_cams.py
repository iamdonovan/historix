#!/usr/bin/env python
from pathlib import Path
from spymicmac import micmac

globstr = 'DZB*.tif'
tapioca_res = 8000 # have to fill in with maximum res for tapioca mulscale.
focal = 304.8 # fill in with focal length (in mm) from calibration report / intrinsics
camname = 'KH9MC' # fill in with camera name from convert_gpcs.py

micmac.tapioca(
    img_pattern=globstr.replace('*.', '.*'),
    res_low=400,
    res_high=tapioca_res
)

micmac.schnaps(
    img_pattern=globstr.replace('*.', '.*')
)

models = ['RadialBasic', 'RadialExtended', 'FraserBasic']

for cam in models:
    micmac.tapas(
        cam_model=cam,
        img_pattern=globstr.replace('*.', '.*'),
        lib_foc=False,
        lib_pp=False,
        lib_cd=False
    )

# extended fraser - radialextended + decentric, affine corrections
micmac.tapas(
    cam_model='RadialExtended',
    img_pattern=globstr.replace('*.', '.*'),
    lib_foc=False,
    lib_pp=False,
    lib_cd=False,
    ori_out='FraserExtended'
)

fn_cam = f"AutoCal_Foc-{int(focal*1000)}_Cam-{camname}.xml" # fill in with
cam = micmac.load_cam_xml(Path('Ori-FraserExtended', fn_cam))
micmac.write_cam_xml(Path('Ori-FraserExtended', fn_cam), cam)
