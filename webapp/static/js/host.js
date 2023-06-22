let socket = io("/test")
const queryString = window.location.search
const urlParams = new URLSearchParams(queryString)
const room = urlParams.get('room')
let order_counter = 0
let mode = 'buzzer'
let time = Date.now();
socket.on('connect', function() {
	socket.emit('test', {data: 'I\'m connected!'})
	socket.emit('join', {"room": room, "client_type": "host", "http_sid": http_sid})
});

function updateScore(change) {
	let target_id = event.srcElement.parentElement.parentElement.dataset.sid
	socket.emit('scoring', {room: room, instruction: "modify", target: target_id, modification: change})
}

function setGamemode() {
	console.log(event.srcElement)
	mode = event.srcElement.value
	socket.emit('gamemode', {room: room, mode: mode})
	document.querySelector("body").className = mode

	if (mode === "timer") {
		lock_all_buzzers()
	}
}

socket.on('buzzed', function(data) {
	let buzzer = document.querySelector(`#${data["player"]}`)
	if (mode === "timer") {
		let timed = Date.now()-time
		let diff = Math.abs(document.querySelector("#timer_aim").value - (Date.now()-time))
		buzzer.querySelector(".timer").innerHTML = `${timed}ms (${diff}ms)`
		buzzer.style.order = diff
	} else if (mode === "buzzer") {
		order_counter++
		buzzer.style.order = order_counter
	}
});

socket.on('scores', function(data) {
	console.log(data)
	for (let sid in data["players"]) {
		console.log(sid)
		document.querySelector(
			`#data div[data-sid="${sid}"]`
		).querySelector(
			'.score_manipulation'
		).querySelector(
			'.score_readout'
		).innerHTML = data["players"][sid]["score"]
	}
})

function lock_all_buzzers() {
	socket.emit('lock', {})
}

function release_all_buzzers() {
	let data = document.querySelector("#data")
	console.log(data)
	for (let i in data.children) {
		data.children.item(i).style.order = 9999
	}
	socket.emit('release', {})
}

socket.on('identify', function() {
	socket.emit('identify', {"type": "host", "room": room, "host": "host"})
})

socket.on('identified', function(data) {
	console.log(data)
	let data_field = document.querySelector("#data")
	data_field.innerHTML = ""
	for (let player in data["players"]) {
		console.log(data["players"][player])
		let div = document.querySelector("#player_template").cloneNode(true)
		console.log(div)
		div.querySelector(".player_name").innerHTML = data["players"][player]["name"]
		div.querySelector(".score_readout").innerHTML = data["players"][player]["score"]
		div.dataset.sid = data["players"][player]["sid"]
		div.style.order = 9999
		div.classList.remove("template")
		div.id = data["players"][player]["name"]
		data_field.appendChild(div)
	}
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