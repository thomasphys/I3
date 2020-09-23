#!/usr/bin/env python

"""
Process the I3 files.
"""

from __future__ import print_function, division  # 2to3

import argparse

from icecube import dataio, icetray, gulliver, simclasses, dataclasses, photonics_service, phys_services, spline_reco, MuonGun
from I3Tray import I3Tray, I3Units, load
from icecube.weighting import get_weighted_primary

from icecube.phys_services import I3Calculator as calc
from icecube.dataclasses import I3Constants
import math

def TruthMuon(frame):

    """
    Count the number of in ice muons and get the most energetic one.

    Adds To Frame
    --------------
    NumInIceMuons : I3Double
        The number of in ice muons from the I3MCTree.

    TruthMuon : I3Particle
        The in ice muon with the largest energy. We take this muon as being
        the "truth".
    """

    tree = frame['I3MCTree']
    muons = []

    for particle in tree:
        if particle.type_string in ('MuPlus', 'MuMinus') and particle.location_type_string== 'InIce':
            muons.append(particle)
    
    tree = frame['BackgroundI3MCTree']

    for particle in tree:
        if particle.type_string in ('MuPlus', 'MuMinus') and particle.location_type_string== 'InIce':
            muons.append(particle)

    max_energy_muon = muons[0]
    
    for muon in muons:
        if muon.energy > max_energy_muon.energy:
            max_energy_muon = muon
    
    frame['TruthMuon_all_ice'] = max_energy_muon
    frame['NumInIceMuons'] = dataclasses.I3Double(len(muons))

    surface = MuonGun.Cylinder(300*I3Units.m, 350*I3Units.m, dataclasses.I3Position(0.,0.,0.-250.0))

    truth_energy = 0
    num_visible_muons = 0

    for track in MuonGun.Track.harvest(frame['I3MCTree'], frame['MMCTrackList']):
        
        # Find distance to entrance and exit from sampling volume
        intersections = surface.intersection(track.pos, track.dir)
        energy = track.get_energy(intersections.first)
        if(intersections.first >= 0 and energy > 0):
            num_visible_muons += 1
            if( energy > truth_energy):
                max_energy_muon = track
                truth_energy = energy
        
    for track in MuonGun.Track.harvest(frame['BackgroundI3MCTree'], frame['BackgroundMMCTrackList']):
        
        # Find distance to entrance and exit from sampling volume
        intersections = surface.intersection(track.pos, track.dir)
        energy = track.get_energy(intersections.first)
        if(intersections.first >= 0 and energy > 0): 
            num_visible_muons += 1
            if( energy > truth_energy):
                max_energy_muon = track
                truth_energy = energy
        
    for muon in muons:
        if(muon.major_id == max_energy_muon.major_id and muon.minor_id == max_energy_muon.minor_id):
            max_energy_muon = muon

    frame['TruthMuon']= max_energy_muon
    frame['NumVisibleMuons_analysis_region'] = dataclasses.I3Double(num_visible_muons)

#def muonTruthEnergy(frame):
#
#    surface = MuonGun.Cylinder(350*I3Units.m, 456*I3Units.m, dataclasses.I3Position(0.,0.,0.-225.0))
#
#    truthmuonenergy = 1e-9
#
#    partVec = MuonGun.muons_at_surfacg(frame, surface)
#
#    for p in partVec:
#        if p.energy > truthmuonenergy:
#            truthmuonenergy = p.energy
#
#    frame['Energy_truth'] = dataclasses.I3Double(truthmuonenergy)

def muonTruthEnergy(frame):

    surface = MuonGun.Cylinder(350*I3Units.m, 456*I3Units.m, dataclasses.I3Position(0.,0.,0.-225.0))
    max_energy_muon = frame['TruthMuon']

    truth_energy = 1e-9

    for track in MuonGun.Track.harvest(frame['I3MCTree'], frame['MMCTrackList']):
        
        if(track.major_id == max_energy_muon.major_id and track.minor_id == max_energy_muon.minor_id):    
            # Find distance to entrance and exit from sampling volume
            intersections = surface.intersection(track.pos, track.dir)
            energy = track.get_energy(intersections.first)
            if(intersections.first >= 0 and energy > 0):
                if( energy > truth_energy):
                    truth_energy = energy
    
    for track in MuonGun.Track.harvest(frame['BackgroundI3MCTree'], frame['BackgroundMMCTrackList']):
        
        if(track.major_id == max_energy_muon.major_id and track.minor_id == max_energy_muon.minor_id):    
            # Find distance to entrance and exit from sampling volume
            intersections = surface.intersection(track.pos, track.dir)
            energy = track.get_energy(intersections.first)
            if(intersections.first >= 0 and energy > 0):
                if( energy > truth_energy):
                    truth_energy = energy

    frame['TruthEnergy'] = dataclasses.I3Double(truth_energy)


def muonRecoEnergy(frame, suffix = 'DOMeff'):

    muonenergy = 1e-9

    surface = MuonGun.Cylinder(350*I3Units.m, 456*I3Units.m, dataclasses.I3Position(0.,0.,0.-225.0))

    p = frame['FiniteRecoFit'+suffix]
    intersections = surface.intersection(p.pos,p.dir)
    length_reco = p.length - intersections.first
    energy = length_reco/4.5
    if energy > muonenergy:
        muonenergy = energy

    frame['Energy_finiteReco'] = dataclasses.I3Double(muonenergy)

#def extract_weight(frame):
#    
#    correction = 1.
#    filters = frame['FilterMask']
#    a_filter_passed = False
#    for key in filters.keys():
#        a_filter_passed = a_filter_passed or filters[key].condition_passed   
#    if a_filter_passed == False:
#        correction = 1/1000.
#    frame['weightCorrection'] =  dataclasses.I3Double(correction)

def dom_data(frame, reco_fit):

    n_ice_group = I3Constants.n_ice_group
    n_ice_phase = I3Constants.n_ice_phase
        
    frame['PhotonArrivalAngleCut'] = dataclasses.I3VectorDouble()

    dom_geo = frame['I3Geometry'].omgeo.items()
    strings = frame['StringCut']
    oms = frame['OMCut']
    cherenkov_distances = frame['RecoDistanceCut']

    mpe = frame[reco_fit]
    for i in range(0,len(strings)):
        for om, geo in dom_geo:
            if(om.string==strings[i] and om.om==oms[i]):
                dom_position = geo.position
        cherenkov_dist = cherenkov_distances[i]
        cherenkov_pos = calc.cherenkov_position(mpe, dom_position, n_ice_group, n_ice_phase)
        perp_position = dataclasses.I3Position(dom_position.x, dom_position.y, cherenkov_pos.z)
        delta = perp_position - cherenkov_pos
        impact_param = delta.magnitude
        if cherenkov_pos.z < dom_position.z:
            ph_angle = math.asin(impact_param / cherenkov_dist)
        else:
            # There is one event that is failing, lets try to correct for it...
            if((impact_param/cherenkov_dist) > 1):
                print("Impact_param= {}".format(impact_param))
                print("Cherenkov_dist = {}".format(cherenkov_dist))
                impact_param = cherenkov_dist
            ph_angle = math.pi - math.asin(impact_param / cherenkov_dist)
        frame['PhotonArrivalAngleCut'].append(ph_angle)

def get_lenght_spe(frame):

    lenght = len(frame['TotalChargeCut'])
    frame['lenghtSPE'] = dataclasses.I3Double(lenght)

#def get_coincident(frame):
#
#    frame['Coincident_MCPEs'] = dataclasses.I3Double(len(frame['BackgroundI3MCPESeriesMap_0.990']))    

def main():

    # The amount of statistics per subRun after running the basic filters on 2015 data is low enough
    # to allow processing one full run into a single output .i3 file
    # TODO, enable that

    parser = argparse.ArgumentParser(description='script for proccessing I3 files')
    parser.add_argument('gcd', help='GCD file for the data')
    parser.add_argument('data', help='data file for processing') 
    parser.add_argument('ofile', help='name of output file')
    parser.add_argument('-s', '--sim', help='turn on extra processing for sim files',
                        action='store_true')
    args = parser.parse_args()

    reco_fit = 'SplineMPE'

    tray = I3Tray()

    # Read the files.
    tray.AddModule('I3Reader', 'I3Reader',
                   Filenamelist=[args.gcd, args.data])

    tray.AddModule(muonRecoEnergy, 'get_reco_energy',
                     suffix = 'DOMeff')
    
    if args.sim:
        # Get the truth muon energy
        tray.AddModule(TruthMuon,'get_truth_muon')

        tray.AddModule(muonTruthEnergy, 'get_truth_energy')
    
        tray.AddModule(get_weighted_primary,'weightedPrimaryMe',
                        MCPrimary='WeightedPrimary' )

        # Extract the weight corrections given our prescale factor of 1/1000

        #tray.AddModule(extract_weight,'ExtractWeightCorrections')

    tray.AddModule(get_lenght_spe,'GetLenghtSPE')
    
    tray.AddModule(dom_data,'DOMdata',
                    reco_fit=reco_fit)

        #tray.AddModule(get_coincident,'GetCoincident')
    
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
