#!/usr/bin/env python
import os, sys
import subprocess

opts = {}

opts["gcd"] = sys.argv[1]
opts["data"] = sys.argv[2]
opts["nevents"] = sys.argv[3]
opts["out"] = sys.argv[4]
opts["sim"] = sys.argv[6]
opts["subdir"] = sys.argv[5]

scratch = '/scratch/tmcelroy/domeff'

files_dir = opts["data"]
folderlist = files_dir.split("/",1000)
folder = folderlist[len(folderlist)-2] + '_' + folderlist[len(folderlist)-1]
file_list_aux = os.listdir(files_dir)
file_list = [x for x in file_list_aux if '.i3.zst' in x]

totaljobs = len(file_list)
filecutsuff = file_list[0].replace('.i3.zst', '')
filenamelist = filecutsuff.split("_",20)
filenameprefix = filenamelist[0]
for i in range(len(filenamelist)-2) :
	filenameprefix = filenameprefix + "_" + filenamelist[i+1]
filenameprefix = filenameprefix + "_"

startnumber = 9999999999
for file in file_list :
	filecutsuff_temp = file.replace('.i3.zst', '')
	filenamelist_temp = filecutsuff_temp.split("_",20)
	if int(filenamelist_temp[len(filenamelist_temp)-1])<startnumber :
		startnumber = int(filenamelist_temp[len(filenamelist_temp)-1])


job_string = '''#!/bin/bash 

eval `/cvmfs/icecube.opensciencegrid.org/py2-v3.1.1/setup.sh`

/cvmfs/icecube.opensciencegrid.org/py2-v3.1.1/RHEL_7_x86_64/metaprojects/combo/V00-00-04/env-shell.sh /home/tmcelroy/icecube/domeff/process_splineMPE_2015.py -g {} -d {} -r $1 -t .i3.zst -o {} -s {}

'''.format(opts["gcd"],files_dir+"/"+filenameprefix,opts["out"]+"/hd5/"+opts["subdir"]+filenameprefix,opts["sim"])
procesfilename = 'domeff_process_' + folder + '.sh'
with open(opts["out"] + '/jobscripts/' + procesfilename, 'w') as ofile:
	ofile.write(job_string)
	subprocess.Popen(['chmod','777',opts["out"] + '/jobscripts/' + procesfilename])

submit_string = '''
executable = {}/jobscripts/{}

transfer_input_files = domanalysis.py,event.py,general.py,geometry.py,process_splineMPE_2015.py,writeEvent.py

Arguments = $$([$(Process)+{}])
output = /home/tmcelroy/icecube/domeff/out/DOMeff_process_{}_$(Process).out
error = /home/tmcelroy/icecube/domeff/error/DOMeff_process_{}_$(Process).err
log = /scratch/tmcelroy/domeff/log/DOMeff_process_{}_$(Process).log

Universe = vanilla
request_memory = 4GB
request_cpus = 1

notification = never

+TransferOutput=""

queue {}
'''.format(opts["out"],procesfilename,str(startnumber),str(startnumber),str(startnumber),str(startnumber),str(totaljobs))

submissionfilename = 'domeff_process_' + folder + '.submit'

with open(opts["out"] + '/submissionscripts/' + submissionfilename, 'w') as ofile:
	ofile.write(submit_string)

submit = subprocess.Popen(['condor_submit',opts["out"] + '/submissionscripts/' + submissionfilename])
