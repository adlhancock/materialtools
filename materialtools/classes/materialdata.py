# -*- coding: utf-8 -*-
"""
Created on Wed Nov  9 11:57:46 2016

@author: dhancock
"""

import sys
import os


import tkinter as tk
from tkinter import filedialog


class MaterialData(dict):
    """ Dictionary based object containing Material objects"""

    def __init__(self,
                 source=None,
                 verbose=False
                 ):
        self.source = source
        self.filename = []
        self.materialnames = []
        
        if source is not None:
            #print("##source is not none ##")
            if os.path.isdir(source) is True:
                self.import_directory(source,
                                      verbose=verbose)
            elif os.path.isfile(source) is True:
                self.import_file(source,
                                 verbose=verbose)
            else:
                print("\n## could not import from {} ##\n".format(source))
            
            
            #self.import_directory
        return
    
    def import_material(self,
                        materialdata,
                        materialname,
                        newname = 'auto',
                        testing=False,
                        verbose=False,
                        ):
        """ imports a single material from a materialdata object"""
        
        if newname is 'auto': newname = materialname
            
        if materialname in materialdata:
            self[newname] = materialdata[materialname]
        else:
            print("{} not found in materialdata object".format(materialname))
            options = [x for x in materialdata if materialname in x]
            if len(options) > 0:
                print("Did you mean one of the following?")
                [print('\t',x) for x in options]

    
    def import_file(self,
                    filename=None,
                    materialname = 'auto',
                    testing=False,
                    verbose=False):
        """ imports a single file """
        
        from materialtools import Material #, MaterialParameter, MaterialProperty  

        if filename is not None: openfile = False        
        
        if testing is True:
            filename = '../sampledata/testdata.xml'
            openfile = True
        
        try:
            with open(filename,'r') as f:
                f.close()
                pass
        
        except FileNotFoundError:
            print('{} not found'.format(filename))
            openfile = True
            
        except TypeError:
            print('No file selected.')
            openfile = True
            
        except:
            raise
    
        if openfile is True:
            print('Opening file selection dialogue...')
            root = tk.Tk()
            root.withdraw()
            filename = filedialog.askopenfilename(
                        #initialdir='./',
                        title = "Select material property file",
                        #initialdir = '/python/data/materialtools',
                        filetypes = [('text, csv, or matml '+
                            'material property file','*.txt;*.xml;*.csv;*.xlsx')])

        if filename.endswith('.txt'):
            from materialtools.read import textfile as read
        elif filename.endswith('.csv'):
            from materialtools.read import csv as read
        elif filename.endswith('.xml'):
            from materialtools.read import matml as read
        elif filename.endswith('.xlsx'):
            from materialtools.read import xlsx as read
        else:
            if filename in (None,''):
                print('No file name given')
            else:
                print('file extension not recognised')
                print(filename)
        try:
            materialdata = read(filename=filename,
                                materialname=materialname)
            self.filename.append(filename)
            for m in materialdata:
                if type(materialdata[m]) is Material:
                    if m in self.materialnames: 
                        if verbose is True:
                            response = input("{} exists. Append conditions to material names? [Y]".format(m))
                        else:
                            response = 'Yes'
                            print("\n{} exists. Appending conditions to material names...".format(m))                        
                        if response not in ['n','N','no']:
                            newname = m + ' ({})'.format(materialdata[m]["Condition"])
                            if newname in self: 
                                newname += " ({})".format(materialdata[m]["DataSource"])
                            print("...Creating {}".format(newname))
                            if m in self:
                                movedname = '{} ({})'.format(m,self[m]["Condition"])
                                print("...Moving {} to {}".format(m,movedname))
                                self[movedname] = self[m]
                                print("...Deleting old {}".format(m))
                                del self[m]
                            print("\n")
                        else:
                            print("WARNING: overwriting properties for",m)
                            newname = m
                        self[newname] = materialdata[m]
                            
                    else:
                        self[m] = materialdata[m]
        except:
            print('[materialdata.py] No material properties imported')
            raise
        self.materialnames = [x["MaterialName"] for x in self.values()
            if type(x) is Material]
        try:
            self.sources = [x["DataSource"] for x in self.values()
                if type(x) is Material]
        except: pass
        if verbose is True: 
            print('Materials in database:')
            [print('\t',name) for name in self.materialnames]
        return materialdata
        
    def import_directory(self, 
                         path = None, 
                         filetype = 'xlsx',
                         verbose = False):
        
        """ imports a directory """
     
        
        if path is None:
            print('Opening folder selection dialogue...')
            root = tk.Tk()
            root.withdraw()
            path = filedialog.askdirectory(
                title = "Select directory containing material data files")
        
        if path.endswith('/') is False:
            path += '/'
        files = [y for y in [x for x in os.listdir(path) 
                                if x.endswith('.'+filetype)] 
                                    if '~' not in y]
        
        materialdata = MaterialData()
        for f in files:
            if verbose is True: 
                print("Importing {}".format(f))
            self.import_file(path+f,verbose=verbose)
        materialdata = self
        return materialdata
        
        
    def export_file(self,
                    filename,
                    verbose=False,
                    **kwargs):
        if filename.endswith('.txt'):
            from materialtools.write import textfile as write
        elif filename.endswith('.csv'):
            from materialtools.write import csv as write
        elif filename.endswith('.json'):
            from materialtools.write import json as write
        elif filename.endswith('/'):
            print("Assuming folder means multiple xlsx files")
            from materialtools.write import xlsx as write
        elif filename.endswith('.xlsx'):
            print("Using target file name as directory name.")
            print("Creating individual material '.xlsx'",
                  "files in {}".format(filename))
            from materialtools.write import xlsx as write
        elif filename.endswith('.xml'):
            from materialtools.write import matml as write
        else:
            if filename is None:
                print('No file name given')
            else:
                print('file extension not recognised',filename[
                                                        filename.rfind('.'):])
            print('No material property imported')
            return
        output = write(self,filename,verbose,**kwargs)
        return output
        
    def list_contents(self,materials='all'):
        """ list contents of materialdata
        
        note:
            ugly
        """
        from materialtools.write import list_contents as lc
        if materials == 'all': materialnames = [m for m in self]
        else: materialnames = materials
        for material in materialnames:
            lc(self[material])
            
    def generate_ids(self):
        
        """ generate unique property and parameter ids 
        
        """
        from materialtools import Material, MaterialParameter, MaterialProperty
        
        propertynames, parameternames, pau, pru = [],[],[],[]
        ids = {}
        materials = [m for m in self.values() 
                        if type(m) is Material]
        # get full lists
        for material in materials:
            properties = [p for p in material.values() 
                            if type(p) is MaterialProperty]
            for property in properties:
                propertynames.append(property["Name"])
                parameters = [p for p in property.values() 
                                if type(p) is MaterialParameter]
                for parameter in parameters:
                    parameternames.append(parameter["Name"])
                
        # dedupe lists
        [pau.append(x) for x in parameternames if x not in pau]
        [pru.append(x) for x in propertynames if x not in pru]
        
        # generate numbers
        for i,p in enumerate(pau):
            ids[p]="pa{}".format(i)
        for i,p in enumerate(pru):
            ids[p]="pr{}".format(i)
            
        # save to materialdata object
        self.ids = ids

        return ids
        
        
        
if __name__ == '__main__':
    import materialtools
    
    materialdata = materialtools.MaterialData()
    materialdata.import_file(testing=True)
    materialdata.export_file('/temp/materialdata.json',verbose=True)
    #materialdata.list_contents()