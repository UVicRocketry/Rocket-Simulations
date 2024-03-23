import numpy as np

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
    
data = np.genfromtxt('./RASAERO_SIM_23-MAR-2024.csv', dtype=float, delimiter=',', names=True)
 

#print(data.dtype.names) 
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





print()
