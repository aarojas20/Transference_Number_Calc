'''AARojas
Updated 3/1/2020
The goal is to calculate the transference number (t+) as a function of time
Read all of the .lst files and compile the resistance values from each into a pd.DataFrame, this is fed to the t+ calculation
Analyze two experiments from one .txt file:  Negative deltaV and positive deltaV of potential applied to a cell
For each experiment:  identify the initial identify each of the twelve 1-hr current profiles from the deltaV biases
                                        at the end of each 1-hr current prof., find the last value of current, feed it to the t+ calculation
Graph the transference number as a function of time with the normalized current as a function of time
Save the t+ values to a .csv file and to a table as .png
'''
from Calc_Transference_FXNS import *
##
area=0.317 #cm^2

import os
lstfiles=[]
zfiles=[]
txtfile=''
for phile in os.listdir():
    if phile.endswith('.lst'):
        lstfiles.append(phile)
    if phile.endswith('.txt'):
        txtfile=phile
    if phile.endswith('.z'):
        zfiles.append(phile)

neg_or_pos=input('Is this the negative or positive potential for analysis? Enter "neg" or "pos".')
if neg_or_pos=='neg':
    i=0
    f=len(zfiles)//2
    lblfile='_neg40mV'
    Ns_initial=0
    zcycle=0
    Ns_CV=3
    Ns_loop_EIS=4
    tmin=0
    tmax=15
if neg_or_pos=='pos':
    i=len(zfiles)//2
    f=len(zfiles)
    lblfile='_pos40mV'
    Ns_initial=6
    zcycle=13 # zcycle start of current profile collection
    Ns_CV=9
    Ns_loop_EIS=10
    tmin=17
    tmax=32

R=[]
Err=[]
loop=[]
for r in range(i,f,1): 
    Rvalues,Error=OpenLSTfile(lstfiles[r])
    R.append(Rvalues)
    Err.append(Error)
    loop.append(int(lstfiles[r][38:-4])-1)  #append the loops
R=pd.DataFrame(R)     # compile all of the R values from all files into an accessible DataFrame
Err=pd.DataFrame(Err)
# graph the R values 
fig=plt.figure(figsize=(3,2),dpi=300)
graphRvalues(loop,R,Err)
plt.axis([loop[0]-.5,loop[-1]+1,0,800])
plt.xticks(np.arange(loop[0],loop[-1]+1,1))
formatGraph()
plt.savefig('Rvalues_'+txtfile[:-21]+lblfile)
#
Rtotal=R.iloc[0,:].sum()    # this computes the sum of all R values from the 0th file (the t=0 EIS)
#
##
#
colors=['darkgreen','limegreen','cadetblue','deepskyblue', 'royalblue','b','c','steelblue','mediumseagreen',
'mediumpurple','darkorchid','m','mediumvioletred','palevioletred','crimson','darkorange',
'sandybrown','peru','saddlebrown','goldenrod','greenyellow','yellowgreen','olive','olivedrab','lightslategrey']
##
#
ocv,Re,Im=InitialConditions(txtfile,Ns_initial)
file=pd.read_csv(txtfile,header=0,sep='\t')
V,I,T=findVITzcycle(file,zcycle,Ns_CV)        
#
deltaV=V.mean()-ocv.iloc[int(len(ocv)/2):].mean()
Izero=I.iloc[1]
Iomega=deltaV/Rtotal*area # this R is in (Ohm cm^2)
print(deltaV,V.mean(),ocv.mean())
##
# graph the Nyquist plots 
fig=plt.figure(figsize=(3,2),dpi=300)
graphEIS(Re*area,Im*area,'-','k','t=0')
for r in range(i,f,1): 
    Re,Im=OpenZviewFit(zfiles[r])
    graphEIS(Re,Im,'-','orange','_nolegend_')
for r in range(i+1,f,1):         
    Re,Im=loopedEIS(txtfile,r,Ns_loop_EIS)      
    graphEIS(Re.iloc[:-2]*area,Im.iloc[:-2]*area,'o',colors[r-1],'loop '+str(r))
plt.axis([0,1200,0,600])
plt.xticks(np.arange(0,1300,200))
formatGraph()
plt.savefig('EIS_'+txtfile[:-4]+lblfile)
#
##
# graph the normalized current and the transference number
tplus=[]
fig=plt.figure(figsize=(3,2),dpi=300)
count=1
for r in range(i,f-1,1):     
    V,I,T=findVITzcycle(txtfile,r,Ns_CV)       
    graphIT(T.iloc[1:],I.iloc[1:]/Iomega,'-',colors[r],'loop '+str(r))
    ratio=I.iloc[-1]/Izero
    transference=ratio*(deltaV-Izero*R.iloc[0,1])/(deltaV-I.iloc[-1]*R.iloc[count,1])   #ratio*(delV-I0*Ri0)/(delV-Iss*Riss), second polarity
    tplus.append(transference)
    print('loop ',str(r),ratio, 'I= ',I.iloc[1],'Iss= ',I.iloc[-1])
    plt.plot(T.iloc[-1],transference,'s',markersize=5,color=colors[r],mec='k',mew=0.5)
    count+=1
plt.axis([tmin,tmax,0,1.1])    #2nd
formatGraph()
plt.savefig('IT_transference_'+txtfile[:-4]+lblfile)
##
tplus=pd.DataFrame(tplus)
tplus.to_csv(path_or_buf='Transference'+lblfile+'_'+txtfile[:-4]+'.csv',header=['Transference'])
# create a table of t+ number
fig=plt.figure(figsize=(1,3),dpi=300)
plt.table(cellText=tplus.round(2).values,colLabels=['t+'],rowLabels=tplus.index,cellLoc='center',rowLoc='center',loc='best')
plt.axis('off')
plt.tight_layout()
plt.savefig('Table_'+txtfile[:-4]+lblfile)
#
##
# write the normalized current to a file for subsequent plotting
I,T=getAll_IT(file,Ns_CV)
ITdata=pd.concat([T.iloc[1:]-T.iloc[1],I.iloc[1:]/Iomega],axis=1)
ITdata.to_csv(path_or_buf='IT_'+txtfile[:-4]+lblfile+'.csv',header=['Time (h)','Norm Current'])
