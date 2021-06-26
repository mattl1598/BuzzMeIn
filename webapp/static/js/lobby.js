const random_word_url = "/random_word"

function control_game() {
    let roomcode = document.getElementById("roomcode").value;
    console.log(roomcode);
    window.location.href = "/remote?room=".concat(roomcode);
}

function start_game() {
    let gamemode = document.getElementById("gamemode").selectedOptions[0].value;
    console.log(gamemode);
    if (gamemode == "snake") {
        let Http = new XMLHttpRequest();
        let word;
        Http.open("GET", random_word_url);
        Http.send();
        Http.onreadystatechange = (e) => {
            if (Http.readyState==4) {
                console.log(Http.responseText);
                word = Http.responseText;
                window.location.href = "/snake?room=".concat(word);
            }
        }
    }
}
