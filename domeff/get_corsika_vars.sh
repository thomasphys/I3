#!/bin/sh
BASE=$(pwd)
dir_list=($(ls -d /data/sim/IceCube/2019/generated/CORSIKA-in-ice/21269/*/signal/test/))

for DIR in ${dir_list[@]}; do
    $BASE/template_submission_script.sh --new $BASE/full-cor_to_pkl.py --dir $DIR
done
