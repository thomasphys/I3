import json

parser = argparse.ArgumentParser()
	parser.add_argument('-i', '--input', help='Input good run list.',type=str,
				default = '')
	parser.add_argument('-o', '--output', help='Output file list.',type=str,
				default = '')

	args = parser.parse_args()

def GetDuration(start,stop) :
	startlist = start.split(" ",1)
	stoplist = start.split(" ",1)

	starttimelist = startlist[1].split(":",2)
	stoptimelist = stoplist[1].split(":",2)

	start_hour = float(starttimelist[0])
	start_min = float(starttimelist[1])
	start_sec = float(starttimelist[2])

	stop_hour = float(stoptimelist[0])
	stop_min = float(stoptimelist[1])
	stop_sec = float(stoptimelist[2])

	duration = 3600.*(stop_hour-start_hour) + 60.*(stop_min-start_min) + (stop_sec-start_sec)
	return duration

def GetDay(date)
	datelist = date.split(" ",1)
	yyyymmdd = datelist[0].split("-",2)
	return int(yyyymmdd[2])

def GetMonth(date)
	datelist = date.split(" ",1)
	yyyymmdd = datelist[0].split("-",2)
	return int(yyyymmdd[1])

def GetYear(date)
	datelist = date.split(" ",1)
	yyyymmdd = datelist[0].split("-",2)
	return int(yyyymmdd[0])

file = open(args.input,'r')
data = json.load(file)

run = []
length = [ 0.0 for i in range(12*31)]

for run in data['runs']:
	if 'short' in run['reason_i3'] : 
		continue
	if 'failed' in run['reason_i3'] :
		continue
	if 'short' in run['reason_it'] :
		continue
	if 'failed' in run['reason_it'] :
		continue

	run.append(int(run['run']))
	month = GetMonth(run['good_tstart'])
	day = GetDay(run['good_tstart'])
	year = GetYear(run['good_tstart'])
	bin = (month-1)*31+day
	length[bin] += GetDuration(run['good_tstart'],run['good_tstop'])

min_val = 9999999999
for value in length :
	if value > 0.0 and value < min_val :
		min_val = value
file.close()

file = open(args.output,'w')

for i in range(len(length)) :
	file.write("%f %f" % (run[i],min_val/length[i]/total))
file.close()

