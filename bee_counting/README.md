# findbees.py
Companion program of trackbees.py.  This program goes through a video file, frame by frame and creates a .txt file with the positions of each bee in each frame.  Also creates a video file of the area examined, with outlines around each bee to show their area, along with a white dot to show the reported x,y position of the bee.  Works best when using video filmed on a monochomatic background with contrast to bee colors (white, green, etc)

USAGE:
```
findbees.py [-h] -i INPUT -m MASK [-s SINGLE] [-d DOUBLE] [-t TRIPPLE]
                   [-a ARTIFACT] [-l BWLIMIT] [-b BOX] [-f FILE] -o OUTPUT
```
- `-i filename`		Input video file
- `-m filename`		Image from same camera as video with no bees in it.  Used as a mask.
- `-o filename`		Video file created of the reduced bee area, with bees outlined by colors.
- `-b x1,y1,x2,y2`	Pair of coordinates to determine reduced area of video to be examined.
- `-f filename`		File created that stores the coordinates of each bee in each frame.
- `-l integer`		Adjust sensitivity as to the significance of change to be detected.
- `-a integer`		Detected area that is not returned as any match.  Removes artifacts.
- `-s integer`		Detected area minimum for a single bee.
- `-d integer`		Detected area minimum for double bees.
- `-t integer`		Detected area minimum for tripple bees.

At this time the program cannot detect more than threee bees that are adjacent to each other.  This is because the area between a large group of three bees and a small group of four bees is too similar to reliably detect at this time.

# trackbees.py
Companion program of trackbees.py.  This program takes the .txt file from findbees.py to create statistics based on where bees entered and exited.  If the optional video created by findbees.py is also included, it will overlay the number of each bee over the appropriate bee in the video file.  This helps with debugging.

USAGE:
```
trackbees.py [-h] -i INPUT [-s MAXSHIFT] [-t MAXTRAVEL] [-b BOUNDARY]
                    [-l FRAMELEN] [-v VIDEOIN] [-o VIDEOOUT]
```
- `-i filename`		This is the text file created by findbees.py
- `-l integer`		The height of a frame in pixels.  This will attempt to be auto detected in a future version.
- `-b integer`		The boundary for bees to enter or exit in pixels.
- `-s integer`		The amount a column of bees can shift left or right in pixels.
- `-t integer`		The maximum amount a bee can travel between frames in pixels.
- `-v filename`		Optional video file created by findbees.py
- `-o filename`		Optional video to create with bee numbers overlayed.

The bee statistics including information on bees with tracking errors is returned in standard out when running this program.
