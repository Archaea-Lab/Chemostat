# -*- coding: utf-8 -*-
"""
Created on Mon Dec  2 16:32:13 2024

@author: Johnmallon

This script reads in the '.txt' file from the chemobot and graphs the OD940 values vs. time in hours

For each cycle count in the chemobot there are two states:
    1. When the OD is increasing over time (growth, normal state)
    2. When the OD is decreasing over time (dilution state)

Each of these two states gets a different value in their 'growthDurationChange' column. So take the first value in this column
for each group and use that to discard the rows that are from the dilution state.

User must:
    1. Update the directory to point accordingly to their chemobot generated '.txt' file. This is on LINE 31.
    2. Specify how many datapoints you want to graph. The chemobot records a datapoint every second. This is, normally, 
    way too many datapoints to graph. Specify the time interval (in minutes) that you want to graph. By default, it is 
    set to graph data at an interval of 5 minutes. This is on LINE 67.


"""
import pandas as pd
import seaborn
import matplotlib.pyplot as plt
from scipy import stats


def getSlope(df):
    slope, intercept, rValue, p_value, std_err = stats.linregress(df['Time (hr)'], df['OD940'])
    return slope,rValue,


def main():
    # Load the .txt file (update the file path and delimiter as needed)
    txtFilePath = r"C:\Users\User\Desktop\2024_12_14_DS2_saltEvolution_first48Hr_1secondInterval.txt"
    csvFilePath = txtFilePath[:-4]+'.csv'
    delimiter = ","  # Change this to the correct delimiter

    # Read the .txt file
    data = pd.read_csv(txtFilePath, delimiter=delimiter)

    # Save it as a .csv file
    data.to_csv(csvFilePath, index=False)
    df = pd.read_csv(csvFilePath)
    
    #convert certain columns to numerical values. the raw data is stored as strings which causes some problems if they are
    #not forced to be numbers. 'Coerce' sets all non numbers to NaN which we can then remove
    df['unixTime'] = pd.to_numeric(df['unixTime'], errors='coerce')
    df['OD940'] = pd.to_numeric(df['OD940'], errors='coerce')
    df['totalCycleCount'] = pd.to_numeric(df['totalCycleCount'], errors='coerce')
    df['growthDurationChange'] = pd.to_numeric(df['growthDurationChange'], errors='coerce')
    
    #remove any rows that do not covert to numbers; usually header rows that come from starting/stopping the machine
    df = df.loc[df['unixTime'].notna()]
    
    #convert time to hours
    df['Time (hr)'] = (df['unixTime']-df['unixTime'].iloc[0])/60/60
    #df = df.loc[df['OD940']>= 0.05]
    #get rid of the data where the bot is diluting the vial with media
    cycles = df.groupby('totalCycleCount')
    cyclesData = []
    for cycle,values in cycles:
        growthIndicator = values['growthDurationChange'].iloc[0]
        subDF = values.loc[values['growthDurationChange']==growthIndicator]
        cyclesData.append(subDF)
    cleanedDF = pd.concat(cyclesData)
    
    #decide how many datapoints to plot (in minutes)
    timeFrameToPlotInMinutes = 2
    subDF = cleanedDF.iloc[::timeFrameToPlotInMinutes*60]
    subDF.loc[subDF['OD940']>=0]

    #plot data
    fig1,ax = plt.subplots(dpi=300)
    seaborn.scatterplot(data=subDF,ax=ax,
                        x='Time (hr)', y='OD940',
                        hue='totalCycleCount',
                        palette=(seaborn.color_palette()),
                        alpha=0.75,ec='k',lw=0.5)
    plt.legend().set_visible(False)
    
    #save figure at a '.svg'
    #fig1.savefig('figureTitle.svg',format='svg',dpi=300)

    cycles = cleanedDF.groupby('totalCycleCount')
    slopes = []
    cycleTimes = []
    for cycle,values in cycles:
        print('Cycle: ', cycle)
        subDF = values.loc[values['OD940']>= 0.005]
        if not subDF.empty:
            slope,rValue = getSlope(subDF)
            #print('Slope: ',slope)
            #print('R^2: ', round(rValue,2))
            slopes.append(round(slope,4))
            cycleStart = subDF['Time (hr)'].iloc[0]
            cycleEnd = subDF['Time (hr)'].iloc[-1]
            cycleTimes.append(cycleEnd-cycleStart)
    
    #plot growth rates
    fig2,bx = plt.subplots(dpi=300)
    seaborn.scatterplot(ax=bx,
                        x=range(len(slopes)),y=slopes)
    bx.set_xlabel('Cycle #')
    bx.set_ylabel('Growth Rate (hr^-1)')
    
    #plot cycle times
    fig3,cx = plt.subplots(dpi=300)
    seaborn.scatterplot(ax=cx,
                        x=range(len(cycleTimes)),y=cycleTimes)
    cx.set_xlabel('Cycle #')
    cx.set_ylabel('Cycle Time (hr)')

        

main()
