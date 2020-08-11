#!/bin/sh /cvmfs/icecube.opensciencegrid.org/py2-v3.1.1/icetray-start
#METAPROJECT combo/V00-00-04

from I3Tray import *
from icecube import icetray, dataclasses, phys_services, sim_services, dataio, earthmodel_service, neutrino_generator, tableio, hdfwriter, simclasses, phys_services, DOMLauncher, DomTools, clsim, trigger_sim
from icecube.simprod import segments
from icecube.icetray import I3Units, I3Frame
from icecube.dataclasses import I3Particle
from icecube.simclasses import I3MMCTrack
from icecube.hdfwriter import I3SimHDFWriter, I3HDFWriter
import numpy as np
import argparse
from icecube import PROPOSAL                                                    
from os.path import expandvars 

parser = argparse.ArgumentParser(description = "A scripts to run the neutrino generation simulation step using Neutrino Generator")

parser.add_argument('-emin', '--energyMin', default = 5.0, help = "the minimum energy")
parser.add_argument('-emax', '--energyMax', default = 8.0, help = "the maximum energy")
parser.add_argument('-n', '--numEvents', default = 10, help = "number of events produced by the simulation")
parser.add_argument('-o', '--outfile', default = "output2",help="name and path of output file")
parser.add_argument('-r', '--runNum', default = 5000, help="run Number")
parser.add_argument("-a", "--ratios",default="1.0:1.0", help="ratio of input neutrino")
parser.add_argument("-t", "--types",default="NuMu:NuMuBar", help="type of input neutrino")

args = parser.parse_args()

typeString = args.types
ratioString = args.ratios

typevec = typeString.split(":")
ratiostvec = ratioString.split(":")
ratiovec = []
for ratio in ratiostvec:
    ratiovec.append(float(ratio))

emin = float(args.energyMin)
emax = float(args.energyMax)
numEvents = int(args.numEvents)
runNum = int(args.runNum)
print(emin, emax, ratiovec, typevec, numEvents, runNum)

cylinder = [float(500), float(1000), float(0), float(0), float(0)]
zenithMin = 0 * I3Units.deg
zenithMax = 90 * I3Units.deg
azimuthMin = 0 * I3Units.deg
azimuthMax = 180 * I3Units.deg
gcd = expandvars("${I3_DATA}/GCD/GeoCalibDetectorStatus_AVG_55697-57531_PASS2_SPE_withScaledNoise.i3.gz")

my_gcd_file = dataio.I3File(gcd)  

tray = I3Tray()

#Random
#randomService  = phys_services.I3GSLRandomService(123456)
randomService = phys_services.I3SPRNGRandomService(
        seed = runNum,
		    nstreams = 50000, #total number of random numbers needed.
        streamnum = 1)

tray.context['I3RandomService'] = randomService
tray.Add("I3InfiniteSource", prefix = gcd)

tray.Add("I3MCEventHeaderGenerator",
	       EventID=0,
	       IncrementEventID=True)

tray.Add("I3EarthModelServiceFactory", "EarthModelService")
#tray.Add("I3EarthModelServiceFactory", "EarthModelService",
#                EarthModels = ["PREM_mmc"],
#                MaterialModels = ["Standard"],
#                IceCapType = "IceSheet",
#                DetectorDepth = 2600*I3Units.m,
#                PathToDataFileDir = "")

tray.Add("I3NuGSteeringFactory", "steering",
                EarthModelName = "EarthModelService",
                NEvents = numEvents,
                SimMode = "Detector",
                VTXGenMode = "NuGen",
                InjectionMode = "surface",
                CylinderParams = cylinder,
                DoMuonRangeExtension = False,
                UseSimpleScatterForm = True,
                MCTreeName = "I3MCTree_nugen"
                )

tray.Add("I3NuGDiffuseSource","diffusesource",
               RandomService = randomService,
               SteeringName = "steering",
               NuTypes = typevec,#['NuTau','NuTauBar'],
               PrimaryTypeRatio = ratiovec,
               GammaIndex = 2.19,
               EnergyMinLog = emin,
               EnergyMaxLog = emax,
               ZenithMin = zenithMin,
               ZenithMax = zenithMax,
               AzimuthMin = azimuthMin,
               AzimuthMax = azimuthMax,
               ZenithWeightParam = 1.0,
               AngleSamplingMode = "COS"
              )

tray.Add("I3NuGInteractionInfoDifferentialFactory", "interaction",
                RandomService = randomService,
                SteeringName = "steering",
                TablesDir = "/home/users/dhilu/P_ONE_dvirhilu/CrossSectionModels",
                CrossSectionModel = "csms_differential_v1.0"
              )

tray.Add("I3NeutrinoGenerator","generator",
                RandomService = randomService,
                SteeringName = "steering",
                InjectorName = "diffusesource",
                InteractionInfoName = "interaction",
                #PropagationWeightMode = "NCGRWEIGHTED",
                InteractionCCFactor = 1.0,
                InteractionNCFactor = 1.0,
                #InteractionGRFactor = 1.0
              )

tray.Add(segments.PropagateMuons, 'ParticlePropagators',
         RandomService=randomService,
         SaveState=True,
         InputMCTreeName="I3MCTree_nugen",
         OutputMCTreeName="I3MCTree")

tray.Add("I3Writer", "writer", 
        Filename = 'test.i3.gz',
 #       DropBuffers=True,
  #      streams = [icetray.I3Frame.DAQ,icetray.I3FramePhysics,icetray.I3Frame.TrayInfo,icetray.I3Frame.Simulation],
        )

tray.AddModule("TrashCan","adios")

tray.Execute()
tray.Finish()
