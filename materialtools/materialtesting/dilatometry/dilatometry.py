# -*- coding: utf-8 -*-
"""materialtools.materialtesting.dilatometry
imports and plots data from Swansea Dilatometry
todo: export to materialtools xlsx format
Created on 2017-11-28

@author: dhancock
"""

from matplotlib import pyplot as plt
import tkinter as tk
from tkinter import filedialog
import os

class DILdata(dict):
    """
    .. class: DILdata(dict)    
    
    dilatometry data object
    
    methods
    ======
    .. function:: import_data(file,path)
    
        creates a dictionary of recorded variables
        from a csv file from Swansea DIL testing
    
    .. function:: plot_data(xparm,yparm,figname="auto",savefig=False,formatfn=None)

        plots the data
        
    """
    def __init__(self,
                 path=None,
                 file=None,
                 date='Unknown',
                 material='Unknown',
                 sampleref = 'unknown',
                 **kwargs):
        self["Test Date"] = date
        self["Material"] = material
        self["Sample Reference"] = sampleref
        if None not in (path,file):
            self.import_data(path,file)
        for arg in kwargs.keys():
            #print(arg)
            self[arg] = kwargs[arg]
        
    
    def import_data(self,path=None,file=None):
        """
        creates a dictionary of recorded variables
        from a csv or text file from Swansea
        strips unneccessary whitespace from variable names
                
        args
        ====
        path (str)
            location of data file
            
        file (str)
            filename of file to be imported
            
        """
        
        ## choose file if none requested
        if None in (path,file):
            root = tk.Tk()
            root.withdraw()
            filename = filedialog.askopenfilename(
                            title = "select data file",
                            filetypes = [("dilatometry data file",
                                          "*.txt")])
            path = os.path.dirname(filename)
            if not path.endswith('/'):
                path += '/'
            file = os.path.basename(filename)
            
        ## read file
        if not path.endswith('/'):
            path += '/'
        with open(path+file,'r') as f:
            rawdata = f.readlines()
            
        ## get headers and raw numerical data
        rawnumdata = []
        for line in rawdata:
            if line.startswith("##"):
                rawparameters = line[2:]
            elif line.startswith("#"):
                headername = line[:line.index(":")].strip()[1:]
                headervalues = [x.strip() for x in line[line.index(":"):][1:].split(",")]
                if len(headervalues) == 1: headervalues = headervalues[0]
                self[headername] = headervalues
            else:
                rawnumdata.append(line)

        ## identify delimiter for raw data
        if "SEMICOLON" in self["SEPARATOR"]: 
            delim = ';'
        elif "COMMA" in self["SEPARATOR"]:
            delim = ','
        
        ## get parameter names for numerical data
        parameternames = [x.strip() for x in rawparameters.split(delim)]
        
        numdata = []
        for line in rawnumdata:
            if line.strip() is not "":
                textline = [x.strip() for x in line.split(delim)]
                temp = float(textline[0])
                vals = [[temp,float(x)]for i,x in enumerate(textline[1:]) 
                            if x is not '']
                numdata.append(vals)
        
        for i, parameter in enumerate(parameternames):
            
            if parameter not in self:
                self[parameter] = [x for x in numdata]
            else:
                self[parameter+"_{}".format(self["SEGMENT"][i])] = [x[i] for x in numdata]

        self.path = path
        self.file = file
        return 
    
    def plot_data(self,
                  segments = "all",
                  yparm = "auto",
                  figname="auto",
                  savefig=False,
                  formatfn=None,
                  **kwargs):
        """
        Plots dilatometry data and optionally saves the figure
        formatfn allows passing a function with a collection of
        arguments to format the function before saving it
        
        
        args
        ====
        xparm,yparm (str)
            parameter names, default to temperature and dL/Lo
        
        figname (str)
            figure name
        
        savefig (bool)
            save the figure?
        
        formatfn (function)
            see below
        
        returns
        =======
        matplotlib figure object
        
        example formatfn
        ================        
        ::
            
            def formatfn():
                f = plt.gcf()
                if "Vanadium" in f.get_label(): 
                    plt.ylim((0,1.2))
                if "Tungsten" in f.get_label():
                    plt.xlim((0,1.5))
        """        
        if "label" in kwargs.keys():
            label = kwargs["label"]
        else:
            label = self.file
        
        xparm = [x for x in self if "Temp" in x][0]


        if segments == "all": 
            pass
        else: 
            print("selection of sections not enabled yet")
            raise ValueError
            return
        
        xparm = [x for x in self if "Temp" in x][0]
        if yparm == "auto":
            yparm = [y for y in self if "dL/Lo" in y][0]
        xs = [x for x in self[xparm]]
        ys = [y for y in self[yparm]]

        if figname is "auto": figname="{} vs. {}".format(yparm,xparm)
        fig = plt.figure(figname,figsize=(6,4))
        plt.plot(xs,ys,label=label)
        plt.xlabel(xparm)
        plt.ylabel(yparm)
        plt.title(figname)
        plt.grid("on")
        plt.legend()
        if formatfn is not None: 
            formatfn()
        if savefig is not False:
            plt.savefig("./dil_plots/"+figname+".png")
        return fig
    
