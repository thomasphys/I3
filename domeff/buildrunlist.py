import json
import argparse
import os, sys
import ROOT

Datacondition_have = ['.tar.bz2','Run','Subrun','PFFilt']
Datacondition_nothave = ['_IT']
GDCcondition_have = ['.i3.','Run','GCD','Level2pass2']
GDCcondition_nothave = ['_IT']

prescale = 1.0

def checkfilename(filename, cond_have, cond_nothave) :

	print(filename)
        for cond in cond_have :
                if cond not in filename :
                        return False
        for cond in cond_nothave :
                if cond in filename :
                        return False
        return True

def checkrunnum(filename, runnumber) :
	if str(runnumber) not in filename :
		return False
	return True

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', help='Input good run list.',type=str,default = '')
parser.add_argument('-o', '--output', help='Output file list.',type=str,default = '')
args = parser.parse_args()

#leave out leap years
monthdays = [31,28,31,30,31,30,31,31,30,31,30,31]

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
length = [ 0.0 for i in range(sum(monthdays))]

runlistyear = 0000
first = True

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
	if(monthdays[month-1] < day) :
		runbin.append(-1)
		continue
	year = GetYear(run['good_tstart'])
	runbin.append(sum([monthdays[i] for i in range(month-1)]) + day-1)

	if first :
		runlistyear = year
		first = False

	#print("data = %d %d %d bin = %d duration = %f"% (year,month,day,runbin[-1],GetDuration(run['good_tstart'],run['good_tstop'])))
	length[runbin[-1]] += GetDuration(run['good_tstart'],run['good_tstop'])

min_val = 9999999999
for value in length :
	if value > 0.0 and value < min_val :
		min_val = value
file.close()

file = open(args.output+".txt",'w')

listOfFiles = list()
gcdfilelist = list()
basedir = "/data/exp/IceCube/"+str(runlistyear)+"/filtered/PFFilt"
print(basedir)
for (dirpath, dirnames, filenames) in os.walk(basedir):
    listOfFiles += [os.path.join(dirpath,x) for x in filenames if checkfilename(x,Datacondition_have, Datacondition_nothave)]
basedir = "/data/exp/IceCube/"+str(runlistyear)+"/filtered/level2pass2/AllGCD"
print(basedir)
for (dirpath, dirnames, filenames) in os.walk(basedir):
    gcdfilelist += [os.path.join(dirpath,x) for x in filenames if checkfilename(x,GDCcondition_have, GDCcondition_nothave)]

for i in range(len(runnum)) :
	print(str(i)+"/"+str(len(runnum)))
	if runbin[i] < 0 : continue
	runfilelist = [x for x in listOfFiles if checkrunnum(x,runnum[i])]
	print(len(runfilelist))
	if len(runfilelist) > 0 :
		pathsplit = runfilelist[0].split("/",1000)
		rundirpath = pathsplit[0]
		for j in range(1,len(pathsplit)-1):
			rundirpath += "/"+pathsplit[j]
		rundirpath += "/"
		outputdir = "/data/user/tmcelroy/submit_domeff_data/"
		extra  = pathsplit[-5]+"/"+pathsplit[-2]
		gcdfile = [x for x in gcdfilelist if checkrunnum(x,runnum[i])]
		print(gcdfile)
		if len(gcdfile)<1 : 
			continue
		nsubruns = len(runfilelist)
		file.write(str(nsubruns) + " :python submit_domeff_data.py " + gcdfile[0] + " " + rundirpath + " Run" "{0:0{1}d}".format(runnum[i],8) + " -1 " + outputdir + " " + extra + " False " + str(prescale*float(min_val/length[runbin[i]])) + "\n")

for i in range(len(monthdays)) :
	for j in range(monthdays[i]) :
		if length[sum([monthdays[k] for k in range(i)]) + j] == 0.0 :
			print("%d %d" % (i+1,j+1))

file.close()

fout = ROOT.TFile.Open(args.output+".root","RECREATE")
DaysExposure = ROOT.TH1F("Exposure","",sum(monthdays),0.5,sum(monthdays)+0.5)
for i in range(len(length)) :
	DaysExposure.SetBinContent(i+1,length[i])
DaysExposure.Write()
fout.Close()

