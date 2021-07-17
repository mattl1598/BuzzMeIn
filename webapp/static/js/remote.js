let socket = io("/test");
const queryString = window.location.search;
const urlParams = new URLSearchParams(queryString);
const room = urlParams.get('room');
// let msg_ele = document.getElementById("message1");

socket.on('connect', function() {
	socket.emit('test', {data: 'I\'m connected!'});
	socket.emit('join', {"room": room, "client_type": "remote"})
});

socket.on('ppAck', function ppAck(data) {
	if (data["content"]) {
		document.getElementById("pp").innerHTML = "Pause Game";
	} else {
		document.getElementById("pp").innerHTML = "Continue Game";
	}
});

function play_pause() {
	socket.emit('play_pause', {"room": room});
}

function restart() {
	socket.emit("restart", {"room": room});
}

function send(msg) {
	socket.emit('remote', {data: msg, "room": room});
}

function arrow() {
	if (event.srcElement.tagName === "path") {
		console.log(event.srcElement.parentElement)
		socket.emit('remote', {data: event.srcElement.parentElement.id, "room": room});
	} else {
		console.log(event.target.id)
		socket.emit('remote', {data: event.target.id, "room": room});
	}
}
