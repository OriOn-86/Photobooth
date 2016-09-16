#! /usr/bin/python
#
# Raspberry Pi PhotoBooth
''' functions file
    declare all functions ''' 

# import required libraries
import io
import MySQLdb
import os
import pygame
import RPi.GPIO as GPIO
import time
from booth_constantes import *

def button_led_blink(e, speed):
	''' function built to be used inside a thread with event e stopping it. '''
	while not e.isSet():
		GPIO.output(PuBuLED_GPIO_PIN, True)## Switch on 
		e.wait(speed)## Wait
		GPIO.output(PuBuLED_GPIO_PIN, False)## Switch off 
		e.wait(speed)## Wait
	GPIO.output(PuBuLED_GPIO_PIN, False)

def create_strips(folder_name):
	''' Creates the 2 photo strips ...
		1 simple for display and download on the webinterface (3 pictures + footer).
		1 double for printout '''
	global xStrip, yStrip
	xMargin = 162 # 324 / 2
	yMargin = 486 # 972 / 2
	photos = os.listdir(folder_name)
	if 'image1.jpeg' not in photos or 'image2.jpeg' not in photos or 'image3.jpeg' not in photos:
		print ("Could not process folder {}".format(folder_name))
		return
	# create the single strip
	Strip = pygame.Surface((xStrip, yStrip))
	background = pygame.image.load(BG_STRIP, 'jpg')
	background = pygame.transform.scale(background, (xStrip, yStrip))
	Strip.blit(background, (0,0))
	i = 1
	while i <= NB_PIC:
		photo_name = folder_name + "image" + str(i) + ".jpeg"
		photo = pygame.image.load(photo_name, 'jpg')
		photo = pygame.transform.scale(photo, (photo.get_width() / 2, photo.get_height() / 2))
		Strip.blit(photo, (xMargin, yMargin))
		i += 1
		yMargin += 2268/2
	pygame.image.save(Strip, folder_name + "SingleStrip.jpg")
	os.system("sudo chown pi " + folder_name + "SingleStrip.jpg")
	os.system("sudo chgrp pi " + folder_name + "SingleStrip.jpg")
	# publish
	db_publish_on_website(folder_name)
	# create the double strip
	DoubleStrip = pygame.Surface((2 * xStrip, yStrip))
	DoubleStrip.blit(Strip, (0, 0))
	DoubleStrip.blit(Strip, (xStrip, 0))
	pygame.image.save(DoubleStrip, folder_name + "DoubleStrip.jpg")
	os.system("sudo chown pi " + folder_name + "DoubleStrip.jpg")
	os.system("sudo chgrp pi " + folder_name + "DoubleStrip.jpg")
	return Strip

def generate_folder():
	''' generate a folder named based on date and time YYYY-MM-DD hh:mm:ss ''' 
	folder_name = LOCAL_DIRECTORY + OUTPUT_DIRECTORY + time.strftime("%Y%m%d_%H%M%S", time.localtime())
	os.makedirs(folder_name)
	os.system("sudo chown pi " + folder_name)
	os.system("sudo chgrp pi " + folder_name)
	return folder_name

def motion_detected(pir_sensor):
	''' when motion is detected, awake the photobooth '''
	WakeUp()

def preview_video_stream(camera):
	''' let the people see themselves before a photo is taken '''
	vid_stream = io.BytesIO()
	camera.capture(vid_stream, use_video_port=True, format='rgba')
	vid_stream.seek(0)
	vid_stream.readinto(bytStream)
	vid_stream.close()
	img = pygame.image.frombuffer(bytStream[0: (xStream * yStream * 4)], sizeStream, 'RGBA')
	return img

def print_strip	(folder_name):
	os.system("lp -d Canon_CP910 " + folder_name + "DoubleStrip.jpg")
	db_print_strip(folder_name)

def snap_photo(camera, file_name):
	''' takes a photo and store it a file with a unique name '''
	camera.resolution = rezPhoto
	camera.capture(file_name, use_video_port=False, format='jpeg', thumbnail=None)
	os.system("sudo chown pi " + file_name)
	os.system("sudo chgrp pi " + file_name)
	camera.resolution = sizeStream

def WakeUp():
	## Turn on screen
	os.system("xset dpms force on")
	## Turn on photo lights
	GPIO.output(LLight_PIN, True)
	GPIO.output(RLight_PIN, True)
	## wait 2 seconds
	time.sleep(2)
	## Turn off the OFF Light
	GPIO.output(OffLight_PIN, True)

def SleepMode():
	## Turn on the OFF Light
	GPIO.output(OffLight_PIN, False)
	## wait 2 seconds
	time.sleep(2)
	## Turn off screen
	os.system("xset dpms force off")
	## Turn off photo lights
	GPIO.output(LLight_PIN, False)
	GPIO.output(RLight_PIN, False)
	
''' SQL Functions '''
def db_connect():
	''' connect to DB '''
	return MySQLdb.connect(host="localhost", user="root", passwd="raspberry", db="photobooth")

def db_print_strip(folder_name):
	''' inform db about printing '''
	db = db_connect()
	cur = db.cursor()
	currentTime = time.strftime("%Y%m%d%H%M%S", time.localtime())
	# update strip table 
	cur.execute("UPDATE `strips` SET `printed`=True WHERE `filename`=%s",(folder_name))
	db.commit()
	# udpate printer table
	paperleft = db_printer_status()
	cur.execute("INSERT INTO `paperleft` (`paperleft`, `time`) VALUES (%s, %s)", (paperleft-1, currentTime))
	db.commit()
	db.close()

def db_printer_status():
	''' Return paper quantity '''
	db = db_connect()
	cur = db.cursor()
	cur.execute("SELECT `paperleft` FROM `printerstatus` ORDER BY `time` DESC LIMIT 1")
	row = cur.fetchone()
	db.close()
	return row

def db_publish_on_website(folder_name):
	''' Add the strip on the website for download '''
	db = db_connect()
	cur = db.cursor()
	currentTime = time.strftime("%Y%m%d%H%M%S", time.localtime())
	# check that name doesn't already exists
	cur.execute("SELECT * FROM `strips` WHERE `filename` = %s", (folder_name))
	if cur.fetchone() == None :
		# Insert new strip in DB
		cur.execute("INSERT INTO `strips` (`filename`, `time`) VALUES (%s, %s)", (folder_name, currentTime))
		db.commit()
	db.close()
	
