#
# Module to output events in HDF5 format
#
from tables import open_file

from icecube import icetray

from event import *

from icecube.weighting.fluxes import  GaisserH4a, GaisserH3a, GaisserH4a_IT, GaisserHillas, Hoerandel, Hoerandel5, Hoerandel_IT

from icecube.weighting import weighting

class EventWriter(icetray.I3Module):
    def __init__(self, context):
        icetray.I3Module.__init__(self, context)
        self.AddParameter('FileName','Name of the file to write out','out.h5')
        self.eventId=0
	self.flux_GaisserH4a = GaisserH4a()
	self.flux_GaisserH3a = GaisserH3a()
	self.flux_GaisserH4a_IT = GaisserH4a_IT()
	self.flux_GaisserHillas = GaisserHillas()
	self.flux_Hoerandel = Hoerandel()
	self.flux_Hoerandel5 = Hoerandel5()
	self.flux_Hoerandel_IT = Hoerandel_IT()

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
	self.events.cols.id.create_index()

    def Physics(self, frame):
        # Create an event entry
        event=self.events.row
        # Get the current event ID number
        event['id']=self.eventId
        event['reco/time']   = frame['SplineMPE'].time
        event['reco/energy'] = frame['SplineMPE'].energy
        event['reco/speed']  = frame['SplineMPE'].speed
        event['reco/length'] = frame['SplineMPE'].length
        event['reco/pos/x'] = frame['SplineMPE'].pos.x
        event['reco/pos/y'] = frame['SplineMPE'].pos.y
        event['reco/pos/z'] = frame['SplineMPE'].pos.z
        event['reco/dir/zenith']  = frame['SplineMPE'].dir.zenith
        event['reco/dir/azimuth'] = frame['SplineMPE'].dir.azimuth

	if frame.Has('CorsikaWeightMap'):
            cwm = frame['CorsikaWeightMap']
            pflux_GaisserH4a = self.flux_GaisserH4a(cwm['PrimaryEnergy'],cwm['PrimaryType'])
            pflux_GaisserH3a = self.flux_GaisserH3a(cwm['PrimaryEnergy'],cwm['PrimaryType'])
            pflux_GaisserH4a_IT = self.flux_GaisserH4a_IT(cwm['PrimaryEnergy'],cwm['PrimaryType'])
            pflux_GaisserHillas = self.flux_GaisserHillas(cwm['PrimaryEnergy'],cwm['PrimaryType'])
            pflux_Hoerandel = self.flux_Hoerandel(cwm['PrimaryEnergy'],cwm['PrimaryType'])
            pflux_Hoerandel5 = self.flux_Hoerandel5(cwm['PrimaryEnergy'],cwm['PrimaryType'])
            pflux_Hoerandel_IT = self.flux_Hoerandel_IT(cwm['PrimaryEnergy'],cwm['PrimaryType'])
            energy_integral = (cwm['EnergyPrimaryMax']**(cwm['PrimarySpectralIndex']+1)-cwm['EnergyPrimaryMin']**(cwm['PrimarySpectralIndex']+1))/(cwm['PrimarySpectralIndex']+1)
            energy_weight = cwm['PrimaryEnergy']**cwm['PrimarySpectralIndex']
            event['weight_GaisserH4a'] = pflux_GaisserH4a *energy_integral/energy_weight * cwm['AreaSum']
            event['weight_GaisserH3a'] = pflux_GaisserH3a *energy_integral/energy_weight * cwm['AreaSum']
            event['weight_GaisserH4a_IT'] = pflux_GaisserH4a_IT *energy_integral/energy_weight * cwm['AreaSum']
            event['weight_GaisserHillas'] = pflux_GaisserHillas *energy_integral/energy_weight * cwm['AreaSum']
            event['weight_Hoerandel'] = pflux_Hoerandel *energy_integral/energy_weight * cwm['AreaSum']
            event['weight_Hoerandel5'] = pflux_Hoerandel5 *energy_integral/energy_weight * cwm['AreaSum']
            event['weight_Hoerandel_IT'] = pflux_Hoerandel_IT *energy_integral/energy_weight * cwm['AreaSum']
	    if self.eventId == 0 :
		runinfo = self.run.row
		runinfo['nevents'] = cwm['NEvents']
		runinfo.append()
        else :
	    print('fail')
            event['weight_GaisserH4a'] = 1.0
            event['weight_GaisserH3a'] = 1.0
            event['weight_GaisserH4a_IT'] = 1.0
            event['weight_GaisserHillas'] = 1.0
            event['weight_Hoerandel'] = 1.0
            event['weight_Hoerandel5'] = 1.0
            event['weight_Hoerandel_IT'] = 1.0

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
