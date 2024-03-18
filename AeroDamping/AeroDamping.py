import numpy as np

class AeroProperties: 
    #this is a class to store aero preperties, this should be changed to something more object based in the future

    def __init__(self, name):
        self.name = name #component name
        self.MACH = np.empty(0) #1D array to store MACH numbers
        self.AOA = np.empty(0) #1D arrry to store angle of attack 
        self.x_cp = np.empty(0) #table to store location of cetner of pressure in meters
        self.C_n_a = np.empty(0) #table to store location of coefficient of normal force



nosecone = AeroProperties("nosecone")


print(nosecone.name)
print(nosecone.MACH)

nosecone.MACH = np.array([[0.1,0.2],[0.5,0.6]])
print(nosecone.MACH)

nosecone.MACH = np.vstack([nosecone.MACH,[2,2,2,2]])
print(nosecone.MACH)
