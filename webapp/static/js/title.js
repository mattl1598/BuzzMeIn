window.onpageshow = function (e) {
    document.getElementById('content').className = ''
}

window.onclick = function(e){
    document.getElementById('content').className = 'out'
    setTimeout(nextPage, 500);
}