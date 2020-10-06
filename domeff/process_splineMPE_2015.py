#! /usr/bin/env python

"""
Process the I3 files.
"""

from __future__ import print_function, division  # 2to3

# Kludge to allow importing from parent directory for shared utility modules
import os
import sys
sys.path.append('/home/tmcelroy/icecube/domeff')
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

# Setup logging
from icecube.icetray.i3logging import *
from icecube import dataio, icetray, finiteReco, gulliver, simclasses, dataclasses, photonics_service, phys_services, spline_reco #, MuonGun
from icecube.common_variables import direct_hits, hit_multiplicity, hit_statistics
from icecube.filterscripts.offlineL2.level2_HitCleaning_WIMP import WimpHitCleaning
from I3Tray import I3Tray, I3Units, load
#from filters_InIceSplit import in_ice, min_bias, SMT8, MPEFit, InIceSMTTriggered
from filters_InIceSplit_2015 import in_ice, min_bias, SMT8, MPEFit, InIceSMTTriggered, FiniteRecoFilter, muon_zenith
from general import get_truth_muon, get_truth_endpoint, count_hits, reco_endpoint, move_cut_variables, totaltimefilter,timestartfilter, tot_charge, movellhparams
from geoanalysis import calc_dist_to_border
from domanalysis import dom_data
from writeEvent import EventWriter
import argparse
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


parser = argparse.ArgumentParser()
parser.add_argument('-d', '--datadir', help='Directory of data files.',type=str,
        default = '/data/user/sanchezh/IC86_2015/Final_Level2_IC86_MPEFit_')
parser.add_argument('-g', '--gcd', help='Geometry file.', type = str,
        default = "${I3_DATA}/GCD/GeoCalibDetectorStatus_AVG_55697-57531_PASS2_SPE.i3.gz")
parser.add_argument('-o', '--output', help='Name of output file.', type=str,
        default = "out.root")
parser.add_argument('-z', '--zenithrange', help='Range of muon Zeniths', type = float,
        nargs = '+',  default = [-180.0,180.0])
parser.add_argument('-q', '--energyrange', help='Range of muon Energies', type = float,
        nargs = "+", default = [0.0, 9999999.00])
parser.add_argument('-s', '--sim', help='Is file simulation', type = bool, default = False)
parser.add_argument('-n', '--nevents', help='Number of events to process.', type = int, default = -1)
parser.add_argument('-t', '--datafiletype', help='Suffix of Datafiles', type = str, default = 'i3.bz2')
parser.add_argument('-r', '--runnum', help='number to identify target file', type = int, default = 0)
parser.add_argument('-p', '--pulsename', help='Name of new pulse list', type = str, default = 'SRTInIcePulsesDOMEff')
parser.add_argument('-m', '--maxdist', help='maximum distance to DOM to consider', type = float, default = 140.0)
args = parser.parse_args()

dom_data_options = {}
#    options['pulses_name'] = 'SplitInIcePulses'
dom_data_options['pulses_name'] = args.pulsename
dom_data_options['max_dist'] = args.maxdist


tray = I3Tray()

datafilename = "{0:0{1}d}".format(args.runnum,5)

# Read the files.
tray.AddModule('I3Reader', 'I3Reader',
               Filenamelist=[args.gcd, args.datadir+datafilename+args.datafiletype])

# Filter the ones with sub_event_stream == InIceSplit
tray.AddModule(in_ice, 'in_ice')

if not args.sim :
	tray.AddModule(timestartfilter,'TimeStartFilter')
	# Filters

	#Thomas - remove minbias for now since only running one run. 
	# Check in FilterMinBias_13 that condition_passed and prescale_passed are both true
	#tray.AddModule(min_bias, 'min_bias')

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
              #PhysMinBiasFlag='PhysMinBiasTriggered',
              #PhysMinBiasConfigID=106,
               DeepCoreSMTFlag='DeepCoreSMTTriggered',
               DeepCoreSMTConfigID=1010)

  # Check that InIceSMTTriggered is true.
	tray.AddModule(InIceSMTTriggered, 'InIceSMTTriggered')


# Generate RTTWOfflinePulses_FR_WIMP, used to generate the finite reco reconstruction in data

# Geoanalysis
# Calculate the distance of each event to the detector border.
#tray.AddModule(calc_dist_to_border, 'calc_dist_to_border')
#Thomas - this is crashing, solve this.
#tray.AddModule(totaltimefilter,'TotalTimeFilter')


#---- Generate filtered pulse series with same configuration as used by Nick and Sebastian -----
# Generate the SRTInIcePulses, which are used for running basic reconstruction algorithms on data

from icecube.STTools.seededRT.configuration_services import I3DOMLinkSeededRTConfigurationService
seededRTConfig = I3DOMLinkSeededRTConfigurationService(
    ic_ic_RTRadius=150.0 * I3Units.m,
    ic_ic_RTTime=1000.0 * I3Units.ns,
    treat_string_36_as_deepcore=False,
    useDustlayerCorrection=False,
    allowSelfCoincidence=True
)

# Notice that we name the pulse series SRTInIcePulsesDOMeff to avoid
# repeating frame objects in the frames that originally had reconstuctions
tray.AddModule('I3SeededRTCleaning_RecoPulseMask_Module', 'North_seededrt',
               InputHitSeriesMapName='SplitInIcePulses',
               OutputHitSeriesMapName=args.pulsename,
               STConfigService=seededRTConfig,
               SeedProcedure='HLCCoreHits',
               NHitsThreshold=2,
               MaxNIterations=3,
               Streams=[icetray.I3Frame.Physics],
               If=lambda f: True
               )

# Generate RTTWOfflinePulses_FR_WIMP, used to generate the finite reco reconstruction in data
# Despite the unusual name this runs the FiniteReco cleaning on the pulse series.

tray.AddSegment(WimpHitCleaning, "WIMPstuff",
                    seededRTConfig = seededRTConfig,
                    If= lambda f: True,
                    suffix='_WIMP_DOMeff'
    )

# ---- Linefit and SPEfit ---------------------------------------------------
tray.AddSegment(SPE,'SPE',
                If = lambda f: True,
                Pulses=args.pulsename,
                suffix='DOMeff',
                LineFit= 'LineFit',
                SPEFitSingle = 'SPEFitSingle',
                SPEFit = 'SPEFit2',
                SPEFitCramerRao = 'SPEFit2CramerRao',
                N_iter = 2
                )

# ---- MPEFit reconstruction ------------------------------------------------
tray.AddSegment(MPE, 'MPE',
                Pulses = args.pulsename,
                Seed = 'SPEFit2',
                #If = which_split(split_name='InIceSplit') & (lambda f:muon_wg(f)),
                If = lambda f: True,
                suffix='DOMeff',
                MPEFit = 'MPEFit',
                MPEFitCramerRao = 'MPEFitCramerRao'
                )
tray.AddModule(MPEFit, 'MPEFit')

# -----Spline Reco -------------------------------------------------------
#spline paths Madison
timingSplinePath = '/cvmfs/icecube.opensciencegrid.org/data/photon-tables/splines/InfBareMu_mie_prob_z20a10_V2.fits'
amplitudeSplinePath = '/cvmfs/icecube.opensciencegrid.org/data/photon-tables/splines/InfBareMu_mie_abs_z20a10_V2.fits'
stochTimingSplinePath = '/cvmfs/icecube.opensciencegrid.org/data/photon-tables/splines/InfHighEStoch_mie_prob_z20a10.fits'
stochAmplitudeSplinePath = '/cvmfs/icecube.opensciencegrid.org/data/photon-tables/splines/InfHighEStoch_mie_abs_z20a10.fits'
#pulses = "SRTOfflinePulses"
EnEstis = ["SplineMPETruncatedEnergy_SPICEMie_AllDOMS_Muon",
           "SplineMPETruncatedEnergy_SPICEMie_DOMS_Muon",
           "SplineMPETruncatedEnergy_SPICEMie_AllBINS_Muon",
           "SplineMPETruncatedEnergy_SPICEMie_BINS_Muon",
            "SplineMPETruncatedEnergy_SPICEMie_ORIG_Muon"
           ]

# splineMPE with default configuration!
tray.AddSegment(spline_reco.SplineMPE, "SplineMPE",
                configuration="default",
                PulsesName= args.pulsename,
                TrackSeedList=["MPEFitDOMeff"],
                BareMuTimingSpline=timingSplinePath,
                BareMuAmplitudeSpline=amplitudeSplinePath,
                fitname="SplineMPE",
                )

#Thomas, will apply this later, want to study impact.
#tray.AddModule(muon_zenith, 'MuonZenithFilter',
#               reco_fit='SplineMPE')
    

# -----Finite Reco------------------------------------------------------------
tray.AddSegment(InstallTables, 'InstallPhotonTables')
tray.AddSegment(FiniteReco,'FiniteReco',
                suffix = 'DOMeff',
                Pulses = 'RTTWOfflinePulses_FR_WIMP_DOMeff')
##                Pulses = 'SRTInIcePulses')
tray.AddModule(FiniteRecoFilter, 'FiniteRecoFilter')

tray.AddService("I3GulliverFinitePhPnhFactory","finitephpnh",
   InputReadout        = 'RTTWOfflinePulses_FR_WIMP_DOMeff')

tray.AddModule("I3StartStopLProb","FiniteRecoStartStopLLH",
   Name        = "StartStopProb",
   ServiceName = "finitephpnh"
)

tray.AddModule(movellhparams, "MoveLLHParams",
		llhparams = 'StartStopProb_StartStopParams',
	      )


# -----Endpoint---------------------------------------------------------------
# Add the reconstructed event endpoint to the frame.
tray.AddModule(reco_endpoint, 'reco_endpoint',
               endpoint_fit='FiniteRecoFitDOMeff'
               )

tray.AddModule(tot_charge,'tot_charge',
                reco_fit='SplineMPE',
                pulses = args.pulsename,
              )

# DOManalysis
# This uses the MPEFit's to calculate TotalCharge, RecoDistance, etc.
tray.AddModule(dom_data, 'dom_data',
#               reco_fit='MPEFitDOMeff',
               reco_fit='SplineMPE',
               options=dom_data_options
               )
 
# General

# Calculate cut variables
tray.AddSegment(direct_hits.I3DirectHitsCalculatorSegment, 'I3DirectHits',
                PulseSeriesMapName=args.pulsename,
#                ParticleName='MPEFitDOMeff',
                ParticleName='SplineMPE',
#                OutputI3DirectHitsValuesBaseName='MPEFitDOMeffDirectHits')
                OutputI3DirectHitsValuesBaseName='SplineMPEDirectHits'
                )
tray.AddSegment(hit_multiplicity.I3HitMultiplicityCalculatorSegment, 'I3HitMultiplicity',
                PulseSeriesMapName=args.pulsename,
                OutputI3HitMultiplicityValuesName='HitMultiplicityValues'
                )
 
tray.AddSegment(hit_statistics.I3HitStatisticsCalculatorSegment, 'I3HitStatistics',
                PulseSeriesMapName=args.pulsename,
                OutputI3HitStatisticsValuesName='HitStatisticsValues'
                )
 
# Move the cut variables into the top level of the frame.
tray.AddModule(move_cut_variables, 'move_cut_variables',
#               direct_hits_name='MPEFitDOMeffDirectHits',
#               fit_params_name='MPEFitDOMeffFitParams')
               direct_hits_name='SplineMPEDirectHits',
               fit_params_name='SplineMPEFitParams'
               )

# Calculate ICAnalysisHits, DCAnalysisHits, ICNHits, and DCNHits
tray.AddModule(count_hits, 'count_hits',
               pulses_name=args.pulsename)
 


# Geoanalysis
# Calculate the distance of each event to the detector border.
tray.AddModule(calc_dist_to_border, 'calc_dist_to_border')

if args.sim :
        # Count the number of in ice muons and get the truth muon
        tray.AddModule(get_truth_muon, 'get_truth_muon')
        tray.AddModule(get_truth_endpoint, 'get_truth_endpoint')


# Write the data out to an HDF5 analysis file

tray.AddModule(EventWriter, 'EventWriter',
               FileName=args.output+datafilename+'.h5')

# Write out the data to an I3 file
#tray.AddModule('I3Writer', 'I3Writer',
#               FileName=opts["out"]+'.i3.gz',
#               SkipKeys=['InIceRecoPulseSeriesPattern.*'],
#               DropOrphanStreams=[icetray.I3Frame.DAQ],
#               Streams=[icetray.I3Frame.TrayInfo,icetray.I3Frame.DAQ,icetray.I3Frame.Physics]
#               )
    
tray.AddModule('TrashCan', 'yeswecan')
if args.nevents > 0 :
  tray.Execute(opts['nevents'])
else :
  tray.Execute()
tray.Finish()
