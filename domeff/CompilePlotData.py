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
import ROOT

opts = {}

# I/O options
opts["data"] = sys.argv[1]
opts["eff"] = sys.argv[2]
opts["out"] = sys.argv[3]

DomCharge_GaisserH4a  = np.zeros(40,dtype=float)
DomCharge_GaisserH3a  = np.zeros(40,dtype=float)
DomCharge_GaisserHillas  = np.zeros(40,dtype=float)
DomCharge_GaisserH4a_IT  = np.zeros(40,dtype=float)
DomCharge_Hoerandel  = np.zeros(40,dtype=float)
DomCharge_Hoerandel5  = np.zeros(40,dtype=float)
DomCharge_Hoerandel_IT  = np.zeros(40,dtype=float)

Distances = [0.0,5.0,10.0,15.0,20.0,25.0,30.0,35.0,40.0,45.0,50.0,55.0,60.0,65.0,70.0,75.0,80.0,85.0,90.0,95.0,100.0,105.0,110.0,115.0,120.0,125.0,130.0,135.0,140.0,145.0,150.0,155.0,160.0,165.0,170.0,175.0,180.0,185.0,190.0,195.0]

files_dir = opts["data"]
file_list_aux = os.listdir(files_dir)
file_list_h5 = [x for x in file_list_aux if '.h5' in x]
file_list_h5 = [x for x in file_list_h5 if opts["eff"] in x]

fout = ROOT.TFile(opts["out"]," RECREATE ")

eventcount = 0
	
for filename in file_list :
	h5file = h5py.File(filename, 'r')

	domtable = h5file.root.doms
	eventtable = h5file.root.events

	eventcount += eventtable.nrows()
	domindex = 0

	for event in eventtable.iterrows() :
		DomCharge_event = np.zeros(40,dtype=float)
		DomCharge_norm = np.zeros(40,dtype=float)
		for dom in domtable.iterrows(domindex) :
			if  event['id'] != dom['eventId'] :
				break
			domindex += 1

			dist = dom['recoDist']
			char = dom['totalCharge']
			i_dist = (int)(dist/5.0)
			if i_dist > 0 and i_dist < 40 :
				DomCharge_event[i] += char
				DomCharge_norm[i] += 1.0

		for j in range(len(DomCorCharge_norm)) :
			if DomCharge_norm[j] > 0.0 :
				DomCharge_GaisserH4a[j] += event['weight_GaisserH4a']*DomCharge_event[j]/DomCharge_norm[j]
				DomCharge_GaisserH3a[j] += event['weight_GaisserH3a']*DomCharge_event[j]/DomCharge_norm[j]
				DomCharge_GaisserH4a_IT[j] += event['weight_GaisserH4a_IT']*DomCharge_event[j]/DomCharge_norm[j]
				DomCharge_Hoerandel[j] += event['weight_Hoerandel']*DomCharge_event[j]/DomCharge_norm[j]
				DomCharge_Hoerandel5[j] += event['weight_Hoerandel5']*DomCharge_event[j]/DomCharge_norm[j]
				DomCharge_Hoerandel_IT[j] += event['weight_Hoerandel_IT']*DomCharge_event[j]/DomCharge_norm[j]
				DomCharge_GaisserHillas[j] += event['weight_GaisserHillas']*DomCharge_event[j]/DomCharge_norm[j]
					
tg_GaisserH4a = ROOT.TGraph(len(Distance),Distance,DomCharge_GaisserH4a)
tg_GaisserH3a = ROOT.TGraph(len(Distance),Distance,DomCharge_GaisserH3a)
tg_GaisserH4a_IT = ROOT.TGraph(len(Distance),Distance,DomCharge_GaisserH4a_IT)
tg_Hoerandel = ROOT.TGraph(len(Distance),Distance,DomCharge_Hoerandel)
tg_Hoerandel5 = ROOT.TGraph(len(Distance),Distance,DomCharge_Hoerandel5)
tg_Hoerandel_IT = ROOT.TGraph(len(Distance),Distance,DomCharge_Hoerandel_IT)
tg_GaisserHillas = ROOT.TGraph(len(Distance),Distance,DomCharge_GaisserHillas)


fout.cd()
tg_GaisserH4a.Write("GaisserH4a")
tg_GaisserH3a.Write("GaisserH3a")
tg_GaisserH4a_IT.Write("GaisserH4a_IT")
tg_Hoerandel.Write("Hoerandel")
tg_Hoerandel5.Write("Hoerandel5")
tg_Hoerandel_IT.Write("Hoerandel_IT")
tg_GaisserHillas.Write("GaisserHillas")
fout.Close()


