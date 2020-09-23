#
# Module to output events in HDF5 format
#
from tables import open_file

from icecube import icetray

from event import *

class EventWriter(icetray.I3Module):
	def __init__(self, context):
		icetray.I3Module.__init__(self, context)
		self.AddParameter('FileName','Name of the file to write out','out.h5')
		self.eventId=0

	def Configure(self):
		self.h5file = open_file(self.GetParameter('FileName'), mode="w", title="DOM Calibration HDF5 File")
		# Create the table to store all the event objects
		self.events = self.h5file.create_table('/', 'events', Event, "Calibration Events")
		# Create the table to store all the DOM hits
		self.doms   = self.h5file.create_table('/', 'doms', DOM, "Hit DOMs")
		# Create the table to store run information.
		self.run = self.h5file.create_table('/','runinfo',Run, "Run Info")
		# Create an index on the event ID
		self.doms.cols.eventId.create_index()
		self.events.cols.eventId.create_index()

	def Physics(self, frame):
		# Create an event entry
		event=self.events.row
		# Get the current event ID number
		event['eventId']=self.eventId
		event['reco/time']   = frame['SplineMPE'].time
		event['reco/energy'] = frame['SplineMPE'].energy
		event['reco/speed']  = frame['SplineMPE'].speed
		event['reco/length'] = frame['SplineMPE'].length
		event['reco/pos/x'] = frame['SplineMPE'].pos.x
		event['reco/pos/y'] = frame['SplineMPE'].pos.y
		event['reco/pos/z'] = frame['SplineMPE'].pos.z
		event['reco/dir/zenith']  = frame['SplineMPE'].dir.zenith
		event['reco/dir/azimuth'] = frame['SplineMPE'].dir.azimuth
		event['startTime/tag'] = frame['I3EventHeader'].start_time
		event['endTime/tag'] = frame['I3EventHeader'].end_time

		if frame.Has('CorsikaWeightMap'):
    
			event['corsika/primaryEnergy'] = frame['CorsikaWeightMap']['PrimaryEnergy']
			event['corsika/primaryType'] = frame['CorsikaWeightMap']['PrimaryType'] 
			event['corsika/primarySpectralIndex'] = frame['CorsikaWeightMap']['PrimarySpectralIndex']
			event['corsika/energyPrimaryMin'] = frame['CorsikaWeightMap']['EnergyPrimaryMin']
			event['corsika/energyPrimaryMax'] = frame['CorsikaWeightMap']['EnergyPrimaryMax']  
			event['corsika/areaSum'] = frame['CorsikaWeightMap']['AreaSum']

		if self.eventId == 0 :
			runinfo = self.run.row
			if frame.Has('CorsikaWeightMap'):
				runinfo['nevents'] = frame['CorsikaWeightMap']['NEvents']
			runinfo['runId'] = frame['I3EventHeader'].run_id
			runinfo['subRunId'] = frame['I3EventHeader'].sub_run_id
			runinfo.append()

		event.append()

		# Loop over the DOM hits and add them to the DOM table
		for i in range(len(frame['DOM_TotalCharge'])):
			dom=self.doms.row
			dom['eventId']           = self.eventId
			dom['string']            = frame['DOM_String'][i]
			dom['om']                = frame['DOM_OM'][i]
			dom['totalCharge']       = frame['DOM_TotalCharge'][i]
			dom['distAboveEndpoint'] = frame['DOM_DistAboveEndpoint'][i]
			dom['impactAngle']       = frame['DOM_ImpactAngle'][i]
			dom['minTimeResidual']   = frame['DOM_MinTimeResidual'][i]
			dom['recoDist']          = frame['DOM_RecoDistance'][i]
			dom.append()
		# Increment the event ID
		self.eventId+=1
		self.PushFrame(frame)                 # push the frame
		return

	def __del__(self):
		#self.events.flush()
		#self.doms.flush()
		#self.h5file.flush()
		self.h5file.close()
