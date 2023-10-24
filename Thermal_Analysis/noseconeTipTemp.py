import numpy as np
import matplotlib.pyplot as plt
import CoolProp.CoolProp as CP

import os
import math
import orhelper
from orhelper import FlightDataType, FlightEvent

dt = 0.1 # timestep [seconds] should be based on OpenRocket, may want to interpolate if needed


#Run OpenRocket Simulation
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

#create empty arrays
t = np.array(data[FlightDataType.TYPE_TIME])
v = np.array(data[FlightDataType.TYPE_VELOCITY_TOTAL])
M = np.array(data[FlightDataType.TYPE_MACH_NUMBER])
alt = np.array(data[FlightDataType.TYPE_ALTITUDE])+370
p_atm = np.array(data[FlightDataType.TYPE_AIR_PRESSURE])
Temp = 298*np.ones(t.size) #temperature at each attlude [K], from OR
T_Tip = np.zeros(t.size)
T_stg = np.zeros(t.size)



#nosecone profile
x = np.linspace(0.001, 3, 10) #create a linear vector of nosecone lenth, use 0.001 as 0 will be undefined
#TODO the angle of end of tip may not be correct
def TangentOgiveNoscone(radius,NoseConelength, tipLength = 3,NumOfPoints=10):
    OgiveRadius = (radius**2 + NoseConelength **2)/(2*radius)
    tipAngleLocation = np.arcsin(NoseConelength/OgiveRadius) 
    endOfTipAngleLocation = np.arcsin(((NoseConelength - tipLength)/(OgiveRadius-radius)))
    angles = np.linspace(tipAngleLocation - 0.01 ,endOfTipAngleLocation ,NumOfPoints) #create points of angles

    print(angles)
    arcLengths = np.absolute(angles*OgiveRadius - tipAngleLocation*OgiveRadius) #compute a set of arcLengths starting from the tip
    
    coordinates = np.zeros((2,NumOfPoints)) #compute a [N x 2] array
    for index, angleTemp in enumerate(angles):
        coordinates[0, index] = NoseConelength - np.tan(angles[index])*(OgiveRadius - radius) #x coordinate
        coordinates[1, index] = np.sqrt(OgiveRadius**2 - (coordinates[0,index]-NoseConelength)**2) + radius - OgiveRadius#y coordinate

    totalConeAngle = 2*np.arctan(coordinates[1,-1]/coordinates[0,-1])

    return coordinates,arcLengths, totalConeAngle

[NC_Coordinates, NC_lengths,coneAngle] = TangentOgiveNoscone(4.7, 27)

print(NC_Coordinates)
plt.plot(NC_Coordinates[0],NC_Coordinates[1])
ax = plt.gca()
ax.set_aspect("equal")
plt.show()


#cone properties
beta = np.radians(coneAngle) #total apex angle of cone, rad
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
#l = 0.5*25.4/1000 #characteristic length [m]
C = 1361 #solar constant [W/m^2]
delta = 1.0 #sky radiation factor, estimated from paper
sigma = 5.670374419e-8 #stefan-boltzman radiation constant [W/(m^2*K^4)]

#fig = plt.figure()
#ax = fig.add_subplot(111)


for index ,length_s in enumerate(NC_lengths):
    l = length_s*25.4/1000
    print(index)
    print(l)
    SkinThickness = NC_Coordinates[1,index]*25.4/1000

    T_1 = 20+273 #temperature, start of time interval [K]
   
    for i,t_i in enumerate(t):
        #print("in loop")
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
        u = CP.PropsSI('VISCOSITY','T',Temp[i],'P',p_i,fluid) #viscosity
        k = CP.PropsSI('CONDUCTIVITY','T',Temp[i],'P',p_i,fluid) # thermal conductivity of air, cool prop
        #print(u)
        #print(k)
        d_i = d(alt_i) #instant density of air, depends on altitude OpenRocket? []
        #print(l)
        h = (0.0017+0.0154*beta**0.5)*(d0**0.8)*k*((v_i*d_i/(u*d0))**0.8)/(l**0.2) #eq 4

        B = e*sigma/h #eq B2
        T_p = T_B + B*(delta*T_A**4+C/sigma) #eq B2
        theta = c*SkinThickness*w /h #eq B2, thermal lag constant [seconds]

        T_m = T_1 # should be avg of T_2 and T_1, need to iterativly solve the correct temp if want more accurate result

        #TODO check if dt/theta < 0.25
        T_2 = (T_p-B*T_1**4)*(1-np.exp(-dt/theta))+T_1*np.exp(-dt/theta)
        T_1 = T_2
        T_Tip[i] = T_2
        T_stg[i] = T_T
    print(T_Tip)


    plt.plot(t,T_Tip-273)
    #plt.plot(t,M)

    """
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

plt.show()
