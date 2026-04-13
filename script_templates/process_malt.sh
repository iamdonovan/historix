#!/bin/bash

globstr=''
crs=''
prefix=''

cat ori_list.txt | while read ori; do
  python ~/data/historix/script_templates/process_dems.py $ori "$globstr" $crs $prefix #--as_block
done
