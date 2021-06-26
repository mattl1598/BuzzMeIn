from webapp import app, socketio
from flask import render_template, url_for, request, redirect, session, flash, abort, make_response, send_file, jsonify
from flask_socketio import emit, join_room, leave_room, send
from copy import deepcopy
from random import randint
from ast import literal_eval
from webapp.games import Snake
from webapp.words import nouns


@app.route("/")
def landing():
	css_files = ["snake.css"]
	return render_template("snake.html", rows=10, cols=10, template_css_files=css_files)


@app.route("/snake")
def snake():
	room = request.args.get("room")
	css_files = ["snake.css"]
	return render_template("snake.html", room=room, rows=10, cols=10, template_css_files=css_files)


@app.route("/lobby")
def lobby():
	return render_template("lobby.html")


@app.route("/headless")
def headless_remote():
	room = request.args.get("room")
	css_files = ["remote.css"]
	return render_template("remote.html", room=room, template_css_files=css_files)


@app.route("/remote")
def remote():
	room = request.args.get("room")
	css_files = ["remote.css"]
	return render_template("remote.html", room=room, template_css_files=css_files)


@app.route("/rooms_test")
def rooms_test():
	return render_template("rooms_test.html")


@socketio.on('remote', namespace="/test")
def handle_message(data):
	room = data["room"]
	print(str(data))
	print('received message: ' + str(data["data"]))
	# emit('test', {'data': data["data"]}, broadcast=True)
	app.game_rooms[room].update_direction(data["data"])


@socketio.on('update', namespace="/test")
def handle_message(data):
	room = data["room"]
	diffs, status = app.game_rooms[room].game_tick()
	if status == "safe":
		emit('grid', {'content': diffs}, broadcast=True, to=room)
	else:
		emit('fail', {'message': "Game Over", "content": diffs}, broadcast=True, to=room)


@socketio.on('restart', namespace="/test")
def handle_message(data):
	room = data["room"]
	diffs = app.game_rooms[room].reset()
	emit('grid', {'content': diffs, "stopped": True, "clear": True}, broadcast=True, to=room)


@socketio.on('play_pause', namespace="/test")
def handle_message(data):
	room = data["room"]
	emit('play_pause', broadcast=True, to=room)


@socketio.on('ppAck', namespace="/test")
def handle_message(data):
	room = data["room"]
	emit('ppAck', data, broadcast=True, to=room)


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
	# diffs = dict(set(app.snake["test"]["grid"].items()).difference(set(app.grid_blank.items())))
	# diffs = app.snake_rooms["test"].diffs_from_blank()
	# emit('grid', {'content': diffs}, broadcast=True, to=room)


@socketio.on('join', namespace="/test")
def handle_join(data):
	room = data["room"]
	client_type = data["client_type"]
	join_room(room)
	print(f'{client_type} joined room "{room}"')
	if client_type == "display":
		app.game_rooms[room] = Snake(rows=10, cols=10, mode="diffs")
		diffs = app.game_rooms[room].diffs_from_blank()
		emit('grid', {'content': diffs}, broadcast=True, to=room)


@socketio.on('leave', namespace="/test")
def handle_leave(data):
	room = data["room"]
	client_type = data["client_type"]
	leave_room(room)
	print(f'{client_type} left room "{room}"')


@socketio.on('reset', namespace="/test")
def handle_message():
	diffs = dict(set(app.snake["test"]["grid"].items()).difference(set(app.grid_blank.items())))
	emit('grid', {'content': diffs}, broadcast=True)
	print("test")


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
