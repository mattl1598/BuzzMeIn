window.onpageshow = function (e) {
    document.getElementById('content').className = ''
}

window.addEventListener("keydown", keyToFunc)

function keyToFunc(e) {
    if (e.keyCode === 83) { // s
        document.getElementById('content').className = 'out'
        setTimeout(function() {
            window.location.href="/scores?room="+room
        }, 1000);
    } else if (e.keyCode === 81) { // q
        document.getElementById('content').className = 'out'
        setTimeout(function() {
            window.location.href="/round_reveal?room="+room
        }, 1000);
    }
}
