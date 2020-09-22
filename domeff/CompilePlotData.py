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
DomCharge_GaisserH4a_dc  = np.zeros(40,dtype=float)
DomCharge_GaisserH3a_dc  = np.zeros(40,dtype=float)
DomCharge_GaisserHillas_dc  = np.zeros(40,dtype=float)
DomCharge_GaisserH4a_IT_dc  = np.zeros(40,dtype=float)
DomCharge_Hoerandel_dc  = np.zeros(40,dtype=float)
DomCharge_Hoerandel5_dc  = np.zeros(40,dtype=float)
DomCharge_Hoerandel_IT_dc  = np.zeros(40,dtype=float)

Distances = [0.0,5.0,10.0,15.0,20.0,25.0,30.0,35.0,40.0,45.0,50.0,55.0,60.0,65.0,70.0,75.0,80.0,85.0,90.0,95.0,100.0,105.0,110.0,115.0,120.0,125.0,130.0,135.0,140.0,145.0,150.0,155.0,160.0,165.0,170.0,175.0,180.0,185.0,190.0,195.0]
DC_Strings = [26,27,37,46,45,35]
IC_Strings = [17,18,19,28,38,47,56,55,54,44,34,25]

files_dir = opts["data"]
file_list_aux = os.listdir(files_dir)
file_list_h5 = [x for x in file_list_aux if '.h5' in x]
file_list = [x for x in file_list_h5 if opts["eff"] in x]

fout = ROOT.TFile.Open(opts["out"],"RECREATE")

eventcount_GaisserH4a = 0
eventcount_GaisserH3a = 0
eventcount_GaisserHillas = 0
eventcount_GaisserH4a_IT = 0
eventcount_Hoerandel = 0
eventcount_Hoerandel5 = 0
eventcount_Hoerandel_IT = 0
eventcount = 0
	
for filename in file_list :
	h5file = open_file(files_dir+filename, mode="r")
	#print('opening file ' + filename)
	#print(h5file)
	domtable = h5file.root.doms
	eventtable = h5file.root.events
	runtable = h5file.root.runinfo

	domindex = 0

	for event in eventtable.iterrows() :
		#print('event = '+str(event['id']))
		DomCharge_event = np.zeros(40,dtype=float)
		DomCharge_norm = np.zeros(40,dtype=float)
		DomCharge_event_dc = np.zeros(40,dtype=float)
		DomCharge_norm_dc = np.zeros(40,dtype=float)
		for dom in domtable.iterrows(domindex) :
			#print('dom index = '+str(domindex)+' dom event = ' + str(dom['eventId']))
			if  event['id'] != dom['eventId'] :
				break
			domindex += 1

			dist = dom['recoDist']
			char = dom['totalCharge']
			i_dist = (int)(dist/5.0)
			if i_dist > 0 and i_dist < 40 :
				if dom['string'] in DC_Strings :
					DomCharge_event_dc[i_dist] += char
					DomCharge_norm_dc[i_dist] += 1.0
				if dom['string'] in IC_Strings :
					DomCharge_event[i_dist] += char
					DomCharge_norm[i_dist] += 1.0

		for j in range(len(DomCharge_GaisserH4a)) :
			if DomCharge_norm[j] > 0.0 :
				DomCharge_GaisserH4a[j] += event['weight_GaisserH4a']*DomCharge_event[j]/DomCharge_norm[j]
				DomCharge_GaisserH3a[j] += event['weight_GaisserH3a']*DomCharge_event[j]/DomCharge_norm[j]
				DomCharge_GaisserH4a_IT[j] += event['weight_GaisserH4a_IT']*DomCharge_event[j]/DomCharge_norm[j]
				DomCharge_Hoerandel[j] += event['weight_Hoerandel']*DomCharge_event[j]/DomCharge_norm[j]
				DomCharge_Hoerandel5[j] += event['weight_Hoerandel5']*DomCharge_event[j]/DomCharge_norm[j]
				DomCharge_Hoerandel_IT[j] += event['weight_Hoerandel_IT']*DomCharge_event[j]/DomCharge_norm[j]
				DomCharge_GaisserHillas[j] += event['weight_GaisserHillas']*DomCharge_event[j]/DomCharge_norm[j]
			if DomCharge_norm_dc[j] > 0.0 :
				DomCharge_GaisserH4a_dc[j] += event['weight_GaisserH4a']*DomCharge_event_dc[j]/DomCharge_norm_dc[j]
				DomCharge_GaisserH3a_dc[j] += event['weight_GaisserH3a']*DomCharge_event_dc[j]/DomCharge_norm_dc[j]
				DomCharge_GaisserH4a_IT_dc[j] += event['weight_GaisserH4a_IT']*DomCharge_event_dc[j]/DomCharge_norm_dc[j]
				DomCharge_Hoerandel_dc[j] += event['weight_Hoerandel']*DomCharge_event_dc[j]/DomCharge_norm_dc[j]
				DomCharge_Hoerandel5_dc[j] += event['weight_Hoerandel5']*DomCharge_event_dc[j]/DomCharge_norm_dc[j]
				DomCharge_Hoerandel_IT_dc[j] += event['weight_Hoerandel_IT']*DomCharge_event_dc[j]/DomCharge_norm_dc[j]
				DomCharge_GaisserHillas_dc[j] += event['weight_GaisserHillas']*DomCharge_event_dc[j]/DomCharge_norm_dc[j]
		eventcount = eventcount + 1
		eventcount_GaisserH4a += event['weight_GaisserH4a'] 
		eventcount_GaisserH3a += event['weight_GaisserH3a']
		eventcount_GaisserHillas += event['weight_GaisserHillas']
		eventcount_GaisserH4a_IT += event['weight_GaisserH4a_IT'] 
		eventcount_Hoerandel += event['weight_Hoerandel']
		eventcount_Hoerandel5 += event['weight_Hoerandel5'] 
		eventcount_Hoerandel_IT += event['weight_Hoerandel_IT']

	h5file.close()

for j in range(len(DomCharge_GaisserH4a)) :
	if eventcount > 0.0 :
		DomCharge_GaisserH4a[j] /= eventcount_GaisserH4a
		DomCharge_GaisserH3a[j] /= eventcount_GaisserH3a
		DomCharge_GaisserH4a_IT[j] /= eventcount_GaisserH4a_IT
		DomCharge_Hoerandel[j] /= eventcount_Hoerandel
		DomCharge_Hoerandel5[j] /= eventcount_Hoerandel5
		DomCharge_Hoerandel_IT[j] /= eventcount_Hoerandel_IT
		DomCharge_GaisserHillas[j] /= eventcount_GaisserHillas
		DomCharge_GaisserH4a_dc[j] /= eventcount_GaisserH4a
                DomCharge_GaisserH3a_dc[j] /= eventcount_GaisserH3a
                DomCharge_GaisserH4a_IT_dc[j] /= eventcount_GaisserH4a_IT
                DomCharge_Hoerandel_dc[j] /= eventcount_Hoerandel
                DomCharge_Hoerandel5_dc[j] /= eventcount_Hoerandel5
                DomCharge_Hoerandel_IT_dc[j] /= eventcount_Hoerandel_IT
                DomCharge_GaisserHillas_dc[j] /= eventcount_GaisserHillas
		
tg_GaisserH4a = ROOT.TGraph(len(Distances),np.array(Distances),np.array(DomCharge_GaisserH4a))
tg_GaisserH3a = ROOT.TGraph(len(Distances),np.array(Distances),np.array(DomCharge_GaisserH3a))
tg_GaisserH4a_IT = ROOT.TGraph(len(Distances),np.array(Distances),np.array(DomCharge_GaisserH4a_IT))
tg_Hoerandel = ROOT.TGraph(len(Distances),np.array(Distances),np.array(DomCharge_Hoerandel))
tg_Hoerandel5 = ROOT.TGraph(len(Distances),np.array(Distances),np.array(DomCharge_Hoerandel5))
tg_Hoerandel_IT = ROOT.TGraph(len(Distances),np.array(Distances),np.array(DomCharge_Hoerandel_IT))
tg_GaisserHillas = ROOT.TGraph(len(Distances),np.array(Distances),np.array(DomCharge_GaisserHillas))

tg_GaisserH4a_dc = ROOT.TGraph(len(Distances),np.array(Distances),np.array(DomCharge_GaisserH4a_dc))
tg_GaisserH3a_dc = ROOT.TGraph(len(Distances),np.array(Distances),np.array(DomCharge_GaisserH3a_dc))
tg_GaisserH4a_IT_dc = ROOT.TGraph(len(Distances),np.array(Distances),np.array(DomCharge_GaisserH4a_IT_dc))
tg_Hoerandel_dc = ROOT.TGraph(len(Distances),np.array(Distances),np.array(DomCharge_Hoerandel_dc))
tg_Hoerandel5_dc = ROOT.TGraph(len(Distances),np.array(Distances),np.array(DomCharge_Hoerandel5_dc))
tg_Hoerandel_IT_dc = ROOT.TGraph(len(Distances),np.array(Distances),np.array(DomCharge_Hoerandel_IT_dc))
tg_GaisserHillas_dc = ROOT.TGraph(len(Distances),np.array(Distances),np.array(DomCharge_GaisserHillas_dc))


fout.cd()
tg_GaisserH4a.Write("GaisserH4a")
tg_GaisserH3a.Write("GaisserH3a")
tg_GaisserH4a_IT.Write("GaisserH4a_IT")
tg_Hoerandel.Write("Hoerandel")
tg_Hoerandel5.Write("Hoerandel5")
tg_Hoerandel_IT.Write("Hoerandel_IT")
tg_GaisserHillas.Write("GaisserHillas")
tg_GaisserH4a_dc.Write("GaisserH4a_dc")
tg_GaisserH3a_dc.Write("GaisserH3a_dc")
tg_GaisserH4a_IT_dc.Write("GaisserH4a_IT_dc")
tg_Hoerandel_dc.Write("Hoerandel_dc")
tg_Hoerandel5_dc.Write("Hoerandel5_dc")
tg_Hoerandel_IT_dc.Write("Hoerandel_IT_dc")
tg_GaisserHillas_dc.Write("GaisserHillas_dc")
fout.Close()


