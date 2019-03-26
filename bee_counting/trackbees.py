#!/bin/env python

import sys
import argparse

#maxtravel=90
#maxshift=10

#boundary=150
#framelen=582

f=open("data.txt","r")

currentBees={}
lostBees={}

#finds the closest bee from the previous frame to a spot in the current frame
#returns the nearest bee, the distance to that bee, and the spot that bee was at
def closestBee(_currentBees,_spot,_maxshift):
    _nearBeeSpot=[0,0]
    _nearBee=0
    _distanceBee=0
    for _bee in _currentBees:
        if _currentBees[_bee]["spot"][-1][0] < _spot[0]+_maxshift and _currentBees[_bee]["spot"][-1][0] > _spot[0]-_maxshift:
            if _nearBeeSpot != [0,0]:
                if abs(_currentBees[_bee]["spot"][-1][1]-_spot[1]) < _distanceBee:
                    _nearBeeSpot=_currentBees[_bee]["spot"][-1]
                    _nearBee=_bee
                    _distanceBee=abs(_currentBees[_bee]["spot"][-1][1]-_spot[1]) 
            else:
                _nearBeeSpot=_currentBees[_bee]["spot"][-1]
                _nearBee=_bee
                _distanceBee=abs(_currentBees[_bee]["spot"][-1][1]-_spot[1])
    return _nearBee, _distanceBee, _nearBeeSpot

#process a frame
#currentBees are the bees that are active in the current frame
#frame is a collection of all belocations in a frame
#framenumber is how many frames we have process - mostly informational, but used to keep track of if we have already updated a bee location as well
#maxshift is the maximum change in x values for a bee in a lane
#maxtravel is the maximum distance a bee can be expected to move in one frame
#boundary is the y value that is put on both sides of travel where a bee can enter or exit expectedly
#framelen is the y dimension of the frame
#beecounter is the number of different bees that have been found so far
def processFrame(_currentBees, _frame, _frameNumber, _maxshift, _maxtravel,_boundary,_framelen,_beeCounter):
    _newBees={}
    _lostBees={}
    _missingBees={}
    _missMoved=[]
    #find bees in frame, determine if they are close to something else
    for _spot in _frame:
        #print _spot
        _nearBee, _distanceBee, _nearBeeSpot=closestBee(_currentBees,_spot,_maxshift)
        #useful debugging
        #print "nearest bee is "+str(_nearBee)+" at "+str(_distanceBee) + " pixels, coordinates "+str(_nearBeeSpot)
        if _nearBee == 0:
            #print "no bees in lane last frame"
            _beeCounter += 1
            print "Bee "+str(_beeCounter)+" new "+str(_spot)+" on frame "+str(_frameNumber)
            _newBees[_beeCounter]=_spot
        elif _distanceBee <= _maxtravel:
            #detect a double match to the spot (two bees within the travel range)
            if _nearBee in _newBees:
                #if the old bee was in entry detection areas
                if _newBees[_nearBee][1]<= _boundary or _newBees[_nearBee][1] >= _framelen-_boundary:
                    _beeCounter += 1
                    print "Bee "+str(_beeCounter)+" new "+str(_newBees[_nearBee])+" on frame "+str(_frameNumber)
                    _newBees[_beeCounter]=_newBees[_nearBee]
                    _newBees[_nearBee]=_spot
                #if the new spot was in entry detection areas
                elif _spot[1]<= _boundary or _spot[1] >= _framelen-_boundary:
                    _beeCounter += 1
                    print "Bee "+str(_beeCounter)+" new "+str(_spot)+" on frame "+str(_frameNumber)
                    _newBees[_beeCounter]=_spot
                #probably a tripple entry mashing into one side
                else:
                    print "Frame: "+_frameNumber+" double bees found outside entry areas in frame "+str(_frameNumber)+" spot "+str(_spot)
                    #print "try decreasing travel distance"
                    #sys.exit()
            else:
                #print str(_nearBee)+" movement detected"
                _newBees[_nearBee]=_spot
        else:
            if _spot[1]>_boundary and _spot[1]<_framelen-_boundary:
                print "Frame: "+_frameNumber+" Error new bee found outside of entry zone"
                #print "training at entry or travel distance or entry boundary could be too low "+str(boundary)+","+str(_framelen-_boundary)
                #print _spot
                _beeCounter += 1
                _newBees[_beeCounter]=_spot
                _missMoved.append(_beeCounter)
            else:
                _beeCounter += 1
                print "Bee "+str(_beeCounter)+" new "+str(_spot)+" on frame "+str(_frameNumber)
                _newBees[_beeCounter]=_spot
    
    #correct for freighttraining at entry
    #check all possible misplaced bees
    _corrected=[]
    for _missplaced in _missMoved:
        #against all total bees
        for _bee in _newBees:
            #dont bother if we are looking at this bee
            if _bee != _missplaced:
                #was there other bees in this lane
                if abs(_newBees[_bee][0]-_newBees[_missplaced][0])<=_maxshift:
                    #print "other bees in this lane"
                    #was there a bee in the top or bottom entry zone of the image
                    if _newBees[_bee][1]<= _boundary or _newBees[_bee][1] >= _framelen-_boundary:
                        #was it also within the traveldistance of the misplaced bee
                        if abs(_newBees[_bee][1]-_newBees[_missplaced][1])<_maxtravel:
                            #we found a misplaced bee, swap the locations
                            _tmploc=_newBees[_bee]
                            _newBees[_bee]=_newBees[_missplaced]
                            _newBees[_missplaced]=_tmploc
                            _corrected.append(_missplaced)
                            print "corrected positions of bees "+ str(_bee) + "," +str(_missplaced)

    #now error if missmoved bees were not _corrected
    for _missplaced in _missMoved:
        if _missplaced not in _corrected:
            print "Frame: "+_frameNumber+" error unable to corect bee "+str(_missplaced)
            #print _newBees[_missplaced]
            #print "newbees dump"
            #print _newBees
            #sys.exit()
                    
                
    #update _currentBees with new locations and frame number
    for _bee in _newBees:
        #very useful debugging
        #print "Bee "+str(_bee)+" coordinates "+str(_newBees[_bee][0])+","+str(_newBees[_bee][1])
        #initalize the bee structure if it does not exist
        if _bee not in _currentBees:
            _currentBees[_bee]={}
            _currentBees[_bee]["spot"]=[]
            _currentBees[_bee]["frame"]=0
        _currentBees[_bee]["spot"].append(_newBees[_bee])
        _currentBees[_bee]["frame"]=_frameNumber
    
    
    #push unframed _currentBees to _lostBees
    for _bee in _currentBees:
        if _currentBees[_bee]["frame"] != _frameNumber:
            if _currentBees[_bee]["spot"][-1][1]>=_framelen-_boundary:
                print "Bee "+str(_bee)+" left at the bottom in frame "+_frameNumber+" Last location: "+str(_currentBees[_bee]["spot"][-1][0])+","+str(_currentBees[_bee]["spot"][-1][1])
                _lostBees[_bee]=_currentBees[_bee]
            elif _currentBees[_bee]["spot"][-1][1]<=_boundary:
                print "Bee "+str(_bee)+" left at the top in frame "+_frameNumber+" Last location: "+str(_currentBees[_bee]["spot"][-1][0])+","+str(_currentBees[_bee]["spot"][-1][1])
                _lostBees[_bee]=_currentBees[_bee]
            else:
                print "Frame: "+_frameNumber+" Error bee "+str(_bee)+" disappeared in the middle and is "+str(_currentBees[_bee]["spot"][-1][0])+","+str(_currentBees[_bee]["spot"][-1][1])
                #print _framelen-_boundary
                _missingBees[_bee]=_currentBees[_bee]
                #sys.exit()
    
    #remove lostbees from currentbees
    for _bee in _lostBees:
        _currentBees.pop(_bee)
    #remove missingbees from currentbees
    for _bee in _missingBees:
        _currentBees.pop(_bee)
    #return bees in current frame as well as those lost, the total number of bees and missing
    return _currentBees,_lostBees,_beeCounter, _missingBees


parser=argparse.ArgumentParser(description="Uses output of findbees.py to determine the number and direction of bee travel")
requiredNamed=parser.add_argument_group('required arguments')
requiredNamed.add_argument('-i','--input',required=True, help="Data file from findbees.py to process")
parser.add_argument('-s','--maxshift', type=int, default=10, help='Maximum change in X value for a bee lane, default 10')
parser.add_argument('-t','--maxtravel', type=int, default=90, help='Maximum y distance a bee can travel between frames, default 90')
parser.add_argument('-b','--boundary', type=int, default=150, help='Y dimension zone length in which a bee can enter or exit, default 150')
parser.add_argument('-l','--framelen', type=int, default=582, help='Y dimension of the frame, default 582') 
_args=vars(parser.parse_args())

f=open(_args['input'],"r")
  
thisframe=0
tmpary=[]
allMissing={}
beeCounter=0
allLostBees={}
for _line in f:
    _lineary=_line.split()
    if(_lineary[0] != thisframe):
        if(thisframe != "0"):
            currentBees,lostBees, beeCounter, missing = processFrame(currentBees,tmpary, thisframe, _args['maxshift'], _args['maxtravel'],_args['boundary'],_args['framelen'],beeCounter)
            allLostBees.update(lostBees)
            allMissing.update(missing)
        thisframe=_lineary[0]
        tmpary=[]
    tmpary.append([int(_lineary[1]),int(_lineary[2])])
currentBees, lostBees, beeCounter, missing = processFrame(currentBees,tmpary, thisframe, _args['maxshift'], _args['maxtravel'],_args['boundary'],_args['framelen'],beeCounter)
allLostBees.update(lostBees)
allMissing.update(missing)

#stat holders
uTurnTop=[]
uTurnBottom=[]
topToBottom=[]
bottomToTop=[]
endFrameLoss=[]

#categorize bees
for bee in allLostBees:
    if allLostBees[bee]["spot"][0][1] < _args['boundary'] and allLostBees[bee]["spot"][-1][1] < _args['boundary']:
        uTurnTop.append(bee)
    elif allLostBees[bee]["spot"][0][1] > _args['framelen']-_args['boundary'] and allLostBees[bee]["spot"][-1][1] > _args['framelen']-_args['boundary']:
        uTurnBottom.append(bee)
    elif allLostBees[bee]["spot"][0][1] < _args['boundary'] and allLostBees[bee]["spot"][-1][1] > _args['framelen']-_args['boundary']:
        topToBottom.append(bee)
    elif allLostBees[bee]["spot"][0][1] > _args['framelen']-_args['boundary'] and allLostBees[bee]["spot"][-1][1] < _args['boundary']:
        bottomToTop.append(bee)
    else:
        endFrameLoss.append(bee)

#print results
print ""
print "Bees entering and leaving top: "+str(len(uTurnTop))
print "Bees entering and leaving bottom: "+str(len(uTurnBottom))
print "Bees traveling from top to bottom: "+str(len(topToBottom))
print "Bees traveling from bottom to top: "+str(len(bottomToTop)) 
print "Bees lost at end frames: "+str(len(endFrameLoss))
print "Bees lost due to tracking errors: "+str(len(allMissing))

    
