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
from icecube import icetray, dataclasses, dataio, simclasses
from icecube.hdfwriter import I3HDFTableService
from icecube.rootwriter import I3ROOTTableService
from icecube.tableio import I3TableWriter

from functions import make_event_cuts, make_dom_cuts, write_cut_metadata, bdt_vars
from cut_options import event_cuts, dom_cuts, dom_keys

def pe_length(frame):
    total_DC = 0
    total_IC = 0
    doms_IC = 0
    doms_DC = 0
    DC_strings = [80,81,82,83,84,85,86]
#    frame['PeLength_IC'] = dataclasses.I3VectorDouble()
#    frame['PeLength_DC'] = dataclasses.I3VectorDouble()
    dc=[]
    ic=[]
    for i, j  in frame['I3MCPESeriesMap_0.990'].iteritems():
#        total_DC = 0
#        total_IC = 0
        if i.string in DC_strings:
            doms_DC+=1
        if (i.string <= 79) & (i.om < 61):
            doms_IC+=1
        for p in j:
            if i.string in DC_strings:
                total_DC+=1
            if (i.string <= 79) and (i.om < 61):
                total_IC+=1
#        frame['PeLength_IC'].append(total_IC)
#        frame['PeLength_DC'].append(total_DC)

    if doms_IC > 0 and doms_DC > 0 and total_DC > 10 and total_IC > 10:
        frame['PeLength_IC'] = dataclasses.I3Double(total_IC/float(doms_IC))
        frame['PeLength_DC'] = dataclasses.I3Double(total_DC/float(doms_DC))


def mcpe_check(frame):
    mcpulse = frame['I3MCPulseSeriesMap']
    tot_doms_dc = 0
    tot_doms_ic = 0
    tot_charge_dc = 0
    tot_charge_ic = 0
    for i, j in mcpulse:
        if i.om >= 11 and i.string >= 80:
            tot_doms_dc+=1
            for p in j:
                tot_charge_dc+=p.charge
        if i.om >=42 and i.om <= 60 and i.string <= 79:
            tot_doms_ic+=1
            for p in j:
                tot_charge_ic+=p.charge
    if tot_doms_dc > 0:
        frame['MCPE_ChargePerDom_DC'] = dataclasses.I3Double(tot_charge_dc/float(tot_doms_dc))
    if tot_doms_ic > 0:    
        frame['MCPE_ChargePerDom_IC'] = dataclasses.I3Double(tot_charge_ic/float(tot_doms_ic))

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
    tray.AddModule(mcpe_check, 'mcpe_check')
    tray.AddModule(pe_length,'pe_length')
    # Get the appropriate output file service
    if args.root:
        ofile_service = I3ROOTTableService(args.ofile)
    else:
        ofile_service = I3HDFTableService(args.ofile)

    tray.AddModule(I3TableWriter, 'I3TableWriter',
                   keys = ['MCPE_ChargePerDom_DC','MCPE_ChargePerDom_IC','PeLength_IC','PeLength_DC','RecoDistance'],
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
