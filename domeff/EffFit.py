import numpy as np
from array import array as arr
from tables import open_file
from iminuit import Minuit
import argparse

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
data_ic = []
data_dc = []
for x in datafile.root.icecube.iterrows() :
	template = {'meandistance':0.0,'sigmadistance':0.0,'meancharge': 0.0,'sigmacharge':0.0}
	template['meandistance']=x['meandistance']
	template['sigmadistance']=x['sigmadistance']
	data_ic.append(template)
for x in datafile.root.deapcore.iterrows() :
	template = {'meandistance':0.0,'sigmadistance':0.0,'meancharge': 0.0,'sigmacharge':0.0}
	template['meandistance']=x['meandistance']
	template['sigmadistance']=x['sigmadistance']
	template['meancharge']=x['meancharge']
	data_dc.append(template)
eff_ic = []
eff_dc = []
eff_ic.append([])
eff_dc.append([])
for x in eff090file.root.icecube.iterrows():
	template = {'meandistance':0.0,'sigmadistance':0.0,'meancharge': 0.0,'sigmacharge':0.0}
	template['meandistance']=x['meandistance']
	template['sigmadistance']=x['sigmadistance']
	template['meancharge']=x['meancharge']
	template['sigmacharge']=x['sigmacharge']
	eff_ic[-1].append(template)
for x in eff090file.root.deapcore.iterrows():
	template = {'meandistance':0.0,'sigmadistance':0.0,'meancharge': 0.0,'sigmacharge':0.0}
	template['meandistance']=x['meandistance']
	template['sigmadistance']=x['sigmadistance']
	template['meancharge']=x['meancharge']
	template['sigmacharge']=x['sigmacharge']
	eff_dc[-1].append(template)
eff_ic.append([])
eff_dc.append([])
for x in eff100file.root.icecube.iterrows() :
	template = {'meandistance':0.0,'sigmadistance':0.0,'meancharge': 0.0,'sigmacharge':0.0}
	template['meandistance']=x['meandistance']
	template['sigmadistance']=x['sigmadistance']
	template['meancharge']=x['meancharge']
	template['sigmacharge']=x['sigmacharge']
	eff_ic[-1].append(template)
for x in eff100file.root.deapcore.iterrows() :
	template = {'meandistance':0.0,'sigmadistance':0.0,'meancharge': 0.0,'sigmacharge':0.0}
	template['meandistance']=x['meandistance']
	template['sigmadistance']=x['sigmadistance']
	template['meancharge']=x['meancharge']
	template['sigmacharge']=x['sigmacharge']
	eff_dc[-1].append(template)
eff_ic.append([])
eff_dc.append([])
for x in eff110file.root.icecube.iterrows() :
	template = {'meandistance':0.0,'sigmadistance':0.0,'meancharge': 0.0,'sigmacharge':0.0}
	template['meandistance']=x['meandistance']
	template['sigmadistance']=x['sigmadistance']
	template['meancharge']=x['meancharge']
	template['sigmacharge']=x['sigmacharge']
	eff_ic[-1].append(template)
for x in eff110file.root.deapcore.iterrows() :
	template = {'meandistance':0.0,'sigmadistance':0.0,'meancharge': 0.0,'sigmacharge':0.0}
	template['meandistance']=x['meandistance']
	template['sigmadistance']=x['sigmadistance']
	template['meancharge']=x['meancharge']
	template['sigmacharge']=x['sigmacharge']
	eff_dc[-1].append(template)
eff_ic.append([])
eff_dc.append([])
for x in eff120file.root.icecube.iterrows() :
	template = {'meandistance':0.0,'sigmadistance':0.0,'meancharge': 0.0,'sigmacharge':0.0}
	template['meandistance']=x['meandistance']
	template['sigmadistance']=x['sigmadistance']
	template['meancharge']=x['meancharge']
	template['sigmacharge']=x['sigmacharge']
	eff_ic[-1].append(template)
for x in eff120file.root.deapcore.iterrows() :
	template = {'meandistance':0.0,'sigmadistance':0.0,'meancharge': 0.0,'sigmacharge':0.0}
	template['meandistance']=x['meandistance']
	template['sigmadistance']=x['sigmadistance']
	template['meancharge']=x['meancharge']
	template['sigmacharge']=x['sigmacharge']
	eff_dc[-1].append(template)

currenteff = []
currentdata = []

def XinterpolationsandYequivError(dist,data):

	distbin = 0
	while data[distbin].get('meandistance') < dist :
		distbin += 1

	x_weight = (dist-data[distbin-1].get('meandistance'))/(data[distbin].get('meandistance')-data[distbin-1].get('meandistance'))

	deriv = data[distbin].get('meancharge')-data[distbin-1].get('meancharge')
	deriv = deriv/(data[distbin].get('meandistance')-data[distbin-1].get('meandistance'))

	yequiv = deriv*((1.0-x_weight)*data[distbin-1].get('sigmadistance') + x_weight*data[distbin].get('sigmadistance'))

	intyerror = (1.0-x_weight)*data[distbin-1].get('sigmacharge') + x_weight*data[distbin].get('sigmacharge')

	yerror = (yequiv*yequiv+intyerror*intyerror)**0.5

	charge = (1.0-x_weight)*data[distbin-1].get('meancharge') + x_weight*data[distbin].get('meancharge')

	return charge , yerror

def SimCharge(eff,dist,sim): 
	#Get efficiency curves to interpolate between.
	binmin = int((eff-0.9)/0.1)
	binmax = binmin+1

	# interpolate x  values for lower curve
	chargelow, errorlow = XinterpolationsandYequivError(dist,sim[binmin])
	chargehigh, errorhigh = XinterpolationsandYequivError(dist,sim[binmax])

	#interpolate between two curves.
	y_weight = (eff-(0.9+0.1*binmin))/0.1

	charge = (1.0-y_weight)*chargelow + y_weight*chargehigh
	chargesig = (1.0-y_weight)*errorlow + y_weight*errorhigh

	return charge, chargesig

def GetYequivError(distbin,data) :

	deriv = data[distbin+1].get('meancharge') - data[distbin-1].get('meancharge')
	deriv = deriv / (data[distbin+1].get('meandistance') - data[distbin-1].get('meandistance'))

	yequiv = deriv*data[distbin+1].get('sigmadistance')
	return (data[distbin+1].get('sigmacharge')**2.0+ yequiv**2.0)**0.5


def calcChi2(eff):
	chisq = 0.0
	for i in range(1,len(currentdata)-1) :
		simval ,  simerror = SimCharge(eff,currentdata[i].get('meandistance'),currenteff)
		dataval = currentdata[i].get('meancharge')
		dataerror = GetYequivError(i,currentdata)
		chisq += ((simval-dataval)**2.0)/(dataerror*dataerror+simerror*simerror)
	return chisq

currenteff = eff_ic
currentdata = data_ic

kwargs = dict(eff=1.1, error_eff=0.1,limit_eff=(0.91,1.19))
m = Minuit(calcChi2,**kwargs)
print("Fit IceCube DOM Efficiency")
m.migrad()
print(m.values)
m.hesse()
print(m.errors)
currenteff = eff_dc
currentdata = data_dc

m = Minuit(calcChi2, **kwargs)
print("Fit DeepCore DOM Efficiency")
m.migrad()
print(m.values)
m.hesse()
print(m.errors)

datafile.close()
eff090file.close()
eff100file.close()
eff110file.close()
eff120file.close()

