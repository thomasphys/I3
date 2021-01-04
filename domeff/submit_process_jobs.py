#!/usr/bin/env python
import os, sys
import subprocess

opts = {}

opts["eff"] = sys.argv[1].replace("\n","")
opts["dir"] = sys.argv[2].replace("\n","")
opts["out"] = sys.argv[3].replace("\n","")
opts["flux"] = sys.argv[4].replace("\n","")

job_string = '''#!/bin/bash 

eval `/cvmfs/icecube.opensciencegrid.org/py2-v3.1.1/setup.sh`

/cvmfs/icecube.opensciencegrid.org/py2-v3.1.1/RHEL_7_x86_64/metaprojects/combo/V00-00-04/env-shell.sh /home/tmcelroy/icecube/domeff/CompilePlotData.py -e {}  -d {} -o {} -f {}

'''.format(opts["eff"],opts["dir"],opts["dir"]+opts["out"],opts["flux"])
procesfilename = opts["out"] + '.sh'
with open("/data/user/tmcelroy/domeff/jobscripts/" + procesfilename, 'w') as ofile:
	ofile.write(job_string)
	subprocess.Popen(['chmod','777',opts["out"] + 'jobscripts/' + procesfilename])

submit_string = '''
executable = /data/user/tmcelroy/domeff/jobscripts/{}

transfer_input_files = event.py,CompilePlotData.py

output = /home/tmcelroy/icecube/domeff/out/{}.out
error = /home/tmcelroy/icecube/domeff/error/{}.err
log = /scratch/tmcelroy/domeff/log/{}.log

Universe = vanilla
request_memory = 4GB
request_cpus = 1

notification = never

+TransferOutput=""

queue
'''.format(procesfilename,opts["out"],opts["out"],opts["out"])

submissionfilename = 'domeff_process_' + folder + '.submit'

with open('/data/user/tmcelroy/domeff/submissionscripts/' + submissionfilename, 'w') as ofile:
	ofile.write(submit_string)

submit = subprocess.Popen(['condor_submit',opts["out"] + '/submissionscripts/' + submissionfilename])