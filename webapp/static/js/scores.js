window.addEventListener("keydown", keyToFunc)

function keyToFunc(e) {
    if (e.keyCode === 84) { // t
        document.getElementById('content').className = 'out'
        setTimeout(function() {
            window.location.href="/title?room="+room
        }, 1000);
    }
}