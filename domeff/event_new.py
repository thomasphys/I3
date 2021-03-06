#
# HDF5 Table for DOMs which have been hit
#
import numpy as np
from tables import *

class Position(IsDescription):
    x = Float64Col()
    y = Float64Col()
    z = Float64Col()

    def distance(self,position2) :
        return np.sqrt((self.x-position2.x)*(self.x-position2.x)
                      +(self.y-position2.y)*(self.y-position2.y)
                      +(self.z-position2.z)*(self.z-position2.z))

class Direction(IsDescription):
    zenith  = Float64Col()
    azimuth = Float64Col()

class Particle(IsDescription):
    id     = UInt32Col()  # Particle ID
    pos    = Position()   # Starting vertex of the particle
    dir    = Direction()  # Direction that the particle came from
    time   = Float64Col()
    energy = Float64Col() # Energy of the particle
    speed  = Float64Col()
    length = Float64Col()

class Event(IsDescription):
    id           = UInt32Col()    # ID number of the event
    dcHitsIn     = UInt32Col()    # Number of hits inside the deep core analysis region
    dcHitsOut    = UInt32Col()    # Number of hits outside the deep core analysis region
    icHitsIn     = UInt32Col()    # Number of hits inside the IceCube analysis region
    icHitsOut    = UInt32Col()    # Number of hits outside the IceCube analysis region
    recoEndpoint = Position()     # Coordinates of the reconstructed track endpoint
    firstHit     = UInt32Col()    # Index of the first DOM hit for this event
    nHits        = UInt32Col()    # Number of DOM hits in this event
    primary      = Particle()     # Polyplopia primary particle
    reco         = Particle()     # Reconstructed particle track

class DOM(IsDescription):
    eventId           = UInt32Col()   # ID number of the event this DOM belongs to
    string            = UInt16Col()   # String containing the DOM
    om                = UInt16Col()   # Opitcal module number of the DOM
    recoDist          = Float64Col()  # Reconstruction distance.
    distAboveEndpoint = Float64Col()  # Distance of the DOM above the endpoint of the track
    impactAngle       = Float64Col()
    totalCharge       = Float64Col()  # Total charge seen by the DOM
    minTimeResidual   = Float64Col()  # Minimum time residual for all pulses
