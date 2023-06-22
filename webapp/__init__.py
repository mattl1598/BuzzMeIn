from random import randint

from flask import Flask
from flask_socketio import SocketIO
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
app.config['ROOT_FOLDER'] = "E:\\004_Repos\\BuzzMeIn"
app.config['FLASK_ENV'] = "development"
app.env = 'development'


# initialise socketio plugin
socketio = SocketIO(app)

app.jinja_env.globals.update(chr=chr, str=str)

from webapp import routes
