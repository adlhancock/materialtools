# -*- coding: utf-8 -*-
"""
Used for presenting material properties in graph or table format

requires a dict generated from a MaterialData object


Created on Tue Jan 12 15:07:12 2016

@author: dhancock

"""
import matplotlib.pyplot as plt
from itertools import cycle
from cycler import cycler
#import matplotlib as mpl

plt.rc("axes",
       prop_cycle=(
                   cycler("color",
                          plt.cm.tab20.colors[::2]+
                          ('b',)+
                          plt.cm.tab20.colors[1:2]
                          ) +
                   cycler("linestyle",['-','--',':','-.']*3)
                  )
       )
#plt.rc("axes",prop_cycle=(cycler("linestyle",['-','--',':','-.'])))

linestyles = cycle(['-',':','--','-.'])

def plotproperty(material,
                 propertyname,
                 xaxis = 'Temperature',
                 yaxis = 'auto',
                 newplot = True,
                 sourcelabels = False,
                 step = 1,
                 **kwargs):
    '''
    Plot a graph of a material property from a materialdata dict file.
    
    optional kwargs are passed to a matplotlib.pyplot.plot call.
    
    '''
    ## allow easier plotting of Elasticity properties
    if propertyname in ["Young's Modulus",
                        "Shear Modulus",
                        "Bulk Modulus",
                        "Poisson's Ratio"]:
        yaxis = propertyname        
        figuretitle = "Elasticity ({})".format(propertyname)
        propertyname = "Elasticity"
        
    ## allow easier plotting of DBTT graphs
    if propertyname in ["Ductile Brittle Transition Temperature"]:
        yaxis = "Reduction in Area"
        #propertyname = ""
        
    ## allow easier plotting of EASY data"
    if "EASY" in propertyname:
        if xaxis == "Temperature": xaxis = "Time"
        
    assert propertyname in material, "{} not found in {} [{}]".format(
                                propertyname,material.name,material.source)    
    #mpl.style.use("fivethirtyeight")
    #mpl.style.use("seaborn-poster")
    #import itertools
    materialname = material.name

    if yaxis == 'auto': yaxis = propertyname

    # get values
    try:
        xvals = material.get_points(propertyname,xaxis)[::step]
        yvals = material.get_points(propertyname,yaxis)[::step]
        #assert (len(xvals) == len(yvals)) "test"
    except:
        print('could not plot {} values for {}'.format(propertyname,material.name))
        #xvals, yvals = [],[]
        raise
        
    ## get units
    try:
        xunits = material[propertyname][xaxis]['Units'][0]
        yunits = material[propertyname][yaxis]['Units'][0]
    except:
        print('could not find {} units for {}'.format(material.name,propertyname))
        xunits, yunits = '',''
    

    ## tweak units for certain properties to make graphs prettier!
    if propertyname in ["Elasticity",]:
        yunits = "GPa"
        newyvals = [x*1e-9 for x in yvals]
        yvals = newyvals

    if propertyname in ["Yield Stress", "Ultimate Tensile Strength"]:
        yunits = "MPa"
        newyvals = [x*1e-6 for x in yvals]
        yvals = newyvals
    
    if propertyname in ["Coefficient of Thermal Expansion",]:
        yunits = "1e-6*C^-1"
        newyvals = [x*1e6 for x in yvals]
        yvals = newyvals
    
    
    ## set figure title
    if "figuretitle" not in list(kwargs.keys())+list(locals().keys()):
        if newplot == True:
            figuretitle = '{} ({}) of {} [{}]'.format(propertyname,yaxis,materialname,material.source)
        else:
            figuretitle = '{} ({}) of Multiple Materials'.format(propertyname,yaxis)
    else:
        figuretitle = kwargs.pop("figuretitle")
    ## create figure    
    fig = plt.figure(figuretitle,
                     #figsize=(8,7),
                     figsize=(6,5),
                     dpi = 100
                     )
    ax = plt.gca()
    """
    global markers 
    markers = itertools.cycle(('x','.','+','o','*'))
    global linestyles
    linestyles = itertools.cycle(('-','--',':','.-'))
    marker = next(itertools.cycle(markers))
    linestyle = next(itertools.cycle(linestyles))
    """
    if 'label' not in kwargs.keys():
        label = '{}'.format(materialname)
        if sourcelabels is True: 
            try: label += " [{}]".format(material["Description"])
            except: label += " [{}]".format(material["no source given"])
    else: 
        label = kwargs['label']
        kwargs.pop('label')
        
    if 'marker' not in kwargs.keys(): 
        if len(yvals)>2: marker = None
        else: marker = 'o'
    else: 
        marker = kwargs['marker']
        kwargs.pop('marker')

    if "linestyle" not in kwargs.keys(): 
        #print("linestyle not in kwargs.keys()")
        if newplot is True:
            #print("newplot is true")
            linestyle = '-'
        #else:            
            #linestyle = next(linestyles)
            #print("iterating",linestyle)
            #pass
    #else: 
        #linestyle = kwargs['linestyle']
        #kwargs.pop('linestyle')
        #pass

    #print(kwargs.keys())
    #print(kwargs['markerstyle'])
    ## plot points
    ax.plot(xvals,
             yvals,
             marker=marker,
             #linestyle = linestyle,
             label = label,
             #linewidth = 3,
             linewidth = 2,
             **kwargs)
    
    ## decorate plot
    ax.legend(
               #fontsize='small',
               ncol = 3,
               loc="upper left",
               #bbox_to_anchor = (0,-0.03,1,-0.1),
               bbox_to_anchor = (0,-0.05,1,-0.1),
               mode = "expand",
               borderaxespad=0,
               #handlelength = 5,
               handlelength = 3,
               )
    ax.set_title('{}'.format(figuretitle))
    ax.set_xlabel(xaxis + ' [' + xunits + ']')
    ax.set_ylabel(yaxis + ' [' + yunits + ']')
    plt.grid(linestyle=":")
    plt.tight_layout(pad = 1.2)
    
    ## make sure the legend fits
    ls, hs = ax.get_legend_handles_labels()
    legendsizes = ((0,0.2),(6,0.25),(9,0.28),(12,0.3),(16,0.35))
    #legendsizes = ((0,0.15),(6,0.23),(9,0.25),(12,0.28),(16,0.3))
    for s in legendsizes:
        if len(ls) > s[0]:
            fig.subplots_adjust(bottom = s[1])
    #plt.show()
    return fig


def printproperty(materialdata,
                  material = 0,
                  propertyname = 0):
    '''
    Prints a table of a material property
    '''
    if type(material) is int:
        materialname = sorted(materialdata.keys())[material]
    else:
        materialname = material

    if type(propertyname) is int:
        keys = sorted(materialdata[materialname].keys())
        if propertyname <= len(keys):
            propertyname = keys[propertyname]
        else:
            print(
                propertyname,
                'is not a valid property index for',
                materialname)
            quit()

    if propertyname in materialdata[materialname]:
        propertydata = materialdata[materialname][propertyname]
        print() # clear a line
        print(propertyname,'(',materialname,')',) # print headings

        keys = sorted(propertydata.keys())
        columns = []
        for key in keys:
            if type(propertydata[key]) is dict:
                columns.append(key)
        for column in columns:
            columnheader = (
                column
                +'['
                +materialdata[materialname][propertyname][column]['units'][0]
                +']'
                )
            #print column headers
            print('{0:30}'.format(columnheader), end = '')
        print('\n')

        #for row in range(len(propertydata[column]['values'])):
        for row, values in enumerate(propertydata[column]['values']):
            for column in columns:
                print(
                    #'{0:30}'.format(values), # doesn't work
                    '{0:30}'.format(propertydata[column]['values'][row]),
                    end = '')
            print()

    else:
        print(propertyname+' is not available for '+materialname)

"""
if __name__ == '__main__':
    import materialtools
    materialdata = materialtools.MaterialData()
    materialdata.import_file('/python/data/materialtools/xml/HHF_materials.xml')
    materialdata['Beryllium'].set_value('density',[20,100],[500,400],'temperature')
    for materialname in materialdata.materialnames:
            material = materialtools.Material(materialname, materialdata)
            try:
                plotproperty(material,
                             propertyname= "Elasticity",
                             yaxis = "Young's Modulus",
                             xaxis='Temperature',
                             newplot=False)
                plotproperty(material,
                             propertyname= "Density",
                             yaxis = "auto",
                             xaxis='Temperature',
                             newplot=False)
                plotproperty(material,
                             propertyname= "Thermal Conductivity",
                             yaxis = "auto",
                             xaxis='Temperature',
                             newplot=False)
            except:
                print('could not plot graph for {}'.format(materialname))
                raise
                
            '''
            try:
                plotproperty(material,
                             propertyname= "density",
                             yaxis = "auto",
                             xaxis='temperature',
                             newplot=False)
            except:
                print('could not plot graph for {}'.format(materialname))
            '''
                
    
    # print table
    #printproperty(steel,'density')

    # plot graph

"""