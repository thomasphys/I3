import os, sys
from tables import open_file
import ROOT
import numpy as np
import argparse
from tables import open_file

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

def calc_charge_info(total_charge_dict):

    
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

    mean_dist = []
    charge = []
    error = []

    for bounds, data in total_charge_dict.items():
        
        print(bounds)
        charges= data[0]
        weights = data[1]
        
        # Defining the weighted average

        mu = sum([ weights[i]*charges[i] for i in range(0,len(charges))]) 
        mu = mu/sum(weights)

        # We use the standard IC procedure to calculate the statistical error for the
        # weighted average

        # There are three main terms
        
        # 1) The  weighted sum of charges, and its variance
        
        wsc = sum([ weights[i]*charges[i] for i in range(0,len(charges))])
        var_wsc = sum([(weights[i]*charges[i])**2 for i in range(0,len(charges))]) 

        # 2) The sum of weights and its variance 

        sw = sum(weights)
        var_sw = sum([weights[i]**2 for i in range(0,len(charges))])

        # 3) The covariance associated to both sums of weights 

        cov = sum([charges[i]*(weights[i]**2) for i in range(0,len(charges))])

        # The error in the weighted average of charges is given by the variance of the quantity 
        # wsc/sw; a division of two sums of weights (for two sets of weights that are correlated). 

        std_mu = var_wsc/(wsc)**2
        std_mu += var_sw/(sw)**2
        std_mu -= 2.*cov/(sw*wsc)
        std_mu = std_mu**(1./2.)
        std_mu *= mu

def ComputeWeightedMeanandError(value,weight):
	nelements = len(value)
	if len(weight) != nelements :
		print("error lists are not of equal length")
		return 0.0,0.0

	mean = 0.0;
	sumweights = 0.0;
	n_nonzero = 0.0;
	sigma = 0.;

	for i in range(0,nelements) :
		mean += weight[i]*value[i]
		sumweights += weight[i]
		if weight[i] > 0.0 : n_nonzero += 1.0

	if sumweights <= 0.0 : 
		print("Sum of weights is zero")
		return 0.0,0.0

	mean = mean/sumweights
	sumweights *= (n_nonzero-1.0)/n_nonzero

	for i in range(0,nelements) :
		sigma += weight[i]*(value[i]-mean)**2.0

	sigma /= sumweights

	return mean,sigma**0.5



def OutputRoot(filename,x_data_ic,x_error_ic,y_data_ic,y_error_ic,x_data_dc,x_error_dc,y_data_dc,y_error_dc,energy,zenith,weights) :
	fout = ROOT.TFile.Open(opts["out"],"RECREATE")

	fout.cd()
	Charge_Distance_IC = ROOT.TGraphErrors(len(x_data_ic),np.array(y_data_ic),np.array(x_errors_ic),np.array(y_errors_ic))
	Charge_Distance_DC = ROOT.TGraphErrors(len(x_data_dc),np.array(y_data_dc),np.array(x_errors_dc),np.array(y_errors_dc))
	Energy = ROOT.TH1F("","",1000,min(energy)*0.9,max(energy)*1.1)
	Energy.Fill(len(energy),np.array(energy),np.array(weights))
	Zenith = ROOT.TH1F("","",180,0,180)
	Zenith.Fill(len(zenith),np.array(zenith),np.array(weights))

	Charge_Distance_IC->Write("Charge_Distance_IC")
	Charge_Distance_DC->Write("Charge_Distance_DC")

	fout.Close()


def OutputHDF5(filename,x_data_ic,x_error_ic,y_data_ic,y_error_ic,x_data_dc,x_error_dc,y_data_dc,y_error_dc,energy,zenith,weights) :
	h5file = open_file(filename, mode="w", title="DOM Calibration HDF5 File")

	distancetable_ic = h5file.create_table('/', 'distance_ic', float, "Distance for IC DOMs")
	distanceErrortable_ic = h5file.create_table('/', 'distanceError_ic', float, "Distance error for IC DOMs")
	chargetable_ic = h5file.create_table('/', 'charge_ic', float, "Charge for IC DOMs")
	chargeErrortable_ic = h5file.create_table('/', 'chargeError_ic', float, "Charge error for IC DOMs")

	distancetable_dc = h5file.create_table('/', 'distance_dc', float, "Distance for DC DOMs")
	distanceErrortable_dc = h5file.create_table('/', 'distanceError_dc', float, "Distance error for DC DOMs")
	chargetable_dc = h5file.create_table('/', 'charge_dc', float, "Charge for DC DOMs")
	chargeErrortable_dc = h5file.create_table('/', 'chargeError_dc', float, "Charge error for DC DOMs")

	energytable = h5file.create_table('/', 'energy', float, "Reconstructed muon energy")
	weightstable = h5file.create_table('/', 'weight', float, "Event weights")
	zenithtable = h5file.create_table('/', 'zenith', float, "Reconstructed zenith angle")


	nelements = len(x_data)

	distance = distancetable.row
	distanceerror = distanceErrortable.row
	charge = chargetable.row
	chargeerror = chargeErrortable.row

	for i in range(0,nelements) :
		distance = x_data[i]
		distanceerror = x_error[i]
		charge = y_data[i]
		chargeerror = y_error[i]
		distance.append()
		distanceerror.append()
		charge.append()
		chargeerror.append()

	nelements = len(energy)

	energyrow = energytable.row
	weightsrow = weightstable.row
	zenithtrow = zenithtable.row

	for i in range(0,nelements) :
		energyrow = energy[i]
		weightsrow = weights[i]
		zenithrow = zenith[i]
		energyrow.append()
		weightsrow.append()
		zenithrow.append()

	h5file.close()


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--data', help='Directory of data files.',type=str,
                    default = '/data/user/sanchezh/IC86_2015/Final_Level2_IC86_MPEFit_*.h5')
    parser.add_argument('-e', '--eff', help='efficiency to be used or data for data.', type = str,
                    nargs = '+', default = "data")
    parser.add_argument('-o', '--output', help='Name of output file.', type=str,
                    nargs = '+', default = "out.root")
    parser.add_argument('-f', '--flux', help='Name of flux model.', type=str,
                    nargs = '+', default = "GaisserH4a")
    parser.add_argument('-z', '--zenithrange', help='Range of muon Zeniths', type = float,
                    nargs = '+',  default = [-180.0,180.0])
    
    args = parser.parse_args()

    DomCharge_ic  = [[],[],[],[],[],[],[],[]]
	weights_ic = [[],[],[],[],[],[],[],[]]
	distance_ic = [[],[],[],[],[],[],[],[]]
	DomCharge_dc  = [[],[],[],[],[],[],[],[]]
	weights_dc = [[],[],[],[],[],[],[],[]]
	distance_dc = [[],[],[],[],[],[],[],[]]
	reconstructedE = []
	zenith = []
	weights_E = []

	DC_Strings = [81,82,83,84,85,86]
	IC_Strings = [17,18,19,25,26,27,28,34,38,44,47,56,54,55]

	files_dir = args.data
	file_list_aux = os.listdir(files_dir)
	file_list_h5 = [x for x in file_list_aux if '.h5' in x]
	file_list = []
	if args.eff == "data" :
		print("need to write this part of code")
	else :
		file_list = [x for x in file_list_h5 if args.eff in x]



	eventcount = 0
	
	for filename in file_list :
		h5file = open_file(files_dir+filename, mode="r")
		print('opening file ' + filename)
		print(h5file)
		domtable = h5file.root.doms
		eventtable = h5file.root.events
		runtable = h5file.root.runs

		domindex = 0

		for event in eventtable.iterrows() :

			if event['reco/dir/zenith'] < args.zenithrange[0] or event['reco/dir/zenith'] > args.zenithrange[1] : 
				continue;

			reconstructedE.append(event['reco/energy'])
			zenith.append(event['reco/dir/zenith'])
			weights_E.append(event[weightname])

			domindexstart = domindex
			for dom in domtable.iterrows(domindexstart) :
				if  event['id'] != dom['eventId'] :
					break
				domindex += 1

				i_dist = (int)(dom['recoDist']/20.0)
				if i_dist >= 0 and i_dist < 8 :
					if dom['string'] in DC_Strings :
						DomCharge_dc[idist].append(dom['totalCharge'])
						weights_dc[idist].append(event[weightname])
						distance_dc[idist].append(dom['recoDist'])
					if dom['string'] in IC_String :
						DomCharge_ic[idist].append(dom['totalCharge'])
						weights_ic[idist].append(event[weightname])
						distance_ic[idist].append(dom['recoDist'])
				
			eventcount = eventcount + 1

		h5file.close()

 	
	distance_dc = np.zeros(8,dtype=float)
	distanceerror_dc = np.zeros(8,dtype=float)
	charge_dc = np.zeros(8,dtype=float)
	chargeerror_dc = np.zeros(8,dtype=float)
	distance_ic = np.zeros(8,dtype=float)
	distanceerror_ic = np.zeros(8,dtype=float)
	charge_ic = np.zeros(8,dtype=float)
	chargeerror_ic = np.zeros(8,dtype=float)

	for i in range(0,8):
		distance_dc[i] , distanceerror_dc[i] = ComputeWeightedMeanandError(distance_dc[i],weights_dc[i])
		charge_dc[i], chargeerror_dc[i] = ComputeWeightedMeanandError(DomCharge_dc[i],weights_dc[i])
		distance_ic[i] , distanceerror_ic[i] = ComputeWeightedMeanandError(distance_ic[i],weights_ic[i])
		charge_ic[i], chargeerror_ic[i] = ComputeWeightedMeanandError(DomCharge_ic[i],weights_ic[i])
		


	 outfilenamelist = args.output.split(".",1)
	 if outfilenamelist[1] == "root" :
	 	OutputRoot(args.output,distance_ic,distanceerror_ic,charge_ic,chargeerror_ic,distance_dc,distanceerror_dc,charge_dc,chargeerror_dc,reconstructedE,zenith,weights_E)
	 elif outfilenamelist[1] == "h5" :
	 	OutputHDF5(args.output,distance_ic,distanceerror_ic,charge_ic,chargeerror_ic,distance_dc,distanceerror_dc,charge_dc,chargeerror_dc,reconstructedE,zenith,weights_E)
	 elif outfilenamelist[1] == "pdf" :
	 	print("not yet supported")

