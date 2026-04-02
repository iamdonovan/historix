from pathlib import Path
from spymicmac import micmac

globstr = 'DZB*.tif'

micmac.tapioca(
    img_pattern=globstr.replace('*.', '.*'),
    res_low=400,
    res_high=8000
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

# extended fraser
micmac.tapas(
    cam_model='RadialExtended',
    img_pattern=globstr.replace('*.', '.*'),
    lib_foc=False,
    lib_pp=False,
    lib_cd=False,
    ori_out='FraserExtended'
)

fn_cam = 'AutoCal_Foc-304800_Cam-KH9MC.xml'
cam = micmac.load_cam_xml(Path('Ori-FraserExtended', fn_cam))
micmac.write_cam_xml(Path('Ori-FraserExtended', fn_cam), cam)
