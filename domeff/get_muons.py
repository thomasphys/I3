#!/usr/bin/env python

"""
Process the I3 files.
"""

from __future__ import print_function, division  # 2to3

import argparse

from icecube import dataio, icetray, gulliver, simclasses, dataclasses, photonics_service, phys_services, spline_reco, MuonGun
from icecube.common_variables import direct_hits, hit_multiplicity, hit_statistics
from I3Tray import I3Tray, I3Units, load
#from filters_InIceSplit import in_ice, min_bias, SMT8, MPEFit, InIceSMTTriggered
from filters_InIceSplit_2015 import in_ice, min_bias, SMT8, MPEFit, InIceSMTTriggered, FiniteRecoFilter, muon_zenith, SplineMPE
from general import get_truth_muon, get_truth_endpoint, count_hits, reco_endpoint, move_cut_variables
from geoanalysis import calc_dist_to_border
from domanalysis import dom_data
from energy_reco_truth import TruthMuon, truth_info
# Pulse series

from icecube.filterscripts.offlineL2.level2_HitCleaning_WIMP import WimpHitCleaning

# Reconstructions

from icecube.filterscripts.offlineL2.level2_Reconstruction_WIMP import FiniteReco
from icecube.filterscripts.offlineL2.level2_Reconstruction_Muon import SPE, MPE
from icecube.filterscripts.offlineL2.PhotonTables import InstallTables
from icecube import cramer_rao

from icecube.phys_services import I3Calculator as calc
from icecube.dataclasses import I3Constants
import math


load('libmue')
load('libipdf')
load('libgulliver')
load('libgulliver-modules')
load('liblilliput')
load('libstatic-twc')
#load('libjeb-filter-2012')
load('libfilterscripts')



def mus(frame):
    tree = frame['I3MCTree']
    muons = []
    analysis_muons = []
    frame['AnalysisMuons']=dataclasses.I3MCTree()
    for particle in tree:
        if particle.type_string in ('MuPlus', 'MuMinus') and particle.location_type_string== 'InIce':
            muons.append(particle)

    tree = frame['BackgroundI3MCTree']

    for particle in tree:
        if particle.type_string in ('MuPlus', 'MuMinus') and particle.location_type_string== 'InIce':
            muons.append(particle)

    # Apparently, some very specific events can have no muons going through the extended analysis region......                                                                                              
    # This is something to investigate as we move forward!                                                                                                                                                  

    # To avoid the program crashing, we might fill the truth muon variable as the first muon in the I3MCTree for those                                                                                      
    # cases (still the number of visible muons will come up as zero in the event, so we can use that to filter events later                                                                                 
    # on, and investigate those extreme cases).                                                                                                                                                             

    max_energy_muon = muons[0] # extreme case....                                                                                                                                                           

    border_space = 140.

    top = -140. + border_space # position of the highest DOM in the analysis region                                                                                                                         
    bottom = - 512.8 # position of the lowest DOM in the analysis region                                                                                                                                    

    height = math.fabs(top - bottom)
    center_z = height/2. + bottom

    radius = 251.07 + border_space

    surface = MuonGun.Cylinder(height*I3Units.m, radius*I3Units.m, dataclasses.I3Position(45.312415731951312, -32.596895679813862, center_z))

    truth_energy = 1e-20
    num_visible_muons = 0

    for track in MuonGun.Track.harvest(frame['I3MCTree'], frame['MMCTrackList']):

        # Find distance to entrance and exit from sampling volume                                                                                                                                           
        intersections = surface.intersection(track.pos, track.dir)
        energy = track.get_energy(intersections.first)
        if(intersections.first >= 0 and energy > 0):
            frame['AnalysisMuons'].insert(track)
            num_visible_muons += 1
            if( energy > truth_energy):
                max_energy_muon = track
                truth_energy = energy



def main():

    parser = argparse.ArgumentParser(description='script for proccessing I3 files')
    parser.add_argument('gcd', help='GCD file for the data')
    parser.add_argument('data', help='data file for processing') 
    parser.add_argument('ofile', help='name of output file')
    parser.add_argument('-s', '--sim', help='turn on extra processing for sim files',
                        action='store_true')
    args = parser.parse_args()

    # Don't touch, unless you know what you're doing
    options = {}
    options['pulses_name'] = 'SRTInIcePulsesDOMeff'
    options['max_dist'] = 140
#    options['partitions'] = 5

    tray = I3Tray()

    # Read the files.
    tray.AddModule('I3Reader', 'I3Reader',
                   Filenamelist=[args.gcd, args.data])




    tray.AddModule(mus, 'mus')





    # Write out the data to an I3 file
    tray.AddModule('I3Writer', 'I3Writer',
                   FileName=args.ofile,
                   #SkipKeys=['InIceRecoPulseSeriesPattern.*'],
                   DropOrphanStreams=[icetray.I3Frame.DAQ],
                   Streams=[icetray.I3Frame.DAQ, icetray.I3Frame.Physics])
    
    tray.AddModule('TrashCan', 'yeswecan')
    tray.Execute()
    tray.Finish()

if __name__ == '__main__':
    main()
