import h5py
import os, sys
import numpy as np
import matplotlib as mpl
from matplotlib.colors import LogNorm, Normalize
import matplotlib.pyplot as plt
import timeit as time
import math
from datetime import datetime
from icecube.weighting.fluxes import  Hoerandel5,GaisserH3a
from icecube.weighting import weighting
import tables

opts = {}

# I/O options
opts["data"] = sys.argv[1]
opts["nevents"] = int(sys.argv[2])
opts["out"] = sys.argv[3]
opts["sim"] = sys.argv[4] == 'true'

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
	file_list = [x for x in file_list_aux if '.h5' in x]

	gen = weighting.from_simprod(simprod_number) #per file generator simprod_number = 12359

    gen = gen*len(file_list)

    per_event_weights = flux(primary_energies,primary_types)/gen(primary_energies,primary_types)
	
	for filename in file_list :
		h5file = h5py.File(filename, 'r')

		domtable = h5file.root.doms

		primaryenergy = np.array(h5file['Events'][:].primary.energy)
		primarytype = np.array(h5file['Events'][:].primary.id)

		flux = GaisserH3a()
		eventweight = np.zeros(len(primaryenergy),dtype=float)
		eventweight = eventweight + 1.0
		if primarytype[0] >= 0 :
			eventweight = flux(primaryenergy,primarytype)/gen(primaryenergies,primarytypes)

		DomCorCharge_event = np.zeros(40,dtype=float)
		DomCorAttenCharge_event = np.zeros(40,dtype=float)
		DomCharge_event = np.zeros(40,dtype=float)
		DomCorCharge_norm = np.zeros(40,dtype=float)
		DomCorAttenCharge_norm = np.zeros(40,dtype=float)
		DomCharge_norm = np.zeros(40,dtype=float)

		i_event = 0

		for dom in domtable.iterrows() :
			if i_event != dom['eventId']
				eventcount += 1.0
				for j in range(len(DomCorCharge_norm)) :
					if DomCorCharge_norm[j] > 0.0 :
						DomCorCharge[j] += eventweight[i_event]*DomCorCharge_event[j]/DomCorCharge_norm[j]
					if DomCorAttenCharge_norm[j] > 0.0 :
						DomCorAttenCharge[j] += eventweight[i_event]*DomCorAttenCharge_event[j]/DomCorAttenCharge_norm[j]
					if DomCharge_norm[j] > 0.0 :
						DomCharge[j] += eventweight[i_event]*DomCharge_event[j]/DomCharge_norm[j]
				i_event = dom['eventId']
				DomCorCharge_norm = np.zeros(40,dtype=float)
				DomCorAttenCharge_norm = np.zeros(40,dtype=float)
				DomCorCharge_event = np.zeros(40,dtype=float)
				DomCorAttenCharge_event = np.zeros(40,dtype=float)
				DomCharge_event = np.zeros(40,dtype=float)
				DomCharge_norm = np.zeros(40,dtype=float)
			
			dist = dom['recoDist']
			char = dom['totalCharge']
			CorChar = correctedcharge(dist,char)
			CorAttenChar = correctedAttencharge(dist,char)
			i_dist = (int)(dist/5.0)
			if i_dist > 0 and i_dist < 40 :
				DomCharge_event[i] += char
				DomCorCharge_event[i] += CorChar
				DomCorAttenCharge_event[i] += CorAttenChar
				DomCharge[i] += char
				DomCorCharge[i] += CorChar
				DomCorAttenCharge[i] += CorAttenChar
				DomCharge_norm[i] += 1.0

		print(DomCharge)



