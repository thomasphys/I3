import os, sys
from tables import open_file
import ROOT
import numpy as np
import argparse
from tables import open_file
from icecube.weighting.fluxes import  GaisserH4a, GaisserH3a, GaisserH4a_IT, GaisserHillas, Hoerandel, Hoerandel5, Hoerandel_IT
from icecube.weighting import weighting
from event import *
from I3Tray import OMKey
from array import array

if __name__ == '__main__':

	parser = argparse.ArgumentParser()
	parser.add_argument('-d', '--data', help='Directory of data files.',type=str,
				default = '/data/user/sanchezh/IC86_2015/Final_Level2_IC86_MPEFit_*.h5')
	parser.add_argument('-e', '--eff', help='efficiency to be used or data for data.', type = str, nargs = '+',
				default = ["eff100"])
	parser.add_argument('-o', '--output', help='Name of output file.', type=str,
				default = "out.root")
	parser.add_argument('-f', '--flux', help='Name of flux model.', type=str,
				default = "data")
	parser.add_argument('-z', '--zenithrange', help='Range of muon Zeniths', type = float,
				nargs = 2,  default = [40.,70.])
	parser.add_argument('-p', '--energyrange', help='Range of muon Energies', type = float,
				nargs = 2, default = [0.0, 9999999.00])
	parser.add_argument('-i','--impactrange',help='Range of DOM impact parameters to include', 
				type = float, nargs = "+", default = [0.0,180.0])
	parser.add_argument('-t','--trackendpoint',help='Distance from track end point to include',
				type = float, default = 100.)
	parser.add_argument('-c','--cherdist', help='Distance from track to include', type = float, 
				nargs = 2, default = [0.0,200.])
	parser.add_argument('-w','--binwidth', help='Width to bin distances', type = float, default = 20.0)
	parser.add_argument('-r','--residual', help='time residual region', type = float, 
				nargs = 2, default = [-15.0,75.0])
	parser.add_argument('-x','--hitsout',help='Max number of hits outside analysis region',type = int, default = 20)
	parser.add_argument('-b','--boarder',help='Distance from bottom and side of detector.',type = float, 
						nargs = 2, default = [-400.0, 100.0])
	parser.add_argument('-n', '--nhits', help='Min number of direct hit DOMs and Max number of Outside analysis hits', 
						type = int, nargs = 2, default = [5,20])
	parser.add_argument('-l', '--likelihood', help='Fit likelyhoods, FiniteReco Likelihood ratio and SplineMPE Rlogl', type = float,
						nargs = 2, default = [10.,10.])
	parser.add_argument('-y', '--skim',help="skim fraction",type = float, default = 1.0)


	args = parser.parse_args()
	weightname = 'weight_'+args.flux

	h5outfile = open_file(args.output+".h5", mode="w", title="DOM Calibration HDF5 File")
	
	icecube = {}
	deapcore = {}

	if args.flux == 'data' :
		icecube =h5outfile.create_table('/', 'icecube', Data, "IceCube Charge vs Distance data")
		deapcore =h5outfile.create_table('/', 'deepcore', Data, "DeepCore Charge vs Distance data")
	else :
		icecube =h5outfile.create_table('/', 'icecube', MC, "IceCube Charge vs Distance data")
		deapcore =h5outfile.create_table('/', 'deepcore', MC, "DeepCore Charge vs Distance data")

	icrow = icecube.row
	dcrow = deapcore.row

	DC_Strings = [81,82,83,84,85,86]
	IC_Strings = [17,18,19,25,26,27,28,34,38,44,47,56,54,55]

	files_dir = args.data
	file_list_aux = os.listdir(files_dir)
	file_list = list()
	for (dirpath, dirnames, filenames) in os.walk(files_dir):
		for eff in args.eff :
			file_list += [os.path.join(dirpath,x) for x in filenames if '.h5' in x and eff in x]
    #remove duclicates
	file_list = list(set(file_list))

	nfiles = len(file_list)

	print(nfiles)

	flux = GaisserH4a()
	if args.flux == "GaisserH3a" : flux = GaisserH3a()
	elif args.flux == "GaisserH4a_IT" : flux = GaisserH4a_IT()
	elif args.flux == "GaisserHillas" : flux = GaisserHillas()
	elif args.flux == "Hoerandel" : flux = Hoerandel()
	elif args.flux == "Hoerandel5" : flux = Hoerandel5()
	elif args.flux == "Hoerandel_IT" : flux = Hoerandel_IT()

	eventcount = 0
	max_weight = 0.0
	totalevent = 0
	#generator = weighting.from_simprod(21269,False,'vm-simprod2.icecube.wisc.edu')
	#generator = weighting.icetop_mc_weights(21269,'/home/tmcelroy/icecube/domeff/datasetConfig.json')
	nfiles = len(file_list)

	rand = ROOT.TRandom3()
	
	for filename in file_list :
		h5file = 0
		try :
			h5file = open_file(filename, mode="r")
		except : continue
		
		domtable = h5file.root.doms
		eventtable = h5file.root.events
		runtable = h5file.root.runinfo

		domindex = 0

		for event in eventtable.iterrows() :

			if args.flux == "data" :
				if rand.Uniform()>args.skim : continue

			totalevent += 1  

			if args.flux == "data" :			
				if event['filterMask/SunFilter_13'] : continue
				if event['filterMask/MoonFilter_13'] : continue 

			#Energy Cut
			if event['totalCharge'] < args.energyrange[0] or event['totalCharge'] > args.energyrange[1] : 
				continue

			#Zenith Cut
			if event['reco/dir/zenith'] < args.zenithrange[0]*ROOT.TMath.Pi()/180. or event['reco/dir/zenith'] > args.zenithrange[1]*ROOT.TMath.Pi()/180. : 
				continue
		
			#Stopping Point Cut
			if event['recoEndPoint/z'] < args.boarder[0] :
				continue

			if event['borderDistance'] < args.boarder[1] :
				continue 

			#Likelihood cuts
			if event['stopLikeRatio'] < args.likelihood[0] :
				continue

			 #Likelihood cuts
            if event['recoLogL'] > args.likelihood[1] :
                continue

			#direct hists
			if event['directHits'] < args.nhits[0]:
				continue

	
			eventcount += 1
			weight = 1.0
			if args.flux != "data" :
				pflux = flux(event['corsika/primaryEnergy'],event['corsika/primaryType'])
				energy_integral = event['corsika/energyPrimaryMax']**(event['corsika/primarySpectralIndex']+1)
				energy_integral = energy_integral - event['corsika/energyPrimaryMin']**(event['corsika/primarySpectralIndex']+1)
				energy_integral = energy_integral / (event['corsika/primarySpectralIndex']+1)
				energy_weight = event['corsika/primaryEnergy']**event['corsika/primarySpectralIndex']
				energy_weight = pflux*energy_integral/energy_weight*event['corsika/areaSum']
				weight = energy_weight/(event['corsika/nEvents'])
				weight = weight/nfiles

			for dom in domtable.iterrows(domindex) :
				if dom['eventId'] < event['eventId'] :
					domindex += 1
					continue
				elif dom['eventId'] == event['eventId'] :
					domindex += 1
				else :
					break
				if dom['impactAngle'] < args.impactrange[0]*3.14/180. or  dom['impactAngle'] > args.impactrange[1]*3.14/180.:
					continue
				if dom['distAboveEndpoint'] < args.trackendpoint :
					continue
				if dom['recoDist'] < args.cherdist[0] or dom['recoDist'] > args.cherdist[1] :
					continue
				if event['icHitsOut']> args.nhits[1] or event['icHitsOut'] < 1 :
					continue; 
			
				if dom['string'] in DC_Strings :
					dcrow['charge'] = dom['totalCharge']
					dcrow['dist'] = dom['recoDist']
					if args.flux != "data" :
						dcrow['weight'] = weight
					dcrow.append()
				if dom['string'] in IC_Strings :
					icrow['charge'] = dom['totalCharge']
					icrow['dist'] = dom['recoDist']
					if args.flux != "data" :
						icrow['weight'] = weight
					icrow.append()
					
		h5file.close()

	h5outfile.close()
	
	print("Total number of events = %d/%d" % (eventcount,totalevent))


