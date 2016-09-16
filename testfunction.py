#!/usr/bin/python

from booth_functions import *
import atexit
import os
import time
import sys
import picamera

camera = picamera.PiCamera()
atexit.register(camera.close)

def print_options():
	print ("for this program you need to enter a parameter:")
	print ("	-c folder_name		for Strip Creation from the folder specified")
	print ("	-p photo_name		for photo snapshot")
	print ("	-s 					screen status")
	print (" 	-w folder_name		to publish on the website")


print ("---")
if len(sys.argv) > 1:
	if sys.argv[1] == "-c":
		''' create strip ''' 
		print ("create strip with " + sys.argv[2])
		create_strips(sys.argv[2])
	
	if sys.argv[1] == "-p":
		''' photo '''
		print ("taking photo : " + sys.argv[2])
		snap_photo(camera, sys.argv[2])
		
	if sys.argv[1] == "-s":
		''' Switch off screen and switch back on '''
		os.system("xset dpms force off")
		time.sleep(5)
		os.system("xset dpms force on")
		
		
	if sys.argv[1] == "-w":
		''' publish '''
		print ("publishing " + sys.argv[2])
		db_publish_on_website(sys.argv[2])
	
	else:
		print_options()
	print ("---")
else:
	print_options()
	
	sys.exit()


