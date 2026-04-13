#!/usr/bin/env python
import os
import subprocess
import argparse
from pathlib import Path
from glob import glob
import pandas as pd
from spymicmac import micmac, orientation


def main():
    parser = argparse.ArgumentParser(description="prepare files for submitting to HISTORIX.",
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('globstr', action='store', type=str,
                        help='Matching pattern for images to process (e.g., DZB*.tif).')
    parser.add_argument('crs', action='store', type=str,
                        help='EPSG code for the output CRS (e.g., 32627).')
    parser.add_argument('pitch', action='store', type=float,
                        help='pixel pitch (resolution in mm) of the images used')

    args = parser.parse_args()
    print(args)

    # experiments needs to have: ori-name, experiment code, details
    experiments_df = pd.read_csv("experiments.csv")

    os.makedirs('submission_files', exist_ok=True)

    # deliverable files:
    # - PREFIX_sparse_pointcloud.laz (sparse pointcloud output from aperi)
    # - PREFIX_dense_pointcloud.laz (sparse pointcloud output from nuage2ply)
    # - PREFIX_camera_model_extrinsics.csv (camera positions
    # - PREFIX_camera_model_intrinsics.csv
    for experiment in experiments_df.itertuples():
        imlist = sorted(glob(args.globstr))

        ori_df = orientation.load_all_orientation(f"Ori-{experiment.ori_final}", imlist).set_crs(int(args.crs))
        extrinsics = pd.DataFrame(data={'image_file_name': ori_df.name,
                                        'lon': ori_df.geometry.x,
                                        'lat': ori_df.geometry.y,
                                        'alt': ori_df.geometry.z})
        extrinsics.to_csv(
            Path('submission_files', '_'.join([experiment.code, 'camera_model_extrinsics.csv'])), index=False
        )

        cam_dict = micmac.load_cam_xml(Path(f"Ori-{experiment.ori_final}", experiment.fn_cam))

        intrinsics = pd.DataFrame(data={'focal_length': cam_dict['focal'] * args.pitch,
                                        'pixel_pitch': args.pitch,
                                        'principal_point_x_mm': cam_dict['pp'][0] * args.pitch,
                                        'principal_point_y_mm': cam_dict['pp'][1] * args.pitch,
                                        'K1': cam_dict['K1'],
                                        'K2': cam_dict['K2'],
                                        'K3': cam_dict['K3'],
                                        'center_dist_x_mm': cam_dict['cdist'][0] * args.pitch,
                                        'center_dist_y_mm': cam_dict['cdist'][1] * args.pitch}, index=[0])

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

        # convert the sparse pointcloud
        translate_args = ['pdal', 'translate', f"{experiment.ori_final}_sparse.ply",
                          Path('submission_files', f"{experiment.code}_sparse_pointcloud.laz"),
                          '-f', 'filters.reprojection',
                          f"--filters.reprojection.in_srs=EPSG:{args.crs}",
                          f"--filters.reprojection.out_srs=EPSG:{args.crs}"]

        p = subprocess.Popen(translate_args, stdout=subprocess.PIPE)
        p.wait()

        # now, convert the .ply files using pdal
        fn_dense_ply = Path('post_processed', f"{experiment.ori_final}.ply")

        if not Path('post_processed', f"{experiment.ori_final}.ply").exists():

            if len(glob(f"{experiment.ori_final}_block*.ply", root_dir='post_processed')) > 0:
                block_ply = sorted(glob(f"{experiment.ori_final}_block*.ply", root_dir='post_processed'))

                merge_args = ['pdal', 'translate']
                merge_args.extend([Path('post_processed', fn) for fn in block_ply])
                merge_args.append(fn_dense_ply)

                print(merge_args)
                p = subprocess.Popen(merge_args, stdout=subprocess.PIPE)
                p.wait()

        translate_args = ['pdal', 'translate', fn_dense_ply,
                          Path('submission_files', experiment.code + '_dense_pointcloud.laz'),
                          '-f', 'filters.reprojection',
                          f"--filters.reprojection.in_srs=EPSG:{args.crs}",
                          f"--filters.reprojection.out_srs=EPSG:{args.crs}"]

        p = subprocess.Popen(translate_args, stdout=subprocess.PIPE)
        p.wait()


if __name__ == "__main__":
    main()
