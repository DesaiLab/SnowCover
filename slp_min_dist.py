'''
slp_min_dist.py retrieves sea level pressure data directly from two sets of
simultaneously-occuring wrfout files in the directory where it's executed
through the creation of numerous local temporary files which are deleted by
the end of its execution.  The program proceeds to evaluate the data and 
graph the trajectories of two simultaneous pressure minimums along with the
difference in pressure between them.

Note: if the program is interrupted before graphing, you may have a lot of
new temporary files in your directory.  Running the program again to completion
should solve this.  If that isn't in the cards then just type the following into
your Linux command line, provided that there are no files with the same naming
convention which you intend to keep:
>rm temp_*
 
Values which may need to be adjusted include the area of interest parameters,
naming conventions for wrfout files, the limits for the secondary y-axis, and
the position of the graph legend.

Ryan Clare
November, 2016
University of Wisconsin-Madison
rclare2@wisc.edu
'''

from commands import *                #Library for executing Linux commands
from numpy import *                   #Library for math
from matplotlib.pyplot import *       #Library for plotting

m = linspace(0.0,142,143)             #Latitude linespace
n = linspace(0.0,208,209)             #Longitude line space


#NCL Processing
#-----------------------------------------------------------------------------#
'''
This section writes and executes a temporary NCL script to gather data for sea 
level pressure by storing values from multiple simultaneous wrfout files into
temporary files which will be deleted later.
'''
#NCL code for temp_ncl.ncl
ncl_content = '\
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"                    \n\
load "$NCARG_ROOT/lib/ncarg/nclscripts/wrf/WRFUserARW.ncl"                  \n\
begin                                                                       \n\
  fList = systemfunc("ls -1 wrfout*")                                       \n\
  gList = systemfunc("ls -1 nosno_*")                                       \n\
  nFiles = dimsizes(fList)                                                  \n\
  do iFile = 0, nFiles - 1                                                  \n\
    filenamea = sprinti("temp_a_slp%03d.txt",iFile)                         \n\
    filenameb = sprinti("temp_b_slp%03d.txt",iFile)                         \n\
    a = addfile(fList(iFile),"r")                                           \n\
    b = addfile(gList(iFile),"r")                                           \n\
    slp_a   = wrf_user_getvar(a,"slp",-1)                                   \n\
    slp_b   = wrf_user_getvar(b,"slp",-1)                                   \n\
    asciiwrite(filenamea, slp_a)                                            \n\
    asciiwrite(filenameb, slp_b)                                            \n\
  end do                                                                    \n\
end'

f = open("temp_ncl.ncl",'w')        #Creates local temporary ncl script
f.write(ncl_content)                #Writes above contents into file
f.close()

getstatusoutput('ncl temp_ncl.ncl') #Runs temporary ncl script


#Initialization
#-----------------------------------------------------------------------------#
'''
This section initializes the loops by counting the necessary iterations and 
creating arrays based on the result.
'''
ls = getstatusoutput('ls')          #Stores contents of local directory
ls = ls[-1]                         #We're not interested in the first bit

f = open("temp_file.txt",'w')       #Creates local temporary file
f.write(ls)                         #Writes contents of directory into file
f.close()

f = open("temp_file.txt",'r')       #Reads file
g = f.readlines()                   #Turns each component into an array item
f.close()

limit = 0
for i in range(len(g)):
	if g[i] == 'temp_a_slp%03d.txt\n' % limit:
		limit+=1                        #Counts the number of files with the naming
	else:                             #convention outlined in the ncl script
		pass

print limit, "files of each variable to sort through."

#Create arrays
slp_a = zeros((limit,len(m),len(n))) #Empty array for sea level pressure in snowy
slp_b = zeros((limit,len(m),len(n))) #Empty array for sea level pressure in snowless

min_a = zeros((2,limit))            #Empty array for minimum pressures by longitude for snowy
min_b = zeros((2,limit))            #Empty array for minimum pressures by longitude for snowless

a_min_loc = zeros((2,limit))        #Empty array to store location of pressure minumums for snowy
b_min_loc = zeros((2,limit))        #Empty array to store location of pressure minumums for snowless

#Area of interest - to avoid picking up pressure minimums on the periphery
min_lat = 25
max_lat = 119
min_long = 80
max_long = n[-1]


#Snowy SLP array
#-----------------------------------------------------------------------------#

for i in range(limit):
	f = open("temp_a_slp%03d.txt" % i, 'r')	#Open temporary snowy slp file
	pcontent = f.readlines()          #Write each line into an array
	f.close()
	l = 0
	for j in range(len(m)):
		for k in range(len(n)):
			slp_a[i,j,k] = pcontent[l]    #Fills array with slp values as ordered in text file
			l+=1		
	p_min = 10000                     #Set impossibly high value for pressure minimum token
	c1 = min_lat                      #Minumum latitude in area of interest
	while c1 <= max_lat:              #Maximum latitude in area of interest
		c2 = min_long                   #Minumum longitude in area of interest
		while c2 <= max_long:           #Maximum longitude in area of interest
			if slp_a[i,c1,c2] < p_min:    #If current value is less than current pressure minimum token
				min_a[0,i] = slp_a[i,c1,c2] #Store current pressure minimum
				a_min_loc[0,i] = c1         #Store latitude of current pressure minimum
				a_min_loc[1,i] = c2         #Store longitude of current pressure minimum
				min_a[1,i] = c2             #Store longitude of pressure minimum
				p_min = min_a[0,i]          #Reset pressure minimum token to current value
			else:
				pass
			c2+=1                         #Advance to next longitude
		c1+=1                           #Advance to next latitude
		
#print a_min_loc
#print min_a


#Snowless SLP array
#-----------------------------------------------------------------------------#

for i in range(limit):
	f = open("temp_b_slp%03d.txt" % i, 'r')	#Open file
	pcontent = f.readlines()          #Write each line into an array
	f.close()
	l = 0
	for j in range(len(m)):
		for k in range(len(n)):
			slp_b[i,j,k] = pcontent[l]    #Fills array with slp values as ordered in text file
			l+=1
	p_min = 10000                     #Set impossibly high value for pressure minimum token
	c1 = min_lat                      #Minumum latitude in area of interest
	while c1 <= max_lat:              #Maximum latitude in area of interest
		c2 = min_long                   #Minumum longitude in area of interest
		while c2 <= max_long:           #Maximum longitude in area of interest
			if slp_b[i,c1,c2] < p_min:    #If current value is less than current pressure minimum token
				min_b[0,i] = slp_b[i,c1,c2] #Store current pressure minimum
				b_min_loc[0,i] = c1         #Store latitude of current pressure minimum
				b_min_loc[1,i] = c2         #Store longitude of current pressure minimum
				min_b[1,i] = c2             #Store longitude of pressure minimum
				p_min = min_b[0,i]          #Reset pressure minimum token to current value
			else:
				pass
			c2+=1                         #Advance to next longitude
		c1+=1                           #Advance to next latitude
		
#print b_min_loc
#print min_b

#diff_loc = b_min_loc - a_min_loc
diff = min_b[0,:] - min_a[0,:]      #Calculates pressure difference
diff_long = (min_b[1,:] + min_a[1,:])/2.  #Estimates corresponding longitude values for dP

#print diff_loc
#print diff
#print diff_long

getstatusoutput('rm temp_*')        #Delete all temporary files


#Plotting
#-----------------------------------------------------------------------------#

fig = figure()
title('02/25-02/27 2008 Pressure minimum trajectory')
ax1 = fig.add_subplot(111)
ax1.plot(a_min_loc[1],a_min_loc[0],'r-')
ax1.plot(b_min_loc[1],b_min_loc[0],'b-')
ax1.set_ylabel('Latitudinal Value')
ax1.set_xlabel('Longitudinal Value')
ax1.legend(['Snowy', 'Snowless',], loc=2) #Controls contents and location of legend

ax2 = ax1.twinx()
ax2.plot(diff_long, diff, 'g-')
ax2.set_ylabel('Snowless SLP - Snowy SLP', color='g')
ax2.set_ylim(0,-7.5)                      #Sets limits on secondary y-axis
for tl in ax2.get_yticklabels():          #Makes secondary y-axis labels green
    tl.set_color('g')
show()

''' - Heatmapping for reference
X,Y = meshgrid(n,m)

figure()		
levels = linspace(800.0, 1050, 251)      #Creates colorbar levels
CP = contourf(X,Y,slp_a[5,:,:],levels)   #Creates contours with colors and data
cb = colorbar(CP)
xlim(0,208)
ylim(0,142)
show()
'''
