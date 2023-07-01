window.addEventListener("keydown", keyToFunc)

function keyToFunc(e) {
	if (e.keyCode === 81) { // q
        document.getElementById('content').className = 'out'
        setTimeout(function() {
            window.location.href="/question?room="+room
        }, 1000);
    } else if (e.keyCode === 84) { // t
        setTimeout(function() {
            window.location.href="/title?room="+room
        }, 1000);
    }
}