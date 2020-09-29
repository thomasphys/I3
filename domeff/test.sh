#!/bin/sh

BASE=/data/user/dgillcrist/dom_eff/my_simulation/corsika_test_sample
lim=367
for num in $(seq  0 1 9999); do
    if [ $num -ge 0 ]; then
        if [ ! -d sample_${num} ]; then
            mkdir ./sample_${num}
        fi    
        cp config.json ./sample_${num}/config-${num}.json
        len=$(awk 'END {print NR}' ./sample_${num}/config-${num}.json) 
        loc=$((len - 5))
        exp="${loc}s"
        sed -i "$exp/$/${num}/" ./sample_${num}/config-${num}.json
        (cd $BASE/sample_${num}/;
         chmod +x ~/template_submission_script.sh; 
         ~/template_submission_script.sh --ice $BASE/sample_${num}/config-${num}.json)
#        (cd $BASE/sample_${num}/;
#         chmod +x ~/misc/submitterfile.sh; 
#         ~/misc/submitterfile.sh python -m iceprod.core.i3exec -f $BASE/sample_${num}/config-${num}.json -d --offline)
    fi
    if [ $num -eq 99 ]; then
        break
    fi
done
