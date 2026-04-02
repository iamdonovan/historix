import subprocess
from pathlib import Path
import pandas as pd
import numpy as np
import lxml.etree as etree
import lxml.builder as builder
from spymicmac import micmac


def convert_gcp_measures_csv(fn_csv):

    gcps = pd.read_csv(fn_csv)

    with open('GCPs.txt', 'w') as f:
        print('#F= N X Y Z', file=f)
        print(f"#Here the coordinates are in UTM X=Easting Y=Northing Z=Altitude", file=f)
        for row in gcps.drop_duplicates('gcp_label').itertuples():
            print(row.gcp_label, row.x_map, row.y_map, row.elev, file=f)

    echo = subprocess.Popen('echo', stdout=subprocess.PIPE)
    p = subprocess.Popen(['mm3d', 'GCPConvert', 'AppInFile', 'GCPs.txt'], stdin=echo.stdout)
    p.wait()

    E = builder.ElementMaker()
    MesureSet = E.SetOfMesureAppuisFlottants()
    
    imlist = gcps['image_file_name'].unique().tolist() 
    
    for im in imlist:
        this_im_mes = E.MesureAppuiFlottant1Im(E.NameIm(im))

        for ind, row in gcps.loc[gcps['image_file_name'] == im].iterrows():
            this_mes = E.OneMesureAF1I(E.NamePt(str(row['gcp_label'])),
                                       E.PtIm(f"{row['x']} {row['y']}"))
            this_im_mes.append(this_mes)


        MesureSet.append(this_im_mes)

    tree = etree.ElementTree(MesureSet)
    tree.write("Measures-S2D.xml", pretty_print=True, xml_declaration=True, encoding="utf-8")


cam_csv = pd.read_csv('../camera_model_intrinsics.csv').loc[0]
film_size = [cam_csv['pixel_pitch'] * 9139] * 2

micmac.create_localchantier_xml(
    name='WildRC10',
    short_name='Wild RC10 UAgI',
    film_size=[np.round(f, 3) for f in film_size],
    pattern='ARBC.*tif',
    focal=cam_csv['focal_length'],
    add_sfs=True
)

convert_gcp_measures_csv('gcp.csv')
