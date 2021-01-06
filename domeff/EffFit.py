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
	return (data[distbin+1].get('sigmacharge')**2.0 + yequiv**2.0)**0.5

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
	chargelow, errorlow   = XinterpolationsandYequivError(dist,sim[binmin])
	chargehigh, errorhigh = XinterpolationsandYequivError(dist,sim[binmax])

	#interpolate between two curves.
	y_weight = (eff-(0.9+0.1*binmin))/0.1

	charge = (1.0-y_weight)*chargelow + y_weight*chargehigh
	chargesig = (1.0-y_weight)*errorlow + y_weight*errorhigh

	return charge, chargesig

def chargedist(dist,amp,base,tau) :
	return base + amp*exp(-dist/tau)

def chargedistChi2(amp,base,tau) :
	chisq = 0.0
	for i in range(2,len(currentdata)-1) :
		data = currentdata[i].get('meancharge')
		error = GetYequivError(i,currentdata)
		exp = chargedist(currentdata[i].get('meandistance'),amp,base,tau)
		chisq += ((data-exp)**2.0)/(error**2.0)
	return chisq

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

currenteff = eff_ic
currentdata = data_ic

#compute the DOM efficency for IceCube by fitting the average scaled charge and then fitting line and taking intercept.
eff_value = 0.9
nominal_eff = 0.94
for eff in eff_ic_norm :
	currentratio = eff
	kwargs = dict(ratio=0.8, error_ratio=0.4,limit_ratio=(0.1,1.9))
	m = Minuit(constChi2,**kwargs)
	m.migrad()
	m.hesse()
	MCDataRatio.append(dict('eff' = eff_value*nominal_eff,'scaledcharge' = m.values[0],'error' = m.errors[0]))
	eff_value += 0.1

kwargs = dict(slope=1.0, error_slope=0.1, inter=0.0, error_inter=0.1)
m = Minuit(linearChi2,**kwargs)
print("Fit IceCube DOM Efficiency from scaled charge")
m.migrad()
slope = m.values.get("slope")
inter = m.values.get("inter")
print("DOM efficiency: %f" % ((1.0-inter)/slope))
m.hesse()
e_slope = m.errors.get("slope")
e_inter = m.errors.get("inter")
print("DOM Efficiency Error: %f" % (((1.0-inter)/slope)*((e_slope/slope)**2.0+(e_inter/(1.0-inter))**2.0)**0.5))

#compute the DOM efficency for IceCube by fitting the average scaled charge and then fitting line and taking intercept.
eff_value = 0.9
nominal_eff = 0.94
for eff in eff_dc_norm :
	currentratio = eff
	kwargs = dict(ratio=0.8, error_ratio=0.4,limit_ratio=(0.1,1.9))
	m = Minuit(constChi2,**kwargs)
	m.migrad()
	m.hesse()
	MCDataRatio.append(dict('eff' = eff_value*nominal_eff,'scaledcharge' = mvalues[0],'error' = m.errors[0]))
	eff_value += 0.1

kwargs = dict(slope=1.0, error_slope=0.1, inter=0.0, error_inter=0.1)
m = Minuit(linearChi2,**kwargs)
print("Fit DeepCore DOM Efficiency from scaled charge")
m.migrad()
slope = m.values.get("slope")
inter = m.values.get("inter")
print("DOM efficiency: %f" % ((1.0-inter)/slope))
m.hesse()
e_slope = m.errors.get("slope")
e_inter = m.errors.get("inter")
print("DOM Efficiency Error: %f" % (((1.0-inter)/slope)*((e_slope/slope)**2.0+(e_inter/(1.0-inter))**2.0)**0.5))

datafile.close()
for file in eff_file :
	file.close()

