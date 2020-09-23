"""
Functions used for analyzing the per-dom (as opposed to per-event) data.
"""

from __future__ import print_function, division  # 2to3

import math

from icecube import dataclasses, finiteReco
from icecube.phys_services import I3Calculator as calc
from icecube.dataclasses import I3Constants


#def om_partition(frame, output_name, options):
#    """
#    Partition the pulses.
#
#    Parameters
#    ----------
#    output_name : str
#    options : dict[str]
#
#    Adds To Frame
#    -------------
#    output_name.format(partition) : I3RecoPulseSeriesMap
#
#    """
#
#    # Initialize the RecoPulseSeriesMaps
#    for partition in range(options['partitions']):
#        key = output_name.format(partition)
#        frame[key] = dataclasses.I3RecoPulseSeriesMap()
#
#    # Get the pulse series
#    pulse_series = frame[options['pulses_name']].apply(frame)
#
#    for dom, pulse_vector in pulse_series.items():
#
#        # Find out which partition the pulse_vector should go in
#        partition_num = (dom.string + dom.om) % options['partitions']
#
#        # Put it in every partition except the one it is in.
#        for partition in range(options['partitions']):
#            if partition != partition_num:
#                key = output_name.format(partition)
#                frame[key][dom] = pulse_vector

def dom_data(frame, reco_fit, options):
    """
    Analyze and save the per-dom data using the provided fit.

    Parameters
    ----------
    reco_fit : str
        The key of the MPEFit reconstruction

    options : dict[str]

    Adds To Frame
    -------------
    TotalCharge : I3VectorDouble
    String : I3VectorDouble
    OM : I3VectorDouble
    DistAboveEndpoint : I3VectorDouble
    ImpactAngle : I3VectorDouble
    RecoDistance : I3VectorDouble

    Returns
    -------
    bool
        Whether any per-dom data was added to the frame. If no data was added,
        return False, because this frame contains no pertinent information.
        Otherwise return True.

    """

    n_ice_group = I3Constants.n_ice_group
    n_ice_phase = I3Constants.n_ice_phase

    IC_strings = [26, 27, 37, 46, 45, 35, 17, 18, 19, 28, 38, 47, 56, 55, 54, 44, 34, 25]
    DC_strings = [81, 82, 83, 84, 85, 86]

    reco_endpoint = frame['RecoEndpoint']

    # Get the pulse series
    pulse_series = frame[options['pulses_name']].apply(frame)

    # Initialize the vectors
    frame['TotalCharge'] = dataclasses.I3VectorDouble()
    frame['String'] = dataclasses.I3VectorDouble()
    frame['OM'] = dataclasses.I3VectorDouble()
    frame['DistAboveEndpoint'] = dataclasses.I3VectorDouble()
    frame['ImpactAngle'] = dataclasses.I3VectorDouble()
    frame['RecoDistance'] = dataclasses.I3VectorDouble()

    dom_geo = frame['I3Geometry'].omgeo.items()
    # We want to be able to also test the cherenkov distance to the Truth Track                                                                                                                             
    # as well as the truth endpoint, for sanity checks                                                                                                                                                     


    # Find all doms above the reconstructed z coord of endpoint and
    # within the specified distance interval of the track
    for dom, geo in dom_geo:  # (OMKey, I3OMGeo)

        # We want to get DOMs that are in the IC/DC strings and below the dust
        # layer (40 and below for IC, 11 and below for DC).
        if (dom.string in IC_strings and dom.om >= 42 and dom.om <=60) or (dom.string in DC_strings and dom.om >= 11 and dom.om <=60):

            dom_position = geo.position
            #partition_num = (dom.string + dom.om) % options['partitions']
            #mpe = frame[reco_fit.format(partition_num)]  # MPEFit0...4
            #mpe = frame['MPEFit']
            mpe = frame[reco_fit]
            # Find cherenkov distance from track to DOM
            reco_dist = calc.cherenkov_distance(mpe, dom_position, n_ice_group, n_ice_phase)
            if reco_dist < options['max_dist']:

                # Keep if track is below DOM
                clos_app_pos = calc.closest_approach_position(mpe, dom_position)
                if clos_app_pos.z < dom_position.z:

                    # Try cherenkov dist
                    cherenkov_pos = calc.cherenkov_position(mpe, dom_position, n_ice_group, n_ice_phase)
                    dist_above_endpoint = calc.distance_along_track(mpe, reco_endpoint) - calc.distance_along_track(mpe, cherenkov_pos)
                    if dist_above_endpoint > 0:

                        frame['RecoDistance'].append(reco_dist)
                        frame['DistAboveEndpoint'].append(dist_above_endpoint)
                        frame['String'].append(dom.string)
                        frame['OM'].append(dom.om)

                        perp_position = dataclasses.I3Position(dom_position.x, dom_position.y, clos_app_pos.z)
                        delta = perp_position - clos_app_pos
                        impact_param = delta.magnitude

                        impact_angle = math.asin(impact_param / calc.closest_approach_distance(mpe, dom_position))
                        frame['ImpactAngle'].append(impact_angle)

                        # TotalCharge and TimeResidual
                        total_charge = 0

                        # If there are pulses, sum the charge of the ones with a
                        # time residual less than 1000 ns.
                        if dom in pulse_series.keys():
                            for pulse in pulse_series[dom]:
                                time_res = calc.time_residual(mpe, dom_position, pulse.time, n_ice_group, n_ice_phase)
                                if time_res < 1000:
                                    total_charge += pulse.charge

                        frame['TotalCharge'].append(total_charge)
#Getting Photon Arrival Angle (SEBASTIANS FUNCTION)                                                                                                                                                         



    n_ice_group = I3Constants.n_ice_group
    n_ice_phase = I3Constants.n_ice_phase

    frame['PhotonArrivalAngle'] = dataclasses.I3VectorDouble()
    strings = frame['String']
    oms = frame['OM']
    cherenkov_distances = frame['RecoDistance']

    mpe = frame[reco_fit]
    for i in range(0,len(strings)):
        for om, geo in dom_geo:
            if(om.string==strings[i] and om.om==oms[i]):
                dom_position = geo.position
        cherenkov_dist = cherenkov_distances[i]
        cherenkov_pos = calc.cherenkov_position(mpe, dom_position, n_ice_group, n_ice_phase)
        perp_position = dataclasses.I3Position(dom_position.x, dom_position.y, cherenkov_pos.z)
        delta = perp_position - cherenkov_pos
        impact_param = delta.magnitude
        if cherenkov_pos.z < dom_position.z:
            ph_angle = math.asin(impact_param / cherenkov_dist)
        else:
            # There is one event that is failing, lets try to correct for it...                                                                                                                            \
                                                                                                                                                                                                            
            if((impact_param/cherenkov_dist) > 1):
                print("Impact_param= {}".format(impact_param))
                print("Cherenkov_dist = {}".format(cherenkov_dist))
                impact_param = cherenkov_dist
            ph_angle = math.pi - math.asin(impact_param / cherenkov_dist)
        frame['PhotonArrivalAngle'].append(ph_angle)

    # After all that, if none of the DOMs made it through, get rid of this
    # frame.
    return len(frame['TotalCharge']) != 0
