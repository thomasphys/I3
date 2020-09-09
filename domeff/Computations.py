import os, sys
import numpy as np
import matplotlib as mpl
from matplotlib.colors import LogNorm, Normalize
import matplotlib.pyplot as plt
import timeit as time
import math
from datetime import datetime

def residualtime(distance,tracktime,pulsetime):
    return pulsetime-distance / (0.3/1.31) + tracktime

def correctedcharge(distance,charge) :
    return distance*charge

def correctedAttencharge(distance,charge) :
    return distance*charge/np.exp(-distance/atten)

def emission_distance_from_start(dom_x,dom_y,dom_z,start_x,start_y,start_z,track_az,track_ze) :
    return 1.0

def emission_distance_from_end(dom_x,dom_y,dom_z,start_x,start_y,start_z,track_az,track_ze) :
    return 1.0


