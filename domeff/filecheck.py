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

gcd_file = '/cvmfs/icecube.opensciencegrid.org/data/GCD/GeoCalibDetectorStatus_IC86_Merged.i3.gz'
gfile = dataio.I3File(gcd_file)
gframe = gfile.pop_frame()
geometry = gframe['I3Geometry']


def residualtime(distance,tracktime,pulsetime):

    texpected = distance / (0.3/1.31) + tracktime

    return pulsetime-texpected

def correctedcharge(distance,charge) :
    return distance*charge


___main___ :

mydom = []
for i in range(len(one_dom)):
    dom = geometry.omgeo[one_dom[i][0]]    
    mydom.append(dom)


infile =  dataio.I3File(os.path.join(files_dir, file_list[i]))

    for frame in infile:  
        frame = infile.pop_physics()             
        fr.append(frame)
        
        mmctracks = frame['MMCTrackList']
        track = mmctracks[0].particle
        tr.append(track)

        pulses = frame['SRTInIcePulsesDOMeff'].apply(frame)

        char = []
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

            for j in range(len(zero)):
            mydom = geometry.omgeo[zero[j]]
            dom.append(mydom)
           
            distance = phys_services.I3Calculator.cherenkov_distance(track, mydom.position)
            dist.append(distance)


			
