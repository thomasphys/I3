import json
import argparse
import os, sys

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', help='Input good run list.',type=str,default = '')
parser.add_argument('-o', '--output', help='Output file list.',type=str,default = '')
args = parser.parse_args()

def GetDay(date) :
	datelist = date.split(" ",1)
	yyyymmdd = datelist[0].split("-",2)
	return int(yyyymmdd[2])

def GetMonth(date) :
	datelist = date.split(" ",1)
	yyyymmdd = datelist[0].split("-",2)
	return int(yyyymmdd[1])

def GetYear(date) :
	datelist = date.split(" ",1)
	yyyymmdd = datelist[0].split("-",2)
	return int(yyyymmdd[0])

def GetDuration(start,stop) :
        startlist = start.split(" ",1)
        stoplist = stop.split(" ",1)

        starttimelist = startlist[1].split(":",2)
        stoptimelist = stoplist[1].split(":",2)

        start_hour = float(starttimelist[0])
        start_min = float(starttimelist[1])
        start_sec = float(starttimelist[2])

        stop_hour = float(stoptimelist[0])
        stop_min = float(stoptimelist[1])
        stop_sec = float(stoptimelist[2])

        duration = 3600.*(stop_hour-start_hour) + 60.*(stop_min-start_min) + (stop_sec-start_sec)
        if GetDay(start) != GetDay(stop) :
                duration += 3600.*24.

        return duration

file = open(args.input,'r')
data = json.load(file)

runnum = []
runbin = []
length = [ 0.0 for i in range(12*31)]

for run in data['runs']:
	if 'short' in run['reason_i3'] :
		#print(run['reason_i3']) 
		continue
	if 'failed' in run['reason_i3'] :
		#print(run['reason_i3'])
		continue
	if 'short' in run['reason_it'] :
		#print(run['reason_it'])
		continue
	if 'failed' in run['reason_it'] :
		#print(run['reason_it'])
		continue

	runnum.append(int(run['run']))
	month = GetMonth(run['good_tstart'])
	day = GetDay(run['good_tstart'])
	year = GetYear(run['good_tstart'])
	runbin.append((month-1)*31+(day-1))

	#print("data = %d %d %d bin = %d duration = %f"% (year,month,day,runbin[-1],GetDuration(run['good_tstart'],run['good_tstop'])))
	length[runbin[-1]] += GetDuration(run['good_tstart'],run['good_tstop'])

min_val = 9999999999
for value in length :
	if value > 0.0 and value < min_val :
		min_val = value
file.close()

file = open(args.output,'w')

for i in range(len(runnum)) :
	file.write("%d %f\n" % (runnum[i],min_val/length[runbin[i]]))

for i in range(1,13) :
	for j in range(1,32) :
		if length[(i-1)*31+(j-1)] == 0.0 :
			print("%d %d" % (i,j))

file.close()

