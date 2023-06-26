var modifiedIDs = []

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
	} else if (e.keyCode === 81) { // q
		modifiedIDs.push("#question-bulk")
		document.querySelector("#question-bulk").classList.add("show")
	} else if (e.keyCode === 65) { // a
		modifiedIDs.push("#question-bulk")
		document.querySelector("#question-bulk").classList.add("flip-answer")
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

// TODO add clear screen transition