# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 15:06:28 2016

@author: dhancock
tools for extracting material property data from a MatML object
requires:
    untangle
"""
#from time import sleep

class MatMLData(dict):
    '''
    MatML data object - contains methods for importing data from suitably
    formatted xml files and exporting as nested dictionaries.
    '''
    from materialtools.read import matml as import_file
    #from collections import OrderedDict
    
    def __init__(self):
        '''
        generates an empty matml object
        '''
        self.filename = 'no file imported yet'

        
    def getunits(self, verbose = False):
        metadata = self.matml['Metadata']
        units = {}
        for ps in ('PropertyDetails','ParameterDetails'):
            for p in metadata[ps]:
                if 'Units' in p:
                    u = []
                    punits = p['Units']['Unit']
                    if type(punits) is not list: punits = [punits]
                    #print(punits)
                    for term in punits:
                        #print('\tterm = ',term['Name'])
                        try: u.append(term['Name']+'^'+term['@power'])
                        except : u.append(term['Name'])
                    units[p['@id']] = '.'.join(u)
                    if verbose is True: print('{:35}: {}'.format(p['Name'],u))
                elif 'Unitless' in p and 'ParameterDetails' in ps: 
                    units[p['@id']] = 'Unitless'
                    if verbose is True: print('{:35}: {}'.format(
                        p['Name'],units[p['@id']]))
                else:
                    units[p['@id']] = '-'
                    if verbose is True: print(
                        '{:35}: units not in in metadata ({})'.format(
                            p['Name'],p['@id']))
        #print(units)
        self.units = units
        
        return units
    def getids(self):
        ids = {}                                                                # get ids from metadata
        metadata = self.matml['Metadata']
        for p in ('PropertyDetails','ParameterDetails'):
            for item in metadata[p]:
                ids.update({item['@id']:item['Name']})
        self.ids = ids
        return ids
        
    def getmaterials(self,verbose = False):
        """ Extracts material names and xml materials """
        from materialtools import Material
        materials = {}

        xmlmaterials = self.matml['Material']
        if type(xmlmaterials) is not list: xmlmaterials = [xmlmaterials]
        self.xmlmaterials = xmlmaterials

        for xmlmaterial in xmlmaterials:
            materialname = xmlmaterial['BulkDetails']['Name']              # get the names
            if materialname not in self.keys():
                material = Material(materialname)
                material.xmlmaterial = xmlmaterial
                try: 
                    description = xmlmaterial['BulkDetails']['Description']
                except: 
                    print(material.name,'has no description') 
                    description = '-'
                material['Description'] = description
                properties = self.getproperties(material,verbose)
                material.update(properties)                
                
            materials[materialname]=material
        
        if verbose is True: [print(x,type(materials[x])) for x in materials]
        
        return materials
    
    def getproperties(self, 
                      material, 
                      verbose=False):

        from materialtools import MaterialProperty
        
        assert 'xmlmaterial' in material.__dir__(), "material does not have xml data attached"
        xmlproperties = material.xmlmaterial['BulkDetails']['PropertyData']
        
        materialname = material['MaterialName']
        materialproperties = {}
        for xmlproperty in xmlproperties:

            # get property name from id
            propertyid = xmlproperty['@property']
            propertyname = self.ids[propertyid]
            
            if propertyname not in materialproperties:
                # create property object
                materialproperty = MaterialProperty(propertyname)
                if verbose is True: print('[getproperties] ',
                                          material.name,
                                          '::',propertyname)
                # attach xml data for reference
                materialproperty.xmlproperty = xmlproperty
                            
                # get top level values if exist
                try:
                    #propertyformat  = materialproperty['Data']['@format']
                    propertyvalues  = [float(x) for x 
                        in xmlproperty['Data']['#text'].split(',') 
                        if x is not '-']
                    if propertyvalues == []: propertyvalues = ['-']
                    materialproperty['Values'] = propertyvalues
                    #materialproperty['Format'] = propertyformat
                except: raise
                
                # get units if exist
                if propertyid in self.units: 
                    units = [self.units[propertyid]]
                else: 
                    units = ['-']
                materialproperty['Units'] = units
    
                # get qualifiers
                try:
                    qualifiers = xmlproperty['Qualifier']
                    if type(qualifiers) is not list:
                        qualifiers = [qualifiers]
                    qdict = {}
                    for q in qualifiers:
                        qdict[q['@name']]=q['#text'].split(',')
                    materialproperty.update(qdict)
                    #print(qdict)                                                #TEMP
    
                except: 
                    if verbose is True: 
                        print('no qualifiers imported for property:',
                              propertyname)
                    pass            


                # get parameters
                try: 
                    materialparameters = self.getparameters(materialproperty, 
                                                            verbose)
                    materialproperty.update(materialparameters)  
                except: 
                    print('[matml.py] could not get parameters for'+
                                ' {} {}'.format(materialname,propertyname))
                    raise
                
                # add property to properties
                materialproperties[propertyname] = materialproperty


        # material.xmlproperties = xmlproperties
                
        return materialproperties
        
    def getparameters(self,
                      materialproperty,
                      verbose = False):
        from materialtools import MaterialParameter
        try: xmlparameters = materialproperty.xmlproperty['ParameterValue']
        except: 
            if verbose is True: print(materialproperty.name,'has no parameters') 
            return {}
        
        materialparameters = {}
        
        if type(xmlparameters) is not list: xmlparameters = [xmlparameters]

        if verbose is True: print(materialproperty.name,'\n','='*80)

        for xmlparameter in xmlparameters:
            materialparameter = MaterialParameter() # create empty parameter
            
            # get parameter name from id
            parameterid = xmlparameter['@parameter']
            parametername = self.ids[parameterid]
            
            materialparameter['Name'] = parametername
            if verbose is True: print(materialproperty.name,'::',parametername)
            
            # get units
            try: 
                materialparameter['Units'] = self.units[parameterid]
                if type(materialparameter['Units']) is str:
                    materialparameter['Units'] = [materialparameter['Units']]
            except: materialparameter['Units'] = ['-']
            
            # get data
            try:
                parametervalues = [float(x) for x 
                    in xmlparameter['Data'].split(',')
                    if x is not '-']            
            except:
                parametervalues = ['-']
            
            materialparameter['Values'] = parametervalues
            if verbose is True: print(parameterid,parametername,parametervalues)
            
            # get qualifiers
            try:
                qualifiers = xmlparameter['Qualifier']
                if type(qualifiers) is not list:
                    qualifiers = [qualifiers]
                qdict = {}
                for q in qualifiers:                               
                    qdict[q['@name']]=q['#text'].split(',')
                materialparameter.update(qdict)
            except: 
                if verbose is True: 
                    print('No qualifiers imported for parameter',
                          parametername); pass
            
            # add parameter to materialparameters
            materialparameters[parametername] = materialparameter
        # add propertyvalues to parametervalues if they exist
        if materialproperty.name not in materialparameters:
            materialparameters[materialproperty["PropertyName"]] = {}
            items = [i for i in materialproperty 
                if type(materialproperty[i]) is list]
            items.append("PropertyName")
            for item in items:
                materialparameters[
                    materialproperty["PropertyName"]][item] = materialproperty[item]
        #except: print("could not assign values to property",materialproperty["Name"]);pass   
        return materialparameters
        
    def getdata(self, verbose = False):
        '''
        Returns a nested dictionary of material property data
        given a similar MatML object extracted using xmltodict
        (See materialtools.read.matml)
        '''
        #from materialtools import MaterialData

        self.getunits()                                                         # get units from metadata
        self.getids()                                                           # get ids
        materials = self.getmaterials()
        self.update(materials)
        if verbose is True: print('\n{}\n'.format(type(self)))

        return


if __name__ == '__main__':
    from materialtools import MaterialData
    # print('Running MatML as script:\n\n')
    materialdata = MaterialData()
    #materialdata = materialdata.import_file('/python/materialtools/sampledata/testdata.xml')
    materialdata.import_file("/python/data/materialtools/xml/grouplibrary.xml",
                             verbose=False)
    #print(materialdata.filename)
    #matml = materialdataobj.matml
    #ids = matmlobj.getids()
    #names = matmlobj.getmaterialnames()
    #units = matmlobj.getunits('no')
    #materialdata.writejson()
