#!/bin/env python

import cv2 as cv
import argparse

cv.setNumThreads(18)

#trims the backgrounds and original image to be the proper size
def trimImage(_image,_x1,_y1,_x2,_y2):
    _image = _image[_x1:_x2, _y1:_y2]
    return _image

def writeData(_file, _framenumber, _x, _y):
    if _file != "":
        _file.write(_framenumber+"\t"+str(_x)+"\t"+str(_y)+"\n")

def findBeesInImage(_image,_mask,_thresh,_single,_double,_tripple,_artifact,_file,_framenumber):
    _differ = cv.subtract(_mask,_image)
 
    #convert the difference to greyscale
    _bwdiffer=cv.cvtColor(_differ, cv.COLOR_BGR2GRAY)
    #make a binary mask of the greyscale image to help determine our boundaries
    _im_bw = cv.threshold(_bwdiffer, _thresh, 255, cv.THRESH_BINARY)[1]
    #find contoured areas in the black or white image
    a, _contours, b = cv.findContours(_im_bw,cv.RETR_LIST,cv.CHAIN_APPROX_SIMPLE)

    #for each contour found...
    for _cnt in _contours:
        #if area is greater than the single bee minimum but not yet double
        if _single<=cv.contourArea(_cnt)<=_double:
            #draw the countour on the image
            cv.drawContours(_image,[_cnt],0,(0,255,0),2) 
            #figure out the rectangle that will contain the countour
            _x,_y,_w,_h=cv.boundingRect(_cnt)
            #let the user know you found a single bee
            print "single "+str(cv.contourArea(_cnt))
            #print the center and draw on image
            print "center is "+str(_x+_w/2)+","+str(_y+_h/2)
            cv.circle(_image,(_x+_w/2,_y+_h/2),3,(255,255,255),3)
            #write to text file if needed
            writeData(_file,str(_framenumber),_x+_w/2,_y+_h/2)
        #if area is great then the double bee minimum but not yet tripple    
        elif _double<cv.contourArea(_cnt)<=_tripple:
            #draw the contour on the image
            cv.drawContours(_image,[_cnt],0,(0,0,255),2) 
            #figure the rectangle that will contain the contour
            _x,_y,_w,_h=cv.boundingRect(_cnt)
            #let the user know you found two bees
            print "double "+str(cv.contourArea(_cnt))
            #print the centers and draw on image
            print "center is "+str(_x+_w/2)+","+str(_y+_h/4)
            cv.circle(_image,(_x+_w/2,_y+_h/4),3,(255,255,255),3)
            #write to text file if needed
            writeData(_file,str(_framenumber),_x+_w/2,_y+_h/4)
            print "center is "+str(_x+_w/2)+","+str(_y+_h-_h/4)
            cv.circle(_image,(_x+_w/2,_y+_h-_h/4),3,(255,255,255),3)
            #write to text file if needed
            writeData(_file,str(_framenumber),_x+_w/2,_y+_h-_h/4)
        #if we are greater than the tripple bee minimum    
        elif cv.contourArea(_cnt)>_tripple:
            #draw the contour on the image
            cv.drawContours(_image,[_cnt],0,(255,0,0),2) 
            #figure the rectangle that will contain the contour
            _x,_y,_w,_h=cv.boundingRect(_cnt)
            #let the user know you found three bees
            print "tripple "+str(cv.contourArea(_cnt))
            #print the centers and draw on image
            print "center is "+str(_x+_w/2)+","+str(_y+_h/6)
            cv.circle(_image,(_x+_w/2,_y+_h/6),3,(255,255,255),3)
            #write to text file if needed
            writeData(_file,str(_framenumber),_x+_w/2,_y+_h/6)
            print "center is "+str(_x+_w/2)+","+str(_y+_h/2)
            cv.circle(_image,(_x+_w/2,_y+_h/2),3,(255,255,255),3)
            #write to text file if needed
            writeData(_file,str(_framenumber),_x+_w/2,_y+_h/2)
            print "center is "+str(_x+_w/2)+","+str(_y+_h-_h/6)
            cv.circle(_image,(_x+_w/2,_y+_h-_h/6),3,(255,255,255),3)
            #write to text file if needed
            writeData(_file,str(_framenumber),_x+_w/2,_y+_h-_h/6)
        #if smaller than a full be, but larger than the artifact cutoff    
        elif _artifact<cv.contourArea(_cnt)<_single :
            #draw the contour on the image
            cv.drawContours(_image,[_cnt],0,(255,0,255),2) 
            #figure the rectangle that will contain the contour
            _x,_y,_w,_h=cv.boundingRect(_cnt)
            #let the user know you found part of a bee
            print "partial "+str(cv.contourArea(_cnt))  
            #print the center and draw on image
            print "center is "+str(_x+_w/2)+","+str(_y+_h/2)
            cv.circle(_image,(_x+_w/2,_y+_h/2),3,(255,255,255),3)
            #write to text file if needed
            writeData(_file,str(_framenumber),_x+_w/2,_y+_h/2)
        #artifacts are small areas found, tend to be minor errors in bee recognition or just noise
        #these need to be ignored to stay sane and only show real data
        #else:
        #    print "artifact"
        
    #return the image we modified
    return _image

parser=argparse.ArgumentParser(description="Finds bees on an image and records their location")
requiredNamed=parser.add_argument_group('required arguments')
requiredNamed.add_argument('-i','--input',required=True, help="Image or video to find bees in")
requiredNamed.add_argument('-m','--mask', required=True, help="Background image without bees")
parser.add_argument('-s','--single', type=int, default=6000, help='Minimum area of a single complete bee, default 6000')
parser.add_argument('-d', '--double', type=int, default=10000, help='Minimum area of two close bees, default 9500')
parser.add_argument('-t','--tripple', type=int, default=18500, help='Minimum area of three close bees, default 17500')
parser.add_argument('-a','--artifact', type=int, default=1100, help='Cutoff level to remove nose and other artifacts, default 700')
parser.add_argument('-l','--bwlimit', type=int, default=50, help='Binarly black or white cutoff limit, determines bee area, default 50')
parser.add_argument('-b','--box', type=str, default="0,0,0,0", help="Bounds of image to edit, format x1,y1,x2,y2, default 0,0,0,0 is do nothing")
parser.add_argument('-f','--file', type=str, default="", help="text file to contain the coordinates of bees in each image, always appends")
requiredNamed.add_argument('-o','--output', required=True, help="Image or video output file")
_args=vars(parser.parse_args())

if _args["file"] != "":
    _args['file']=open(_args['file'],"a+")

#single image processing
if _args["input"].endswith(".jpg") and _args["output"].endswith(".jpg"):
    #image to process
    image = cv.imread(_args["input"])
    #background image to subtract
    mask = cv.imread(_args["mask"])

    #unless box is set to zeros for do nothing, trim it
    if _args["box"] != '0,0,0,0':
        box = [x.strip() for x in _args["box"].split(',')]
        box = [int(x) for x in box]
        image = trimImage(image,box[0],box[1],box[2],box[3])
        mask = trimImage(mask,box[0],box[1],box[2],box[3])
    #find the bees    
    image=findBeesInImage(image,mask,_args["bwlimit"],_args["single"],_args["double"],_args["tripple"],_args["artifact"],_args["file"],framenumber)
    #write out the final image
    cv.imwrite(_args["output"], image)
#video processing
elif _args["input"].endswith(".mp4") and _args["output"].endswith(".mp4"):
    print "process like a movie"
    #background image to subtract
    mask = cv.imread(_args["mask"])
    #trim mask if necessary
    if _args["box"] != '0,0,0,0':
        box = [x.strip() for x in _args["box"].split(',')]
        box = [int(x) for x in box]
        mask = trimImage(mask,box[0],box[1],box[2],box[3])
    #open the input video
    vidin = cv.VideoCapture(_args["input"])
    #set up the output video
    height, width, layers = mask.shape
    #the hexnumber is tells to use mp4 codec
    #the 30 is frames per second
    vidout = cv.VideoWriter(_args["output"],0x7634706d,30, (width,height))
    #try to read the first frame
    success,image = vidin.read()
    #set the initial frame number
    framenumber=1
    #keep going so long as we can read frames
    while success:
        #trim if necessary
        if _args["box"] != '0,0,0,0':
            image=trimImage(image,box[0],box[1],box[2],box[3])
        #find the bees
        image=findBeesInImage(image,mask,_args["bwlimit"],_args["single"],_args["double"],_args["tripple"],_args["artifact"],_args["file"],framenumber)
        #add image to the video
        vidout.write(image)
        #try to get another frame
        success, image = vidin.read()
        #increment frame number
        framenumber+=1
    #close it all down
    cv.destroyAllWindows()
    vidout.release()
#catch all for mismatched inputs and untested formats
else:
    print "input and output formats do not match or have not been tested"
