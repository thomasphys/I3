import os, sys
from tables import open_file
import ROOT
import numpy as np
import argparse
from tables import open_file
from icecube.weighting.fluxes import  GaisserH4a, GaisserH3a, GaisserH4a_IT, GaisserHillas, Hoerandel, Hoerandel5, Hoerandel_IT
from icecube.weighting import weighting
from event import *

def find_error_bootstrap(values,weights):
# this needs to be eddited, I do not thing this was programmed corerctly.

	total = len(values)
	sum_weights = sum([weights[i] for i in range(0,len(weights))])
	mu = sum([vales[i]*weights[i] for i in range(0,len(weights))])
	mu = mu/sum_weights
	std_mu = []
	for j in range(0,11) :
		means = []
		size = 0.1 + (0.065)*j
		sum_weights = 0.0
		for i in range(0,100):
			resampled = np.random.randint(low=0.0, high=total, size=size)
			sum_weights = sum([weights[i] for i in resampled])
			mu = sum([charge_list[i]*weights[i] for i in resampled])
			mu = mu/sum_weights
			means.append(mu)
			std_mu.append(np.std(means,ddof=1))

	return std_mu_limit

def calc_charge_info(values,weights):

    
	"""
	Calculate the mean distance of the bin, (average) charge, and error in average charge

	Parameters
	----------
	total_charge_dict: dict
	Contains the total_charge_dict data.

	Returns
	-------
	charge_info: dict
	Contains the mean distance, charge, and error of each thing.
	"""
        
	# Defining the weighted average
	mu = sum([ weights[i]*values[i] for i in range(0,len(values))]) 
	mu = mu/sum(weights)
		
	# We use the standard IC procedure to calculate the statistical error for the
	# weighted average
	# There are three main terms
	# 1) The  weighted sum of charges, and its variance
	wsc = sum([ weights[i]*values[i] for i in range(0,len(values))])
	var_wsc = sum([(weights[i]*values[i])**2 for i in range(0,len(values))]) 
	# 2) The sum of weights and its variance 
	sw = sum(weights)
	var_sw = sum([weights[i]**2 for i in range(0,len(values))])
	# 3) The covariance associated to both sums of weights 
	cov = sum([charges[i]*(weights[i]**2) for i in range(0,len(values))])
	# The error in the weighted average of charges is given by the variance of the quantity 
	# wsc/sw; a division of two sums of weights (for two sets of weights that are correlated). \
	std_mu = var_wsc/(wsc)**2
	std_mu += var_sw/(sw)**2
	std_mu -= 2.*cov/(sw*wsc)
	std_mu = std_mu**0.5
	std_mu *= mu

	return mu , std_mu

def ComputeMeanandError(value,weight) :

	nelements = len(value)
	for i in range(0,nelements) :
		mean += value[i]/nelements

	for i in range(0,nelements) :
		sigma += ((value[i]-mean)**2.0)/nelements

	return mean, sigma**0.5


def ComputeWeightedMeanandError(value,weight):

	'''
	This function computes the standard error of the mean for a weighted set following the bootstrap validated formulation here:
	https://en.wikipedia.org/wiki/Weighted_arithmetic_mean#:~:text=Statistical%20properties,-The%20weighted%20sample&text=can%20be%20called%20the%20standard,weights%20except%20one%20are%20zero.

	'''

	nelements = len(value)
	if len(weight) != nelements :
		print("error lists are not of equal length")
		return 0.0,0.0

	mean = 0.0
	sumweights = 0.0
	sumweights_sqr = 0.0
	n_nonzero = 0.0
	sigma = 0.

	for i in range(0,nelements) :
		sumweights = sumweights+weight[i]
		sumweights_sqr = sumweights_sqr+(weight[i]/sumweights)**2.0
		if weight[i] > 0.0 : n_nonzero += 1.0

	#Compute mean
	mean2 = 0.0
	for i in range(0,nelements) :
		mean += weight[i]*value[i]/sumweights
		mean2 += value[i]/nelements

	if n_nonzero == 0.0 : 
		print("Sum of weights is zero")
		return 0.0,0.0	

	for i in range(0,nelements) :
		sigma += (weight[i]*(value[i]-mean)/sumweights)**2.0

	#Compute standard error squared
	sigma /= (n_nonzero-1.0)/n_nonzero

	return mean, sigma**0.5


def OutputRoot(filename,x_data_ic,x_error_ic,y_data_ic,y_error_ic,x_data_dc,x_error_dc,y_data_dc,y_error_dc,energy,zenith,weights) :
	fout = ROOT.TFile.Open(filename,"RECREATE")

	fout.cd()

	Charge_Distance_IC = ROOT.TGraphErrors(len(x_data_ic),x_data_ic,y_data_ic,x_error_ic,y_error_ic)
	Charge_Distance_DC = ROOT.TGraphErrors(len(x_data_dc),x_data_dc,y_data_dc,x_error_dc,y_error_dc)
	Energy = ROOT.TH1F("Energy","",1000,min(energy)*0.9,max(energy)*1.1)
	Zenith = ROOT.TH1F("Zenith","",360,-180,180)

	for i in range(0,len(weights)) :
		Energy.Fill(energy[i],weights[i])
		Zenith.Fill(zenith[i]*180/3.14,weights[i])

	Charge_Distance_IC.Write("Charge_Distance_IC")
	Charge_Distance_DC.Write("Charge_Distance_DC")
	Energy.Write()
	Zenith.Write()

	fout.Close()


def OutputHDF5(filename,x_data_ic,x_error_ic,y_data_ic,y_error_ic,x_data_dc,x_error_dc,y_data_dc,y_error_dc,energy,zenith,weights,args) :
	h5file = open_file(filename, mode="w", title="DOM Calibration HDF5 File")
	
	icecube = h5file.create_table('/', 'icecube', DataPoint, "IceCube Charge vs Distance data")
	deapcore = h5file.create_table('/', 'deapcore', DataPoint, "DeepCore Charge vs Distance data")
	flux = h5file.create_table('/', 'flux', Flux, "Information on the events")
	state = h5file.create_table('/','state',State,"Information on the data cuts")

	nelements = len(x_data_ic)

	icrow = icecube.row
	dcrow = deapcore.row
	fluxrow = flux.row
	staterow = state.row

	staterow['data'] = args.data
	staterow['eff'] = args.eff
	staterow['flux'] = args.flux
	staterow['zenithmin'] = args.zenithrange[0]
	staterow['zenithmax'] = args.zenithrange[1]
	staterow['energymin'] = args.energyrange[0]
	staterow['impactanglemin'] = args.energyrange[1]
	staterow['impactanglemax'] = args.impactrange[0]
	staterow['trackendpoint'] = args.impactrange[1]
	staterow['cherdistmin'] = args.cherdist[0]
	staterow['cherdistmax'] = args.cherdist[1]
	staterow['binwidth'] = args.binwidth
	staterow.append()

	for i in range(0,nelements) :
		icrow['meandistance'] = x_data_ic[i]
		icrow['sigmadistance'] = x_error_ic[i]
		icrow['meancharge'] = y_data_ic[i]
		icrow['sigmacharge'] = y_error_ic[i]
		icrow.append()
		dcrow['meandistance'] = x_data_dc[i]
		dcrow['sigmadistance'] = x_error_dc[i]
		dcrow['meancharge'] = y_data_dc[i]
		dcrow['sigmacharge'] = y_error_dc[i]
		dcrow.append()

	nelements = len(energy)

	for i in range(0,nelements) :
		fluxrow['energy'] = energy[i]
		fluxrow['weight'] = weights[i]
		fluxrow['zenith'] = zenith[i]
		fluxrow['totalcharge'] = totalcharge[i]
		fluxrow.append()

	h5file.close()


if __name__ == '__main__':

	parser = argparse.ArgumentParser()
	parser.add_argument('-d', '--data', help='Directory of data files.',type=str,
				default = '/data/user/sanchezh/IC86_2015/Final_Level2_IC86_MPEFit_*.h5')
	parser.add_argument('-e', '--eff', help='efficiency to be used or data for data.', type = str,
				default = "eff100")
	parser.add_argument('-o', '--output', help='Name of output file.', type=str,
				default = "out.root")
	parser.add_argument('-f', '--flux', help='Name of flux model.', type=str,
				default = "data")
	parser.add_argument('-z', '--zenithrange', help='Range of muon Zeniths', type = float,
				nargs = '+',  default = [-180.0,180.0])
	parser.add_argument('-p', '--energyrange', help='Range of muon Energies', type = float,
				nargs = "+", default = [0.0, 9999999.00])
	parser.add_argument('-i','--impactrange',help='Range of DOM impact parameters to include', 
				type = float, nargs = "+", default = [0.0,180.0])
	parser.add_argument('-t','--trackendpoint',help='Distance from track end point to include',
				type = float, default = 50.)
	parser.add_argument('-c','--cherdist', help='Distance from track to include', type = float, 
				nargs = "+", default = [0.0,140.])
	parser.add_argument('-b','--binwidth', help='Width to bin distances', type = float, 
				nargs = "+", default = 20.0)
    
	args = parser.parse_args()

	weightname = 'weight_'+args.flux

	# compute how many 20m bins to use.
	nbins = int(args.cherdist[1] / args.binwidth)

	DomCharge_ic  = [[] for i in range(nbins)]
	weights_ic = [[] for i in range(nbins)]
	distance_ic = [[] for i in range(nbins)]
	DomCharge_dc  = [[] for i in range(nbins)]
	weights_dc = [[] for i in range(nbins)]
	distance_dc = [[] for i in range(nbins)]
	reconstructedE = []
	zenith = []
	weights_E = []
	EnergyTruth = []
	ZenithTruth = []
	totalcharge = []

	DC_Strings = [81,82,83,84,85,86]
	IC_Strings = [17,18,19,25,26,27,28,34,38,44,47,56,54,55]

	files_dir = args.data
	file_list_aux = os.listdir(files_dir)
	file_list_h5 = [x for x in file_list_aux if '.h5' in x]
	#file_list = [x for x in file_list_h5 if (args.eff in x and os.path.getsize(files_dir+x) > 1000000 )]
	file_list = [x for x in file_list_h5 if (args.eff in x)]

	flux = GaisserH4a()
	if args.flux == "GaisserH3a" : flux = GaisserH3a()
	elif args.flux == "GaisserH4a_IT" : flux = GaisserH4a_IT()
	elif args.flux == "GaisserHillas" : flux = GaisserHillas()
	elif args.flux == "Hoerandel" : flux = Hoerandel()
	elif args.flux == "Hoerandel5" : flux = Hoerandel5()
	elif args.flux == "Hoerandel_IT" : flux = Hoerandel_IT()
	
	for filename in file_list :
		h5file = open_file(files_dir+filename, mode="r")
		domtable = h5file.root.doms
		eventtable = h5file.root.events
		runtable = h5file.root.runinfo

		domindex = 0

		for event in eventtable.iterrows() :

			#Energy Cut
			if event['reco/energy'] < args.energyrange[0] or event['reco/energy'] > args.energyrange[1] : 
				continue;

			#Zenith Cut
			if event['reco/dir/zenith'] < args.zenithrange[0]*3.14/180. or event['reco/dir/zenith'] > args.zenithrange[1]*3.14/180. : 
				continue;

			reconstructedE.append(event['reco/energy'])
			zenith.append(event['reco/dir/zenith'])
			if args.flux != "data" :
				pflux = flux(event['corsika/primaryEnergy'],event['corsika/primaryType'])
				energy_integral = event['corsika/energyPrimaryMax']**(event['corsika/primarySpectralIndex']+1)
				energy_integral = energy_integral - event['corsika/energyPrimaryMin']**(event['corsika/primarySpectralIndex']+1)
				energy_integral = energy_integral / (event['corsika/primarySpectralIndex']+1)
				energy_weight = event['corsika/primaryEnergy']**event['corsika/primarySpectralIndex']
				energy_weight = pflux*energy_integral/energy_weight*event['corsika/areaSum']
				weights_E.append(energy_weight)
			else :
				weights_E.append(1.0)

			alldomcharge = 0.0;
			for dom in domtable.iterrows(domindex) :
				if dom['eventId'] == event['eventId'] :
					domindex += 1
				else :
					break
				alldomcharge += dom['totalCharge']
				if dom['impactAngle'] < args.impactrange[0] or  dom['impactAngle'] > args.impactrange[1]: 
					continue
				if dom['distAboveEndpoint'] < args.trackendpoint : 
					continue
				if dom['recoDist'] < args.cherdist[0] or dom['recoDist'] > args.cherdist[1] : 
					continue 
				i_dist = (int)(dom['recoDist']/args.binwidth)
				if i_dist > -1 and i_dist < nbins :
					if dom['string'] in DC_Strings :
						DomCharge_dc[i_dist].append(dom['totalCharge'])
						weights_dc[i_dist].append(weights_E[-1])
						distance_dc[i_dist].append(dom['recoDist'])
					if dom['string'] in IC_Strings :
						DomCharge_ic[i_dist].append(dom['totalCharge'])
						weights_ic[i_dist].append(weights_E[-1])
						distance_ic[i_dist].append(dom['recoDist'])
			totalcharge.append(alldomcharge)

		h5file.close()

	
	binneddistance_dc = np.zeros(nbins,dtype=float)
	binneddistanceerror_dc = np.zeros(nbins,dtype=float)
	binnedcharge_dc = np.zeros(nbins,dtype=float)
	binnedchargeerror_dc = np.zeros(nbins,dtype=float)
	binneddistance_ic = np.zeros(nbins,dtype=float)
	binneddistanceerror_ic = np.zeros(nbins,dtype=float)
	binnedcharge_ic = np.zeros(nbins,dtype=float)
	binnedchargeerror_ic = np.zeros(nbins,dtype=float)

	for i in range(0,len(distance_dc)):
		if len(weights_ic[i]) > 0 :
			binneddistance_dc[i] , binneddistanceerror_dc[i] = ComputeWeightedMeanandError(distance_dc[i],weights_dc[i])
			binnedcharge_dc[i], binnedchargeerror_dc[i] = ComputeWeightedMeanandError(DomCharge_dc[i],weights_dc[i])
			binneddistance_ic[i] , binneddistanceerror_ic[i] = ComputeWeightedMeanandError(distance_ic[i],weights_ic[i])
			binnedcharge_ic[i], binnedchargeerror_ic[i] = ComputeWeightedMeanandError(DomCharge_ic[i],weights_ic[i])
		

	outfilenamelist = args.output.split(".",1)
	if "root" in outfilenamelist[1] :
		OutputRoot(args.output,
					np.array(binneddistance_ic),
					np.array(binneddistanceerror_ic),
					np.array(binnedcharge_ic),
					np.array(binnedchargeerror_ic),
					np.array(binneddistance_dc),
					np.array(binneddistanceerror_dc),
					np.array(binnedcharge_dc),
					np.array(binnedchargeerror_dc),
					reconstructedE,
					zenith,
					weights_E)

	elif "h5" in outfilenamelist[1] :
		OutputHDF5(args.output,
				   binneddistance_ic,
				   binneddistanceerror_ic,
				   binnedcharge_ic,
				   binnedchargeerror_ic,
				   binneddistance_dc,
				   binneddistanceerror_dc,
				   binnedcharge_dc,
				   binnedchargeerror_dc,
				   reconstructedE,
				   zenith,
				   weights_E,
				   args)
	elif "pdf" in outfilenamelist[1] :
		print("not yet supported")


