#!/bin/bash

tmpdir=/tmp/scratch/malt
cwd=$(pwd)

globstr=''
crs=''
prefix=''

mkdir -p $tmpdir
cp -v $globstr $tmpdir

cat ori_list.txt | while read ori; do
  cp -rv Ori-$ori $tmpdir;
done

cp ori_list.txt $tmpdir

cd $tmpdir

cat ori_list.txt | while read ori; do
  python ~/data/historix/script_templates/process_dems.py $ori "$globstr" $crs $prefix $cwd #--as_block

  rm -r MEC-$ori*
done
