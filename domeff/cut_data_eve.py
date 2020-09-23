#!/usr/bin/env python

"""
Script for making event and DOM cuts.

The cuts to make are specified in a file called "cut_options.py". The directory
containing this file needs to be added to the PYTHONPATH in order for this file
to find and import it. See example in the current directory for an example.
"""

from __future__ import print_function, division  # 2to3

import argparse
import math
import glob
import numpy as np
import I3Tray
from icecube import icetray, dataclasses, dataio
from icecube.hdfwriter import I3HDFTableService
from icecube.rootwriter import I3ROOTTableService
from icecube.tableio import I3TableWriter
from icecube.dataclasses import I3Constants
from icecube.phys_services import I3Calculator as calc
from functions import make_event_cuts, make_dom_cuts, write_cut_metadata
from cut_options_data import event_cuts, dom_cuts, dom_keys

def tot_charge(frame,reco_fit,pulses):
    n_ice_group = I3Constants.n_ice_group
    n_ice_phase = I3Constants.n_ice_phase
    pulse_series = frame[pulses].apply(frame)
    dom_geo = frame['I3Geometry'].omgeo.items()
    total_charge = 0
    for dom, geo in dom_geo:
        dom_position = geo.position
        mpe = frame[reco_fit]
        if dom in pulse_series.keys():
            for pulse in pulse_series[dom]:
                time_res = calc.time_residual(mpe, dom_position, pulse.time, n_ice_group, n_ice_phase)
                if time_res < 1000:
                    total_charge += pulse.charge
    frame['EventCharge'] = dataclasses.I3Double(total_charge)


def pulse_reader(frame):
    pass2_charge = []
    pass1_charge = []
    pass2_dist = []
    pass1_dist = []
    test1 = frame['I3SuperDSTUnChargeCorrected'].unpack()
    event = frame['I3EventHeader']
    totalcharge = np.array(frame['TotalCharge'])
    distance = np.array(frame['RecoDistance'])
    test2 = frame['I3SuperDST'].apply(frame)
    oms = np.array(frame['OM'])
    strings = np.array(frame['String'])
    charged_oms = oms[np.where(totalcharge > 0)]
    charged_strings = strings[np.where(totalcharge > 0)]
    om_string = []
    for i in range(len(charged_oms)):
        om_string.append([charged_oms[i],charged_strings[i]])
        
    om_string = list(om_string)
    
    for i,j in test2:
        temptot = 0
        temp = [i.om,i.string]
            
        if temp in om_string:
            index = om_string.index(temp)
            for p in j:
                temptot+=(p.charge)
            pass2_charge.append(temptot)
            pass2_dist.append(distance[index])
    frame['Pass2_Charge'] = dataclasses.I3VectorDouble(pass2_charge)
    frame['Pass2_Dist'] = dataclasses.I3VectorDouble(pass2_dist)

    for i,j in test1:
        temptot = 0
        temp = [i.om,i.string]

        if temp in om_string:
            for p in j:
                temptot+=(p.charge)
            pass1_charge.append(temptot)
            pass1_dist.append(distance[index])

    frame['Pass1_Charge'] = dataclasses.I3VectorDouble(pass1_charge)
    frame['Pass1_Dist'] = dataclasses.I3VectorDouble(pass1_dist)

def main():

    parser = argparse.ArgumentParser(description='script for making event and DOM cuts')
    parser.add_argument('-g','--gcd', help = 'GCD file', required = True)
    parser.add_argument('-d', '--datadirectory', help='data files to make the cuts on',
                        required=True)
    parser.add_argument('-o', '--ofile', help='name of output file',
                        required=True)
    parser.add_argument('--root', help='write output to ROOT file instead',
                        action='store_true')
    args = parser.parse_args()
    gcd = (args.gcd)
    files = [gcd]
    datafiles = list(glob.glob(args.datadirectory + '/*'))
    #    datafiles = args.datadirector
    files.extend(datafiles)
   # print(files)
    tray = I3Tray.I3Tray()
    
    tray.AddModule('I3Reader', 'I3Reader',
                   Filenamelist=files)
    # Cut out the frames that do not pass the event cuts.
    tray.AddModule(make_event_cuts, 'make_event_cuts',
                   event_cuts=event_cuts)

    # The remaining frames pass all the event cuts. Now go into the
    # dom data of each frame and make the dom cuts.
    tray.AddModule(make_dom_cuts, 'make_dom_cuts',
                   dom_cuts=dom_cuts,
                   dom_keys=dom_keys)
#    tray.AddModule(pulse_change, 'pulse_change')
    # Get the appropriate output file service
    tray.AddModule(tot_charge,'tot_charge',
                   reco_fit='SplineMPE',
                   pulses='SRTInIcePulsesDOMeff')


    if args.root:
        ofile_service = I3ROOTTableService(args.ofile)
    else:
        ofile_service = I3HDFTableService(args.ofile)

    tray.AddModule(I3TableWriter, 'I3TableWriter',
#                   keys = ['RecoEndpoint','MPEFitDOMeff','FiniteRecoFitDOMeff','TotalChargeCut','SplineMPE','DistAboveEndpointCut','ImpactAngleCut','ICNHits','NDirDoms','NumInIceMuons','OMCut','PolyplopiaPrimary','RecoDistanceCut','RecoEndpoint','RecoEndpointZ','StringCut','rlogl','PrimaryParticle','DomsInEvent','PhotonArrivalAngleCut'],
                   keys = ['RecoEndpoint','MPEFitDOMeff','FiniteRecoFitDOMeff','TotalChargeCut','SplineMPE','DistAboveEndpointCut','ImpactAngleCut','ICNHits','NDirDoms','NumInIceMuons','OMCut','RecoDistanceCut','RecoEndpoint','RecoEndpointZ','StringCut','rlog','DomsInEvent','PhotonArrivalAngleCut','TruthDistanceCut','FiniteRecoLLHRatio','TruthEndpoint','EventCharge','OM','ImpactAngle','String','TotalCharge','DistAboveEndpoint','AllDoms','EventCharge'],
                   TableService=ofile_service,
                   BookEverything=False,
                   SubEventStreams=['InIceSplit'])

    tray.Execute()
    tray.Finish()

    if not args.root:
        # Write the cuts to the HDF5 as metadata (so we know for later).
        write_cut_metadata(args.ofile, event_cuts, dom_cuts)


if __name__ == '__main__':
    main()
