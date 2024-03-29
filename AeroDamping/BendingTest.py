import pandas as pd


#exclude motor mass including casing
massProp = pd.read_csv('Python_Mass_Output_Test.csv', header=[0], index_col=[0]) 
massProp.index.name = None
airframe_dryMass_noMotor = sum(massProp['Assembly Mass'])
airframe_dryCG_noMotor = sum(massProp['Assembly Mass']*massProp['CG From Nosecone']/airframe_dryMass_noMotor)

#TODO: the following code should be a function and will be changed during the trajectory
#get instantaneous force and cp location
test_NormalForce = 2000 #N
test_cp = 2.1 #m from nosecone
current_rocket_totalMass = 18.03 #kg
current_rocket_CG = 1.962

current_motorMass = current_rocket_totalMass - airframe_dryMass_noMotor
current_motorCG = ((airframe_dryMass_noMotor + current_motorMass)*current_rocket_CG - airframe_dryCG_noMotor*airframe_dryMass_noMotor)/current_motorMass

total_acceleration = test_NormalForce/(airframe_dryMass_noMotor + current_rocket_totalMass)
rocket_MOI = sum(massProp['Assembly Mass']*(massProp['CG From Nosecone'] - current_rocket_CG)**2) + current_motorMass*(current_motorCG - current_rocket_CG)**2 #refer UVR-STD-03, sum of all airframe components + motor

print(rocket_MOI)

#print(rocket_MOI)
