# -*- coding: utf-8 -*-
"""A set of tools for calculating various material values

Includes a couple of figures of merit as well as tools for checking and updating units

.. :author:: dhancock

"""

def thermal_stress_fom(material,temperature=20,verbose = False):
    r"""Calculates the Thermal Stress Figure of Merit (**M**) for a :class:`Material`
    using the equation: 


    
    .. math::
       
       M = \frac{\sigma_{UTS} k_{th}(1-\upsilon)}{\alpha_{th} E}
    
    
    :math:`\sigma_{UTS}=`   Ultimate Tensile Stress
    
    :math:`k_th=`           Thermal Conductivity
    
    :math:`\upsilon=`       Poisson's Ratio
    
    :math:`\alpha_{th}=`    Coefficient of Thermal Expansion
    
    :math:`E=`              Young's Modulus
    
    Parameters
    ----------
        material: 
            :class:`materialtools.Material`
        temperature:
            :class:`int`
        verbose:
           :class:`bool`
            
    Returns
    -------
        M: 
            :class:`float`
    
    """
    
    
    ## this is the list of properties needed to calculate the fom
    properties = (["Ultimate Tensile Strength"]*2,
                  ["Thermal Conductivity"]*2,
                  ["Coefficient of Thermal Expansion"]*2,
                  ["Elasticity","Poisson's Ratio"],
                  ["Elasticity","Young's Modulus"])
    
    ## check that the material has the properties needed
    for p in properties:
        assert p[0] in material, "{} not found in {} [{}]".format(p[0], 
                                                             material.name,
                                                             material.source)
        ## check each property has the parameters needed        
        assert p[1] in material[p[0]], \
            "{} not found in {} for {} [{}]".format(p[1],
                                                    p[0], 
                                                    material.name, 
                                                    material.source)
    ## try to calculate the variables
    variables = [temperature]
    for p in properties:
        try: variables.append(
            material.get_value(p[0],
                               temperature,
                               'Temperature',
                               p[1],
                               #verbose
                               ))
        except: 
            if verbose is True: print("Could not get {} at {}".format(
                                                            p[1],temperature))
            raise
            return None

    ## extract the variables
    t,uts,k_th,a_th,nu,E = variables
    if None in variables:
        #return 0
        pass
    ## calculate M
    M = (uts * k_th * (1 - nu)) / (a_th * E)
    return M
    
    
def thermal_missmatch_stress(material1, 
                             material2,
                             thickness_1,
                             thickness_2,
                             heat_flux,
                             htc,
                             T_coolant,
                             T_ref = 293):
    r""" Calculates Thermal mismatch stress
    
    Parameters
    ----------
        material1, material2:
            :class:`materialtools.Material` objects for the armour and
            substructure respectively
        
        thickness1, thickness2:
            layer thickness in :math:`m` of armour and substructure
        
        heat_flux:
            incident heat flux in :math:`W.m^{-2}`
        
        htc:
            convective heat transfer coefficient in :math:`W.m^{-2}.K^{-1}`
        
        T_coolant:
            bulk temperature of the coolant in :math:`K`
        
        T_ref:
            reference temperature in :math:`K`
    
    Returns
    -------
        mismatch_stress:
            thermal mismatch stress in :math:`Pa`    
    
    Calculation
    -----------
    
    .. math::
        
        \sigma_{mm} & = \frac{\alpha_{2}(T_{2,mean}-T_{ref}) 
							- \alpha_{1}(T_{1,mean} - T_{ref})}
						{\frac{(1-\upsilon_{2})t_{1}}{t_{2}E_{2}} 
							+ \frac{1-\upsilon_{1}}{E_{1}}}\\
      T_{1,mean} & = T_{coolant} + \frac{q}{h} + \frac{q.t_1}{2.k_1}\\
      T_{2,mean} & = T_{coolant} + \frac{q}{h} + \frac{q.t_1}{k_1} + \frac{q.t_2}{2.k_2}\\

    where 
    
    :math:`\phi_{mm}` is the mismatch stress,
    
    :math:`T_{ref}` is the reference starting temperature of the component,
    
    :math:`T_{coolant}` is the bulk coolant temperature,
    
    :math:`q` is the incident heat flux,
    
    :math:`t_1 and t_2` are the thicknesses of structure and armour respectively,

    :math:`T_{1,mean}` and :math:`T_{2,mean}` 
    are the mean temperatures in each material,

    :math:`\nu_1` and :math:`\nu_2` are Poisson's ratios,

    :math:`\alpha_1` and :math:`\alpha_2` are thermal expansion coefficients,

    and 
    :math:`E_1` and :math:`E_2` are Young's moduli

    """    
    q = heat_flux
    h = htc

    T1,T2 = T_coolant, T_coolant
    method = "linear"
    tolerance = 200
    for iteration in range(3):
        a1, a2  = (material.get_value('Coefficient of Thermal Expansion',
                                      T,
                                      method=method,
                                      tolerance=tolerance) 
                            for material,T in [(material1, T1), (material2,T2)])
    
        nu1,nu2 = (material.get_value('Elasticity',
                                      T,
                                      'Temperature',
                                      "Poisson's Ratio",
                                      method=method,
                                      tolerance=tolerance) 
                            for material,T in [(material1, T1), (material2,T2)])
        E1, E2  = (material.get_value('Elasticity',
                                      T,
                                      'Temperature',
                                      "Young's Modulus",
                                      method=method,
                                      tolerance=tolerance) 
                            for material,T in [(material1, T1), (material2,T2)])
    
        k1, k2 =  (material.get_value('Thermal Conductivity',
                                      T,
                                      method=method,
                                      tolerance=tolerance) 
                            for material,T in [(material1, T1), (material2,T2)])
    
        t1,t2   = thickness_1, thickness_2
        
        T1mean = T_coolant + q/h + (q*t1)/(2*k1)
        T2mean = T_coolant + q/h + (q*t1)/k1 + (q*t2)/(2*k2)

        T1,T2 = T1mean,T2mean
    
    mismatch_stress = (a2*(T2mean-T_ref) - a1*(T1mean-T_ref)) / \
                            (((1-nu2)*t1)/(t2*E2) + (1-nu1)/E1)
    #print("T_{:},mean = {:3.0f}, T_{:},mean = {:3.0f}".format(material1.name,T1mean-273,material2.name,T2mean-273))    
    
    return mismatch_stress


def check_units(parameters):
    """ Checks that units are consistent 
    """
    from materialtools import MaterialParameter
    assert all(type(p)==MaterialParameter for p in parameters), \
                            "list must contain only MaterialParameter objects"

    allunits = []
    [[allunits.append(unit) for unit in p["Units"]] for p in parameters]
    #print(allunits)
    unitsmatch = allunits[1:] == allunits[:-1]
    return unitsmatch

def fix_units(parameter):
    """ TO DO - will include some conversion factors
    """
    
    return

if __name__ == '__main__':
    import materialtools
    from matplotlib import pyplot as plt
    import numpy as np

    materialdata = materialtools.MaterialData()
    out = materialdata.import_file('/python/data/materialtools/xml/HHF_materials.xml')
    for m in materialdata:
            material = materialdata[m]
            material.set_value('Ultimate Tensile Strength',[20,500,1000],[500e6,200e6,100e6])
            Ms = []
            temps = np.linspace(0,500,100)
            for temp in temps:
                try:
                    Ms.append(thermal_stress_fom(material,
                                           temperature = temp))
                except:
                    Ms.append(0)
            plt.plot(temps,Ms,'-',label=material.name)
    plt.xlabel('temperature')
    plt.ylabel('M')
    plt.legend(fontsize='x-small')

    '''
    data.sort(key=lambda x: x[1],reverse=True)
    print('_'*80)
    print('{:^40}:{:^20}'.format('material','M'))
    print('='*80)
    a = [print('{:^40}:{:^20.2e}'.format(x[0],x[1])) for x in data]
    '''