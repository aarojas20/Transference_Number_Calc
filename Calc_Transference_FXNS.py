'''Adriana A. Rojas
Updated 2/10/2020
The following contains a collection of functions to read data from different files (.z files, .lst files, and .txt files) that are generated from
an experiment to determine the transference number of an electrolyte
'''
##
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pprint as pprint
from matplotlib import rcParams
rcParams['font.family']='sans-serif'
rcParams['font.sans-serif']=['Arial']
size=10
##
def OpenZviewFit(zfilename):
    '''input: zfilename is of type string, it is the name of a .z file containing the fit curve to an EIS data
    output: the Real and Imaginary impedances of type pd.DataFrame
'''
    file=pd.read_csv(zfilename,header=23,sep='\t')
    Real=pd.to_numeric(file["Z'(a)"],downcast='float',errors='coerce')
    Imaginary=pd.to_numeric(file["Z''(b)"],downcast='float',errors='coerce')*-1
    return Real,Imaginary
##
def OpenLSTfile(filename):
    '''input: filename is of type string; it is the name of a .lst file containing a table of parameters to the EIS fit result
    output:  the resistance values, Rvals, and the associated error, Error, each of type np.array

    Rvals and Error are determined based on its location in the file
    I first find the index, n,  of a particular line preceding the location of the data (" ESTIMATED ERROR(%)')
    The data is located between n+1 and n+9, variables a and b, respectively
    The data was written in scientific notation, with 'D' as base 10.  This is changed to 'E' for simplicity of conversion to float
    '''
    file=pd.read_csv(filename,header=None,sep='\n')
    n=file.loc[file[0]=='   ESTIMATED ERROR (%)'].index  # identify the index
    a=n+1
    b=n+9
    vals=file.iloc[a[0]:b[0]].replace(to_replace='D',value='E',regex=True)
    new=vals[0].str.split(' ',n=9,expand=True)  # split the data based on a space
    vals['Param']=pd.to_numeric(new[6],downcast='float',errors='coerce') # convert to float
    vals['Error']=pd.to_numeric(new[8],downcast='float',errors='coerce')
    vals['% Error']=pd.to_numeric(new[9],downcast='float',errors='coerce')
    vals.drop(columns=[0],inplace=True)
    R_b=vals.iloc[0,0]  # the electrolyte resistance
    R_int=vals.iloc[2,0]    # the interfacial resistance
    R_e=vals.iloc[5,0]      # the diffusion resistance 
    Rvals=np.array([R_b,R_int,R_e])
    Err_b=vals['Error'].iloc[0] # the error associated with the electrolyte resistance
    Err_ct1=vals['Error'].iloc[2] # the error associated with the interfacial resistance
    Err_ct2=vals['Error'].iloc[5] # the error associated with the diffusion resistance
    Error=np.array([Err_b,Err_ct1,Err_ct2])
    return Rvals,Error
##
def loopedEIS(filename,zcycle,Ns):
    '''input: filename is of type string; it is the name of a .txt file containing the data to the experiment
    output: for a particular cycle, zcycle, identify the Real and Imaginary impedances as pd.Series'''
    file=pd.read_csv(filename,header=0,sep='\t')
    filterforEIS = file[(file['Ns'] == Ns) & (file['z cycle'] == zcycle)]  # the step end code indicates that the step time was reached
    Real=pd.to_numeric(filterforEIS['Re(Z)/Ohm'],downcast='float',errors='coerce')
    Imaginary=pd.to_numeric(filterforEIS['-Im(Z)/Ohm'],downcast='float',errors='coerce')
    return Real,Imaginary
##
def InitialConditions(filename,Ns_initial):
    '''input:  filename is of type string
                    Ns_initial  is of type integer, it is the technique number associated with the OCV step
    Determine the initial conditions of the experiment:  the voltage at t=0 (OCV) and the initial impedances
    output:  ocv is of type float, Real and Imaginary are pd.Series'''
    file=pd.read_csv(filename,header=0,sep='\t')
    filterforOCV = file[file['Ns'] == Ns_initial]  
    ocv=pd.to_numeric(filterforOCV['Ewe/V'],downcast='float',errors='coerce')*1000     # convert from V to mV
#
    filterforEIS = file[file['Ns'] == Ns_initial+1]   
    Real=pd.to_numeric(filterforEIS['Re(Z)/Ohm'],downcast='float',errors='coerce')
    Imaginary=pd.to_numeric(filterforEIS['-Im(Z)/Ohm'],downcast='float',errors='coerce')
    return ocv,Real,Imaginary
##
def findVITzcycle(file,zcycle,Ns):
    '''input: file is a pd.DataFrame
    output:  identifies the voltage, current, and time associated with each cycle in the experiment
'''
    filterforprofiles = file[(file['Ns'] ==Ns) & (file['z cycle'] == zcycle)]   
    voltage=pd.to_numeric(filterforprofiles['Ewe/V'],downcast='float',errors='coerce')*1000     # convert from V to mV   
    current=pd.to_numeric(filterforprofiles['I/mA'],downcast='float',errors='coerce')
    time=pd.to_numeric(filterforprofiles['time/s'],downcast='float',errors='coerce')/3600   # convert from seconds to hours
    return voltage,current,time
def getAll_IT(file,Ns):
    '''input: file is a pd.DataFrame
    output:  identify the full current and time profiles associated with the experiment (does not filter by cycle)
'''
    filterforprofiles= file[file['Ns'] ==Ns]
    current=pd.to_numeric(filterforprofiles['I/mA'],downcast='float',errors='coerce')
    time=pd.to_numeric(filterforprofiles['time/s'],downcast='float',errors='coerce')/3600   # convert from seconds to hours
    return current,time
##
def graphRvalues(loop,Rmatrix,Err):
    '''input:  loop is a list of integers, Rmatrix is a pd.dataFrame with the Rvalues'''
    plt.errorbar(loop,Rmatrix[0],yerr=Err[0],fmt='o-',color='dodgerblue',mec='k',label='R$_{electrolyte}$')
    plt.errorbar(loop,Rmatrix[1],yerr=Err[1],fmt='^-',color='mediumorchid',mec='k',label='R$_{interface}$')
    plt.errorbar(loop,Rmatrix[2],yerr=Err[2],fmt='s-',color='forestgreen',mec='k',label='R$_{el}$')
    plt.xlabel('Loop')
    plt.ylabel('Resistance ($\Omega\cdot$cm$^2$)')
    return
def formatGraph():
    '''format the graph to have ticks inside on all borders, include a legend, and ensure nothing gets cropped out of the window'''
    plt.tick_params(labelsize=size)
    plt.tick_params(which='major',right='on',direction='in',top='on',length=6)
    plt.tick_params(which='minor',right='on',direction='in',top='on',length=3)
    plt.legend(loc='best',fontsize=size-4,ncol=3)
    plt.tight_layout()
    return
##
def graphIT(x,y,sym,clr,samp):
    ''' input: x and y can be of type pd.Series
                    sym is of type string, it contains the symbol indicated for the marker
                    clr is of type string, it codes for the color desired
                    samp is of type string, it specifies the label indicated in a legend
        output:  graph x and y with the specified formatting
        '''
    plt.plot(x,y,sym,color=clr,mec=clr,markersize=2,markevery=5,label=samp)
    plt.xlabel('Time (h)',fontsize=size)
    plt.ylabel('Normalized Current, I$_t$/I$_\Omega$', fontsize=size)
    return
#
def graphEIS(x,y,sym,clr,samp):
        ''' input: x and y can be of type pd.Series
                    sym is of type string, it contains the symbol indicated for the marker
                    clr is of type string, it codes for the color desired
                    samp is of type string, it specifies the label indicated in a legend
        output:  graph x and y with the specified formatting
        '''
    plt.plot(x,y,sym,color=clr,mec='k',markersize=2.5,markevery=2,label=samp,mew=0.2,linewidth=0.5)
    plt.xlabel('Real ($\Omega\cdot$cm$^2$)',fontsize=size)
    plt.ylabel('Imaginary ($\Omega\cdot$cm$^2$)', fontsize=size)
    return
##
