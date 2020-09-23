#!/usr/bin/env python

"""
Process the I3 files.
"""

from __future__ import print_function, division  # 2to3

import argparse

from icecube import dataio, icetray, gulliver, simclasses, dataclasses, photonics_service, phys_services, spline_reco #, MuonGun
from icecube.common_variables import direct_hits, hit_multiplicity, hit_statistics
from I3Tray import I3Tray, I3Units, load
#from filters_InIceSplit import in_ice, min_bias, SMT8, MPEFit, InIceSMTTriggered
from domanalysis import dom_data

load('libmue')
load('libipdf')
load('libgulliver')
load('libgulliver-modules')
load('liblilliput')
load('libstatic-twc')
#load('libjeb-filter-2012')
load('libfilterscripts')

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
    options['pulses_name'] = 'InIcePulses'
    options['max_dist'] = 140
#    options['partitions'] = 5

    tray = I3Tray()

    # Read the files.
    tray.AddModule('I3Reader', 'I3Reader',
                   Filenamelist=[args.gcd, args.data])
    # Domanalysis
    # This uses the MPEFit to calculate TotalCharge, RecoDistance, etc.
     
    tray.AddModule(dom_data, 'dom_data',
                    reco_fit='TruthMuon',
                    options=options)
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
