import os, sys
from tables import open_file
import ROOT
import numpy as np
import argparse
from tables import open_file

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
		sigma += weight[i]*(value[i]-mean)*(value[i]-mean)

	sigma /= sumweights

	return mean,sigma



def OutputRoot(filename,x_data,x_error,y_data,y_error) :
	fout = ROOT.TFile.Open(opts["out"],"RECREATE")

	fout.cd()
	tg_GaisserH4a = ROOT.TGraph(len(Distances),np.array(Distances),np.array(DomCharge_GaisserH4a))
	tg_GaisserH4a.Write("GaisserH4a")

	fout.Close()


def OutputHDF5(filename,x_data,x_error,y_data,y_error) :
	h5file = open_file(filename, mode="w", title="DOM Calibration HDF5 File")

	distancetable = self.h5file.create_table('/', 'distance', float, "Distance")
	distanceErrortable = self.h5file.create_table('/', 'distanceError', float, "Distance error")
	chargetable = self.h5file.create_table('/', 'charge', float, "Charge")
	chargeErrortable = self.h5file.create_table('/', 'chargeError', float, "Charge error")

	nelements = length(x_data)

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
                    nargs = '+',  default = [0.0,40.0])
    
    args = parser.parse_args()

    DomCharge_ic  = [[],[],[],[],[],[],[],[]]
	weights_ic = [[],[],[],[],[],[],[],[]]
	distance_ic = [[],[],[],[],[],[],[],[]]
	DomCharge_dc  = [[],[],[],[],[],[],[],[]]
	weights_dc = [[],[],[],[],[],[],[],[]]
	distance_dc = [[],[],[],[],[],[],[],[]]
	reconstructedE = []
	weights_E = []

	Distances = [0.0,20.0,40.0,60.0,80.0,100.0,120.0,140.0]
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

			for dom in domtable.iterrows(domindex) :
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

 	



