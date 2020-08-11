eval `/cvmfs/icecube.opensciencegrid.org/py2-v3.1.1/setup.sh` 
#source /cvmfs/icecube.opensciencegrid.org/py2-v3.1.1/RHEL_7_x86_64/metaprojects/combo/V00-00-04/env-shell.sh

export i3env=/cvmfs/icecube.opensciencegrid.org/py2-v3.1.1/RHEL_7_x86_64/metaprojects/combo/V00-00-04/env-shell.sh
#i3src=/cvmfs/icecube.opensciencegrid.org/py2-v3.1.1/RHEL_7_x86_64/metaprojects/combo/V00-00-04/
export level1script=/cvmfs/icecube.opensciencegrid.org/py2-v3.1.1/RHEL_7_x86_64/metaprojects/combo/V00-00-04/filterscripts/resources/scripts/SimulationFiltering.py
export level2script=/cvmfs/icecube.opensciencegrid.org/py2-v3.1.1/RHEL_7_x86_64/metaprojects/combo/V00-00-04/filterscripts/resources/scripts/offlineL2/process.py
export i3data=/cvmfs/icecube.opensciencegrid.org/data 
export GCD_FILE=$i3data/GCD/GeoCalibDetectorStatus_AVG_55697-57531_PASS2_SPE_withScaledNoise.i3.gz

$i3env $level1script -g $GCD_FILE -i test3.i3.gz -o test_l1.i3.gz

$i3env $level2script -g $GCD_FILE -i test_l1.i3.gz -o test_l2.i3.gz
