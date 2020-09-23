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

import I3Tray
from icecube import icetray, dataclasses, dataio
from icecube.hdfwriter import I3HDFTableService
from icecube.rootwriter import I3ROOTTableService
from icecube.tableio import I3TableWriter

from functions import make_event_cuts, make_dom_cuts, write_cut_metadata, bdt_vars
from cut_options import event_cuts, dom_cuts, dom_keys

def frame_checker(frame):
    keys = ['DomsInEvent','PrimaryParticle']
    for i in range(len(keys)):
        if keys[i] in frame:
            flag = True
        else:
            flag = False
            break
    return flag

def main():

    parser = argparse.ArgumentParser(description='script for making event and DOM cuts')
    parser.add_argument('-d', '--datafiles', help='data files to make the cuts on',
                        nargs='+', required=True)
    parser.add_argument('-o', '--ofile', help='name of output file',
                        required=True)
    parser.add_argument('--root', help='write output to ROOT file instead',
                        action='store_true')
    args = parser.parse_args()

    tray = I3Tray.I3Tray()

    tray.AddModule('I3Reader', 'I3Reader',
                   Filenamelist=args.datafiles)
    # Cut out the frames that do not pass the event cuts.
    tray.AddModule(make_event_cuts, 'make_event_cuts',
                   event_cuts=event_cuts)

    # The remaining frames pass all the event cuts. Now go into the
    # dom data of each frame and make the dom cuts.
    tray.AddModule(make_dom_cuts, 'make_dom_cuts',
                   dom_cuts=dom_cuts,
                   dom_keys=dom_keys)
    tray.AddModule(frame_checker, 'frame_checker')
    # Get the appropriate output file service
    if args.root:
        ofile_service = I3ROOTTableService(args.ofile)
    else:
        ofile_service = I3HDFTableService(args.ofile)

    tray.AddModule(I3TableWriter, 'I3TableWriter',
                   keys = ['TruthMuon','RecoEndpoint','MPEFitDOMeff','FiniteRecoFitDOMeff','TotalChargeCut','SplineMPE','DistAboveEndpointCut','ImpactAngleCut','ICNHits','NDirDoms','NumInIceMuons','OMCut','PolyplopiaPrimary','RecoDistanceCut','RecoEndpoint','RecoEndpointZ','StringCut','rlogl','PrimaryParticle','DomsInEvent','NumVisibleMuons_analysis_region','PhotonArrivalAngleCut','TruthDistanceCut','TruthEnergy','FiniteRecoLLHRatio','TruthEndpoint','EventCharge','OM','ImpactAngle','String','TotalCharge','DistAboveEndpoint','AllDoms'],
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
