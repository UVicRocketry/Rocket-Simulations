#Author: Gordon So
#This script is meant to automate certain process of OpenRocket simulation
#Graphics will be generated with name "xxxx" (TBD) for reports
#
#The orhelper is used for this script, for setup see: https://github.com/SilentSys/orhelper

#UNITS
#All units are in SI, see OpenRocket GitHub page for more info: https://github.com/openrocket/openrocket/wiki/Developer's-Guide#units-used-in-openrocket

import os
import math
import numpy as np
from matplotlib import pyplot as plt

import orhelper
from orhelper import FlightDataType, FlightEvent

#change varaible as needed, depends on the analysis you are doing
#you can iterate the varaibles and feed them thru sims



with orhelper.OpenRocketInstance() as instance:

    save_graphs = False
    iterate_windSpeed = False
    iterate_launchAngle = False
    threeD_trajectory = False

    wind_speed_range = np.array([0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0])*1000/3600 #array([km/hr]) to m/s
    launch_an = 1
    orh = orhelper.Helper(instance)

    #load .ork files in the program directory

    doc = orh.load_doc(os.path.join('Xenia-2_test.ork'))
    sim = doc.getSimulation(0)

    #setup sim settings
    #settings are accessed from the OR simulation.SimulationOption class, see https://github.com/openrocket/openrocket/blob/unstable/core/src/net/sf/openrocket/simulation/SimulationOptions.java

    sim.getOptions().setTimeStep(0.05) #seconds
    sim.getOptions().setLaunchRodLength(5.18) #meters
    sim.getOptions().setLaunchRodAngle(math.radians(6)) #rad
    sim.getOptions().setWindSpeedDeviation(0)
    sim.getOptions().setWindDirection(math.radians(90))
    sim.getOptions().setLaunchAltitude(370) #meters
    sim.getOptions().setLaunchLatitude(48) #deg
    sim.getOptions().setLaunchLongitude(-81.9) #deg
    
    
    def simulate_windSpeed(wind_speed, ang, sim):
        sim.getOptions().setWindSpeedAverage(wind_speed) #m/s
        sim.getOptions().setLaunchRodAngle(math.radians(ang))
        orh.run_simulation(sim)
        return orh.get_timeseries(sim, [FlightDataType.TYPE_TIME, FlightDataType.TYPE_ALTITUDE, FlightDataType.TYPE_STABILITY, FlightDataType.TYPE_MACH_NUMBER])

    data_runs = dict() 

    for windSpd in wind_speed_range:
       #if iterate_launchAngle is True:
           
       data_runs[windSpd] = simulate_windSpeed( windSpd, 6, sim)

    #data = orh.get_timeseries(sim, [FlightDataType.TYPE_TIME, FlightDataType.TYPE_ALTITUDE, FlightDataType.TYPE_VELOCITY_TOTAL, FlightDataType.TYPE_STABILITY, FlightDataType.TYPE_MACH_NUMBER])
    #events = orh.get_events(sim)

    # Make a custom plot of the simulation


    events_to_annotate = {
        FlightEvent.BURNOUT: 'Motor burnout',
        FlightEvent.APOGEE: 'Apogee',
        FlightEvent.LAUNCHROD: 'Launch rod clearance'
    }

    fig = plt.figure(figsize=(15,5))
    ax1 = fig.add_subplot(131)
    ax2 = fig.add_subplot(132)
    ax3 = fig.add_subplot(133)

    for spd, data in data_runs.items():
        ax1.plot(data[FlightDataType.TYPE_TIME],data[FlightDataType.TYPE_ALTITUDE], label = str(round(spd*3600/1000, 0))+" km/h")
        ax2.plot(data[FlightDataType.TYPE_TIME],data[FlightDataType.TYPE_STABILITY], label = str(round(spd*3600/1000, 0))+" km/h")
        ax3.plot(data[FlightDataType.TYPE_TIME],data[FlightDataType.TYPE_MACH_NUMBER], label = str(round(spd*3600/1000, 0))+" km/h")
   
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('AGL (m)', color='b')
    change_color = lambda ax, col: [x.set_color(col) for x in ax.get_yticklabels()]
    change_color(ax1, 'b')
    ax1.legend()

    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Stability', color='b')
    change_color = lambda ax, col: [x.set_color(col) for x in ax.get_yticklabels()]
    change_color(ax2, 'b')
    ax2.legend()

    ax3.set_xlabel('Time (s)')
    ax3.set_ylabel('MACH', color='b')
    change_color = lambda ax, col: [x.set_color(col) for x in ax.get_yticklabels()]
    change_color(ax2, 'b')
    ax3.legend()

    ax1.grid(True)
    ax2.grid(True)
    ax3.grid(True)

    #if save_graph is true:
        #save file

# Leave OpenRocketInstance context before showing plot in order to shutdown JVM first
plt.savefig("test.png",dpi=600)
plt.show()

