from random import randint

from flask import Flask
from flask_socketio import SocketIO
import os
from copy import deepcopy
from ast import literal_eval
from webapp.games import Snake

app = Flask(__name__)
# app.config['SECRET_KEY']
# save current working directory as root folder for webapp
app.config['ROOT_FOLDER'] = os.getcwd()

app.game_rooms = {}

# initialise socketio plugin
socketio = SocketIO(app)

app.jinja_env.globals.update(chr=chr, str=str)

from webapp import routes
