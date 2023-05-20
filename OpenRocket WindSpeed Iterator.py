#This script is meant to automate certain process of OpenRocket simulation
#Graphics will be generated with name "xxxx" (TBD) for reports
#
#The orhelper is used for this script, for setup see: https://github.com/SilentSys/orhelper

import os
import math
import numpy as np
from matplotlib import pyplot as plt

import orhelper
from orhelper import FlightDataType, FlightEvent

#change varaible as needed, depends on the analysis you are doing
#you can iterate the varaibles and feed them thru sims



with orhelper.OpenRocketInstance() as instance:
    wind_speed_kmh = 0.0
    wind_speed_range = np.array([0,5,10,15,20,25,30])
    orh = orhelper.Helper(instance)

    #load .ork files in the program directory

    doc = orh.load_doc(os.path.join('Xenia-2_test.ork'))
    sim = doc.getSimulation(0)

    #setup sim settings
    #settings are accessed from the OR simulation.SimulationOption class, see https://github.com/openrocket/openrocket/blob/unstable/core/src/net/sf/openrocket/simulation/SimulationOptions.java
    sim.getOptions().setLaunchRodLength(5.18)
    sim.getOptions().setLaunchRodAngle(math.radians(6))
    sim.getOptions().setWindSpeedAverage(wind_speed_kmh)
    sim.getOptions().setWindSpeedDeviation(0)
    sim.getOptions().setWindDirection(90)
    sim.getOptions().setLaunchAltitude(370)
    sim.getOptions().setLaunchLatitude(48)
    sim.getOptions().setLaunchLongitude(-81.9)
    
    
    def simulate_windSpeed(wind_speed, sim):
        sim.getOptions().setWindSpeedAverage(wind_speed)
        orh.run_simulation(sim)
        return orh.get_timeseries(sim, [FlightDataType.TYPE_TIME, FlightDataType.TYPE_ALTITUDE])

    data_runs = dict() 
    for windSpd in wind_speed_range:
       data_runs[windSpd] = simulate_windSpeed( windSpd, sim)

    #data = orh.get_timeseries(sim, [FlightDataType.TYPE_TIME, FlightDataType.TYPE_ALTITUDE, FlightDataType.TYPE_VELOCITY_TOTAL, FlightDataType.TYPE_STABILITY, FlightDataType.TYPE_MACH_NUMBER])
    #events = orh.get_events(sim)

    # Make a custom plot of the simulation


    events_to_annotate = {
        FlightEvent.BURNOUT: 'Motor burnout',
        FlightEvent.APOGEE: 'Apogee',
        FlightEvent.LAUNCHROD: 'Launch rod clearance'
    }

    fig = plt.figure()
    ax1 = fig.add_subplot(111)

    for spd, data in data_runs.items():
        ax1.plot(data[FlightDataType.TYPE_TIME],data[FlightDataType.TYPE_ALTITUDE], label = spd)
   
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Stability', color='b')
    change_color = lambda ax, col: [x.set_color(col) for x in ax.get_yticklabels()]
    change_color(ax1, 'b')


    ax1.grid(True)

# Leave OpenRocketInstance context before showing plot in order to shutdown JVM first
plt.show()
