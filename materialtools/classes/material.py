# -*- coding: utf-8 -*-
"""module containing Material class
Created on Wed Nov  9 11:58:36 2016

@author: dhancock
"""

class Material(dict):
    """Dictionary-based Material object containing MaterialProperty objects

    """
    def __init__(self,
                 materialname=None,
                 verbose = False):
        self.name = materialname
        self["MaterialName"] = materialname
        self["Condition"] = None
        self.source = None
        self["DataSource"] = None
        self["Description"] = None

        return

    def import_materialdata(self,
                            materialdata,
                            materialname,
                            verbose = False):

        """imports a material from a materialtools.MaterialData object

        Parameters
        ----------
            materialdata
                :class:`materialtools.MaterialData`
            
            materialname
                str            
            
            verbose
                bool

        """
        if type(materialname) is int:
            materialname = sorted(materialdata.keys())[materialname]
        try:
            self.update(materialdata[materialname])
        except KeyError:
            print(materialname,'not found in MaterialData object')
        except TypeError:
            if materialdata is None:
                if verbose is True: print('WARNING: material data is empty')
                self.update({})
        except:
            raise

    def get_value(self,
                  propertyname,
                  p2val = None,
                  parameter2 = 'Temperature',
                  parameter1 = 'auto',
                  verbose = False,
                  tolerance = 100,
                  method="linear"):
        """ return a value for a property
        
        Parameters
        ----------
            propertyname (:class:`str`): 
                name of property
                
            p2val (:class:`float`): 
                value of parameter 2 at which you want the value of parameter 1
                
            parameter2 :class:`str`
                name of independent parameter            
            
            parameter1 (:class:`str`):
                name of dependent parameter
                
            verbose (:class:`bool`):
                how much detail do you want back?
                
            tolerance (:class:`float`):
                allows for non-exact values
            method (:class:`str`):
                "linear" regression or "nearest" value
                
        Returns
        -------
            value (:class:`float`)
                if suitable value exists:
                    value of `parameter1` at `parameter2` = `index`
                
                if suitable value doesn't exist:
                    :class:`None`
        
        """
        
        # calculate fom if it doesn't exist already'
        if propertyname == "Thermal Stress FOM":
            assert parameter2 == "Temperature", "index value must be a temperature"
            from materialtools.calculators import thermal_stress_fom
            value = thermal_stress_fom(self,p2val)
            return value

        ## check material has this property
        assert propertyname in self, '{} not found in {}'.format(propertyname,
                                                                 self.name)

        if parameter1 == 'auto': parameter1 = propertyname

        ## check this property has these parameters
        for x in (parameter1,parameter2):
            assert x in self[propertyname], \
                "{} is not in {} for {} [{}]".format(
                    x,propertyname,self.name,self.source)

        ## get list of values for property
        try:
            values = self[propertyname][parameter1]['Values']
        except:
            try: values = self[propertyname]["Values"]
            except:
                raise

        ## if no index specified, return first value
        if p2val is None: return values[0]

        ## get list of values for parameter2
        p2values = self[propertyname][parameter2]['Values']

        ## locate value by index if possible
        if p2val in p2values: 
            return values[p2values.index(p2val)]

        elif method is "nearest":
            ## if precise value for property not found, find nearest
            differences = [abs(x-p2val) for x in p2values]

            bestlocation = differences.index(min(differences))
            bestp2value = p2values[bestlocation]
            bestvalue = values[bestlocation]
            if min(differences) > tolerance:
                if verbose is True:
                    print(
                "No value for {} of {} available within {} of {}".format(
                    parameter1,self.name,tolerance,p2val)+\
                "\nNearest value is {:} at {:}".format(bestvalue,bestp2value))
                return None

            if verbose is True:
                print('WARNING:',parameter1,'not given for',
                      self.name,'at',parameter2,'=',p2val)
                print('\tUsing nearest available value at',
                      parameter2,'=',bestp2value)
        elif method is "linear":
            # get value by linear regression
            xn = p2val

            data = [x for x in zip(p2values,values)]

            sorteddata = sorted(data+[(xn,None)])
            loc = sorteddata.index((xn,None))        

            if p2val < min(p2values):
                if abs(p2val-p2values[0]) < tolerance:
                    print("taking first value")
                    bestvalue = values[0]
                else: 
                    print("no value available within tolerance for {}".format(xn))
                    raise ValueError
            elif p2val > max(p2values):
                if abs(p2val-p2values[-1]) < tolerance:                    
                    print("taking last value")
                    bestvalue = values[-1]
                else: 
                    print("no value available within tolerance for {}".format(xn))
                    raise ValueError
            else:
                try: 
                    x1,y1 = sorteddata[loc-1] 
                    x2,y2 = sorteddata[loc+1] 
                    bestvalue = y2 - (x2-xn)*(y2-y1)/(x2-x1)
                except:
                    print(x1,y1)
                    print(x2,y2)
                    print(xn,bestvalue)
                    raise ValueError
       
            
        else:
            print("no value available")
            #raise ValueError
        #print(bestvalue)
        return bestvalue


    def get_points(self,propertyname,parametername='Temperature',verbose=False):
        """ return all the values for a given :class:`MaterialParameter`
        
        Parameters
        ----------
        propertyname
            :class:`str`
        
        parametername
            :class:`str`
        
        verbose
            :class:`bool`
        """
        try:
            indices = self[propertyname][parametername]['Values']
        except KeyError:
            if verbose is True:
                print('ERROR: Values for {} not found in {}'.format(
                                                    propertyname,self.name))
            raise
        except:
            raise
        return indices

    def get_units(self,propertyname,parametername):
        """ returns the units for a :class:`MaterialParameter` """
        units = self[propertyname][parametername]["Units"][0]
        return units

    def set_value(self,
                  propertyname,
                  parameter1values,
                  parameter2values,
                  parameter1name='Temperature',
                  parameter2name='auto'):
        """ Sets values for a property - requires at least 2 parameters
        """
        if parameter2name == 'auto': parameter2name = propertyname

        newparameter = {propertyname:{
                            parameter1name:{'Values':parameter1values},
                            parameter2name:{'Values':parameter2values},
                            'values':['-'],
                            'format':'string'
                            }
                        }
        self.update(newparameter)
        return

    def plotproperty(self,
                     propertyname,
                     xaxis="Temperature",
                     yaxis="auto",
                     newplot=True,
                     sourcelabels = False,
                     **kwargs):
        """ Plots a material property using :func:`materialtools.display.plotproperty`
        
        .. :automethod::`materialtools.display.plotproperty`
        
        """
        from materialtools.display import plotproperty as plot
        fig = plot(self,propertyname,xaxis,yaxis,newplot,sourcelabels,**kwargs)
        return fig

    def populate_thermal_stress_fom(self,
                                    temperatures=range(0,2000,50),
                                    verbose=False,
                                    ):
        """populates the thermal stress figure of merit"""
	
        from materialtools import MaterialProperty, MaterialParameter
        from materialtools.calculators import thermal_stress_fom
        fomparameter = MaterialProperty(name = "Thermal Stress Figure of Merit",
                                  units = ['-'],
                                  source = "calculated")
        temps = MaterialParameter(name="Temperature",
                                   units = ["C"],
                                   values = [])
        tsfom = MaterialParameter(name="Thermal Stress Figure of Merit",
                                  units = ["-"],
                                  values = [])
        for temp in temperatures:
             try:
                 tsfom["Values"].append(thermal_stress_fom(self,temp,verbose))
                 temps["Values"].append(temp)
             except:
                 if verbose is True: 
                     print("could not calculate tosfm at {}".format(temp))
        assert len(temps["Values"])>0, "Could not calculate any values for thermal stress fom for {}".format(self.name)
        fomparameter["Temperature"] = temps
        fomparameter["Thermal Stress Figure of Merit"] = tsfom
        self["Thermal Stress Figure of Merit"] = fomparameter
        return fomparameter

if __name__ == '__main__':
    import materialtools
    materialdata = materialtools.MaterialData()
    materialdata.import_file('/python/data/materialtools/xml/grouplibrary.xml')
    steel = materialtools.Material(sorted(materialdata.keys())[0], materialdata)
    temps = steel.get_points('Density')
    for temp in temps:
        density = steel.get_value('Density',temp)
        print(temp,':',density)

