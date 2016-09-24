#! /usr/bin/python
#
# Raspberry Pi PhotoBooth
''' Constants file
    stores all fix parameter of the program '''

# GPIO pin for the different elements
PIR_GPIO_PIN = 17 #PIR sensor
PuBu_GPIO_PIN = 23 #Push Button
PuBuLED_GPIO_PIN = 24 # Push Button LED
Coin_GPIO_PIN = 22 # Coin Signal
OffLight_PIN = 26 # Off Light
LLight_PIN = 19 # Left Light
RLight_PIN = 13 # Right Light

# paths
LOCAL_DIRECTORY = "/home/pi/orionbooth/"
WWW_DIRECTORY = "/var/www/boothpictures/"
OUTPUT_DIRECTORY = "Photobooth_images/"
IMAGES_FOLDER = "images/"
SETTINGS_FILE = "Camera_Settings"

# Screens Normal Theme
BG_STRIP = LOCAL_DIRECTORY + IMAGES_FOLDER + "bgStrip.jpg"
DISPLAY_SCREEN = LOCAL_DIRECTORY + IMAGES_FOLDER + "After_photo_screen.jpg"
MAIN_SCREEN = LOCAL_DIRECTORY + IMAGES_FOLDER + "WelcomeScreen.jpg" 
PREPARE_SCREEN = LOCAL_DIRECTORY + IMAGES_FOLDER + "Preparing.jpg"
PRINT_SCREEN = LOCAL_DIRECTORY + IMAGES_FOLDER + "Printing.jpg"
# Screens BG Theme
BG_STRIP_COMIC = LOCAL_DIRECTORY + IMAGES_FOLDER + "bgStripComic.jpg"
DISPLAY_SCREEN_COMIC = LOCAL_DIRECTORY + IMAGES_FOLDER + "After_photo_screenComic.jpg"
MAIN_SCREEN_COMIC = LOCAL_DIRECTORY + IMAGES_FOLDER + "WelcomeScreenComic.jpg" 
PREPARE_SCREEN_COMIC = LOCAL_DIRECTORY + IMAGES_FOLDER + "PreparingComic.jpg"
# common
COUNTDOWN_1 = LOCAL_DIRECTORY + IMAGES_FOLDER + "1.png"
COUNTDOWN_2 = LOCAL_DIRECTORY + IMAGES_FOLDER + "2.png"
COUNTDOWN_3 = LOCAL_DIRECTORY + IMAGES_FOLDER + "3.png"

# Main loop different states
MAIN, SHOOT, DISPLAY, PRINT = range(4)

# time vars
TIME_INTERVAL = 3
TIME_DISPLAY = 10
TIME_BLINK = 0.5

# photo vars
xPhoto, yPhoto = 2592, 1944
rezPhoto = (xPhoto, yPhoto)

# screen vars
xScreen, yScreen = 1280, 1024
rezScreen = (xScreen, yScreen)

# stream vars
xStream, yStream = 640, 400
sizeStream = (xStream, yStream)
bytStream = bytearray(xStream * yStream * 4)

# Strip vars
NB_PIC = 3
xStrip = 1620 # 3240 / 2
yStrip = 4795 # 9590 / 2