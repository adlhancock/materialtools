# -*- coding: utf-8 -*-
"""
Created on Fri Dec 15 16:20:44 2017

@author: dhancock
"""

#import materialtools
from openpyxl import load_workbook
from matplotlib import pyplot as plt

class USGS_historical:
    """ used to pull data from the USGS formatted excel spreadsheets
    
    """
    def __init__(self,materialname="No Name"):
        self.data = {}
        self.name = materialname
        pass
    
    def load_file(self,filename):
        wb = load_workbook(filename, 
                           read_only=True, 
                           data_only=True)
        ws = wb.get_active_sheet()
        ws_rows = [x for x in ws.rows]
        self.headers = [[y.value for y in x if y.value is not None] for x in ws_rows[:4]]
        self.column_names = [x.value for x in ws_rows[4]]
        #print(self.column_names)
        
        for i, header in enumerate(self.column_names):
            self.data[header] = [row[i].value for row in ws_rows[5:]]
            
    def plot(self,
             xvar="Year",
             yvar="Unit value ($/t)",
             figtitle="USGS Data",
             linestyle="-"):
        fig = plt.figure(figtitle,figsize=(6,4))
        data = [(x,y) for x, y in zip(self.data[xvar],self.data[yvar])
            if all([type(n) is not str for n in (x,y)])]
        xs, ys = [x[0] for x in data], [y[1] for y in data]
        plt.plot(xs,ys,
                 label=self.name,
                 linestyle=linestyle,
                 linewidth=2)
        plt.xlabel(xvar)
        plt.ylabel(yvar)
        plt.legend(fontsize="small")
        #plt.grid("on")
        return fig

