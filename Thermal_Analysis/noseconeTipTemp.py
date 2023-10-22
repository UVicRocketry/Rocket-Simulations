import numpy as np
import matplotlib as plt
import CoolProp.CoolProp as CP


dt = 0.01 # timestep [seconds] should be based on OpenRocket, may want to interpolate if needed
t = np.arange(1,10,dt)
v = 1.5*t + 343.4*1.5 #instant speed, from OpenRocket [m/s] 
M = v/343.4 #instant mach number, from OpenRocket 
alt = v*t
Temp = 298*np.ones(t.size) #temperature at each attlude [K], from OR

#cone properties
beta = np.radians(10) #total apex angle of cone, rad
c = 903 #specific heat of skin material [J/(Kg*K)], 6061-T6 in this case
SkinThickness = 0.065*25.4/1000 #skin thickness [m]
w = 2700 #specific weight of skin material [kg/m^3]

#idea gas properties
y = 1.4 #ratio of specific heats of air
fluid = 'Air'

#thermal properties
e = 0.2 #emissivity
d0 = 1.225 #density of standard atmosphere at sea level [kg/m^3]
d = lambda alt : d0*np.exp(-9.81*0.0289644*(alt-0)/(8.31446*288.15))
l = 0.1*25.4/1000 #characteristic length [m]
C = 1361 #solar constant [W/m^2]
delta = 1.0 #sky radiation factor, estimated from paper
sigma = 5.670374419e-8 #stefan-boltzman radiation constant [W/(m^2*K^4)]


T_1 = 50+273 #temperature, start of time interval [K]
for i,t_i in enumerate(t):
    #things that change based on velocity/altitude
    v_i = v[i]  #clean up here later
    M_i = M[i] 
    alt_i = alt[i] 

    T_A = Temp[i] # ambient atm temp absolute [K], change with altitude
    T_T =  T_A*(1+0.5*(y - 1)*M_i**2) # stagnation temperature [K]
    K_recovery = 1.0 # thermal conductivity of air []
    T_B = T_A + K_recovery*(T_T - T_A) #boundary layer temperature [K]

    #TODO update the pressure vlaue
    u = CP.PropsSI('VISCOSITY','T',T_1,'P',101325,fluid) #viscosity
    k = CP.PropsSI('CONDUCTIVITY','T',T_1,'P',101325,fluid) # thermal conductivity of air, cool prop
    d_i = d(alt_i) #instant density of air, depends on altitude OpenRocket? []

    h = (0.0017+0.0154*beta**0.5)*(d0**0.8)*k*((v_i*d_i/(u*d0))**0.8)/l**0.2 #eq 4

    B = e*sigma/h #eq B2
    T_p = T_B + B*(delta*T_A+C/sigma) #eq B2
    theta = c*SkinThickness*w /h #eq B2, thermal lag constant [seconds]

    T_m = T_1 # should be avg of T_2 and T_1, need to iterativly solve the correct temp if want more accurate result

    #TODO check if dt/theta < 0.25
    T_2 = (T_p-B*T_1**4)*(1-np.exp(-dt/theta))+T_1*np.exp(-dt/theta)
    T_1 = T_2
    print(T_2-273)

"""
TODO
- check meaning of l again
- check delta again
- get actual value of OR sims
"""
