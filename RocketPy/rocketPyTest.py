from rocketpy import Environment, SolidMotor, Rocket, Flight

import os

absolute_path = os.path.dirname(__file__)

#TODO: Add a sim summary report generator and store graph/document (DO IT IN JPY Notebook)

#define sim enviroment

env = Environment(latitude=32.990254, longitude=-106.974998, elevation=1400) #TODO: Update to LC
env.set_date((2023,12,15,12)) #TODO:must be within a range, add the get time thing
env.set_atmospheric_model(type="Forecast", file="GFS")

#env.info() #uncomment to print


Pro75M1670 = SolidMotor(
    thrust_source=os.path.join(absolute_path,"motor/Cesaroni_M1670.eng"),
    dry_mass=1.815,
    dry_inertia=(0.125, 0.125, 0.002),
    center_of_dry_mass_position=0.317,
    grains_center_of_mass_position=0.397,
    burn_time=3.9,
    grain_number=5,
    grain_separation=0.005,
    grain_density=1815,
    grain_outer_radius=0.033,
    grain_initial_inner_radius=0.015,
    grain_initial_height=0.12,
    nozzle_radius=0.033,
    throat_radius=0.011,
    interpolation_method="linear",
    nozzle_position=0,
    coordinate_system_orientation="nozzle_to_combustion_chamber",
)

#Pro75M1670.info() uncomment to show 

#Rocket info
anduril1 = Rocket(
    radius = 5*25.4/1000/2, # airframe outter radius [m]
    mass=14.426, #rocket mass WITHOUT MOTOR [kg]
    inertia=(6.321,6.321,0.034), #(I11,I22,I33) => I11, I22 inertia around perpendicular, I33 around the rocket center axis
    power_off_drag=os.path.join(absolute_path,"data/sampleDrag.csv"), # can get one from RASAero see https://docs.rocketpy.org/en/latest/user/rocket.html#drag-curves
    power_on_drag=os.path.join(absolute_path,"data/sampleDrag.csv"), # can get one from RASAero see https://docs.rocketpy.org/en/latest/user/rocket.html#drag-curves
    center_of_mass_without_motor=0, #TODO: change ref frame
    coordinate_system_orientation="tail_to_nose", #TODO: change ref frame
)

#adding motor
anduril1.add_motor(Pro75M1670, position=-1.255) #check funtion for defintion of motor

#Can add rail buttons if needed

#adding aero surfaces
nose_cone = anduril1.add_nose( # will need to change the rocketpy.rocket.aero_surface module to add custom geometry
    length=0.55829, kind="von karman", position=1.278 #TODO: seems like limited nosecone profile, check how to do custom one
)

fin_set = anduril1.add_trapezoidal_fins(
    n=4,
    root_chord=0.120,
    tip_chord=0.060,
    span=0.110,
    position = -1.04965,
    cant_angle=0.5,
    #airfoil= #can import custom data if needed, default to flat plat 
)

tail = anduril1.add_tail(
    top_radius=0.0635, 
    bottom_radius=0.0435, 
    length=0.060, 
    position=-1.194656
)

#add parachutes
main = anduril1.add_parachute(
    name="main",
    cd_s=10.0,
    trigger=800,      # ejection altitude in meters
    sampling_rate=105,
    lag=1.5,
    noise=(0, 8.3, 0.5),
)

drogue = anduril1.add_parachute(
    name="drogue",
    cd_s=1.0,
    trigger="apogee",  # ejection at apogee
    sampling_rate=105,
    lag=1.5,
    noise=(0, 8.3, 0.5),
)

#anduril1.plots.static_margin()
#anduril1.draw()

#run sim
test_flight = Flight(
    rocket=anduril1, environment=env, rail_length=5.2, inclination=85, heading=0
    )


#plots
#test_flight.plots.trajectory_3d()
#test_flight.plots.stability_and_control_data()

test_flight.all_info()

"""
Good to have => report generation
Layout:
[Title] = XXX Flight Simulation
[Date & Time]

[TOC]

[Key Summary of Simulation data] #think about report stuff

[Rocket Information]
{Rocket plot in rocketpy}
- Motor specs
- airframe specs 
- Nosecone specs
- fin specs
- tail specs
- parachite specs

[Plots]
- Trajectory
- Stability #https://docs.rocketpy.org/en/latest/user/first_simulation.html#stability-margin-and-frequency-response

Advance stuff
- angular velocity

- Aero forces #https://docs.rocketpy.org/en/latest/user/first_simulation.html#aerodynamic-forces-and-moments



"""