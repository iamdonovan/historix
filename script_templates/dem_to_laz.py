import os
import argparse
from pathlib import Path
import numpy as np
import rasterio as rio
import xdem
import pdal
import pandas as pd


def raster2points(fn_dem, fn_out, width, height):
    with open(fn_out, 'w') as f:
        print('x y z', file=f)

    with rio.open(fn_dem) as src:
        for row_off in np.arange(0, src.height + 1, height):
            if row_off + height > src.height:
                this_height = src.height - row_off
            else:
                this_height = height

            for col_off in np.arange(0, src.width + 1, width):
                if col_off + width > src.width:
                    this_width = src.width - col_off
                else:
                    this_width = width

                window = rio.windows.Window(col_off, row_off, this_width, this_height)

                tile = src.read(1, window=window)
                tile[tile == src.nodata] = np.nan

                tile_dem = xdem.DEM.from_array(tile, src.window_transform(window), src.crs, nodata=src.nodata)

                pc = tile_dem.to_pointcloud(data_column_name='z', force_pixel_offset='center')
                pc['x'] = pc.geometry.x
                pc['y'] = pc.geometry.y

                pc.ds[['x', 'y', 'z']].to_csv(fn_out, sep=' ', mode='a', index=False, header=False)


def main():
    parser = argparse.ArgumentParser(description="process DEMs for an orientation directory",
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('local_crs', action='store', type=str,
                        help='EPSG code for the output CRS (e.g., 32627).')

    args = parser.parse_args()
    print(args)

    experiments_df = pd.read_csv('experiments.csv')

    for experiment in experiments_df.itertuples():
        raster2points(Path('post_processed', f"{experiment.ori_final}_Z.tif"),
                      'tmp_pc.txt', 8000, 8000)

        reproj = f"""
        [
            "tmp_pc.txt",
            {{
                "type": "filters.reprojection",
                "in_srs": "EPSG:{args.local_crs}",
                "out_srs": "EPSG:{args.local_crs}"
            }},
            "post_processed/{experiment.ori_final}.laz"
        ]
        """

        pipeline = pdal.Pipeline(reproj)
        pipeline.execute()

        os.remove('tmp_pc.txt')


if __name__ == "__main__":
    main()
