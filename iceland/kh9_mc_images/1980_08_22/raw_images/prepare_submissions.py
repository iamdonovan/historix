#!/usr/bin/env python
import os
import subprocess
from pathlib import Path
from glob import glob
import pandas as pd
from spymicmac import micmac, orientation


globstr = 'OIS*.tif' # need to fill in with image matching pattern
crs = 32627 # need to fill in with epsg code
pitch = 1/140 # need to fill in with pixel pitch of images

# experiments needs to have: ori-name, experiment code, details
experiments_df = pd.read_csv("experiments.csv")

os.makedirs('submission_files', exist_ok=True)

# deliverable files:
# - PREFIX_sparse_pointcloud.laz (sparse pointcloud output from aperi)
# - PREFIX_dense_pointcloud.laz (sparse pointcloud output from nuage2ply)
# - PREFIX_camera_model_extrinsics.csv (camera positions
# - PREFIX_camera_model_intrinsics.csv
for experiment in experiments_df.itertuples():
    imlist = sorted(glob(globstr))

    ori_df = orientation.load_all_orientation(f"Ori-{experiment.ori_final}", imlist).set_crs(crs)
    extrinsics = pd.DataFrame(data={'image_file_name': ori_df.name,
                                    'lon': ori_df.geometry.x,
                                    'lat': ori_df.geometry.y,
                                    'alt': ori_df.geometry.z})
    extrinsics.to_csv(
        Path('submission_files', '_'.join([experiment.code, 'camera_model_extrinsics.csv'])), index=False
    )

    cam_dict = micmac.load_cam_xml(Path(f"Ori-{experiment.ori_final}", experiment.fn_cam))

    intrinsics = pd.DataFrame(data={'focal_length': cam_dict['focal'] * pitch,
                                    'pixel_pitch': pitch,
                                    'principal_point_x_mm': cam_dict['pp'][0] * pitch,
                                    'principal_point_y_mm': cam_dict['pp'][1] * pitch,
                                    'K1': cam_dict['K1'],
                                    'K2': cam_dict['K2'],
                                    'K3': cam_dict['K3'],
                                    'center_dist_x_mm': cam_dict['cdist'][0] * pitch,
                                    'center_dist_y_mm': cam_dict['cdist'][1] * pitch}, index=[0])

    for coeff in ['K4', 'K5']:
        cols = list(intrinsics.columns)
        if coeff in cam_dict.keys():
            intrinsics[coeff] = cam_dict[coeff]
            ind = cols.index('center_dist_x_mm')
            cols.insert(ind, coeff)
            intrinsics = intrinsics[cols]
    else:
        cols = intrinsics.columns

    if 'P1' in cam_dict.keys():
        cols = list(intrinsics.columns)

        for coeff in ['P1', 'P2', 'b1', 'b2']:
            intrinsics[coeff] = cam_dict[coeff]
            ind = cols.index('center_dist_x_mm')
            cols.insert(ind, coeff)
            intrinsics = intrinsics[cols]
    else:
        cols = intrinsics.columns

    intrinsics[cols].to_csv(
        Path('submission_files', '_'.join([experiment.code, 'camera_model_intrinsics.csv'])), index=False
    )

    # create the sparse pointcloud
    micmac.apericloud(
        experiment.ori_final,
        globstr.replace('*.', '.*'),
        fn_out = f"{experiment.ori_final}_sparse.ply",
        with_cam = False
    )
    # convert the sparse pointcloud
    translate_args = ['pdal', 'translate', f"{experiment.ori_final}_sparse.ply",
                      Path('submision_files', experiment.code + '_sparse_pointcloud.laz'),
                      '-f', 'filters.reprojection',
                      f"--filters.reprojection.in_srs=EPSG:{crs}",
                      f"--filters.reprojection.out_srs=EPSG:{crs}"]

    p = subprocess.Popen(translate_args, stdout=subprocess.PIPE)
    p.wait()

    # now, convert the .ply files using pdal
    fn_dense_ply = Path('post_processed', f"Terrain{experiment.ori_final}.ply")

    translate_args = ['pdal', 'translate', fn_dense_ply,
                      Path('submission_files', experiment.code + '_dense_pointcloud.laz'),
                      '-f', 'filters.reprojection',
                      f"--filters.reprojection.in_srs=EPSG:{crs}",
                      f"--filters.reprojection.out_srs=EPSG:{crs}"]

    p = subprocess.Popen(translate_args, stdout=subprocess.PIPE)
    p.wait()
