import os, sys
from tables import open_file
import ROOT
import numpy as np

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
file_list = [x for x in file_list_h5 if opts["eff"] in x]

fout = ROOT.TFile.Open(opts["out"],"RECREATE")

eventcount = 0
	
for filename in file_list :
	h5file = open_file(files_dir+filename, mode="r")
	print('opening file ' + filename)
	print(h5file)
	domtable = h5file.root.doms
	eventtable = h5file.root.events

	domindex = 0

	for event in eventtable.iterrows() :
		print('event = '+str(event['id']))
		DomCharge_event = np.zeros(40,dtype=float)
		DomCharge_norm = np.zeros(40,dtype=float)
		for dom in domtable.iterrows(domindex) :
			print('dom index = '+str(domindex)+' dom event = ' + str(dom['eventId']))
			if  event['id'] != dom['eventId'] :
				break
			domindex += 1

			dist = dom['recoDist']
			char = dom['totalCharge']
			i_dist = (int)(dist/5.0)
			if i_dist > 0 and i_dist < 40 :
				DomCharge_event[i] += char
				DomCharge_norm[i] += 1.0

		for j in range(len(DomCharge_GaisserH4a)) :
			if DomCharge_norm[j] > 0.0 :
				DomCharge_GaisserH4a[j] += event['weight_GaisserH4a']*DomCharge_event[j]/DomCharge_norm[j]
				DomCharge_GaisserH3a[j] += event['weight_GaisserH3a']*DomCharge_event[j]/DomCharge_norm[j]
				DomCharge_GaisserH4a_IT[j] += event['weight_GaisserH4a_IT']*DomCharge_event[j]/DomCharge_norm[j]
				DomCharge_Hoerandel[j] += event['weight_Hoerandel']*DomCharge_event[j]/DomCharge_norm[j]
				DomCharge_Hoerandel5[j] += event['weight_Hoerandel5']*DomCharge_event[j]/DomCharge_norm[j]
				DomCharge_Hoerandel_IT[j] += event['weight_Hoerandel_IT']*DomCharge_event[j]/DomCharge_norm[j]
				DomCharge_GaisserHillas[j] += event['weight_GaisserHillas']*DomCharge_event[j]/DomCharge_norm[j]
		eventcount = eventcount + 1

	h5file.close()

 for j in range(len(DomCharge_GaisserH4a)) :
 	if eventcount > 0.0 :
        	DomCharge_GaisserH4a[j] /= eventcount
                DomCharge_GaisserH3a[j] /= eventcount
                DomCharge_GaisserH4a_IT[j] /= eventcount 
                DomCharge_Hoerandel[j] /= eventcount
                DomCharge_Hoerandel5[j] /= eventcount 
                DomCharge_Hoerandel_IT[j] /= eventcount 
                DomCharge_GaisserHillas[j] /= eventcount 
		
tg_GaisserH4a = ROOT.TGraph(len(Distances),np.array(Distances),np.array(DomCharge_GaisserH4a))
tg_GaisserH3a = ROOT.TGraph(len(Distances),np.array(Distances),np.array(DomCharge_GaisserH3a))
tg_GaisserH4a_IT = ROOT.TGraph(len(Distances),np.array(Distances),np.array(DomCharge_GaisserH4a_IT))
tg_Hoerandel = ROOT.TGraph(len(Distances),np.array(Distances),np.array(DomCharge_Hoerandel))
tg_Hoerandel5 = ROOT.TGraph(len(Distances),np.array(Distances),np.array(DomCharge_Hoerandel5))
tg_Hoerandel_IT = ROOT.TGraph(len(Distances),np.array(Distances),np.array(DomCharge_Hoerandel_IT))
tg_GaisserHillas = ROOT.TGraph(len(Distances),np.array(Distances),np.array(DomCharge_GaisserHillas))


fout.cd()
tg_GaisserH4a.Write("GaisserH4a")
tg_GaisserH3a.Write("GaisserH3a")
tg_GaisserH4a_IT.Write("GaisserH4a_IT")
tg_Hoerandel.Write("Hoerandel")
tg_Hoerandel5.Write("Hoerandel5")
tg_Hoerandel_IT.Write("Hoerandel_IT")
tg_GaisserHillas.Write("GaisserHillas")
fout.Close()


