const socket = io("/test");
const queryString = window.location.search;
const urlParams = new URLSearchParams(queryString);
const room = urlParams.get('room');
let updater;
let play_status = false;

socket.on('connect', function() {
	socket.emit('test', {data: 'I\'m connected!'});
    socket.emit('join', {"room": room, "client_type": "display"})
});

socket.on('test', function (data) {
	let testElement = document.getElementById("output");
	testElement.innerHTML = data.data;
});

socket.on('grid', function(data) {
	try {
		if (data["stopped"]) {
			clearTimeout(updater);
			socket.emit('ppAck', {"content": false, "room": room})
			play_status = !play_status
		}
	} catch (e) {

	}
	try {
		if (data["clear"]) {
			resetGrid();
		}
	} catch (e) {

	}
	for (let key in data.content) {
		let ele = document.getElementById(key);
		ele.innerText = data.content[key];
	}
});

socket.on('fail', function(data){
	clearTimeout(updater);
	socket.emit('ppAck', {"content": false, "room": room});
	play_status = false;
	resetGrid();
	//alert(data["content"]);
	socket.emit('restart', {"room": room});
});

function resetGrid() {
	let cells = [...document.getElementsByClassName('output-cell')];
	cells.forEach(function(cell) {
		cell.innerHTML = ".";
	});
}

function callUpdate() {
	socket.emit('update', {"room": room})
	updater = setTimeout(callUpdate, 1000);
}

socket.on('play_pause', function play_pause() {
	if (play_status) {
		clearTimeout(updater);
		socket.emit('ppAck', {"content": false, "room": room})
		play_status = !play_status
	} else {
		socket.emit('ppAck', {"content": true, "room": room})
		callUpdate();
		play_status = !play_status
	}
});
