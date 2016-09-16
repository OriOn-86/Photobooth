#! /usr/bin/python
#
# Raspberry Pi PhotoBooth Managers 

#imports
from booth_constantes import *
from booth_functions import *
from sense_hat import SenseHat
import atexit
import os
import pygame
import random
import time

# pygame init
pygame.init()
pygame.mouse.set_visible(False)
pygame.time.Clock.tick(1) # 1fps?
Screen = pygame.display.set_mode((xScreen,yScreen))

# sensehat init
sense = SenseHat()
atexit.register(sense.clear())


Green = (34, 177, 76)
Orange = (255, 127, 39)
Red = (237, 28, 36)
OFF = (0, 0, 0)

MainFlag = True
while MainFlag:
	# list folders 
	folderList = [x[0] for x in os.walk(LOCAL_DIRECTORY + OUTPUT_DIRECTORY)]
	# display strip of randomly selected folder.
	Random_Strip = pygame.image.load(folderList[random.randrange(0, len(folderList), 1)] + "/SingleStrip.jpg")
	
	Screen.blit(Random_Strip, ((xScreen - Random_Strip.get_width()) / 2, (yScreen - Random_Strip.get_height()) / 2))
	pygame.display.flip()
	
	# get quantity of paper left in the printer and display it on the LED matrix.
	nbPaperLeft = os.system("php /var/www/pyhtonjobs.php?op=info")
	
	if nbPaperLeft <= 2:
		ON = Red
	elif nbPaperLeft <= 8:
		ON = Orange
	else:
		ON = Green

	LED_Matrix = []

	if nbPaperLeft > 0:
        nbPaperLeft *= 2
        for j in range(nbPaperLeft):
			LED_Matrix.append(ON)
        for k in range(64-nbPaperLeft):
			LED_Matrix.append(OFF)
        sense.set_pixels(LED_Matrix)
        time.sleep(5)
	else:
        LED_OFF = []
        for i in range(64):
			LED_Matrix.append(ON)
			LED_OFF.append(OFF)
        for i in range(5):
			sense.set_pixels(LED_Matrix)
			time.sleep(0.2)
			sense.set_pixels(LED_OFF)
			time.sleep(0.2)

