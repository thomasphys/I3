#!/usr/bin/env python

"""
Process the I3 files.
"""

from __future__ import print_function, division  # 2to3

import argparse
import time

from icecube import dataio, icetray, gulliver, simclasses, dataclasses, photonics_service, phys_services, spline_reco #, MuonGun
from icecube.common_variables import direct_hits, hit_multiplicity, hit_statistics
from I3Tray import I3Tray, I3Units, load
from filters_InIceSplit_2015 import in_ice, min_bias, SMT8, MPEFit, InIceSMTTriggered, FiniteRecoFilter, muon_zenith, SplineMPE
from general import get_truth_muon, get_truth_endpoint, count_hits, reco_endpoint, move_cut_variables, timestartMPE, totaltimeMPE, timestartSpline, totaltimeSpline, totaltimeall, timestartall, totaltimefilter,timestartfilter, movellhparams
from geoanalysis import calc_dist_to_border
from domanalysis import dom_data
from icecube.filterscripts.offlineL2.level2_HitCleaning_WIMP import WimpHitCleaning

# Reconstructions

from icecube.filterscripts.offlineL2.level2_Reconstruction_WIMP import FiniteReco
from icecube.filterscripts.offlineL2.level2_Reconstruction_Muon import SPE, MPE
from icecube.filterscripts.offlineL2.PhotonTables import InstallTables
from icecube import cramer_rao

load('libipdf')
load('libgulliver')
load('libgulliver-modules')
load('liblilliput')
load('libstatic-twc')
#load('libjeb-filter-2012')
load('libfilterscripts')
load('libmue')

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
    
    # Don't touch, unless you know what you're doing
    options = {}
#    options['pulses_name'] = 'SplitInIcePulses'
    options['pulses_name'] = 'SRTInIcePulsesDOMeff'
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

    # ---- Linefit and SPEfit ---------------------------------------------------
    tray.AddModule(timestartall,'TimeStartall')
    tray.AddSegment(SPE,'SPE',
                    If = lambda f: True,
                    Pulses=options['pulses_name'],
                    suffix='DOMeff',
                    LineFit= 'LineFit',
                    SPEFitSingle = 'SPEFitSingle',
                    SPEFit = 'SPEFit2',
                    SPEFitCramerRao = 'SPEFit2CramerRao',
                    N_iter = 2)
    # ---- MPEFit reconstruction ------------------------------------------------
    tray.AddModule(timestartMPE,'TimeStartMPE')
    tray.AddSegment(MPE, 'MPE',
                    Pulses = options['pulses_name'],
                    Seed = 'SPEFit2',
                    #If = which_split(split_name='InIceSplit') & (lambda f:muon_wg(f)),
                    If = lambda f: True,
                    suffix='DOMeff',
                    MPEFit = 'MPEFit',
                    MPEFitCramerRao = 'MPEFitCramerRao')

    tray.AddModule(MPEFit, 'MPEFit')    
    tray.AddModule(totaltimeMPE,'TotalTimeMPE')


    # ---- MuEx Reconstruction -------------------------------------------------                                                                                                                            

    tray.AddModule("muex", "muex")(
        ("pulses", options['pulses_name']),
        ("rectrk", ""), # have muex do its own directional reconstruction                                                                                                                                  
        ("result", "MuEx"),
        ("lcspan", 0),
        ("repeat", 16), # iterate reconstruction 16 times with bootstrapping                                                                                                                               
        ("rectyp", True), # use a muon track hypothesis                                                                                                                                                    
        ("usempe", True), # use the MPE likelihood (leading edge time + total charge)                                                                                                                      
        ("detail", True), # unfold energy losses                                                                                                                                                           
        ("energy", True) # compute an energy estimate                                                                                                                                                      
        )


    # -----Spline Reco -------------------------------------------------------
    
    tray.AddModule(timestartSpline,'TimeStartSpline')
    #spline paths Madison
    timingSplinePath = '/cvmfs/icecube.opensciencegrid.org/data/photon-tables/splines/InfBareMu_mie_prob_z20a10_V2.fits'
    amplitudeSplinePath = '/cvmfs/icecube.opensciencegrid.org/data/photon-tables/splines/InfBareMu_mie_abs_z20a10_V2.fits'
    stochTimingSplinePath = '/cvmfs/icecube.opensciencegrid.org/data/photon-tables/splines/InfHighEStoch_mie_prob_z20a10.fits'
    stochAmplitudeSplinePath = '/cvmfs/icecube.opensciencegrid.org/data/photon-tables/splines/InfHighEStoch_mie_abs_z20a10.fits'
    #pulses = "SRTOfflinePulses"
    EnEstis = ["SplineMPETruncatedEnergy_SPICEMie_AllDOMS_Muon","SplineMPETruncatedEnergy_SPICEMie_DOMS_Muon",
                "SplineMPETruncatedEnergy_SPICEMie_AllBINS_Muon","SplineMPETruncatedEnergy_SPICEMie_BINS_Muon",
                "SplineMPETruncatedEnergy_SPICEMie_ORIG_Muon"]

    # splineMPE with default configuration!
    tray.AddSegment(spline_reco.SplineMPE, "SplineMPE",configuration="recommended", PulsesName= options['pulses_name'], TrackSeedList=["MuEx"], BareMuTimingSpline=timingSplinePath, BareMuAmplitudeSpline=amplitudeSplinePath,EnergyEstimators=EnEstis)
    
    tray.AddModule(totaltimeSpline,'TotalTimeSpline')

    tray.AddModule(muon_zenith, 'MuonZenithFilter',
                   reco_fit='SplineMPE')
    
    
    # -----Finite Reco------------------------------------------------------------


    tray.AddSegment(InstallTables, 'InstallPhotonTables')

    tray.AddSegment(FiniteReco,'FiniteReco',
                    suffix = 'DOMeff',
                    Pulses = options['pulses_name'])

    tray.AddModule(FiniteRecoFilter, 'FiniteRecoFilter')


    # Endpoint

    # Add the reconstructed event endpoint to the frame.
    tray.AddModule(reco_endpoint, 'reco_endpoint',
                   endpoint_fit='FiniteRecoFitDOMeff')
    #Move LLH paramets for Finite Reco Cuts
    tray.AddModule(movellhparams,'movellhparams',
               llhparams = 'FiniteRecoLlhDOMeff')

    # Domanalysis
    # This uses the MPEFit's to calculate TotalCharge, RecoDistance, etc.
         
    tray.AddModule(dom_data, 'dom_data',
#                    reco_fit='MPEFitDOMeff',
                    reco_fit='SplineMPE',
                    options=options)
 
    # General
 
    # Calculate cut variables
    tray.AddSegment(direct_hits.I3DirectHitsCalculatorSegment, 'I3DirectHits',
                     PulseSeriesMapName=options['pulses_name'],
                     ParticleName='SplineMPE',
#                     ParticleName='SplineMPE',
#                     OutputI3DirectHitsValuesBaseName='MPEFitDOMeffDirectHits')
                     OutputI3DirectHitsValuesBaseName='SplineMPEDirectHits')

    tray.AddSegment(hit_multiplicity.I3HitMultiplicityCalculatorSegment, 'I3HitMultiplicity',
                     PulseSeriesMapName=options['pulses_name'],
                     OutputI3HitMultiplicityValuesName='HitMultiplicityValues')
 
    tray.AddSegment(hit_statistics.I3HitStatisticsCalculatorSegment, 'I3HitStatistics',
                     PulseSeriesMapName=options['pulses_name'],
                     OutputI3HitStatisticsValuesName='HitStatisticsValues')
 
    # Move the cut variables into the top level of the frame.
    tray.AddModule(move_cut_variables, 'move_cut_variables',
                    direct_hits_name='SplineMPEDirectHits',
                    fit_params_name='SplineMPEFitParams')
#                     direct_hits_name='SplineMPEDirectHits',
#                     fit_params_name='SplineMPEFitParams')

    # Calculate ICAnalysisHits, DCAnalysisHits, ICNHits, and DCNHits
    tray.AddModule(count_hits, 'count_hits',
                    pulses_name=options['pulses_name'])
 

    # Geoanalysis 
    # Calculate the distance of each event to the detector border.
    tray.AddModule(calc_dist_to_border, 'calc_dist_to_border')
    tray.AddModule(totaltimeall,'TotalTimeall')
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
