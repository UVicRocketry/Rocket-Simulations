import pandas as pd
import numpy as np


#exclude motor mass including casing
#this mass table is met to be importated once and be used and not edited
massProp = pd.read_csv('Python_Mass_Output_Test.csv', header=[0], index_col=[0]) 
massProp.index.name = None
airframe_dryMass_noMotor = sum(massProp['Assembly Mass'])
airframe_dryCG_noMotor = sum(massProp['Assembly Mass']*massProp['CG From Nosecone']/airframe_dryMass_noMotor)

#TODO: the following code should be a function and will be changed during the trajectory
#get instantaneous force and cp location
current_NormalForce = 2000 #N
current_rocket_CP = 2.1 #m from nosecone
current_rocket_totalMass = 18.03 #kg
current_rocket_CG = 1.962

current_motorMass = current_rocket_totalMass - airframe_dryMass_noMotor
current_motorCG = ((airframe_dryMass_noMotor + current_motorMass)*current_rocket_CG - airframe_dryCG_noMotor*airframe_dryMass_noMotor)/current_motorMass

total_acceleration = current_NormalForce/(airframe_dryMass_noMotor + current_rocket_totalMass)

current_rocket_MOI = sum(massProp['Assembly Mass']*(massProp['CG From Nosecone'] - current_rocket_CG)**2) + current_motorMass*(current_motorCG - current_rocket_CG)**2 #refer UVR-STD-03, sum of all airframe components + motor
rocket_angularAccel = current_NormalForce*(current_rocket_CP-current_rocket_CG)/current_rocket_MOI # Moment around rocket CG/MOI

F_inertia = -massProp['Assembly Mass']*((massProp['CG From Nosecone'] - current_rocket_CG)*rocket_angularAccel + total_acceleration) #neg since it is "reaction" and will be pointing opposite direction from normal force

compiled_ForceArray = pd.DataFrame(index=massProp.index) # create a new empty data frame
compiled_ForceArray['Location'] = massProp['CG From Nosecone']
compiled_ForceArray['Forces'] = F_inertia

#TODO: add the new rows for the CG lift (total force), figure out how to do add the shear and moment colum
#for shear -> probably use .loc or something like that
#for moment -> probably use .loc plus and if condition

print(massProp)
print(compiled_ForceArray)


#print(rocket_MOI)
