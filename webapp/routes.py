import random
from datetime import datetime

import corha as corha

from webapp import app, socketio
from flask import render_template, send_from_directory, url_for, request, redirect, session, flash, abort, \
	make_response, send_file, jsonify
from flask_socketio import emit, join_room, leave_room, send, rooms
from copy import deepcopy
from random import randint
from ast import literal_eval
from webapp.games import Snake
from webapp.words import nouns


questions = {
	"music": {
		0: {"q": "/audio/boogiewonderland.mp3", "a": "Boogie Wonderland", "f": 8, "t": 17.3},
		1: {"q": "/audio/reach.mp3", "a": "Reach", "f": 8, "t": 16.1},
		2: {"q": "/audio/dontstop.mp3", "a": "Don't Stop", "f": 9, "t": 17.5},
		3: {"q": "/audio/thriller.mp3", "a": "Thriller", "f": 40, "t": 59}
	},
	"smash": {
		0: {
			"q": "What are the Officials in Tennis are called?",
			"i": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/56/Donald_Trump_official_portrait.jpg/330px-Donald_Trump_official_portrait.jpg",
			"a": "Donald Trumpires"
		},
		1: {
			"q": "Which Author wrote the Discworld series of books?",
			"i": "/img/hatter.jpg",
			"a": "The Mad HatTerry Pratchett"
		},
		2: {
			"q": "What institution is currently responsible for putting up interest rates?",
			"i": "/img/caliban.jpg",
			"a": "CaliBank of England"
		},
		3: {
			"q": "Who helped Jason retrieve the golden fleece?",
			"i": "/img/abanazar.jpg",
			"a": "AbanazARgonauts"
		},
		4: {
			"q": "The act that had a hit with Seven Nation Army were The......",
			"i": "/img/snowwhite.jpg",
			"a": "Snow White Stripes"
		}
	},
	"averages": {
		0: {
			"q": "How many words in the Tempest?",
			"a": "16,663"
		},
		1: {
			"q": "According to boxofficemojo, How much in US$ did Tim Burtons' Alice in Wonderland make at the box office worldwide?",
			"a": "$1,025,467,110"
		},
		2: {
			"q": "According to our records – How many photos from past shows are currently available on our website?",
			"a": "6,964"
		},
		3: {
			"q": "According the boxofficemojo, How much did Noel Coward’s 1945 film Brief Encounter make at the box office worldwide?",
			"a": "$87,103"
		},
		4: {
			"q": "According to our records - including tonight - What is the total amount the Silchester Players have given to charity?",
			"a":  "£50,010"
		}
	},
	"gho": {
		0: {
			"q": "Which of our 2013 plays took us into space?",
			"a": "They Came From Mars And Landed Outside the Farndale Avenue Church Hall In Time For the Townswomen's Guild Coffee Morning"
		},
		1: {
			"q": "The Players performed The Tempest recently but which Shakespeare play is about two star-crossed lovers?",
			"a": "Romeo and Juliet"
		},
		2: {
			"q": "Which play by Oscar Wilde features the line 'A Handbag'",
			"a": "The Importance of Being Earnest"
		},
		3: {
			"q": "In 2004, which comedy by Norman Robbins did we perform that was the sequel to “A Tomb with a View?",
			"a": "Tiptoe through the Tombstones"
		},
		4: {
			"q": "In 2001 we performed which Agatha Christie play set on a mysterious island?",
			"a": "And Then There Were None"
		},
		5: {
			"q": "Which of our recent Pantomimes was also our first in 1976?",
			"a": "Snow White and the Seven Dwarves"
		}
	},
	"dating": {
		0: {
			"q": "We performed The Tempest recently but in which year was Shakespeare born?",
			"a": "1564"
		},
		1: {
			"q": "In what year was Alice in Wonderland by Lewis Carrol first published? ",
			"a": "1865"
		},
		2: {
			"q": "In what year was Disney’s Snow White and the Seven Dwarves released?",
			"a": "1937"
		},
		3: {
			"q": "Richard Whittington was the inspiration for “Dick Whittington” but when did he become Lord Mayor of London?",
			"a": "1397"
		},
		4: {
			"q": "In Rhythm of Life we performed songs from the musical Matilda, but what year was the novel by Roald Dahl first published?",
			"a": "1988"
		}
	}
}

@app.route("/")
def landing():
	return redirect(url_for("lobby"))


@app.route("/lobby")
def lobby():
	return render_template("lobby.html")


@app.route("/join")
def join_menu():
	room = request.args.get("room")
	css_files = ["remote.css"]
	return render_template("join.html", room=room, template_css_files=css_files)


@app.route("/host")
def host():
	css_files = ["host.css"]
	return render_template("host.html", template_css_files=css_files)


@app.route("/remote")
def remote():
	room = request.args.get("room")
	player = request.args.get("player")
	css_files = ["remote.css"]
	http_sid = session["session_id"]
	return render_template("remote.html", room=room, player=player, template_css_files=css_files, http_sid=http_sid)


@app.route("/title")
def title():
	css_files = ["title.css"]
	room = request.args.get("room")
	if room is None:
		return redirect("/title?room=demo&goto=scores")
	goto = request.args.get("goto")
	with open(app.config['IMG_FOLDER'] + "logo.svg", "r") as f:
		logo = f.read()
	return render_template(
		"title.html",
		logo=logo,
		goto=goto,
		room=room,
		template_css_files=css_files
	)


@app.route("/scores")
def scores():
	room = request.args.get("room")
	css_files = ["scores.css"]
	players = []

	if room is None:
		return redirect("/scores?room=demo")
	elif room == "demo":
		imax = 6
		for i in range(0, imax):
			players.append({"name": nouns["nouns"][int((i+1)*len(nouns["nouns"])/imax)-1], "score": random.randint(0, 30)})
	elif room in app.game_rooms.keys():
		game = app.game_rooms[room]["players"]
		for player in game.values():
			players.append(
				{"name": player["name"], "score": player["score"]}
			)
	else:
		abort(404)

	players.sort(key=lambda i: i.get("score"), reverse=True)
	return render_template(
		"scores.html",
		room=room,
		players=players,
		template_css_files=css_files
	)


@app.get("/round_reveal")
def round_reveal():
	room = request.args.get("room")
	css_files = ["round_reveal.css"]
	round_name = ""
	if room is None:
		return redirect("/round_reveal?room=demo")
	elif room == "demo":
		round_name = "Games Hall of"
	elif room in app.game_rooms.keys():
		round_lookup = {
			"smash": "Answer Smash",
			"averages": "Distinctly Average",
			"music": "Win When They're Singing",
			"gho": "Games Hall of",
			"dating": "I'm Terrible at Dating"
		}
		round_name = round_lookup.get(app.game_rooms[room]["mode"])

	return render_template(
		"round_reveal.html",
		round_name=round_name,
		room=room,
		template_css_files=css_files
	)


@app.get("/blank")
def blank():
	room = request.args.get("room")
	css_files = ["round_reveal.css"]
	if room is None:
		return redirect("/blank?room=demo")

	return render_template(
		"round_reveal.html",
		round_name="",
		blank=True,
		room=room,
		template_css_files=css_files
	)


@app.get("/question")
def question():
	room = request.args.get("room")
	css_files = ["question.css"]
	mode = ""
	if room is None:
		return redirect("/question?room=demo")
	elif room == "demo":
		# mode = "averages"
		# mode = "gho"
		# mode = "dating"
		mode = "smash"
		# mode = "music"
		players = []
		imax = 6
		for i in range(0, imax):
			players.append(
				{"name": nouns["nouns"][int((i + 1) * len(nouns["nouns"]) / imax) - 1], "score": random.randint(0, 30)})
	elif room in app.game_rooms.keys():
		mode = app.game_rooms[room]["mode"]
		players = []
		game = app.game_rooms[room]["players"]
		for player in game.values():
			players.append(
				{"name": player["name"], "score": player["score"]}
			)
	return render_template(
		"question.html",
		players=players,
		questions=questions,
		room=room,
		mode=mode,
		template_css_files=css_files
	)


@app.get("/timer_results")
def timer_results():
	room = request.args.get("room")
	target = 16.9
	if room is None:
		abort(404)
	elif room == "demo":
		data = []
		imax = 6
		for i in range(0, imax):
			data.append(
				[
					nouns["nouns"][
						int((i + 1) * len(nouns["nouns"]) / imax) - 1
					],
					random.random()*30,
					0
				]
			)

		data[min(range(len(data)), key=lambda i: abs(data[i][1] - target))][2] = 1
		return jsonify(data)
	elif room in app.game_rooms.keys():
		data = []
		for player in app.game_rooms[room]["players"].values():
			data.append(
				[
					player["name"],
					player["timer"]/1000,
					0
				]
			)
		data[min(range(len(data)), key=lambda i: abs(data[i][1] - target))][2] = 1
		return jsonify(data)
	else:
		abort(404)


@socketio.on('music', namespace="/test")
def music_timer(data):
	for player, content in app.game_rooms[data["room"]]["players"].items():
		if content["name"] == data["player"]:
			sid = player
	app.game_rooms[data["room"]]["players"][sid]["timer"] = data["time"]


@socketio.on('startTimer', namespace="/test")
def start_timer(data):
	print("starttimer")
	emit('startTimer', data, broadcast=True)


@socketio.on('firstBuzz', namespace="/test")
def firstBuzz(data):
	emit('firstBuzz', data, broadcast=True)


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
			"score": data["score"],
			"timer": 0
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
		if data["mode"] == "dating":
			emit('gamemode', {"mode": "dating"}, broadcast=True)


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
				"score": 0,
				"timer": 0
			}
	elif client_type == "question":
		valid = True
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


@app.get("/img/<filename>")
def images(filename):
	print(app.config['IMG_FOLDER'], filename)
	return send_from_directory(
		app.config['IMG_FOLDER'],
		filename,
		as_attachment=False
	)\


@app.get("/audio/<filename>")
def audio(filename):
	# print(app.config['AUDIO_FOLDER'], filename)
	return send_from_directory(
		app.config['AUDIO_FOLDER'],
		filename,
		as_attachment=False
	)

# refactor that shit into proper separate routes
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
