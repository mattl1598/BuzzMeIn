var modifiedIDs = []
var winnerID = ""
var winnerTime = 16.9
let socket = io("/test")
var qNum = 0;
var audio_url = ""
var fadeTime = 0

window.onpageshow = function (e) {
    nextQuestion()
}

function nextQuestion() {
	if (mode === "music") {
		audio_url = questions[qNum]["q"]
		fadeTime = questions[qNum]["f"]
		winnerTime = questions[qNum]["t"]
		document.querySelector("#answer-text").innerHTML = questions[qNum]["a"]
	} else if (mode === "smash") {
		document.querySelector("#smash-img").src = questions[qNum]["i"]
		document.querySelector("#smash-question").innerHTML = questions[qNum]["q"]
		document.querySelector("#smash-answer").innerHTML = questions[qNum]["a"]
	} else if (mode === "averages") {
		document.querySelector("#question-text").innerHTML = questions[qNum]["q"]
		document.querySelector("#answer-text").innerHTML = questions[qNum]["a"]
	} else if (mode === "dating") {
		document.querySelector("#question-text").innerHTML = questions[qNum]["q"]
		document.querySelector("#answer-text").innerHTML = questions[qNum]["a"]
	} else if (mode === "gho") {
		document.querySelector("#question-text").innerHTML = questions[qNum]["q"]
		let gho_ans = document.querySelector("#answer-gho")
		gho_ans.innerHTML = ""
		let answer = questions[qNum]["a"].split(" ")
		let answer_ordered = [...answer].sort(function (a, b) {
			    return a.localeCompare(b);
			})
		for (let i in answer) {
			let node = document.createElement("div");
			node.innerHTML = answer[i]
			node.style.order = answer_ordered.indexOf(answer[i]).toString()
			gho_ans.appendChild(node)
		}
	}
	qNum++
}

socket.on('firstBuzz', function(data) {
	document.querySelector("#smash-buzz-name").innerHTML = data["name"]
	document.querySelector("#smash-buzz").classList.add("show")
	modifiedIDs.push("#smash-buzz")
})

socket.on('connect', function() {
	socket.emit('test', {data: 'I\'m connected!'})
	socket.emit('join', {"room": room, "client_type": "question"})
});

window.addEventListener("keydown", keyToFunc)

function keyToFunc(e) {
	if (e.keyCode === 49) { // number row 1
		modifiedIDs.push("#pair1")
		showAvgPair(1)
	} else if (e.keyCode === 50) { // number row 2
		modifiedIDs.push("#pair2")
		showAvgPair(2)
	} else if (e.keyCode === 51) { // number row 3
		modifiedIDs.push("#pair3")
		showAvgPair(3)
	} else if (e.keyCode === 32) { // space
		clearPage()
		setTimeout(nextQuestion, 1000)
	} else if (e.keyCode === 84) { // t
		clearPage()
		setTimeout(function() {
			document.getElementById('content').className = 'out'
		}, 1000)
		setTimeout(function() {
			window.location.href = `/title?room=${room}`
		}, 1500)
	} else if (e.keyCode === 81) { // q
		modifiedIDs.push("#question-bulk")
		document.querySelector("#question-bulk").classList.add("show")
		modifiedIDs.push("#smash-question")
		document.querySelector("#smash-question").classList.add("show")
	} else if (e.keyCode === 65) { // a
		modifiedIDs.push("#question-bulk")
		document.querySelector("#question-bulk").classList.add("flip-answer")
		modifiedIDs.push("#smash-buzz")
		document.querySelector("#smash-buzz").classList.add("flip-answer")
		document.querySelector("#smash-buzz").classList.add("show")
		music_results()

	} else if (e.keyCode === 77) { // m
		let audio = new Audio(audio_url);

		var timer_text = document.querySelector("#answer-text")
		var timer = 0.1
		modifiedIDs.push("#answer-text")
		let interval = setInterval(function() {
			timer_text.innerHTML = timer.toFixed(1)
			timer += 0.1
		}, 100)
		audio.play();
		fadeOutAudio(audio, winnerTime+5);
		setTimeout(function() {
				clearInterval(interval)
				document.querySelector(winnerID).classList.add("winner")
				modifiedIDs.push(winnerID)
			}, winnerTime*1000)
	} else if (e.keyCode === 80) { // p
		socket.emit('startTimer', {"goal": winnerTime})
		let audio = new Audio(audio_url);
		audio.play();
		fadeOutAudio(audio, fadeTime);
	} else if (e.keyCode === 190) { // fullstop
	}
}

function showAvgPair(pairnum) {
	document.querySelector("#pair"+pairnum).classList.add("show")
}

function clearPage() {

	for (let i in modifiedIDs) {
		let id = modifiedIDs[i]
		let elem = document.querySelector(id)
		elem.classList.value = elem.dataset.class
	}
}

function music_results() {
	fetch('/timer_results?room='+room)
    .then(response => response.json()) // parse the JSON from the server
    .then(data => {
      // Here is your data
		console.log(data)
	    data.sort(function(a, b) {
		    return a[1] - b[1];
		});
	    for (let i in data) {
			let j = 1 + parseInt(i)
			let elem_id = "#player" + j
			let elem = document.querySelector(elem_id)
		    elem.querySelector("div.player-name").innerHTML = data[i][0]
		    elem.querySelector("div.player-time").innerHTML = data[i][1].toFixed(2)
		    if (data[i][2]) {
				winnerID = elem_id;
		    }
	    }

    })
    .catch(err => {
      console.error('An error occurred:', err)
    })
}


function fadeOutAudio (sound, time) {

    // var sound = document.getElementById(audiosnippetId);

    // Set the point in playback that fadeout begins. This is for a 2 second fade out.
    var fadePoint = time-2;
	setTimeout(function() {
		sound.pause()
		sound.currentTime = 0
	}, (time)*1000)

    var fadeAudio = setInterval(function () {

        // Only fade if past the fade out point or not at zero already
        if ((sound.currentTime >= fadePoint) && (sound.volume > 0.0)) {
            sound.volume -= 0.1;
        }
        // When volume at zero stop all the intervalling
        if (sound.volume <= 0.0) {
            clearInterval(fadeAudio);
        }
    }, 200);

}