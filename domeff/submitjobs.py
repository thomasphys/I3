#!/usr/bin/env python
import os, sys
import subprocess

subprocess1 = subprocess.Popen(['lsof', '-i:'+str(port)],stdout=subprocess.PIPE)
        output, error = subprocess1.communicate()
        target_process = "python3"
        for line in output.splitlines() :
            if target_process in str(line) :
                pid = int(line.split(None,2)[1])
                os.kill(pid,9)

totaljobs = 0
jobcountproc = subprocess.Popen(['condor_q'],stdout=subprocess.PIPE)
jobcountout, error = jobcountproc.communicate()
for line in jobcountout.splitline() :
	sline = str(line)
	if "Total for tmcelroy" in sline :
		 jobarray = sline.split(",",100)
		 for job in jobarray :
		 	if "idle" in job :
		 		totaljobs += int(job.split(" ",2)[0]) 
		 	elif "running" in job :
		 		totaljobs += int(job.split(" ",2)[0]) 

avaliblejobs = 10000-totaljobs

jobcount = []
submission = []

jobfilelist = ["",
			   "",
			   ""] 

for filename in jobfilelist :
	file_object  = open(filename, "r") 	
	fl = file_object.readlines()
	for line in fl:
		data_array=str.split(line)
		jobcount.append(int(data_array[0]))
		submission.append(data_array[1])
			
