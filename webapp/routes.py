from datetime import datetime

import corha as corha

from webapp import app, socketio
from flask import render_template, url_for, request, redirect, session, flash, abort, make_response, send_file, jsonify
from flask_socketio import emit, join_room, leave_room, send, rooms
from copy import deepcopy
from random import randint
from ast import literal_eval
from webapp.games import Snake
from webapp.words import nouns


@app.route("/")
def landing():
	return redirect(url_for("lobby"))


@app.route("/lobby")
def lobby():
	return render_template("lobby.html")


@app.route("/host")
def host():
	css_files = ["host.css"]
	return render_template("host.html", template_css_files=css_files)


@app.route("/remote")
def remote():
	room = request.args.get("room")
	player = request.args.get("room")
	css_files = ["remote.css"]
	http_sid = session["session_id"]
	return render_template("remote.html", room=room, player=player, template_css_files=css_files, http_sid=http_sid)


@socketio.on('rooms', namespace="/test")
def rooms_test(data):
	identify({"type": "server", "room": data["room"]})
	emit('identify', {}, broadcast=True, include_self=True)


@socketio.on('identify', namespace="/test")
def identify(data):
	if data["type"] == "server":
		app.game_rooms[data["room"]] = {"mode": "buzzer", "host": "", "players": {}}
	elif data["type"] == "host":
		app.game_rooms[data["room"]]["host"] = request.sid
	elif data["type"] == "player":
		app.game_rooms[data["room"]]["players"][request.sid] = {
			"name": data["player"],
			"sid": request.sid,
			"score": data["score"]
		}
		# if app.game_rooms[data["room"]]["players"].get(request.sid) is None:
		# else:
		# 	# update this
		# 	app.game_rooms[data["room"]]["players"][request.sid] = {
		# 		"name": data["player"],
		# 		"sid": request.sid,
		# 		"score": data["score"]
		# 	}

	emit("identified", app.game_rooms[data["room"]], broadcast=True)


@socketio.on('scoring', namespace="/test")
def scoring(data):
	if request.sid == app.game_rooms[data["room"]]["host"]:
		if data["instruction"] == "modify":
			app.game_rooms[data["room"]]["players"][data["target"]]["score"] += data["modification"]

		emit("scores", app.game_rooms[data["room"]], broadcast=True)


@socketio.on('gamemode', namespace="/test")
def gamemode(data):
	if request.sid == app.game_rooms[data["room"]]["host"]:
		app.game_rooms[data["room"]]["mode"] = data["mode"]
		print(app.game_rooms[data["room"]]["mode"])


@socketio.on('buzz', namespace="/test")
def handle_buzz(data):
	print(str(data))
	emit('buzzed', data, broadcast=True)


@socketio.on('lock', namespace="/test")
def handle_lock(data):
	emit('lock', data, broadcast=True)


@socketio.on('release', namespace="/test")
def handle_release(data):
	emit('release', data, broadcast=True)


# socket io testing
# TODO clean up, remove if not needed
@socketio.on('test', namespace="/test")
def handle_message(data):
	print(str(data))
	print('received message: ' + str(data["data"]))
	emit('test', {'data': data["data"]}, broadcast=True)


# more different socket io testing
@socketio.on('connect', namespace="/test")
def handle_connect():
	print("connection made")
	print(request.sid)


@socketio.on('join', namespace="/test")
def handle_join(data):
	room = data["room"]
	client_type = data["client_type"]

	valid = True

	# if room doesn't exist
	if app.game_rooms.get(room) is None and client_type == "remote":
		emit('error', {"error": "room does not exist"})
		valid = False
	elif client_type == "host" and app.game_rooms.get(room) is None:
		print("created room")
		http_sid = data["http_sid"]
		app.session_map[http_sid] = request.sid
		app.game_rooms[room] = {"mode": "buzzer", "host": request.sid, "players": {}}
		print(app.game_rooms[room])
	elif client_type == "host":
		http_sid = data["http_sid"]
		if app.session_map[http_sid] == app.game_rooms[room]["host"]:
			app.session_map[http_sid] = request.sid
			app.game_rooms[room]["host"] = request.sid
		else:
			emit('error', {"error": "host already connected"})
			valid = False
	elif client_type == "remote":
		# synchronising socket session id with http session id
		if (old_sid := app.session_map.get("http_sid")) is not None and app.game_rooms[room]["players"].get(old_sid) is not None:
			http_sid = data["http_sid"]
			app.session_map[http_sid] = request.sid
			app.game_rooms[room]["players"][request.sid] = app.game_rooms[room]["players"].pop(old_sid)
		else:
			app.game_rooms[room]["players"][request.sid] = {
				"name": data["name"],
				"sid": request.sid,
				"score": 0
			}
	if valid:
		join_room(room)
		emit('connected', {"sid": request.sid})
		print(f'{client_type} joined room "{room}"')
		emit("identified", app.game_rooms[room], broadcast=True)


@socketio.on('leave', namespace="/test")
def handle_leave(data):
	room = data["room"]
	client_type = data["client_type"]
	leave_room(room)
	print(f'{client_type} left room "{room}"')


@app.route("/random_word")
def random_word():
	used_words = app.game_rooms.keys()
	unused_words = list(set(nouns["nouns"]).difference(set(used_words)))
	new_word = str(unused_words[randint(0, len(unused_words) - 1)])
	print(new_word)
	return new_word


@app.route("/static", methods=["GET"])
def static_loader():
	"""
	GET:
		description: single route for requesting concatenated static files, either JS or CSS

		args:
			t: type of file, either "js" or "css"

			q: filenames of requested files in order, separated by "&" in the url

		security: None required

		responses:
			200: returns the requested js or css files all concatenated together

			404: error not found if the requested filetype is neither js or css

	:authors:
		- Matt
	:returns: HTTP Response
	"""
	# lookup table for mimetypes
	mimetype_lookup = {
		"js": "text/javascript",
		"css": "text/css"
	}
	# load url args from request object
	args = request.args
	filetype = args["t"]
	if filetype in ["js", "css"]:
		file_list = args["q"].split(" ")
		output = []
		for file in file_list:
			# load and concatenate all of the requested files
			with open(
					str(app.config['ROOT_FOLDER'] + "/webapp/static/" + filetype + "/" + file).replace("\\", "/"),
					"r") as contents:
				output.append(contents.read())
		# create http response from concatenated files
		response = make_response("\n".join(output))
		# set correct mimetype for response
		response.mimetype = mimetype_lookup[filetype]
		return response
	else:
		abort(404)


@app.before_request
def before_request():
	if session.get("session_id") is None:
		session["session_id"] = corha.rand_string(datetime.utcnow().isoformat(), 64, [])
		session.modified = True
