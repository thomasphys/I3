import numpy as np
from array import array as arr
from tables import open_file
from iminuit import Minuit
import argparse

currenteff = []
currentdata = []
currentratio = []
MCDataRatio = []

def GetYequivError(distbin,data) :

	deriv = data[distbin+1].get('meancharge') - data[distbin-1].get('meancharge')
	deriv = deriv / (data[distbin+1].get('meandistance') - data[distbin-1].get('meandistance'))

	yequiv = deriv*data[distbin+1].get('sigmadistance')
	return (data[distbin+1].get('sigmacharge')**2.0+ yequiv**2.0)**0.5

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

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--data', help='Directory of data files.',type=str,
			default = '/data/user/sanchezh/IC86_2015/Final_Level2_IC86_MPEFit_*.h5')
parser.add_argument('-e', '--eff', help='Ordered list of efficiency simulations to use, 0.9,1.0,1.1,1.2', type = str,
			nargs = '+', default =["","","",""])
args = parser.parse_args()

datafile = open_file(args.data, mode="r")
eff_file = [open_file(args.eff[0], mode="r"),open_file(args.eff[1], mode="r"),open_file(args.eff[2], mode="r"),open_file(args.eff[3], mode="r")]
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
eff_ic_norm = []
eff_dc = []
eff_dc_norm = []


for file in eff_file :
	eff_ic.append([])
	eff_dc.append([])
	eff_ic_norm.append([])
	eff_dc_norm.append([])
	for x in file.root.icecube.iterrows():
		template = {'meandistance':0.0,'sigmadistance':0.0,'meancharge': 0.0,'sigmacharge':0.0}
		template['meandistance']=x['meandistance']
		template['sigmadistance']=x['sigmadistance']
		template['meancharge']=x['meancharge']
		template['sigmacharge']=x['sigmacharge']
		eff_ic[-1].append(template)
		charge, error = XinterpolationsandYequivError(x['meandistance'],data_ic)
		template['meancharge']=x['meancharge']/charge
		template['sigmacharge']=(x['meancharge']/charge)*((x['sigmacharge']/x['meancharge'])**2.0+(error/charge)**2.0)**0.5
		eff_ic_norm[-1].append(template)
	for x in file.root.deapcore.iterrows():
		template = {'meandistance':0.0,'sigmadistance':0.0,'meancharge': 0.0,'sigmacharge':0.0}
		template['meandistance']=x['meandistance']
		template['sigmadistance']=x['sigmadistance']
		template['meancharge']=x['meancharge']
		template['sigmacharge']=x['sigmacharge']
		eff_dc[-1].append(template)
		charge, error = XinterpolationsandYequivError(x['meandistance'],data_dc)
		template['meancharge']=x['meancharge']/charge
		template['sigmacharge']=(x['meancharge']/charge)*((x['sigmacharge']/x['meancharge'])**2.0+(error/charge)**2.0)**0.5
		eff_dc_norm[-1].append(template)


def calcChi2(eff):
	chisq = 0.0
	for i in range(1,len(currentdata)-1) :
		simval ,  simerror = SimCharge(eff,currentdata[i].get('meandistance'),currenteff)
		dataval = currentdata[i].get('meancharge')
		dataerror = GetYequivError(i,currentdata)
		chisq += ((simval-dataval)**2.0)/(dataerror*dataerror+simerror*simerror)
	return chisq

def constChi2(ratio):
	chisq = 0.0
	for i in range(1,len(currentratio)-1) :
		chisq += ((ratio - currentratio[i].get['meancharge'])**2.0)/(currentratio.get['sigmacharge']**2.0)
	return chisq

def linear(slope, intercept, eff) :
	return intercept + eff*slope

def linearChi2(slope, intercept):
	chisq = 0.0

	for i in range(len(MCDataRatio)) :
		chisq += ((MCDataRatio[i]['scaledcharge']-linear(slope, intercept, MCDataRatio[i]['eff']))**2.0)/(MCDataRatio[i]['error']**2.0)
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

eff_value = 0.9
for eff in eff_ic_norm :
	currentratio = eff
	kwargs = dict(ratio=0.8, error_ratio=0.4,limit_ratio=(0.1,1.9))
	m = Minuit(constChi2,**kwargs)
	m.migrad()
	m.hesse()
	MCDataRatio.append(dict('eff' = eff_value,'scaledcharge' = mvalues[0],'error' = m.errors[0]))
	eff_value += 0.1

kwargs = dict(eff=0.8, error_eff=0.4,limit_eff=(0.91,1.19))
m = Minuit(linearChi2,**kwargs)
m.migrad()
print(m.values)
m.hesse()
print(m.errors)

datafile.close()
for file in eff_file :
	file.close()

