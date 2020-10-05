import numpy as np
from array import array as arr
import matplotlib . pyplot as plt
from tables import open_file
from iminuit import Minuit

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--data', help='Directory of data files.',type=str,
			default = '/data/user/sanchezh/IC86_2015/Final_Level2_IC86_MPEFit_*.h5')
parser.add_argument('-e', '--eff', help='Ordered list of efficiency simulations to use, 0.9,1.0,1.1,1.2', type = str,
			nargs = '+', default =["","","",""])
args = parser.parse_args()

datafile = open_file(args.data, mode="r")
eff090file = open_file(args.eff[0], mode="r")
eff100file = open_file(args.eff[1], mode="r")
eff110file = open_file(args.eff[2], mode="r")
eff120file = open_file(args.eff[3], mode="r")

data_ic = [x for x in datafile.root.icecube.iterrows()]
data_dc = [x for x in datafile.root.deepcore.iterrows()]
eff_ic = []
eff_dc = []
eff_ic.append([x for x in eff090file.root.icecube.iterrows()])
eff_dc.append([x for x in eff090file.root.deepcore.iterrows()])
eff_ic.append([x for x in eff100file.root.icecube.iterrows()])
eff_dc.append([x for x in eff100file.root.deepcore.iterrows()])
eff_ic.append([x for x in eff110file.root.icecube.iterrows()])
eff_dc.append([x for x in eff110file.root.deepcore.iterrows()])
eff_ic.append([x for x in eff120file.root.icecube.iterrows()])
eff_dc.append([x for x in eff120file.root.deepcore.iterrows()])

currenteff = []
currentdata = []

def XinterpolationsandYequivError(dist,data):

    distbin = 0
	while data[distbin]['meandistance'] < dist : ++distbin

	x_weight = (dist-data[distbin-1]['meandistance'])/(data[distbin]-data[distbin-1])

	deriv = (data[distbin]['meancharge']-data[distbin-1]['meancharge'])
	deriv = deriv/(data[distbin]['meandistance']-data[distbin-1]['meandistance'])

	yequiv = deriv*((1.0-x_weight)*data[distbin-1]['sigmadistance'] + x_weight*data[distbin]['sigmadistance'])

	intyerror = (1.0-x_weight)*data[distbin-1]['sigmacharge'] + x_weight*data[distbin]['sigmacharge']

	yerror = (yequiv*yequiv+intyerror*intyerror)**0.5

	charge = (1.0-x_weight)*data[distbin-1]['meancharge'] + x_weight*data[distbin]['meancharge']

	return charge , yerror

def SimCharge_(eff,dist,sim): 
	#Get efficiency curves to interpolate between.
	binmin = int((x-0.9)/0.1)
	binmax = binmin+1

	# interpolate x  values for lower curve
	chargelow, errorlow = XinterpolationsandYequivError(dist,sim[binmin])
	chargehigh, errorhigh = XinterpolationsandYequivError(dist,sim[binmax])

	#interpolate between two curves.
	y_weight = (x-(0.9+0.1*binmin))/0.1

	charge = (1.0-y_weight)*chargelow + y_weight*chargehigh
	chargesig = (1.0-y_weight)*errorlow + y_weight*errorhigh

	return charge, chargessig

def GetYequivError(distbin,data) :

	deriv = data[distbin+1]['meancharge'] - data[distbin-1]['meancharge']
	deriv = deriv / (data[distbin+1]['meandistance'] - data[distbin-1]['meandistance'])

	yequiv = deriv*data[distbin+1]['sigmadistance']
	return (data[distbin+1]['sigmacharge']**2.0+ yequiv**2.0)**0.5


def calcChi2(eff,data,sim):
	chisq = 0.0
	for i in range(1,len(data)-1) :
		simval ,  simerror = SimCharge(eff,data[i]['meandistance'],sim)
		dataval = data[i]['meancharge']
		dataerror = GetYequivError(i,data)
		chisq += ((simval-dataval)**2.0)/(dataerror*dataerror+simerror*simerror)
	return chisq

currenteff = eff_ic
currentdata = data_ic

m = Minuit(calcChi2, eff = 1.0)
print("Fit IceCube DOM Efficiency")
m.migrad()

currenteff = eff_dc
currentdata = data_dc

m = Minuit(calcChi2, eff = 1.0)
print("Fit DeepCore DOM Efficiency")
m.migrad()

