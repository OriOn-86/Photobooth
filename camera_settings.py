#! /usr/bin/python
import atexit
import io
import picamera
import pickle
import pygame
import time

''' default settings ...
	camera.PARAMETER = DEFAULT
		[Range of values available for parameter]
	camera.sharpness = 0
		[-100; 100]
	camera.contrast = 0
		[-100; 100]
	camera.brightness = 50
		[0; 100]
	camera.saturation = 0
		[-100; 100]
	camera.ISO = 0
		[100; 800]
	camera.exposure_compensation = 0
		[-10; 10]
	camera.exposure_mode = 'auto'
		[auto, night, nightpreview, backlight, spotlight, sport, snow, beach, verylong, fixedfps, antishake, fireworks]
	camera.meter_mode = 'average'
		[average, spot, backlit, matrix]
	camera.awb_mode = 'auto'
		[off, auto, sun, cloud, shade, tungsten, fluorescent, incandescent, flash, horizon]
	'''

SETTINGS_FILE = "Camera_Settings"
xStream, yStream = 640, 400
sizeStream = (xStream, yStream)
bytStream = bytearray(xStream * yStream * 4)

def preview_video_stream(camera):
	''' let user see parameters result '''
	vid_stream = io.BytesIO()
	camera.capture(vid_stream, use_video_port=True, format='rgba')
	vid_stream.seek(0)
	vid_stream.readinto(bytStream)
	vid_stream.close()
	img = pygame.image.frombuffer(bytStream[0: (xStream * yStream * 4)], sizeStream, 'RGBA')
	return img

def edit_parameter(parameter, value, increase):
	''' set a new value to paramter '''
	xMin = str(parameter) + "min"
	xMax = str(parameter) + "max"
	xStep = str(parameter) + "step"
	xValues = str(parameter) + "values"
	if parameter < 7:
		if increase:
			if value < camera_settings_range[xMax]:
				value = camera_settings[selected_setting[parameter]] + camera_settings_range[xStep]
		else:
			if value > camera_settings_range[xMin]:
				value = camera_settings[selected_setting[parameter]] - camera_settings_range[xStep]
	else:
		paramList = camera_settings_range[xValues]
		for keys, values in paramList.items():
			if values == value:
				x = keys
		if increase:
			if x < camera_settings_range[xMax]:
				value = paramList[x+1]
		else:
			if x > camera_settings_range[xMin]:
				value = paramList[x-1]
	return value


# init
camera_settings = dict()
camera_settings_range = {"1min":-100, "1max":100, "1step":1, "2min":-100, "2max":100, "2step":1, "3min":0, "3max":100, "3step":1, "4min":-100, "4max":100, "4step":1, "5min":0, "5max":800, "5step":100, "6min":-10, "6max":10, "6step":1, "7min":0, "7max":9, "7values":{0:"auto", 1:"night", 2:"nightpreview", 3:"backlight", 4:"spotlight", 5:"snow", 6:"beach", 7:"verylong", 8:"antishake", 9:"fireworks"}, "8min":0, "8max":4, "8values":{1:"average", 2:"spot", 3:"backlit", 4:"matrix"}, "9min":0, "9max":7, "9values":{0:"off", 1:"auto", 2:"shade", 3:"tungsten", 4:"fluorescent", 5:"incandescent", 6:"flash", 7:"horizon"}}
selected_setting = {1:"sharpness", 2:"contrast", 3:"brightness", 4:"saturation", 5:"ISO", 6:"exposure_compensation", 7:"exposure_mode", 8:"meter_mode", 9:"awb_mode"}
selected = 1
pygame.init()
pygame.mouse.set_visible(False)
Screen = pygame.display.set_mode(sizeStream)
camera = picamera.PiCamera()
camera.vflip = True
camera.resolution = sizeStream
atexit.register(camera.close)
time.sleep(2) # warm-up
font = pygame.font.Font(None, 20)

camera_settings["sharpness"] =  camera.sharpness 
camera_settings["contrast"] =  camera.contrast 
camera_settings["brightness"] = camera.brightness 
camera_settings["saturation"] = camera.saturation 
camera_settings["ISO"] = camera.ISO
camera_settings["exposure_compensation"] = camera.exposure_compensation 
camera_settings["exposure_mode"] = camera.exposure_mode
camera_settings["meter_mode"] = camera.meter_mode
camera_settings["awb_mode"] = camera.awb_mode

# Setting loop
SettingFlag = True
while SettingFlag:
	camera.sharpness = camera_settings["sharpness"]
	camera.contrast = camera_settings["contrast"]
	camera.brightness = camera_settings["brightness"]
	camera.saturation = camera_settings["saturation"] 
	camera.ISO = camera_settings["ISO"]
	camera.exposure_compensation = camera_settings["exposure_compensation"]
	camera.exposure_mode = camera_settings["exposure_mode"]
	camera.meter_mode = camera_settings["meter_mode"]
	camera.awb_mode = camera_settings["awb_mode"]

	img = preview_video_stream(camera)
	Screen.blit(img, (0,0))
	for i in range (1, 10):
		if i == selected:
			fontcolor = (255,255,255)
		else:
			fontcolor = (10,10,10)
		text = font.render(selected_setting[i], True, fontcolor)
		Screen.blit(text, (20,20*i))
		text = font.render(str(camera_settings[selected_setting[i]]), True, fontcolor)
		Screen.blit(text, (200, 20*i))
	pygame.display.update()
	for event in pygame.event.get():
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				SettingFlag = False
			if event.key == pygame.K_DOWN and selected < 9:
				selected += 1
			if event.key == pygame.K_UP and selected > 1:
				selected -= 1
			if event.key == pygame.K_RIGHT:
				camera_settings[selected_setting[selected]] = edit_parameter(selected, camera_settings[selected_setting[selected]], True)
			if event.key == pygame.K_LEFT:
				camera_settings[selected_setting[selected]] = edit_parameter(selected, camera_settings[selected_setting[selected]], False)

# save settings
with open(SETTINGS_FILE, "wb") as fichier:
	My_pikler = pickle.Pickler(fichier)
	My_pikler.dump(camera_settings)