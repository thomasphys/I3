import os, sys
import numpy as np
import matplotlib as mpl
from matplotlib.colors import LogNorm, Normalize
import matplotlib.pyplot as plt
import timeit as time
import math
from datetime import datetime

files_dir = '/data/sim/IceCube/2016/generated/CORSIKA-in-ice/21269/IC86_2016_spe_templates_DOM_oversize1/level2/redo'
file_list_aux = os.listdir(files_dir)
file_list = [x for x in file_list_aux if '.i3.bz2' in x]

nfiles = len(file_list)

def func(frame):

    pulses = frame['SRTInIcePulsesDOMeff'].apply(frame)
    one_dom = pulses.items()
    charge = []
    
    for i in range(len(one_dom)):  
        char = 0
        for pulse in one_dom[i][1]:
            char += pulse.charge        
        if char > 0:
            charge.append(char)
        
    gcd_file = '/cvmfs/icecube.opensciencegrid.org/data/GCD/GeoCalibDetectorStatus_IC86_Merged.i3.gz'
    gfile = dataio.I3File(gcd_file)
    gframe = gfile.pop_frame()
    geometry = gframe['I3Geometry']
    
    mydom = []
    for i in range(len(one_dom)):
        dom = geometry.omgeo[one_dom[i][0]]    
        mydom.append(dom) 
        
    mmctracks = frame['MMCTrackList']
    track = mmctracks[0].particle

    dis = np.sqrt((mydom[len(mydom)-1].position.x - mydom[0].position.x)**2 + 
                  (mydom[len(mydom)-1].position.y - mydom[0].position.y)**2
    +(mydom[len(mydom)-1].position.z - mydom[0].position.z)**2)
    
    distance = []
    for i in range(len(mydom)):
        d = phys_services.I3Calculator.cherenkov_distance(track, mydom[i].position)
        distance.append(d)
        
    corrected_charge = []
    for i in range(len(distance)):
        att_length = 50. 
        corrected = charge[i]*distance[i]
        corrected_charge.append(corrected)
    
    return corrected_charge, dis

___main___ :

gcd_file = '/cvmfs/icecube.opensciencegrid.org/data/GCD/GeoCalibDetectorStatus_IC86_Merged.i3.gz'
gfile = dataio.I3File(gcd_file)
gframe = gfile.pop_frame()

geometry = gframe['I3Geometry']

mydom = []
for i in range(len(one_dom)):
    dom = geometry.omgeo[one_dom[i][0]]    
    mydom.append(dom)

distance = []
for i in range(len(mydom)):
    d = phys_services.I3Calculator.cherenkov_distance(track, mydom[i].position)
    distance.append(d)

char = []

for i in range(nfiles):
    with dataio.I3File(os.path.join(files_dir, file_list[i])) as infile:
        for frame in infile:  
            frame = infile.pop_physics()             
            fr.append(frame)
            pulses = frame['SRTInIcePulsesDOMeff'].apply(frame)

zero = []
one = []

for i in range(len(pulses)):
    one_dom = pulses.popitem()
   
    charge = 0
    for pulse in one_dom[1]:
        charge += pulse.charge
    char.append(charge)
    zero.append(one_dom[0])
    one.append(one_dom[1])


dom=[]
tr=[]
dist = []

for i in range(nfiles):
    with dataio.I3File(os.path.join(files_dir, file_list[i])) as infile:
        for frame in infile:  
            frame = infile.pop_physics()             
            fr.append(frame)
        
            mmctracks = frame['MMCTrackList']
            track = mmctracks[0].particle
            tr.append(track)
        
        gframe = gfile.pop_frame()    
        geometry = gframe['I3Geometry']

for j in range(len(zero)):
    mydom = geometry.omgeo[zero[j]]
    dom.append(mydom)
           
    distance = phys_services.I3Calculator.cherenkov_distance(track, mydom.position)
    dist.append(distance)




for i in range(nfiles):
	    with dataio.I3File(os.path.join(files_dir, file_list[i])) as infile:
		for frame in infile:
			if infile.stream.id != 'P': continue

			
