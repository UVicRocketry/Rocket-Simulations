import numpy as np
import matplotlib.pyplot as plt
import CoolProp.CoolProp as CP

import os
import math
import orhelper
from orhelper import FlightDataType, FlightEvent

dt = 0.01 # timestep [seconds] should be based on OpenRocket, may want to interpolate if needed

with orhelper.OpenRocketInstance() as instance:

    save_graphs = False
    iterate_windSpeed = False
    iterate_launchAngle = False
    threeD_trajectory = False

    launchLocation = [48,-81.9]
    launch_an = 1
    orh = orhelper.Helper(instance)

    #load .ork files in the program directory

    doc = orh.load_doc(os.path.join('TestRocket.ork')) #MAKE SURE RUNNING IN THE CORRECT DIRECTORY
    sim = doc.getSimulation(0)

    #setup sim settings
    #settings are accessed from the OR simulation.SimulationOption class, see https://github.com/openrocket/openrocket/blob/unstable/core/src/net/sf/openrocket/simulation/SimulationOptions.java

    sim.getOptions().setTimeStep(dt) #seconds
    sim.getOptions().setLaunchRodLength(5.18) #meters
    sim.getOptions().setLaunchRodAngle(math.radians(6)) #rad
    sim.getOptions().setLaunchRodDirection(math.radians(270))
    sim.getOptions().setWindSpeedDeviation(0)
    sim.getOptions().setWindDirection(math.radians(90))
    sim.getOptions().setLaunchAltitude(370) #meters
    sim.getOptions().setLaunchLatitude(launchLocation[0]) #deg
    sim.getOptions().setLaunchLongitude(launchLocation[1]) #deg
    sim.getOptions().setWindSpeedAverage(0) #m/s
    sim.getOptions().setLaunchRodAngle(math.radians(6))
    orh.run_simulation(sim)
    data = orh.get_timeseries(sim,[FlightDataType.TYPE_TIME,FlightDataType.TYPE_VELOCITY_TOTAL,FlightDataType.TYPE_MACH_NUMBER,FlightDataType.TYPE_AIR_PRESSURE,FlightDataType.TYPE_ALTITUDE])


t = np.array(data[FlightDataType.TYPE_TIME])
v = np.array(data[FlightDataType.TYPE_VELOCITY_TOTAL])
M = np.array(data[FlightDataType.TYPE_MACH_NUMBER])
alt = np.array(data[FlightDataType.TYPE_ALTITUDE])+370
p_atm = np.array(data[FlightDataType.TYPE_AIR_PRESSURE])
Temp = 298*np.ones(t.size) #temperature at each attlude [K], from OR
T_Tip = np.zeros(t.size)
T_stg = np.zeros(t.size)


#cone properties
beta = np.radians(20) #total apex angle of cone, rad
c = 903 #specific heat of skin material [J/(Kg*K)], 6061-T6 in this case
SkinThickness = 0.5*25.4/1000 #skin thickness [m]
w = 2700 #specific weight of skin material [kg/m^3]

#idea gas properties
y = 1.4 #ratio of specific heats of air
fluid = 'Air'

#thermal properties
e = 0.2 #emissivity
d0 = 1.225 #density of standard atmosphere at sea level [kg/m^3]
d = lambda alt : d0*np.exp(-9.81*0.0289644*(alt-0)/(8.31446*288.15))
l = 0.5*25.4/1000 #characteristic length [m]
C = 1361 #solar constant [W/m^2]
delta = 1.0 #sky radiation factor, estimated from paper
sigma = 5.670374419e-8 #stefan-boltzman radiation constant [W/(m^2*K^4)]


T_1 = 20+273 #temperature, start of time interval [K]
for i,t_i in enumerate(t):
    #things that change based on velocity/altitude
    v_i = v[i]  #clean up here later
    M_i = M[i] 
    alt_i = alt[i] 
    p_i = p_atm[i]

    T_A = Temp[i] # ambient atm temp absolute [K], change with altitude
    T_T =  T_A*(1+0.5*(y - 1)*M_i**2) # stagnation temperature [K]
    K_recovery = 1.0 # thermal conductivity of air []
    T_B = T_A + K_recovery*(T_T - T_A) #boundary layer temperature [K]

    #TODO update the pressure vlaue
    u = CP.PropsSI('VISCOSITY','T',T_1,'P',p_i,fluid) #viscosity
    k = CP.PropsSI('CONDUCTIVITY','T',T_1,'P',p_i,fluid) # thermal conductivity of air, cool prop
    d_i = d(alt_i) #instant density of air, depends on altitude OpenRocket? []

    h = (0.0017+0.0154*beta**0.5)*(d0**0.8)*k*((v_i*d_i/(u*d0))**0.8)/l**0.2 #eq 4

    B = e*sigma/h #eq B2
    T_p = T_B + B*(delta*T_A**4+C/sigma) #eq B2
    theta = c*SkinThickness*w /h #eq B2, thermal lag constant [seconds]

    T_m = T_1 # should be avg of T_2 and T_1, need to iterativly solve the correct temp if want more accurate result

    #TODO check if dt/theta < 0.25
    T_2 = (T_p-B*T_1**4)*(1-np.exp(-dt/theta))+T_1*np.exp(-dt/theta)
    T_1 = T_2
    T_Tip[i] = T_2
    T_stg[i] = T_T
    print(T_2-273)


#plt.plot(t,T_Tip-273)
#plt.plot(t,M)

fig = plt.figure()
ax = fig.add_subplot(111)
plt1 = ax.plot(t, T_Tip - 273, color = 'r', label = "Tip Temp")
plt3 = ax.plot(t, T_stg-273, color = 'y', label = 'T_stg')
ax2 = ax.twinx()
plt2 = ax2.plot(t, M, color = 'b', label = 'Mach Number')

ax.set_xlabel("time")
ax2.set_ylabel("Mach Number")
ax.set_ylabel("Tip Temp (C)")

lns = plt1 +plt2 + plt3
labs = [l.get_label() for l in lns]
ax.legend(lns, labs, loc="upper right")

plt.show()

"""
TODO
- check meaning of l again
- check delta again
- get actual value of OR sims
"""
