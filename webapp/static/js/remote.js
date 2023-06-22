let socket = io("/test");
const queryString = window.location.search;
const urlParams = new URLSearchParams(queryString);
const room = urlParams.get('room');
const player = urlParams.get('player');
let buzzed = false;
let buzzer_elem = document.querySelector("#buzzer");
let score = 0;
let sid = ""

socket.on('connect', function() {
	// socket.emit('test', {data: 'I\'m connected!'});
	socket.emit('join', {"room": room, "client_type": "remote", "http_sid": http_sid, "name": player})
});

// socket.on('connected', function(data) {
// 	sid = data["sid"]
// 	socket.emit('identify', {"type": "player", "room": room, "player": player, "score": score})
// });

function send_buzz() {
	if (!buzzed) {
		socket.emit('buzz', {"room": room, "player": player})
		buzzed = true;
		buzzer_elem.classList.add("buzzed")
	}
}

socket.on('release', function() {
	buzzed = false
	buzzer_elem.classList.remove("buzzed")
});

socket.on('lock', function() {
	buzzed = true
	buzzer_elem.classList.add("buzzed")
});

socket.on('identify', function() {
	socket.emit('identify', {"type": "player", "room": room, "player": player, "score": score})
})

socket.on('scores', function(data) {
	console.log(data["players"])
	score = data["players"][sid]["score"]
})

socket.on('error', function(data) {
	if (data["error"] === "room does not exist") {
		alert("This game room does not exist. Redirecting to lobby")
		let dest = window.location.protocol + "//" + window.location.host + "/"
		window.location.replace(dest);
	} else {
		alert("An error occurred. Redirecting to lobby")
		let dest = window.location.protocol + "//" + window.location.host + "/"
		window.location.replace(dest);
	}
});

function send(msg) {
	socket.emit('remote', {data: msg, "room": room});
}