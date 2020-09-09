#!/usr/bin/env python

"""
Process the I3 files.
"""

from __future__ import print_function, division  # 2to3

# Kludge to allow importing from parent directory for shared utility modules
import os
import sys
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

# Setup logging
from icecube.icetray.i3logging import *

opts = {}

# I/O options
opts["gcd"] = sys.argv[1]
opts["data"] = sys.argv[2]
opts["nevents"] = int(sys.argv[3])
opts["out"] = sys.argv[4]
opts["sim"]=bool(sys.argv[5])

from icecube import dataio, icetray, gulliver, simclasses, dataclasses, photonics_service, phys_services, spline_reco #, MuonGun
from icecube.common_variables import direct_hits, hit_multiplicity, hit_statistics
from I3Tray import I3Tray, I3Units, load
#from filters_InIceSplit import in_ice, min_bias, SMT8, MPEFit, InIceSMTTriggered
from filters_InIceSplit_2015 import in_ice, min_bias, SMT8, MPEFit, InIceSMTTriggered, FiniteRecoFilter, muon_zenith
from general import get_truth_muon, get_truth_endpoint, count_hits, reco_endpoint, move_cut_variables
from geoanalysis import calc_dist_to_border
from domanalysis import dom_data
from writeEvent import EventWriter

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

# Don't touch, unless you know what you're doing
options = {}
#options['pulses_name'] = 'SplitInIcePulses'
#options['pulses_name'] = 'SRTInIcePulsesDOMeff'
options['pulses_name'] = 'SRTInIcePulsesDOMEff'
options['max_dist'] = 140
#options['partitions'] = 5

tray = I3Tray()

# Read the files.
tray.AddModule('I3Reader', 'I3Reader',
               Filenamelist=[opts["gcd"], opts["data"]])

# *********TEMPORARY FIX *********
# Only allow the InIneSplit stream to pass
def inIceSplitOnly(frame):
    return frame["I3EventHeader"].sub_event_stream == "InIceSplit"
tray.AddModule(inIceSplitOnly, 'InIceSplitOnly', Streams = [icetray.I3Frame.Physics])


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
               OutputHitSeriesMapName='SRTInIcePulsesDOMEff',
               STConfigService=seededRTConfig,
               SeedProcedure='HLCCoreHits',
               NHitsThreshold=2,
               MaxNIterations=3,
               Streams=[icetray.I3Frame.Physics],
               If=lambda f: True
               )

# Generate RTTWOfflinePulses_FR_WIMP, used to generate the finite reco reconstruction in data
# Despite the unusual name this runs the FiniteReco cleaning on the pulse series.
from icecube.filterscripts.offlineL2.level2_HitCleaning_WIMP import WimpHitCleaning
tray.AddSegment(WimpHitCleaning, "WIMPstuff",
                seededRTConfig=seededRTConfig,
                If=lambda f: True,
                suffix='_WIMP_DOMeff'
                )

# ---- Linefit and SPEfit ---------------------------------------------------
tray.AddSegment(SPE,'SPE',
                If = lambda f: True,
                Pulses=options['pulses_name'],
                suffix='DOMeff',
                LineFit= 'LineFit',
                SPEFitSingle = 'SPEFitSingle',
                SPEFit = 'SPEFit2',
                SPEFitCramerRao = 'SPEFit2CramerRao',
                N_iter = 2
                )

# ---- MPEFit reconstruction ------------------------------------------------
tray.AddSegment(MPE, 'MPE',
                Pulses = options['pulses_name'],
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
                PulsesName= options['pulses_name'],
                TrackSeedList=["MPEFitDOMeff"],
                BareMuTimingSpline=timingSplinePath,
                BareMuAmplitudeSpline=amplitudeSplinePath,
                fitname="SplineMPE",
                )

tray.AddModule(muon_zenith, 'MuonZenithFilter',
               reco_fit='SplineMPE')
    

# -----Finite Reco------------------------------------------------------------
tray.AddSegment(InstallTables, 'InstallPhotonTables')
tray.AddSegment(FiniteReco,'FiniteReco',
                suffix = 'DOMeff',
                Pulses = 'RTTWOfflinePulses_FR_WIMP_DOMeff')
##                Pulses = 'SRTInIcePulses')
tray.AddModule(FiniteRecoFilter, 'FiniteRecoFilter')


# -----Endpoint---------------------------------------------------------------
# Add the reconstructed event endpoint to the frame.
tray.AddModule(reco_endpoint, 'reco_endpoint',
               endpoint_fit='FiniteRecoFitDOMeff'
               )

# DOManalysis
# This uses the MPEFit's to calculate TotalCharge, RecoDistance, etc.
tray.AddModule(dom_data, 'dom_data',
#               reco_fit='MPEFitDOMeff',
               reco_fit='SplineMPE',
               options=options
               )
 
# General

# Calculate cut variables
tray.AddSegment(direct_hits.I3DirectHitsCalculatorSegment, 'I3DirectHits',
                PulseSeriesMapName=options['pulses_name'],
#                ParticleName='MPEFitDOMeff',
                ParticleName='SplineMPE',
#                OutputI3DirectHitsValuesBaseName='MPEFitDOMeffDirectHits')
                OutputI3DirectHitsValuesBaseName='SplineMPEDirectHits'
                )
tray.AddSegment(hit_multiplicity.I3HitMultiplicityCalculatorSegment, 'I3HitMultiplicity',
                PulseSeriesMapName=options['pulses_name'],
                OutputI3HitMultiplicityValuesName='HitMultiplicityValues'
                )
 
tray.AddSegment(hit_statistics.I3HitStatisticsCalculatorSegment, 'I3HitStatistics',
                PulseSeriesMapName=options['pulses_name'],
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
               pulses_name=options['pulses_name'])
 
#    if args.sim:
    # Get the truth muon energy
#        tray.AddModule(muonTruthEnergy, 'get_truth_energy')
#         tray.AddModule(get_truth_endpoint, 'get_truth_endpoint')
 
#    tray.AddModule(muonRecoEnergy, 'get_reco_energy',
#                     suffix = 'DOMeff')

# Geoanalysis
# Calculate the distance of each event to the detector border.
tray.AddModule(calc_dist_to_border, 'calc_dist_to_border')

# Write the data out to an HDF5 analysis file
tray.AddModule(EventWriter, 'EventWriter',
               FileName=opts["out"]+'.h5')

# Write out the data to an I3 file
#tray.AddModule('I3Writer', 'I3Writer',
#               FileName=opts["out"]+'.i3.gz',
#               SkipKeys=['InIceRecoPulseSeriesPattern.*'],
#               DropOrphanStreams=[icetray.I3Frame.DAQ],
#               Streams=[icetray.I3Frame.TrayInfo,icetray.I3Frame.DAQ,icetray.I3Frame.Physics]
#               )
    
tray.AddModule('TrashCan', 'yeswecan')
if opt['nevents'] > 0 :
  tray.Execute(opt['nevents'])
else :
  tray.Execute()
tray.Finish()