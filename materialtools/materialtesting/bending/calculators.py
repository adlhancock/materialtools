#! /usr/bin/python3

''' materialtools.materialtesting.bending.calculators
set of calculators for three and four point bending tests
'''

def set_sample_dimensions(depth=2.5e-3,width=2e-3,length=30e-3):
    """ set the four point bending sample dimensions
    
    inputs:
        depth:
            default 2.5e-3 m
        
        width:
            default 2e-3 m
        
        length:
            default 30e-3 m
    
    """
    dims = {'depth':depth,'width':width,'length':length}
    for dim in ('depth', 'width', 'length'):
        if dims[dim] is None:
            dims[dim] = float(input(dim+':'))
    return dims

def set_support_dimensions(loading_span=10e-3,support_span=20e-3):
    """set the jig dimensions
    
    inputs:
        loading_span:
            default 10mm
        support_span:
            default 20mm
    
    """
    
    
    dims = {'loading_span':loading_span, 'support_span':support_span}
    dims['spanratio'] = loading_span / support_span
    return dims


def stress_flexural(load,
                    sample_dimensions,
                    support_dimensions,
                    ):
    r""" Flexural stress in a three or four point bending test
    
    inputs:
        - load
        - sample dimensions
        - support dimensions
        
    returns:
        - flexural stress
        
    calculation:
        [from ASTM D790]
        
    .. math:: 
        
            \sigma_{f} = A \frac{F.L}{b.d^{2}}
            
            A = \begin{cases} 
                    3/2 & \text{when the loading span is 1/2 of the support span}\\
                    3/4 & \text{when the loading span is 1/3 of the support span}\\
                    1   & \text{for a three point bending test}
                \end{cases}
    """

    ls = support_dimensions['loading_span']
    ss = support_dimensions['support_span']
    F = load
    L = ss
    b = sample_dimensions['width']
    d = sample_dimensions['depth']
    
    if ls == 0:
        A = 3/2
    elif ls/ss == 0.5: 
        A = 3/4
    elif ls/ss == 1/3:
        A = 1
    else:
        raise ValueError('Incorrect support dimensions')
        
    return A*F*L/(b*d**2)
   

def displacement_maximum(load,
                         E,
                         sample_dimensions, 
                         support_dimensions,
                         ):
    r"""Calculate maximum displacement of a bending sample
    
    Input:
        - sample_dimensions: sample dimensions
        - support_dimensions support dimensions
        - load
        - E: Young's modulus
        
        
    Returns:
        - maximum displacement
        
    Calculation:
        [From Roark]
        
    .. math:: 
        y_A = -W\frac{l-a}{6E.I}(2l^2 + 2a.l - a^2)
    """    
    
    W = load/2
    l = support_dimensions['support_span']/2
    a = support_dimensions['loading_span']/2
    E = E
    I = (sample_dimensions['depth']**3) * sample_dimensions['width'] / 12
    
    y_A = -W*(l-a) / (6*E*I) * (2*l**2 + 2*a*l - a**2)
        
    return y_A

def modulus_flexural(force_displacement_gradient,
                     sample_dimensions,
                     support_dimensions):
    r""" Flexural strength for a four point bending test
    
    Input:
        - force displacement gradient
        - sample dimensions
        - support dimensions
    
    Calculation:
        [from ASTM D790]
        
    .. math::
        F_f = A \frac{S^3 m}{b h^3}

        A = \begin{cases}
                0.17, & \text{if span ratio} = 1/2\\
                0.21, & \text{if span ratio} = 1/3\\
                0.25, & \text{for three point bending}
            \end{cases}
            
    m = force displacement gradient,
    S = support span,
    b = sample width,
    h = sample height,
    """
    S = support_dimensions['support_span']
    m = force_displacement_gradient
    b = sample_dimensions['width']
    h = sample_dimensions['depth']
    if support_dimensions['spanratio'] == 0.5:    A = 0.17
    elif support_dimensions['spanratio'] == 1/3:  A = 0.21
    elif support_dimensions['load_span'] == 0:    A = 0.25
    else: raise ValueError(
        'span ratio ({:}) not supported'.format(support_dimensions['spanratio']))
    
    F_s = A*S**3*m/(b*h**3)

    return abs(F_s)

if __name__ == '__main__':

    pass