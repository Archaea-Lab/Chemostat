#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 29 18:01:23 2024

@author: johnmallon

This program will read in '.csv' files from the Turbidostat machine and separate data based on
dilution cycle number and then graph Optical Density vs time
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
from sklearn.metrics import r2_score
from IPython.display import display, Math


def exponentialEquation(x,y,k,a,c):
    return a*np.exp(k*x)+0  #do we use 0 or a variable? 


def fitExponential(group,x,y,DTs,R2s,Xs,yFits,groups):
    popt, pcov = curve_fit(exponentialEquation,x,y,maxfev=10000)
    x = np.array(x)
    yFit = exponentialEquation(x,*popt)
    rSquaredValue =  r2_score(y, yFit)
    R2s.append(round(rSquaredValue,2))
    print('R^2: ', round(rSquaredValue,2))
    print('Growth Rate: ', popt[1])
    print('Doubling Time (min): ', np.log(2)/popt[1]*60)
    DTs.append(int(round(np.log(2)/popt[1]*60,0)))
    
    Xs.extend(x)
    yFits.extend(yFit)
    cycle = [group] * len(yFit)
    groups += cycle 
    
    
    #warnings.resetwarnings()
    return DTs, R2s, Xs, yFits, groups

def main():
    #open and filter data
    directory = '/Users/johnmallon/Downloads/'
    file = "2024_06_04 ecoli 37C program 30Cincubator.csv" 
    df = pd.read_csv(directory+file)
    df['Time (hr)'] = df['currentProgramTime']/60/60
    df = df.loc[df["neutralMediaDispenseCount"]==0]
    
    #graph growth
    subDF = df.iloc[::120]
    fig1, ax = plt.subplots(dpi=300)
    sns.scatterplot(data=subDF,ax=ax,
                 x='Time (hr)',y='OD940',
                 hue='totalCycleCount',
                 alpha=0.75,ec='k',lw=50)


    #separate data into cycles and fit exponentials
    cycles = df.groupby('totalCycleCount')
    max_length = max(len(group) for _, group in cycles)
    dfGroup = pd.DataFrame(index=range(max_length))

    #Iterate through each group and create a DataFrame for each
    count = 0
    DTs = []
    groups = []
    R2s = []
    Xs = []
    yFits = []
    groupz = []
    for group, values in cycles:
        print(group)
        groups.append(group)
        time = values['Time (hr)'].to_list()
        od940 = values['OD940'].to_list()
        DTs,R2s,Xs,yFits,groupz = fitExponential(group,time,od940,DTs,R2s,Xs,yFits,groupz)
        time.extend([None] * (max_length - len(time)))
        od940.extend([None] * (max_length - len(od940)))
    
        dfGroup[str(count)+' Time'] = time
        dfGroup[group] = od940
        count+=1
    
    fitsDF = pd.DataFrame(columns=['Cycle #','X','yFit'])
    fitsDF['Cycle #'] = groupz
    fitsDF['X'] = Xs
    fitsDF['yFit'] = yFits
    
    sns.lineplot(data=fitsDF,ax=ax,
                 x='X',y='yFit',
                 hue='Cycle #',palette=['k'],
                 alpha=1.0,lw=1.0)
    
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    plt.legend().set_visible(False)
    
    fig2, bx = plt.subplots(dpi=300)
    cycles = range(len(DTs))
    sns.scatterplot(ax=bx,
                 x=cycles,y=DTs
                 )
    bx.set_xlabel('Time (hr)')
    bx.set_ylabel('Doubling Time (min)')

    dfGrowth = pd.DataFrame()
    dfGrowth['Cycle #']= groups
    dfGrowth['Doubling Time (min)'] = DTs
    dfGrowth['R^2'] = R2s
    
    print(dfGrowth)
    
    dfGrowth.to_csv(directory+'chemostat_doublingTimes.csv')
    fig1.savefig(directory+'growthCurve.svg',format='svg',dpi=300)
    

main()