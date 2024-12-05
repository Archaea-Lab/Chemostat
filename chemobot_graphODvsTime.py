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


def main():
    # Load the .txt file (update the file path and delimiter as needed)
    txtFilePath = "your_file.txt"
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
    
    #get rid of the data where the bot is diluting the vial with media
    cycles = df.groupby('totalCycleCount')
    cyclesData = []
    for cycle,values in cycles:
        growthIndicator = values['growthDurationChange'].iloc[0]
        print('Cycle: ',cycle)
        print(growthIndicator)
        subDF = values.loc[values['growthDurationChange']==growthIndicator]
        cyclesData.append(subDF)
    cleanedDF = pd.concat(cyclesData)
    
    #decide how many datapoints to plot (in minutes)
    timeFrameToPlotInMinutes = 5 
    subDF = cleanedDF.iloc[::timeFrameToPlotInMinutes*60]
    subDF.loc[subDF['OD940']>=0]

    #plot data
    figure,ax = plt.subplots(dpi=300)
    seaborn.scatterplot(data=subDF,ax=ax,
                        x='Time (hr)', y='OD940',
                        hue='totalCycleCount',
                        palette=(seaborn.color_palette()),
                        alpha=0.75,ec='k',lw=0.5)
    plt.legend().set_visible(False)
    
    #save figure at a '.svg'
    figure.savefig('figureTitle.svg',format='svg',dpi=300)

main()
