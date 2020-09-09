import h5py
import os, sys
import numpy as np
import matplotlib as mpl
from matplotlib.colors import LogNorm, Normalize
import matplotlib.pyplot as plt
import timeit as time
import math
from datetime import datetime

opts = {}

# I/O options
opts["gcd"] = sys.argv[1]
opts["data"] = sys.argv[2]
opts["nevents"] = int(sys.argv[3])
opts["out"] = sys.argv[4]

dset = f['mydataset']

gcd_file = '/cvmfs/icecube.opensciencegrid.org/data/GCD/GeoCalibDetectorStatus_IC86_Merged.i3.gz'
gfile = dataio.I3File(gcd_file)
gframe = gfile.pop_frame()
geometry = gframe['I3Geometry']

DomCharge = np.zeros(40,dtype=float)
DomCorCharge = np.zeros(40,dtype=float)
DomCorAttenCharge = np.zeros(40,dtype=float)

DomCharge_cor = np.zeros(40,dtype=float)
DomCorCharge_cor = np.zeros(40,dtype=float)
DomCorAttenCharge_cor = np.zeros(40,dtype=float)

eventcount = 0.0;


___main___ :

	files_dir = opts["data"]
	file_list_aux = os.listdir(files_dir)
	file_list = [x for x in file_list_aux if '.hdf5' in x]

	mydom = []
	for i in range(len(one_dom)):
    dom = geometry.omgeo[one_dom[i][0]]    
    mydom.append(dom)
	
	for filename in file_list :
		h5file = h5py.File(filename, 'r')

		domtable = h5file.root.doms

		DomCorCharge_event = np.zeros(40,dtype=float)
		DomCorAttenCharge_event = np.zeros(40,dtype=float)
		DomCharge_event = np.zeros(40,dtype=float)
		DomCorCharge_norm = np.zeros(40,dtype=float)
		DomCorAttenCharge_norm = np.zeros(40,dtype=float)
		DomCharge_norm = np.zeros(40,dtype=float)

		i_event = 0

		for dom in table.iterrows() :
			if i_event != dom['eventId']
				eventcount += 1.0
				for j in range(len(DomCorCharge_norm)) :
					#if DomCorCharge_norm[j] > 0.0 :
						#DomCorCharge_cor[j] += DomCorCharge_event[j]/DomCorCharge_norm[j]

					#if DomCorAttenCharge_norm[j] > 0.0 :
					#	DomCorAttenCharge_cor[j] += DomCorAttenCharge_event[j]/DomCorAttenCharge_norm[j]
					#if DomCharge_norm[j] > 0.0 :
					#	DomCharge_cor[j] += DomCharge_event[j]/DomCharge_norm[j]

				DomCorCharge_norm = np.zeros(40,dtype=float)
				DomCorAttenCharge_norm = np.zeros(40,dtype=float)
				DomCorCharge_event = np.zeros(40,dtype=float)
				DomCorAttenCharge_event = np.zeros(40,dtype=float)
			dominfo = geometry.omgeo[dom['om']]
			dist = dom['recoDist']
			char = dom['totalCharge']
			CorChar = correctedcharge(dist,char)
			CorAttenChar = correctedAttencharge(dist,char)
			i_dist = (int)(dist/5.0)
			DomCharge_event[i] += char
			DomCorCharge_event[i] += CorChar
			DomCorAttenCharge_event[i] += CorAttenChar
			DomCharge[i] += char
			DomCorCharge[i] += CorChar
			DomCorAttenCharge[i] += CorAttenChar

			#for i in range(len(mydom)):

			#	dist_from_start = emission_distance_from_start()
			#	dist_from_end = emission_distance_from_end()

			#	dist = phys_services.I3Calculator.cherenkov_distance(track,mydom.position)
			#	i_dist = (int)(dist/5.0)
			#	DomCharge_norm[idist] += 1.0
			#	DomCorCharge_norm[i_dist] += correctedcharge(dist,1.0)
			#	DomCorAttenCharge_norm[i_dist] += correctedAttencharge(dist,1.0)
		print(DomCharge)



