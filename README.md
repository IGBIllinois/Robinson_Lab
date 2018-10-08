# Robinson_Lab
forager.py
Forager.py is a program that can be used to determine the date that a bee becomes a forager.
The inputs are
-i input.file 
  This input file must contain data separated by commas, with the first line being the heading for the data fields.  Each line
  of data must start with a bee number, followed by pairs of integers (be exit counts) at peak and nonpeak times for each date.
  The header is used to print out a resulting date when the testing criteria are met.
-o output.file
  The output file contains a line for each bee with the date it became a forager or NA if it never did
-m integer (default 6)
  Minimum number of events per day for a bee to be a forager
-t integer (default 12)
  Minimum number of total threshold events for a bee to be a forager
-d integer (default 2)
  Minmum number of datys above value from -m
-e integer (default 4)
  Minimum number of events in a day to switch to a forager
-f float (default 0.5)
  Ratio of nonpeak to peak time.
