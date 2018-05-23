# -*- coding: utf-8 -*-
""" convert

Created on Wed Mar  8 11:46:42 2017

@author: dhancock
"""

import materialtools

def convert_file(sourcefile,targetfile,verbose = False):
    """ Converts one material property file to another [#]_
    
    
    arguments:
        sourcefile: 
            string path
        
        targetfile: 
            string path
        
        verbose: 
            boolean prints which files are imported and 
            exported including number of materials
    
    returns:
        materialtools.MaterialData object
        
    .. [#] This is unchecked, as it hasn't been used for a while 
    """
    data = materialtools.MaterialData()
    data.import_file(sourcefile)
    data.export_file(targetfile)
    if verbose is True:
        print("*"*80)
        print("convert_File:","imported {} materials from {}".format(len(data),sourcefile))
        print("convert_File:","exported to {}".format(targetfile))
        print("*"*80)
    return data

"""    
def convert_directory(sourcedir,targetdir,fileextension):
    print("NOT READY YET")
    pass    
"""


if __name__ == "__main__":
    data = []
    for filetype in ["xlsx",
                     "json",
                     "csv"]:
        data.append(
            convert_file("../sampledata/HHF_materials.xml", 
                         "/convert_test."+filetype,
                         True))
