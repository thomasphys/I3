#!/usr/bin/env python

"""
Process the I3 files.
"""

from __future__ import print_function, division  # 2to3

import argparse


from icecube import dataio, icetray, gulliver, simclasses, dataclasses, photonics_service, phys_services
from icecube.common_variables import direct_hits, hit_multiplicity, hit_statistics
from I3Tray import I3Tray, I3Units, load
from filters_InIceSplit_2015 import in_ice, min_bias, SMT8, MPEFit, InIceSMTTriggered,SplineMPE
from general import get_truth_muon, get_truth_endpoint, count_hits, reco_endpoint, move_cut_variables,totaltimefilter,timestartfilter
from geoanalysis import calc_dist_to_border
from domanalysis import dom_data

from icecube.filterscripts.offlineL2.level2_HitCleaning_WIMP import WimpHitCleaning

#load('libipdf')
#load('libgulliver')
#load('libgulliver-modules')
#load('liblilliput')
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
    options['pulses_name'] = 'SplitInIcePulses' # Subset of InIcePulses within the SMT8/3 trigger time window in the p-frame 
    options['max_dist'] = 140
#    options['partitions'] = 5

    tray = I3Tray()
    # Read the files.
    tray.AddModule('I3Reader', 'I3Reader',
                   Filenamelist=[args.gcd, args.data])
    tray.AddModule(timestartfilter,'TimeStartFilter')
    # Filters

    # Filter the ones with sub_event_stream == InIceSplit
    tray.AddModule(in_ice, 'in_ice')

    # Check in FilterMinBias_13 that condition_passed and prescale_passed are both true
    tray.AddModule(min_bias, 'min_bias')

    # Make sure that the length of SplitInIcePulses is >= 8
    tray.AddModule(SMT8, 'SMT8')

    # Check that the fit_status of MPEFit is OK, and that 40 < zenith < 70
    # tray.AddModule(MPEFit, 'MPEFit')

    # Trigger check
    # jeb-filter-2012
    tray.AddModule('TriggerCheck_13', 'TriggerCheck_13',
                   I3TriggerHierarchy='I3TriggerHierarchy',
                   InIceSMTFlag='InIceSMTTriggered',
                   IceTopSMTFlag='IceTopSMTTriggered',
                   InIceStringFlag='InIceStringTriggered',
                   PhysMinBiasFlag='PhysMinBiasTriggered',
                   PhysMinBiasConfigID=106,
                   DeepCoreSMTFlag='DeepCoreSMTTriggered',
                   DeepCoreSMTConfigID=1010)

    # Check that InIceSMTTriggered is true.
    tray.AddModule(InIceSMTTriggered, 'InIceSMTTriggered')

    # Generate the SRTInIcePulses, which are used for running basic reconstruction algorithms on data

    from icecube.STTools.seededRT.configuration_services import I3DOMLinkSeededRTConfigurationService
    seededRTConfig = I3DOMLinkSeededRTConfigurationService(
                    ic_ic_RTRadius              = 150.0*I3Units.m,
                    ic_ic_RTTime                = 1000.0*I3Units.ns,
                    treat_string_36_as_deepcore = False,
                    useDustlayerCorrection      = False,
                    allowSelfCoincidence        = True
    
                    )

    # Notice that we named the pulse series SRTInIcePulsesDOMeff to avoid
    # repeating frame objects in the frames that originally had reconstuctions

    tray.AddModule('I3SeededRTCleaning_RecoPulseMask_Module', 'North_seededrt',
                    InputHitSeriesMapName  = 'SplitInIcePulses',
                    OutputHitSeriesMapName = 'SRTInIcePulsesDOMeff',
                    STConfigService        = seededRTConfig,
                    SeedProcedure          = 'HLCCoreHits',
                    NHitsThreshold         = 2,
                    MaxNIterations         = 3,
                    Streams                = [icetray.I3Frame.Physics],
                    If = lambda f: True
    )


    # Generate RTTWOfflinePulses_FR_WIMP, used to generate the finite reco reconstruction in data

    tray.AddSegment(WimpHitCleaning, "WIMPstuff",
                    seededRTConfig = seededRTConfig,
                    If= lambda f: True,
                    suffix='_WIMP_DOMeff'
    )

    if args.sim:
        # Count the number of in ice muons and get the truth muon
        tray.AddModule(get_truth_muon, 'get_truth_muon')
        tray.AddModule(get_truth_endpoint, 'get_truth_endpoint')

    # Geoanalysis

    # Calculate the distance of each event to the detector border.
    #tray.AddModule(calc_dist_to_border, 'calc_dist_to_border')
    tray.AddModule(totaltimefilter,'TotalTimeFilter')
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
