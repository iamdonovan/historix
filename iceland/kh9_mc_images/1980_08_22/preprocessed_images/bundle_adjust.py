#!/usr/bin/env python
import os
from pathlib import Path
import pandas as pd
import geopandas as gpd
import numpy as np
from spymicmac import micmac, register


os.makedirs('plots', exist_ok=True)

globstr = 'DZB*.tif' # need to fill in with image matching pattern
crs = 32627 # need to fill in with epsg code

models = ['RadialBasic', 'RadialExtended', 'FraserBasic', 'FraserExtended']

gcps = pd.read_csv('GCPs.txt', delimiter=' ', header=2, names=['id', 'x', 'y', 'elevation'])
gcps['id'] = gcps['id'].astype(str)

gcps = gpd.GeoDataFrame(gcps, geometry=gpd.points_from_xy(gcps.x, gcps.y, crs=crs))
gcps.drop(columns=['x', 'y']).to_file('GCPs.gpkg')

for cam in models:
    gcps = gpd.read_file('GCPs.gpkg')
    gcps = micmac.bascule(
        gcps,
        outdir='.',
        img_pattern=globstr.replace('*.', '.*'),
        sub='',
        ori=cam,
        outori='Init' + cam,
        fn_gcp='GCPs',
        fn_meas='Measures'
    )

    gcps = micmac.campari(
        gcps,
        outdir='.',
        img_pattern=globstr.replace('*.', '.*'),
        sub='',
        fn_gcp='GCPs',
        fn_meas='Measures',
        inori='Init' + cam,
        outori='Terrain' + cam,
        allfree=True,
        sig_abs=5,
        sig_pix=1,
        rap_txt=f"Terrain{cam}_rapport.txt"
    )

    gcps['camp_xy'] = np.sqrt(gcps.camp_xres ** 2 + gcps.camp_yres ** 2)

    fig = register._plot_residuals(gcps.dropna())
    fig.savefig(Path('plots', f"{cam}_gcp_residuals.png"), bbox_inches='tight', dpi=200)
