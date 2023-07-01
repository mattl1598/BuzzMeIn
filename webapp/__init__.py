import json
from datetime import datetime
import random

from flask import Flask
from flask_socketio import SocketIO
from sass import compile
import os
from copy import deepcopy
from ast import literal_eval
from webapp.games import Snake


class Thermos(Flask):
	def __init__(self, *args):
		Flask.__init__(self, *args)
		self.game_rooms = {}
		self.session_map = {}


app = Thermos(__name__)
app.config['SECRET_KEY'] = "a secret key"
# save current working directory as root folder for webapp
app.config['ROOT_FOLDER'] = "C:/Users/mattl/PycharmProjects/BuzzMeIn"
app.config['IMG_FOLDER'] = app.config['ROOT_FOLDER'] + "/webapp/static/img/"
app.config['AUDIO_FOLDER'] = app.config['ROOT_FOLDER'] + "/webapp/static/audio/"
app.config['FLASK_ENV'] = "development"
app.env = 'development'

app.root = os.getcwd().replace("\\", "/")

app.scss_path = "static/scss/"
scss_paths = [
	app.root + "webapp/" + app.scss_path,
	app.root + "webapp/" + app.scss_path + "partials"
]


def get_text_colour(bg_colour):
	def luminance(RsRGB, GsRGB, BsRGB):
		if RsRGB <= 0.03928:
			R = RsRGB/12.92
		else:
			R = ((RsRGB+0.055)/1.055)**2.4
		if GsRGB <= 0.03928:
			G = GsRGB/12.92
		else:
			G = ((GsRGB+0.055)/1.055)**2.4
		if BsRGB <= 0.03928:
			B = BsRGB/12.92
		else:
			B = ((BsRGB+0.055)/1.055)**2.4

		return 0.2126*R + 0.7152*G + 0.0722*B

	def sRGB(r,g,b):
		return r/255, g/255, b/255

	def div(a, b):
		return a / b

	def hex_to_rgb(hex_string):
		if isinstance(hex_string, str):
			hex_string = hex_string.strip("#")
			part_length = len(hex_string) // 3
			hex_split = [hex_string[i:i + part_length] for i in range(0, len(hex_string), part_length)]

			rgb = [int(i, 16) for i in hex_split]

			return rgb
		else:
			return [
				float(hex_string.r),
				float(hex_string.g),
				float(hex_string.b)
			]

	bg_rgb = hex_to_rgb(bg_colour)
	bl_rgb = hex_to_rgb("#000000")
	wh_rgb = hex_to_rgb("#ffffff")

	bl_bg_contrast = div(*sorted([luminance(*sRGB(*bg_rgb))+0.05, luminance(*sRGB(*bl_rgb))+0.05], reverse=True))
	wh_bg_contrast = div(*sorted([luminance(*sRGB(*bg_rgb))+0.05, luminance(*sRGB(*wh_rgb))+0.05], reverse=True))

	if wh_bg_contrast > bl_bg_contrast:
		return "#ffffff"
	else:
		return "#000000"


def rand(x):
	# return Number(random.random()*int(x))
	return str(random.random()*int(x.value))


def mod(x, y):
	# return Number(x % y)
	return str(int(x.value % y.value))


def ordinal(number: int) -> str:
	if number in [11,12,13]:
		pass
	elif number % 10 == 1:
		return "st"
	elif number % 10 == 2:
		return "nd"
	elif number % 10 == 3:
		return "rd"

	return "th"


compile(
	dirname=(app.config['ROOT_FOLDER']+"/webapp/static/scss", "webapp/static/css/"),
	output_style="compressed",
	custom_functions={
		'random': rand,
		'mod': mod,
		'get_text_colour': get_text_colour
	}
)


# initialise socketio plugin
socketio = SocketIO(app)

app.jinja_env.globals.update(
			chr=chr,
			str=str,
			len=len,
			type=type,
			list=list,
			datetime=datetime,
			json=json,
			get_text_colour=get_text_colour,
			ordinal=ordinal
		)

from webapp import routes
