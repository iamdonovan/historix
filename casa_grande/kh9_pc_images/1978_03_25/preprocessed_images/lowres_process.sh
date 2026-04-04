#!/bin/bash

# must be same seed dem as was used for mapproject
seed_dem="dem_blur.tif"

# arguments to pass to parallel_stereo
ps_args="--stereo-algorithm asp_mgm --subpixel-mode 9 --corr-seed-mode 1"

nn=0
cat overlaps.txt | while read pair; do
  (( nn = nn + 1 ))
  parr=($pair);
  parallel_stereo ${parr[0]%.tif}.map-ba.tif ${parr[1]%.tif}.map-ba.tif ba/all-${parr[0]%.tif}.tsai ba/all-${parr[1]%.tif}.tsai st_small/pair$nn $seed_dem $ps_args

  point2dem st_small/pair$nn-PC.tif --tr 30
done
