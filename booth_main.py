#! /usr/bin/python
#
# Raspberry Pi PhotoBooth
''' Main file '''

# import required libraries 
import atexit
import io
import os
import picamera
import pickle
import pygame
import RPi.GPIO as GPIO
import sys
import threading
import time
from booth_constantes import *
from booth_functions import *

# try to load custom parameters file
cam_default_settings = True
try: 
	with open(SETTINGS_FILE, "rb") as file:
		depikler = pickle.Unpickler(file)
		camera_settings = depikler.load()
		cam_default_settings = False
	# check brightness parameter to validate the file.
	try:
		set_brightness = camera_settings[brightness]
	except KeyError:
		cam_default_settings = True
except:
	cam_default_settings = True
# if file found, ask user for use of custom parameters.
if not cam_default_settings:
	UseCustom = str()
	while UseCustom.lower() != "y" and UseCustom.lower() != "n":
		UseCustom = input("Custom settings for the camera are available. Do you want to use them ? (y/n) ")
	if UseCustom.lower() == "n":
		cam_default_settings = True

# select theme	
selectedTheme = "N"
while Theme.lower()	!= "c" and Theme.lower() != "n":
	Theme = input("Select theme to use. (n: normal or c: comic) ")
if Theme.lower() == "c":
	selectedTheme = "C"

''' setup GPIO pins '''
GPIO.setmode(GPIO.BCM)
atexit.register(GPIO.cleanup)
GPIO.setup(PIR_GPIO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PuBu_GPIO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(Coin_GPIO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(PuBuLED_GPIO_PIN, GPIO.OUT)

''' initialization of pygame '''
pygame.init()
pygame.mouse.set_visible(False)
Screen = pygame.display.set_mode((xScreen,yScreen))
if selectedTheme == "N":
	# load frames for normal theme
	Home_Screen = pygame.image.load(MAIN_SCREEN)
	Display_Screen = pygame.image.load(DISPLAY_SCREEN)
	Prepare_Screen = pygame.image.load(PREPARE_SCREEN)
	Print_Screen = pygame.image.load(PRINT_SCREEN)
else:
	# load frames for comics theme
	Home_Screen = pygame.image.load(MAIN_SCREEN_COMIC)
	Display_Screen = pygame.image.load(DISPLAY_SCREEN_COMIC)
	Prepare_Screen = pygame.image.load(PREPARE_SCREEN_COMIC)
# load oter frames
Disp1 = pygame.image.load(COUNTDOWN_1)
Disp2 = pygame.image.load(COUNTDOWN_2)
Disp3 = pygame.image.load(COUNTDOWN_3)

''' Main loop '''
status = MAIN
MainFlag = True
while MainFlag:
	if status == MAIN:
		''' MAIN ...
			- display welcome screen
			- make button blink
			- wait for user input '''
		# Screen update
		Screen.blit(Home_Screen, (0,0))
		pygame.display.flip()
		# Blink
		e = threading.Event()
		blinkThread = threading.Thread(target=button_led_blink, args=(e,TIME_BLINK))
		blinkThread.start()
		# wait for button        
		WaitForButton = True
		while WaitForButton:
			if not GPIO.input(PuBu_GPIO_PIN):
				WaitForButton = False
				e.set()
				status = SHOOT
			for event in pygame.event.get():
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_ESCAPE:
						WaitForButton = False
						e.set()
						MainFlag = False

	elif status == SHOOT:
		''' SHOOT ...
			- Init Camera
			- Create folder
			- Start stream
			- Shoot 3 pictures 
			- Make the strips '''
		# Init camera settings 
		Screen = pygame.display.set_mode(sizeStream)
		camera = picamera.PiCamera()
		camera.vflip = True
		camera.hflip = True
		camera.resolution = sizeStream
		atexit.register(camera.close)
		if not cam_default_settings:
			LoadCameraSettings(camera)
		# folder
		new_folder = generate_folder()
		new_folder += "/"
		# Start streaming
		img = preview_video_stream(camera)
		Screen.blit(img, (0,0))
		pygame.display.update()
		# 5 seconds to get ready
		Tstart = time.clock()
		while time.clock() - Tstart < 5:
			img = preview_video_stream(camera)
			Screen.blit(img, (0,0))
			pygame.display.update()
		# shoot photos 
		for i in range(1,4):
			LastPhotoTime = time.clock()
			while time.clock() - LastPhotoTime < TIME_INTERVAL:
				img = preview_video_stream(camera)
				Screen.blit(img, (0,0))
				if time.clock() - TIME_INTERVAL + 1 > LastPhotoTime:
					Screen.blit(Disp1,((xStream - Disp1.get_width()) / 2, (yStream - Disp1.get_height()) / 2))
				elif time.clock() - TIME_INTERVAL + 2 > LastPhotoTime:
					Screen.blit(Disp2,((xStream - Disp2.get_width()) / 2, (yStream - Disp2.get_height()) / 2))
				elif time.clock() - TIME_INTERVAL + 3 > LastPhotoTime:
					Screen.blit(Disp3,((xStream - Disp3.get_width()) / 2, (yStream - Disp3.get_height()) / 2))
				else:
					Screen.blit(DispSave,(0,0))
				pygame.display.update()
			snap_photo(camera, new_folder + "image" + str(i) + ".jpeg")
		camera.close()
		# Make the strips
		Screen = pygame.display.set_mode((xScreen,yScreen))
		Screen.blit(Prepare_Screen, (0,0))
		pygame.display.update()
		if selectedTheme == "N":
			DispStrip = create_strips(new_folder)
		else:
			DispStrip = create_comicStrips(new_folder)
		status = DISPLAY

	elif status == DISPLAY:
		''' display and eventual coin to print '''
		# screen
		Screen.blit(Display_Screen, (0,0))
		DispStrip = pygame.transform.scale(DispStrip, (324, 959))
		Screen.blit(DispStrip, (0,0))
		pygame.display.update()
		# publish on the webpage
		db_publish_on_website(new_folder)
		# Coin or leave
		WaitForCoin = True
		Tstart = time.clock()
		while WaitForCoin:
			if GPIO.input(Coin_GPIO_PIN):
				status = PRINT
				WaitForCoin = False
			if (time.clock() - Tstart) > (TIME_DISPLAY * 2):
				status = MAIN
				WaitForCoin = False

	elif status == PRINT:
		''' printout the dual strips '''
		# screen
		Screen.blit(Print_Screen, (0, 0))
		pygame.display.update()
		# print
		print_strip(new_folder)
		# end
		time.sleep(TIME_DISPLAY)
		status = MAIN

	else:
		status = MAIN
