"""
Functions used in cut.py.
"""

import numpy as np
import tables
from I3Tray import I3Units
from icecube import icetray, dataclasses, dataio,MuonGun

def muon_timing(frame):
    tree = frame['I3MCTree']
    muons = []

    for particle in tree:
        if particle.type_string in ('MuPlus', 'MuMinus') and particle.location_type_string== 'InIce':
            muons.append(particle)

    tree = frame['BackgroundI3MCTree']

    for particle in tree:
        if particle.type_string in ('MuPlus', 'MuMinus') and particle.location_type_string== 'InIce':
            muons.append(particle)

    max_energy_muon = muons[0]

    for muon in muons:
        if muon.energy > max_energy_muon.energy:
            max_energy_muon = muon

    surface = MuonGun.Cylinder(300*I3Units.m, 350*I3Units.m, dataclasses.I3Position(0.,0.,0.-250.0))

    truth_energy = 0
    num_visible_muons = 0
    timewindow = []
    for track in MuonGun.Track.harvest(frame['I3MCTree'], frame['MMCTrackList']):

        # Find distance to entrance and exit from sampling volume                                   
        intersections = surface.intersection(track.pos, track.dir)
        energy = track.get_energy(intersections.first)
        if(intersections.first >= 0 and energy > 0):
            timewindow.append(intersections.second - intersections.first)

    frame['TimeWindow'] = dataclasses.I3Double(np.average(timewindow))

def AR_timing(frame):
    IC_strings = [26, 27, 37, 46, 45, 35, 17, 18, 19, 28, 38, 47, 56, 55, 54, 44, 34, 25]
    pulses = frame['SRTInIcePulsesDOMeff'].apply(frame)
    times = []
    for i,pulse in pulses:
        if (i.om <= 60) and (i.om > 42) and (i.string in IC_strings):
            for j in pulse:
                times.append(j.time)
    if len(times) >= 2:
        frame['TimeWindow'] = dataclasses.I3Double(max(times) - min(times))

def AR_timing_long(frame):
    pulses = frame['SRTInIcePulsesDOMeff'].apply(frame)
    times = []
    for i,pulse in pulses:
        if (i.om <= 60):
            for j in pulse:
                times.append(j.time)
    if len(times) >= 2:
        frame['TimeWindow_Long'] = dataclasses.I3Double(max(times) - min(times))


def bdt_vars(frame):
    frame['ALLDOMTime'] = dataclasses.I3VectorDouble()
    frame['ALLDOMCharge'] = dataclasses.I3VectorDouble()
    frame['ALLDOMOM'] = dataclasses.I3VectorDouble()
    frame['ALLDOMString'] = dataclasses.I3VectorDouble()

    pulse_series = frame['SRTInIcePulsesDOMeff'].apply(frame)

    for i,pulse in pulse_series:
        for j in pulse:
            frame['ALLDOMOM'].append(i.om)
            frame['ALLDOMString'].append(i.string)
            frame['ALLDOMCharge'].append(j.charge)
            frame['ALLDOMTime'].append(j.time)
    total_len = len(frame['ALLDOMTime'])
    frame['ALLDOMTotalDoms'] = dataclasses.I3Double(total_len)
def make_event_cuts(frame, event_cuts):
    """
    Cut out the frames that do not pass the event cuts.

    Parameters
    ----------
    event_cuts : dict[str] -> tuple
        Contains the event cuts. The keys are the names of the objects within
        the frame, and the values are tuples containing the information on the
        cut to make. For example, event_cuts['NDirDoms'] = (operator.gt, 5)
        means we only keep frames with an 'NDirDoms' that is greater than 5. Easy.

    Returns
    -------
    bool
        Indicates if the frame passed all the event cuts.
    """

    for key, (function, value) in event_cuts.items():
        # Get the data for making the cut.
        data = frame[key].value

        # Make the appropriate cut.
        pass_cut = function(data, value)

        # If it didn't pass the cut, return False.
        if not pass_cut:
            return False

    # It passed all the cuts, so return True.
    return True


def make_dom_cuts(frame, dom_cuts, dom_keys):
    """
    Cut out the data for the DOMs that do not pass the dom cuts, then resave
    the data that did pass into the frame.

    Parameters
    ----------
    dom_cuts : dict[str] -> tuple
        Contains the information about the dom cuts. The layout of this
        dictionary is the same as event_cuts. Ie.
        dom_cuts['DistAboveEndpoint'] = (operator.gt, 100)
        means only keep the dom data with a 'DistAboveEndpoint' that is greater
        than 100.

    dom_keys : list of str
        The keys of the dom data to make a cut on. These are the keys that are
        written to the HDF5 file.

    Adds To Frame
    -------------
    NameOfDOMKeyCut : I3VectorDouble
        The cut DOM data. This is done for all the keys in dom_keys.
    """
    # pass_cut is a boolean array that records which data passes the
    # dom cuts. We need to initialize it to an array the same length as the dom
    # data (in this case using 'String', but it doesn't matter). We need to
    # explicitly say "dtype=bool" in the case that len(frame['String']) == 0.
    pass_cut = np.array([True] * len(frame['String']), dtype=bool)

    # Iterate over the data and make the cuts.
    for key, (function, value) in dom_cuts.items():
        data = np.array(frame[key])

        # Update pass_cut for the events that pass the cut.
        pass_cut &= function(data, value)

    # Iterate over the dom keys we want to keep and make the cut.
    for key in dom_keys:

        # Get the data.
        data = np.array(frame[key])

        # Make the cut.
        pass_cut_data = data[pass_cut]

        # Put it back in the frame.
        frame[key + 'Cut'] = dataclasses.I3VectorDouble(pass_cut_data)
   
    doms_in_event = len(frame['OMCut'])
    frame['DomsInEvent'] = dataclasses.I3Double(doms_in_event)


def write_cut_metadata(ofile, event_cuts, dom_cuts):
    """
    Write the cuts to the HDF5 file as metadata.
    In PyTables lingo, these are called "attributes". You can recover them later
    by opening the file and getting

    infile.root._v_attrs.event_cuts
    infile.root._v_attrs.dom_cuts

    Parameters
    ----------
    ofile : str
        Path to the output HDF5 file.

    event_cuts : dict[str] -> tuple
        Contains the event cuts. The keys are the names of the objects within
        the frame, and the values are tuples containing the information on the
        cut to make. For example, event_cuts['NDirDoms'] = (operator.gt, 5)
        means we only keep frames with an 'NDirDoms' that is greater than 5. Easy.

    dom_cuts : dict[str] -> tuple
        Contains the information about the dom cuts. The layout of this
        dictionary is the same as event_cuts. Ie.
        dom_cuts['DistAboveEndpoint'] = (operator.gt, 100)
        means only keep the dom data with a 'DistAboveEndpoint' that is greater
        than 100.
    """

    infile = tables.open_file(ofile, 'a')

    infile.root._v_attrs.event_cuts = event_cuts
    infile.root._v_attrs.dom_cuts = dom_cuts

    infile.close()
