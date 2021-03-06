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

def BasicHitFilter(frame):
  hits = 0
  if frame.Has("I3Photons"):
    hits = len(frame.Get("I3Photons"))
  if hits>0:
    return True
  else:
    return False

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

#This is typically the first break in the simulation stream. Up to know the
#detector geometry is needed beyond the cylinder that you are shooting the
#neutrinos at.

#Now propagate photons

tray.AddModule("I3GeometryDecomposer","I3ModuleGeoMap")

tray.AddSegment(clsim.I3CLSimMakePhotons, 'goCLSIM',
                UseCPUs=False,
                UseGPUs=True,
                MCTreeName="I3MCTree",
                OutputMCTreeName="I3MCTree_clsim",
                FlasherInfoVectName=None,
                #MMCTrackListName="MMCTrackList",
                PhotonSeriesName = "I3Photons",
                #ParallelEvents=1000,
                RandomService=randomService,
                #IceModelLocation=icemodel_path,
                #UseGeant4=True,
                #CrossoverEnergyEM=0.1,
                #CrossoverEnergyHadron=float(options.CROSSENERGY),
                StopDetectedPhotons=True,
                #HoleIceParameterization=expandvars("$I3_SRC/ice-models/resources/models/angsens/as.flasher_p1_0.30_p2_-1"),
                DoNotParallelize=False,
                DOMOversizeFactor=1., 
                UnshadowedFraction=1.0,
                #GCDFile=gcd_file,
                GCDFile=gcd,
                )

tray.AddModule(BasicHitFilter, 'FilterNullPhotons', Streams =
              [icetray.I3Frame.DAQ, icetray.I3Frame.Physics]
              )

#This is the next typical breakpoint.

tray.AddSegment(clsim.I3CLSimMakeHitsFromPhotons, "makeHitsFromPhotons",
    PhotonSeriesName="I3Photons",
    MCPESeriesName="MCPESeriesMap_2",
    RandomService=randomService,
    DOMOversizeFactor=1.,
    UnshadowedFraction=1.,
    IceModelLocation = expandvars("$I3_SRC/ice-models/resources/models/spice_mie"),
    GCDFile=gcd,
    #HoleIceParameterization=expandvars("$I3_SRC/ice-models/resources/models/spice_mie"),
    #HoleIceParameterization=expandvars("$I3_SRC/ice-models/resources/models/angsens_unified/%s"%options.HOLEICE),
    )

tray.AddModule("PMTResponseSimulator","rosencrantz",
               Input="MCPESeriesMap_2",  
               Output="MCPESeriesMap_3",
               MergeHits=True,
              )

tray.AddModule("DOMLauncher", "guildenstern",
               Input= "MCPESeriesMap_3",
               Output="MCPESeriesMap_4",
#               UseTabulatedPT=True, #might be taking too much memory? causing
#               segmentation violation.
              )

tray.AddModule("I3DOMLaunchCleaning","launchcleaning")(
              ("InIceInput","MCPESeriesMap_4"),
              ("InIceOutput","MCPESeriesMap_5"),
              #("FirstLaunchCleaning",False),
              #("CleanedKeys",BadDoms),
              )

tray.AddSegment(trigger_sim.TriggerSim, "trig",                                 
                gcd_file = my_gcd_file,                                                        
                #time_shift_args = {"SkipKeys" : ["BundleGen"]},                             
                run_id=1,
                )

#converts q frames?
#tray.Add("I3NullSplitter",
#       SubEventStreamName = "fullevent")

#creates HDF5 file
#tray.AddSegment(I3HDFWriter,
#                output="foo.hdf5",
#                keys=['LineFit','InIceRawData'],
#                SubEventStreams=['in_ice'],
#               )

tray.Add("I3Writer", "writer", 
        Filename = 'test.i3.gz',
 #       DropBuffers=True,
  #      streams = [icetray.I3Frame.DAQ,icetray.I3FramePhysics,icetray.I3Frame.TrayInfo,icetray.I3Frame.Simulation],
        )

tray.AddModule("TrashCan","adios")

tray.Execute()
tray.Finish()
