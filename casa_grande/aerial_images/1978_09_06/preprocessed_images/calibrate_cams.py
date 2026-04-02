from pathlib import Path
from spymicmac import micmac

globstr = 'ARBC*.tif'

micmac.tapioca(
    img_pattern=globstr.replace('*.', '.*'),
    res_low=400,
    res_high=1200
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
        lib_cd=False,
        dir_homol='Homol_mini'
    )

# extended fraser
micmac.tapas(
    cam_model='RadialExtended',
    img_pattern=globstr.replace('*.', '.*'),
    lib_foc=False,
    lib_pp=False,
    lib_cd=False,
    ori_out='FraserExtended',
    dir_homol='Homol_mini'
)

fn_cam = 'AutoCal_Foc-152865_Cam-WildRC10.xml'
cam = micmac.load_cam_xml(Path('Ori-FraserExtended', fn_cam))
micmac.write_cam_xml(Path('Ori-FraserExtended', fn_cam), cam)
