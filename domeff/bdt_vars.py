
def dbt_vars(frame,pulses):
    # Get the pulse series
    frame['Time'] = dataclasses.I3VectorDouble()
    pulse_series = frame[pulses].apply(frame)
    for pulse in pulse_series[dom]:
        frame['Time'].append(pulse.time)
   
