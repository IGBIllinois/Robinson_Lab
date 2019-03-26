#!/usr/bin/env python

#This program parses a data file of bees leaving a hive to determine when a bee become a forager
#Arguments are as defined below in the parders giving the -h flag will display them as well
import argparse
from collections import deque

def chomp(_line):
    #removes newline from the end of a string
    return _line.rstrip("\n\r")


parser=argparse.ArgumentParser(description="Determine the date at which a bee become a forager")
requiredNamed=parser.add_argument_group('required arguments')
requiredNamed.add_argument('-i','--input', type=argparse.FileType('r'),required=True, help="File from which to read data")
parser.add_argument('-m','--mday', type=int, default=6, help='Minimum number of threshold events per day, default 6')
parser.add_argument('-t', '--mtot', type=int, default=12, help='Minimum number of total threshold events, default 12')
parser.add_argument('-d','--days', type=int, default=2, help='Minimum days above total threshold events, default 2')
parser.add_argument('-e','--minevents', type=int, default=4, help='Minimum number of events in a day to allow a forager, default 4')
parser.add_argument('-f','--tfrac', type=float, default=0.5, help='Fraction of events before/after the propose time threshold, default 0.5')
requiredNamed.add_argument('-o','--output', type=argparse.FileType('wb', 0), required=True, help="Single output file to write to")
_args=parser.parse_args()

for line in _args.input:
    #remove the annoying newline character
    line=chomp(line)
    #split on commas
    datapoints=line.split(',')
    #reset line position
    index=0
    #reset number of days above threshold
    daysabove=0
    #set the default result to NA
    forageDate="NA"
    #first line has the header, if that does not exist, build the header list
    if 'dates' in globals():
        #convert to integers
        datapoints=[int(n) for n in datapoints]
        #days moves in increments of two based one of nonpeak time an the other value of peak time of the same day
        for i in range(1, len(datapoints),2):
            #count days above minim threshold
            if int(datapoints[i])+int(datapoints[i+1])>=_args.mday:
                daysabove+=1
            #count events before and after (which also includes) today    
            eventsBefore=sum(datapoints[1:i-1])    
            eventsAfter=sum(datapoints[i:len(datapoints)])
            #if all tests are met, set it as a forager
            #testing for NA ensures we do not overwrite with a newer date
            if forageDate == "NA" and \
                sum(datapoints[1:i+1]) >= _args.mtot and \
                daysabove >= _args.days and \
                datapoints[i]+datapoints[i+1] >= _args.minevents and \
                datapoints[i+1]*_args.tfrac >= datapoints[i]:
                    forageDate=dates[i+1]
        #write data to file
        _args.output.write(str(datapoints[0])+" "+forageDate+"\n")
    else:
        #build data structure of dates
        #this will be used to display the date at which a bee transitions
        dates=[]
        for datapoint in datapoints:
            dates.append(datapoint)
            
