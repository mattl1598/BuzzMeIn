const socket = io("/test");
const room = "test";

function join() {
    socket.emit('join', {"room": room})
}

function leave() {
    socket.emit('leave', {"room": room})
}