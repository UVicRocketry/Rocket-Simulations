import numpy as np
from numpy.lib.recfunctions import append_fields
import matplotlib.pyplot as plt

class SI_Constants:
    GRAVITY = 9.81 #m/s^2
    
class Tools:
    """ A class for conversions"""

    def lbm_to_kg(num):
        """ method to convert lbf to N"""
        return num*0.45359237

    def lbf_to_N(num):
        """ method to convert lbf to N"""
        return num*4.44822
        
    def in_to_m(num):
        """method to convert inches to meters"""
        return num*0.0254
    
    def ft_to_m(num):
        """method to convert foot to meters, applicable for units such as ft/sec^2, ft/sec"""
        return num*0.3048
    
def to_Normal(AOA, lift, drag):
    """Convert to nomral force/coeff, AOA take in as degrees"""
    AOA = np.radians(AOA)
    return lift*np.cos(AOA)+drag*np.sin(AOA)

def to_Axial(AOA, lift, drag):
    """Convert to axial force/coeff, AOA take in as degrees"""
    AOA = np.radians(AOA)
    return -lift*np.sin(AOA)+drag*np.cos(AOA)


data = np.genfromtxt('./RASAERO_SIM_23-MAR-2024.csv', dtype=float, delimiter=',', names=True)
 


#convert to SI
data['Weight'] = Tools.lbm_to_kg(data['Weight'])
data['Drag'] = Tools.lbf_to_N(data['Drag'])
data['Lift'] = Tools.lbf_to_N(data['Lift'])
data['CG'] = Tools.in_to_m(data['CG'])
data['CP'] = Tools.in_to_m(data['CP'])
data['Accel'] = Tools.ft_to_m(data['Accel'])
data['AccelV'] = Tools.ft_to_m(data['AccelV'])
data['AccelH'] = Tools.ft_to_m(data['AccelH'])
data['Velocity'] = Tools.ft_to_m(data['Velocity'])
data['VelV'] = Tools.ft_to_m(data['VelV'])
data['VelH'] = Tools.ft_to_m(data['VelH'])
data['Altitude'] = Tools.ft_to_m(data['Altitude'])
data['Distance'] = Tools.ft_to_m(data['Distance'])

#append Normal Force and Axial Force
data = append_fields(data, 'Normal_Force', to_Normal(data['Angle_of_Attack'], data['Lift'], data['Drag']))
data = append_fields(data, 'Axial_Force', to_Axial(data['Angle_of_Attack'], data['Lift'], data['Drag']))


print(data.dtype.names) 

plt.plot(data['Time'], data['CP'], label = 'Lift')
#plt.plot(data['Time'],data['Angle_of_Attack'], label = 'AOA')
plt.legend()
plt.show()

