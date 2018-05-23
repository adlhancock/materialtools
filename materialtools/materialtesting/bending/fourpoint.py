# -*- coding: utf-8 -*-
"""materialtools.materialtesting.bending.plot

Reads in a text file from the Phoenix rig (Thor)
from a four point bending test and plots load v stroke
todo: export in materialtools xlsx format

Created on Thu Oct 26 09:41:08 2017

@author: dhancock
"""


import matplotlib.pyplot as plt
from . import calculators as fp
import numpy as np


def import_file(filename):
   """ Reads in a text file from the Phoenix rig (Thor)
   """
   print('importing {}'.format(filename))
	with open(filename, 'r') as f:
		raw = f.readlines()
	headers = [x.strip() for x in raw[0].strip().split(',')]
	numbers = [[float(i) for i in x.strip().split(',')] 
                 for x in raw[1:]]
	data={}
	for i, header in enumerate(headers):
			data[header]=[x[i] for x in numbers]
	return data


def plot_loadvstroke(data,
                     date='2018xxxx',
                     sample='N'
                     ,temp='RT'
                     ,figname='auto'):
    """ plots a quick load vs stroke graph
    taking into account the negative signals"""
    
    if figname=='auto': figname='Load vs. Displacement'
    fig = plt.figure(figname)
    label = '{}_{}_{}'.format(date,sample,temp)
    
    plt.plot([-x*1e-3 for x in data['Extens.']],
             [-x*1e-3 for x in data['Load']], 
             label=label)

    ## prettify plot
    plt.title('Four Point Bending'.format(temp))
    plt.xlabel('Displacement [m]')
    plt.ylabel('Load [N]')
    plt.grid('on')
    plt.legend()
    
    return fig

def plot_modulus_manually(xs,
                          ys,
                          data,
                          sample_dimensions,
                          support_dimensions,
                          stroke_offset=0,
                          npoints = 200,
                          figname = 'auto'):
    """ plot force displacement curve and add manual modulus calculation
    
        inputs:
            - xs
            - ys
            
        ** NB: work in progress - not finished**
        
    """    
    ## set up figure
    if figname=='auto': figname = "Load vs. Displacement (manual)"
    fig = plt.figure(figname)

    sampling = int(len(data['Load'])/npoints)

    loads    = [-x*1e3 for x in data['Load'][::sampling]]
    strokes  = [-x*1e-3+stroke_offset for x in data['Extens.'][::sampling]]
    stresses = [fp.stress_flexural(x,sample_dimensions,support_dimensions)
                    for x in loads]    
                        
    gradient = (ys[1]-ys[0])/(xs[1]-xs[0])
    modulus    = fp.modulus_flexural(gradient,
                                     sample_dimensions,
                                     support_dimensions)
    
    ##  plot modulus vs stroke
    ax1 = fig.add_subplot(111)
    ax1.plot([x for x in strokes],
             [x for x in loads],'-b')
    plt.xlabel('Displacement [m]')
    plt.ylabel('Load [N]',color='b')
    plt.yticks(color='b')
    
    plt.title(figname)

    plt.grid('on')
    
    ## plot xs and ys

    ax1.plot(xs,ys,'-r',marker='x')
    

    

    plt.annotate('E={:.2e}'.format(modulus),xy=(xs[1],ys[1]))
    
    ax2=ax1.twinx()
    ax2.plot([x for x in strokes],
             [x*1e-6 for x in stresses],color='r',linestyle='',marker='')
    plt.ylabel('Stress [MPa]',color='r')
    plt.yticks(color='r')

    plt.tight_layout(pad=1.2)
    return fig


    
def plot_modulus_by_gradient(data,
                             sample_dimensions,
                             support_dimensions,
                             npoints = 100,
                             stroke_offset=0,
                             figname = 'auto'):
    
    """ plot force displacement graph and overlay calculation of modulus 
    by calculating the gradient between each point
    
    
    ** Note: doesn't quite work yet**
    """
    
    if figname=='auto': figname = "force vs. displacement (auto)"
    fig = plt.figure(figname)

    sampling = int(len(data['Load'])/npoints)

    loads    = [-x*1e3 for x in data['Load'][::sampling]]
    strokes  = [-x*1e-3+stroke_offset for x in data['Extens.'][::sampling]]

    gradients = np.gradient(np.array([strokes,loads]))
    slopes = gradients[1][1,:]
    print(gradients)
    moduli    = [fp.modulus_flexural(slope/10,
                                  sample_dimensions,
                                  support_dimensions)
                    for slope in slopes]

    ##  plot modulus vs stroke
    ax1 = fig.add_subplot(111)
    ax1.plot(strokes,
             [x*1e-9 for x in moduli],
             '-b')
    plt.xlabel('Displacement [m]')
    plt.ylabel('Modulus [GPa]',color='b')
    plt.yticks(color='b')
    
    plt.title(figname)

    plt.grid('on')
    
    ## also plot load displacement curve
    ax2 = ax1.twinx()
    ax2.plot(strokes,loads,'-r')
    plt.ylabel('Load [N]',color='r')
    plt.yticks(color='r')
    plt.tight_layout(pad=1.2)
    return [fig,gradients]
    
if __name__ == '__main__':
    pass