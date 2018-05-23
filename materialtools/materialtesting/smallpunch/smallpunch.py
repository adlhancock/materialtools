# -*- coding: utf-8 -*-
"""materialtools.testing.smallpunch.smallpunch.py
imports and plots data from the Phoenix rigs
todo: export to materialtools xlsx format
Created on Tue Jul 25 16:39:53 2017

@author: dhancock
"""

from matplotlib import pyplot as plt
import tkinter as tk
from tkinter import filedialog
import os

class SPdata(dict):
    """
    .. class: SPdata(dict)    
    
    small punch data object
    
    methods
    ======
    .. function:: import_data(file,path)
    
        creates a dictionary of recorded variables
        from a csv file from the Thor or Odin Phoenix rigs
    
    .. function:: plot_data(xparm,yparm,figname="auto",savefig=False,formatfn=None)

        plots the data
        
    """
    def __init__(self,
                 path=None,
                 file=None,
                 date='Unknown',
                 material='Unknown',
                 **kwargs):
        self["Test Date"]= date
        self["Material"] = material
        if None not in (path,file):
            self.import_data(path,file)
        for arg in kwargs.keys():
            #print(arg)
            self[arg] = kwargs[arg]
        
    
    def import_data(self,path=None,file=None):
        """
        creates a dictionary of recorded variables
        from a csv file from the Thor or Odin Phoenix rigs
        strips unneccessary whitespace from variable names
                
        args
        ====
        path (str)
            location of data file
            
        file (str)
            filename of file to be imported
            
        """
        if None in (path,file):
            root = tk.Tk()
            root.withdraw()
            filename = filedialog.askopenfilename(
                            title = "select data file",
                            filetypes = [("small punch data file",
                                          "*.txt")])
            path = os.path.dirname(filename)
            if not path.endswith('/'):
                path += '/'
            file = os.path.basename(filename)
            
        with open(path+file,'r') as f:
            rawdata = f.readlines()
        headers = [x.strip() for x in rawdata[0].split(",")]
        numdata=[[float(x) for x in row.split(",")] for row in rawdata[1:]]
        for i, header in enumerate(headers):
            self[header] = [row[i] for row in numdata] 
        self.path = path
        self.file = file
        self.headers = headers                 
        return 
    
    def plot_data(self,xparm,yparm,
                  figname="auto",
                  savefig=False,
                  formatfn=None,
                  **kwargs):
        """
        Plots small punch data and optionally saves the figure
        formatfn allows passing a function with a collection of
        arguments to format the function before saving it
        
        
        args
        ====
        xparm,yparm (str)
            parameter names
            
            if these are "Load","Stroke", or "Extens." the sign is 
            reversed for clarity of plotting
        
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
        
        signx, signy = 1,1
        if xparm in ["Load","Stroke", "Extens."]:
            signx = -1
        if yparm in ["Load","Stroke", "Extens."]:
            signy = -1
            
        xs = [signx*x for x in self[xparm]]
        ys = [signy*y for y in self[yparm]]
        if figname is "auto": figname="{} vs. {}".format(yparm,xparm)
        fig = plt.figure(figname,figsize=(10,10))
        plt.plot(xs,ys,label=label)
        plt.xlabel(xparm)
        plt.ylabel(yparm)
        plt.title(figname)
        plt.grid("on")
        plt.legend()
        if formatfn is not None: 
            formatfn()
        if savefig is not False:
            plt.savefig("./sp_plots/"+figname+".png")
        return fig
    
