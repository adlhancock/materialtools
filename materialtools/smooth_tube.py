# -*- coding: utf-8 -*-
""" Smooth tube geometry element

Created on Thu Mar  9 16:08:21 2017


"""
import numpy as np
# shape
class smooth_pipe():
    """ Smooth tube geometry element [*]_
    
    
    .. [*] Not entirely sure why this module is in materialtools 

    """
    def __init__(self,**kwargs):
        attributes = ['pipediameter','length','roughness','bendradius','bendangle']
        for arg in kwargs.keys():
            if arg in attributes:
                self.__dict__[arg] = kwargs[arg]
            else: 
                print(arg,"is not a valid argument - ignoring")
        self.f = 1
        self.Vfactor = 1
        self.D_h = self.pipediameter
        self.area = np.pi * (self.pipediameter/2)**2  
        self.volume = self.area * self.length


