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
from geoanalysis import calc_dist_to_border, calc_dist_to_border_mctruth
from domanalysis import dom_data
from writeEvent import EventWriter
import argparse
# Reconstructions
from icecube.filterscripts.offlineL2 import Globals
from icecube.filterscripts.offlineL2.level2_Reconstruction_WIMP import FiniteReco
from icecube.filterscripts.offlineL2.level2_Reconstruction_Muon import SPE, MPE
from icecube.filterscripts.offlineL2.PhotonTables import InstallTables
from icecube import cramer_rao
import ROOT

load('libipdf')
load('libgulliver')
load('libgulliver-modules')
load('liblilliput')
load('libstatic-twc')
#load('libjeb-filter-2012')
load('libfilterscripts')

def printtag(frame,message) :
	print(message)
	return True

eventcount1 = 0.0
def countevents1(frame) :
	global eventcount1
	eventcount1 += 1.0

eventcount2 = 0.0
def countevents2(frame) :
	global eventcount2
        eventcount2 += 1.0

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
parser.add_argument('-m', '--maxdist', help='maximum distance to DOM to consider', type = float, default = 200.0)

args = parser.parse_args()

datafilename = "{0:0{1}d}".format(args.runnum,5)

outputrootfile = ROOT.TFile(args.output+datafilename+".root","RECREATE")
originalLine = ROOT.TH1F("originalLine","",100,0.0,1.0)
originalSPE = ROOT.TH1F("originalSPE","",100,0.0,1.0)
originalLine_all = ROOT.TH1F("originalLine","",100,0.0,1.0)
originalSPE_all = ROOT.TH1F("originalSPE","",100,0.0,1.0)

def FillRootPlots(frame):
  global originalLine
  global originalSPE

  originalLine.Fill(ROOT.TMath.Cos(frame['LineFit'].dir.zenith))
  originalSPE.Fill(ROOT.TMath.Cos(frame['SPEFit2'].dir.zenith))

def FillRootPlots_all(frame):
  global originalLine_all
  global originalSPE_all

  originalLine_all.Fill(ROOT.TMath.Cos(frame['LineFit'].dir.zenith))
  originalSPE_all.Fill(ROOT.TMath.Cos(frame['SPEFit2'].dir.zenith))


dom_data_options = {}
#    options['pulses_name'] = 'SplitInIcePulses' 
dom_data_options['pulses_name'] = args.pulsename
dom_data_options['max_dist'] = args.maxdist

tray = I3Tray()

# Read the files.
tray.AddModule('I3Reader', 'I3Reader',
               Filenamelist=[args.gcd, args.datadir+datafilename+args.datafiletype])

#tray.AddModule(printtag, 'printtag_newevent',message = "new event")
# Filter the ones with sub_event_stream == InIceSplit
tray.AddModule(in_ice, 'in_ice')

tray.AddModule(FillRootPlots_all,'alleventsgraphs')
#tray.AddModule(printtag, 'printtag_in_ice',message = "passed in_ice")
# Make sure that the length of SplitInIcePulses is >= 8

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
tray.AddModule(SMT8, 'SMT8')
tray.AddModule(min_bias, 'min_bias')

tray.AddModule(FillRootPlots,'eventsgraphs')

    
tray.AddModule('TrashCan', 'yeswecan')
if args.nevents > 0 :
  tray.Execute(opts['nevents'])
else :
  tray.Execute()
tray.Finish()
print("events %f / %f passed" % (eventcount1,eventcount2)) 
originalLine.Write()
originalSPE.Write()
originalLine_all.Write()
originalSPE_all.Write()
outputrootfile.Close()
