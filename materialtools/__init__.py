# -*- coding: utf-8 -*-
"""materialtools
A set of tools to handle material data

Created on Tue Jan 12 15:02:25 2016

.. moduleauthor:: adlhancock
"""


__all__ = ['MaterialData',
           'Material',
           'MaterialProperty',
           'MaterialParameter',
           'MatMLData',
           'calculators',
           'display',
           'convert',
           'write_matml',
           'materialtesting',
           ]

from .classes import (MaterialData,
        		     Material,
        		     MaterialProperty,
        		     MaterialParameter,
        		     MatMLData
        		     )

#from . import calculators, display, convert

# from .display import (plotproperty,
#                       printproperty
#                       )

#import .calculators

