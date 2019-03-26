#!/bin/env python

import sys
import argparse
import cv2 as cv

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
def processFrame(_oldBees, _frame, _frameNumber, _maxshift, _maxtravel,_boundary,_framelen,_beeCounter):
    _newBees={}
    _beesInRange={}
    _spotsInFrame={}
    _beeInFrame=1
    _bestMatches={}
    _oldMatches={}
    _properBeeExit={}
    _errorBeeExit={}
    _frameNumber=int(_frameNumber)
    
    #assign each been in frame a number
    #create dicts containing their locations and the locations of other bees in range from the previous frame
    for _spot in _frame:
        _beesInRange[_beeInFrame]=getBeesInRange(_spot, _oldBees,_maxshift,_maxtravel,_frameNumber)
        _spotsInFrame[_beeInFrame]=_spot
        _beeInFrame+=1

    #get a dict of the best matches based on distance    
    for _bee in _spotsInFrame:
        if _beesInRange[_bee] == {}:
            #no prior bees in range of this bee, so set the previously matching bee to zero
            _bestMatches[_bee]=0
            #Add to check if in entry or exit zone, warn if not
        else:
            #ok, this bee matches something from earlier, lets get the closest one
            _bestMatch=0
            _bestDistance=_maxtravel
            for _oldMatch in _beesInRange[_bee]:
                if changeInY(_beesInRange[_bee][_oldMatch],_spotsInFrame[_bee]) <= _bestDistance:
                    _bestDistance=changeInY(_beesInRange[_bee][_oldMatch],_spotsInFrame[_bee])
                    _bestMatch=_oldMatch
            #print "Bee in frame "+str(_bee)+" located at "+str(_spotsInFrame[_bee])+" best matches Bee Number "+str(_bestMatch)+" at "+str(_beesInRange[_bee][_bestMatch])
            _bestMatches[_bee]=_bestMatch
    #_bestMatches is now a dict of newBee to oldBee

    #dict of old Bees to new bees
    for _bestMatch in _bestMatches:
        #initialize if the array does not exist
        if _bestMatches[_bestMatch] not in _oldMatches:
            _oldMatches[_bestMatches[_bestMatch]]=[]
        #if not zero, append it
        #zero is a previously nonexistant bee (a new one)
        if _bestMatches[_bestMatch] != 0:
            _oldMatches[_bestMatches[_bestMatch]].append(_bestMatch)
    #_oldMatches now is an Dict of oldbees, containing an array of newbees that have that oldbee as their best match
    
    #now each new bee should only match one old bee, we need to find the best
    #this is for when two bee enter connected to each other
    for _oldMatch in _oldMatches:
        if len(_oldMatches[_oldMatch])>1:
            #well crap, now we need to pick one
            #print "Found two matches to prevous bee "+str(_oldMatch)+" in frame "+str(_frameNumber)
            _keeping=0
            for _matchInFrame in _oldMatches[_oldMatch]:
                #hopefully one is in the entry boundary
                #print str(_matchInFrame)+" is at "+str(_spotsInFrame[_matchInFrame])
                if _spotsInFrame[_matchInFrame][1] <= _boundary or _spotsInFrame[_matchInFrame][1] >= _framelen-_boundary:
                    #yay one is in the boundary, make it a new one
                    #print "new bee at "+str(_spotsInFrame[_matchInFrame])+" remove match for "+str(_matchInFrame)
                    _bestMatches[_matchInFrame]=0
                #else this one we need to keep
            if _keeping > 1:
                print "Error more than one bee matches a bee from the previous in frame "+str(_frameNumber)
                sys.exit()
        #else one is fine
    
    #check for issues with bestmatches and leavers (always picking wrong of double)
    #check each bee from last frame
    for _bee in _oldBees:
        #are no bees in this frame matching it (is it missing)
        if _bee not in _bestMatches.values():
            #if it went missing outside of the boundary, then we have an issue
            if _oldBees[_bee][sorted(_oldBees[_bee])[-1]][1] > _boundary and  _oldBees[_bee][sorted(_oldBees[_bee])[-1]][1] < _framelen-_boundary:
                #ok, now we have a problem
                #print "Missing Bee outside of boundary "+str(_bee)+" in Frame "+str(sorted(_oldBees[_bee])[-1])+" at "+str(_oldBees[_bee][sorted(_oldBees[_bee])[-1]])
                #was there a closer bee to the boundary that was in movement range if the old bee
                _oldBeesInRange=getBeesInRange(_oldBees[_bee][sorted(_oldBees[_bee])[-1]],_oldBees,_maxshift,_maxtravel,_frameNumber)
                if len(_oldBeesInRange)>1:
                       #print "But there was another old bee in range"
                       #print _oldBeesInRange
                       #lets check and see if there are some closer to the boundary
                       for _oldBeeInRange in _oldBeesInRange:
                           #no need to check the same bee, thats stupid
                           if _oldBeeInRange != _bee:
                               #print "possibly replacing "+str(_oldBeeInRange)
                               #check if it has a value _oldBeeInRange is present in the values of bestmatches (see if it was defined as a match)
                               if _oldBeeInRange in _bestMatches.values():
                                   #print "and it has a match"
                                   #check if this match was in the boundary areas
                                   if  _oldBees[_oldBeeInRange][sorted(_oldBees[_bee])[-1]][1] <= _boundary or _oldBees[_oldBeeInRange][sorted(_oldBees[_bee])[-1]][1] >= _framelen-_boundary:
                                       #print "and it is in the boundary so swap"
                                       #if it was in the boundary, then update so that the bee in the boundary is lost and not the other
                                       for _match in _bestMatches:
                                           #print "testing "+str(_match)+" was "+str(_bestMatches[_match])
                                           if _bestMatches[_match] == _oldBeeInRange:
                                               #print "set Bee "+str(_match)+" to "+str(_oldBeeInRange)
                                               _bestMatches[_match]=_bee
                           
    #use _bestMatches to determine the new bee information
    for _bee in _bestMatches:
        if _bestMatches[_bee] == 0:
            #we found a new bee
            _beeCounter+=1
            _newBees[_beeCounter]={}
            _newBees[_beeCounter][_frameNumber]=_spotsInFrame[_bee]
            print "Bee "+str(_bee)+" in frame is new bee "+str(_beeCounter)+" located at "+str(_spotsInFrame[_bee])
        else:
            #we have an previouly existing bee
            #copy the old frames
            _newBees[_bestMatches[_bee]]=_oldBees[_bestMatches[_bee]]
            #add this frame
            _newBees[_bestMatches[_bee]][_frameNumber]=_spotsInFrame[_bee]
    
    #get list of bees that are now gone
    #look at all the old bees
    for _bee in _oldBees:
        #is the _bee still in _newBees
        if _bee not in _newBees:
            if _frameNumber-1 in _oldBees[_bee]:
                if _oldBees[_bee][_frameNumber-1][1] <= _boundary or _oldBees[_bee][_frameNumber-1][1] >= _framelen-_boundary:
                    _properBeeExit[_bee]=_oldBees[_bee]
                    print "Bee "+str(_bee)+" left at boundary"
                else:
                    print "Error: Bee "+str(_bee)+" left outside of boundary"
                    _errorBeeExit[_bee]=_oldBees[_bee]
            #else then previous frame had no bees
        #else then it is still present
                                        
    return _newBees, _beeCounter, _properBeeExit, _errorBeeExit 

def changeInY(_pointa,_pointb):
    return abs(_pointa[1]-_pointb[1])
    
def getBeesInRange(_spot,_oldBees,_maxshift,_maxtravel,_frameNumber):
    _beesInRange={}
    _matchCount=0
    _lastframe=_frameNumber-1
    #print "find bees in rage"
    for _bee in _oldBees:
        if _lastframe in _oldBees[_bee]:
            if abs(_spot[0]-_oldBees[_bee][_lastframe][0])<=_maxshift and abs(_spot[1]-_oldBees[_bee][_lastframe][1])<=_maxtravel:
                #print "old bee "+str(_bee)+" is near at "+str(_oldBees[_bee][_lastframe])
                _beesInRange[_bee]=_oldBees[_bee][_lastframe]
                _matchCount+=1
        else:
            print "probably empty frame preceeding "+str(_frameNumber)
    #print "done finding bees"
    return _beesInRange

def numberBeeVideo(_currentBees,_vidin,_vidout,_frameNumber):
    #just copy frames if the current frame number in _currentBees is less than the frame count
    #this happens when we have frames with no bees in them
    #the sorted part here just grabs the last frame number from the first key in _currentBees
    while _frameNumber < sorted(_currentBees[_currentBees.keys()[0]])[-1]:
        #print "empty frame "+str(_frameNumber)
        #read an image
        _success,_image = _vidin.read()
        if _success:
            #write the image
            _vidout.write(_image)
            #we moved up a frame
            _frameNumber+=1
        else:
            print "Error: Could not read next frame"
            sys.exit()
    #now we just do the current frame
    _success,_image = _vidin.read()
    if _success:
        #write out each bee number at the right location
        for _bee in _currentBees:
            #print "last location "+str(_bee)+" is frame "+str(sorted(_currentBees[_bee])[-1])+" location "+str(_currentBees[_bee][sorted(_currentBees[_bee])[-1]])
            cv.putText(_image,str(_bee),(_currentBees[_bee][sorted(_currentBees[_bee])[-1]][0]-20,_currentBees[_bee][sorted(_currentBees[_bee])[-1]][1]),cv.FONT_HERSHEY_SIMPLEX,1,(255,0,0),2,cv.LINE_AA)
        #write the image
        _vidout.write(_image)
        #move be ready for the next frame
        _frameNumber+=1
    else:
        print "Error: Could not read frame"
        sys.exit()
    return _frameNumber
        
def oldnumberBeeVideo(_currentBees,_vidin,_vidout,_frameNumber):
    #figure out how not to do an iteritems here
    print _currentBees
    for _key,_value in _currentBees.iteritems():
        while _frameNumber<int(_value['frame']):
            print "empty frame "+str(_frameNumber)
            #error checking for success here
            _success,_image = _vidin.read()
            _vidout.write(_image)
            _frameNumber+=1
    #error checking for success here
    _success,_image = _vidin.read()
    for key,value in _currentBees.iteritems():
        cv.putText(_image,str(key),(value['spot'][-1][0]-20,value['spot'][-1][1]),cv.FONT_HERSHEY_SIMPLEX,1,(255,0,0),2,cv.LINE_AA)
    _vidout.write(_image)
    _frameNumber+=1
    return _frameNumber
          
    

parser=argparse.ArgumentParser(description="Uses output of findbees.py to determine the number and direction of bee travel")
requiredNamed=parser.add_argument_group('required arguments')
requiredNamed.add_argument('-i','--input',required=True, help="Data file from findbees.py to process")
parser.add_argument('-s','--maxshift', type=int, default=10, help='Maximum change in X value for a bee lane, default 10')
parser.add_argument('-t','--maxtravel', type=int, default=90, help='Maximum y distance a bee can travel between frames, default 90')
parser.add_argument('-b','--boundary', type=int, default=150, help='Y dimension zone length in which a bee can enter or exit, default 150')
parser.add_argument('-l','--framelen', type=int, default=582, help='Y dimension of the frame, default 582')
parser.add_argument('-v','--videoIn', help="Video file to number")
parser.add_argument('-o','--videoOut', help="Number video file output")
_args=vars(parser.parse_args())

f=open(_args['input'],"r")
  
thisframe=0
tmpary=[]
allProperBeeExit={}
allErrorBeeExit={}
beeCounter=0

try:
    _args['videoIn']
except NameError:
    _args['videoIn']=None

try:
    _args['videoOut']
except NameError:
    _args['videoOut']=None
    
if _args['videoIn'] != None and _args['videoOut'] != None:
    print "--videoIn and --videoOut are present, proceeding with video processing"
    vidin = cv.VideoCapture(_args["videoIn"])
    width = float(vidin.get(cv.CAP_PROP_FRAME_WIDTH))   # float
    height = float(vidin.get(cv.CAP_PROP_FRAME_HEIGHT)) # float
    vidout = cv.VideoWriter(_args["videoOut"],0x7634706d,30,(int(width),int(height)))
    frameNumber=1
else:
    print "--videoIn and/or --videoOut are not defined, proceeding with text only"
    
lastframe=0
for _line in f:
    _lineary=_line.split()
    if(_lineary[0] != thisframe):
        if(thisframe != 0):
            #print "Frame is "+str(thisframe)
            currentBees, beeCounter, properBeeExit, errorBeeExit = processFrame(currentBees,tmpary, thisframe, _args['maxshift'], _args['maxtravel'],_args['boundary'],_args['framelen'],beeCounter)

            if _args['videoIn'] != None and _args['videoOut'] != None:
                frameNumber=numberBeeVideo(currentBees,vidin,vidout,frameNumber)
            allProperBeeExit.update(properBeeExit)
            allErrorBeeExit.update(errorBeeExit)
        thisframe=_lineary[0]
        tmpary=[]
    tmpary.append([int(_lineary[1]),int(_lineary[2])])
currentBees, beeCounter, properBeeExit, errorBeeExit = processFrame(currentBees,tmpary, thisframe, _args['maxshift'], _args['maxtravel'],_args['boundary'],_args['framelen'],beeCounter)
if _args['videoIn'] != None and _args['videoOut'] != None:
    frameNumber=numberBeeVideo(currentBees,vidin,vidout,frameNumber)
allProperBeeExit.update(properBeeExit)
allErrorBeeExit.update(errorBeeExit)

#stat holders
uTurnTop=[]
uTurnBottom=[]
topToBottom=[]
bottomToTop=[]
endFrameLoss=[]
errorCount=0


print ""
print "Bees entering outside of boundary area"
print ""
#categorize the bees
for _bee in allProperBeeExit:
    #entering and leaving the top
    if allProperBeeExit[_bee][sorted(allProperBeeExit[_bee])[0]][1] <= _args['boundary'] and allProperBeeExit[_bee][sorted(allProperBeeExit[_bee])[-1]][1] <= _args['boundary']:
        uTurnTop.append(_bee)
    #entering top, leaving bottom
    elif allProperBeeExit[_bee][sorted(allProperBeeExit[_bee])[0]][1] <= _args['boundary'] and allProperBeeExit[_bee][sorted(allProperBeeExit[_bee])[-1]][1] >= _args['framelen']-_args['boundary']:
        topToBottom.append(_bee)
    #entering bottom, leaving top
    elif allProperBeeExit[_bee][sorted(allProperBeeExit[_bee])[0]][1] >= _args['framelen']-_args['boundary'] and allProperBeeExit[_bee][sorted(allProperBeeExit[_bee])[-1]][1] <= _args['boundary']:
        bottomToTop.append(_bee)
    #entering and leaving bottom
    elif allProperBeeExit[_bee][sorted(allProperBeeExit[_bee])[0]][1] >= _args['framelen']-_args['boundary'] and allProperBeeExit[_bee][sorted(allProperBeeExit[_bee])[-1]][1] >= _args['framelen']-_args['boundary']:
        uTurnBottom.append(_bee)
    #should not happen
    else:
        #first frame does not count
        if sorted(allProperBeeExit[_bee])[0] != 1:
            print "Bee "+str(_bee)+" first frame "+str(sorted(allProperBeeExit[_bee])[0])+" location "+str(allProperBeeExit[_bee][sorted(allProperBeeExit[_bee])[0]])+" last frame "+str(sorted(allProperBeeExit[_bee])[-1])+" location "+str(allProperBeeExit[_bee][sorted(allProperBeeExit[_bee])[-1]])
            errorCount+=1
        #but we need to keep track of them for the stats to add up
        else:
            print "Video Start Error: Bee "+str(_bee)+" first frame "+str(sorted(allProperBeeExit[_bee])[0])+" location "+str(allProperBeeExit[_bee][sorted(allProperBeeExit[_bee])[0]])+" last frame "+str(sorted(allProperBeeExit[_bee])[-1])+" location "+str(allProperBeeExit[_bee][sorted(allProperBeeExit[_bee])[-1]])
            errorCount+=1          

print ""
print "Bees exiting outside of boundary area"
print ""
for _bee in allErrorBeeExit:
    print "Bee "+str(_bee)+" first frame "+str(sorted(allErrorBeeExit[_bee])[0])+" location "+str(allErrorBeeExit[_bee][sorted(allErrorBeeExit[_bee])[0]])+" last frame "+str(sorted(allErrorBeeExit[_bee])[-1])+" location "+str(allErrorBeeExit[_bee][sorted(allErrorBeeExit[_bee])[-1]])
    errorCount+=1

#print results
print ""
print "Stats for bees exiting as expected"
print ""
print "Bees entering and leaving top: "+str(len(uTurnTop))
print "Bees entering and leaving bottom: "+str(len(uTurnBottom))
print "Bees traveling from top to bottom: "+str(len(topToBottom))
print "Bees traveling from bottom to top: "+str(len(bottomToTop))
print ""
print str(errorCount)+" total errors"
print str(beeCounter)+" total bees"
