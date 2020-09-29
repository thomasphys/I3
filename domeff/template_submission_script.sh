#!/bin/bash 

# This is a base template submission script to submit to npx with.
# Whenever using this script there are a few options that need to 
# used when running. Those are --new, --old, and --ice. These are 
# the options that get parsed forward to specify the the varaible
# environment and, if relevant, the corresponding metaproject. Old 
# is py2-v3.1.1 environment with the V00-00-01 combo metaproject. 
# New is a precompiled combo built from py3-4.0.1. And Ice is the
# shell protocol for running IceProd config.json files interactively.
# You will need to specify the ammount of memory, gpus, and cpus your
# job requires.

# Please specify your file here, either in a raw directory string with options given in the submit line
# or you may define $FILE as a $(echo "...") statement which includes your arguments. It may also be called 
# as an input argument
FILE=/data/user/dgillcrist/test-dir/validator.py
if [[ $# -gt 1 ]]; then
    FILE="${@:2}"
fi

New=$(echo "/data/user/dgillcrist/dom_eff/metaproject/py3-v4.1.0/RHEL_7/combo/build/env-shell.sh python $FILE")
Old=$(echo "/data/user/dgillcrist/dom_eff/metaproject/py2-v3.1.1/RHEL_7combo/build/env-shell.sh python $FILE")
Ice=$(echo "python -m iceprod.core.i3exec -f $FILE -d --offline")

switch=true
if [[ -z $1 ]]; then
    switch=null
else
    case $1 in
    
        '--new')
            declare -a pairs=('new' $New) ;;
    
        '--old')
            declare -a pairs=('old' $Old) ;;
    
        '--ice')
            declare -a pairs=('ice' $Ice) ;;
    
        *)
            switch=false ;;
    
    esac
fi

meta="${pairs[0]}"
gpu=0
cpu=1
mem='3GB'

if [ "$switch" == true ]; then
    # This is the submit line. --gpu, --cpu, and --mem options may be omitted, as the 
    # ~/submit_npx.sh script will default to set values. --meta is necessary and must not 
    # removed. --BREAK is necessary as it is required to separate options for ~/submit_npx 
    # and the arguments needed for the npx-execs files.
    ~/submit_npx3.sh --meta $meta --gpu $gpu --cpu $cpu --mem $mem --BREAK "${pairs[@]:1}"
elif [ "$switch" == null ]; then
    echo "Error: Please choose environment type, either --new, --old, or --ice"
elif [ "$switch" == false ]; then
    echo "Error: Invalid options where chosen for the environent. Choices are --new, --old, --ice"
fi
