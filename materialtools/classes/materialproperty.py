# -*- coding: utf-8 -*-
"""
Created on Wed Nov  9 11:58:51 2016

@author: dhancock
"""

class MaterialProperty(dict):
    
    def __init__(self, 
                 name = None,
                 units = [], 
                 values = [], 
                 source = None,
                 comments = None):
        self.name = name
        self['PropertyName']=name
        self["DataSource"] = source
        self["Units"] = units
        self["Values"] = values
        self["Comments"] = comments
        
    class Calculated:
        """
        a material property value in the format:
            self.value = a + b*T + c*T**2... +[x]*T**n
            given coefficients = [a,b,c,...x]
        """
        def __init__(self,
                     name,
                     units,
                     coefficients=[0],
                     temperaturerange = [100,3000],
                     comments = "none"):

            for name,value in locals().items():
                self.__dict__[name] = value

        def value(self,T):
            value = 0
            for i,c in enumerate(self.coefficients):
                value =+ c*T**i
            return value

        def tabulate(outfile):
            pass
    
    def write_csv(self,
                  filename,
                  mode = 'a',
                  verbose = False):
        
        if mode.lower() in ('a','append'): 
            mode = 'a'
                
        elif mode.lower() in ('w','write'): 
            mode = 'w'
            try: 
                with open(filename,'x') as f:
                    pass
    
            except FileExistsError:
                print(filename,'exists.')
                overwritecommand  = input('Overwrite? [Y/n]')
                if overwritecommand.lower() not in ['n','no']:
                    pass
                else: return
            except: raise
        elif mode.lower() in ('o','overwrite'):
            mode = 'w'
        descriptornames = [x for x in self.keys() if type(self[x]) is not dict]
        parameternames = [x for x in self.keys() if type(self[x]) is dict]
        
        with open(filename,mode) as f:
            f.write('{}, {}\n'.format('Name',self['Name']))
            descriptornames.remove('Name')
            for d in descriptornames:
                f.write('{}, {}\n'.format(d,self[d]))
            f.write('\n{:}, '.format('i'))
            
            for p in parameternames:
                f.write('{:}, '.format(p))
            f.write('\n')

            for i,v in enumerate(self[parameternames[0]]['Values']):
                f.write('{:}, '.format(i))
                for p in parameternames:
                    f.write('{:}, '.format(self[p]['Values'][i]))
                f.write('\n')
            f.write('\n'*2)
        if verbose is True: print('Wrote {} to {}'.format(self['Name'],filename))
            
class MaterialParameter(dict):
    def __init__(self, 
                 name = None, 
                 units = [], 
                 values = []):
        self.name = name
        self['ParameterName'] = name
        self['Units']= units
        self['Values']= values
        
        
if __name__ == '__main__':

    from materialtools import MaterialData, MaterialProperty
    materialdata = MaterialData()
    file = "/python/data/materialtools/xml/HHF_materials.xml"
    materialdata.import_file(file)
    
    
    props = [p for p in materialdata['Tungsten'].values() if type(p) is MaterialProperty]
    
    p.write_csv('F:/{}.csv'.format(p['Name']),'a',True)


    