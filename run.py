from webapp import app, socketio

if __name__ == '__main__':
	# app.run(debug=True, host="0.0.0.0")  # run app using the default flask dev engine
	socketio.run(app, debug=True, host="0.0.0.0", allow_unsafe_werkzeug=True)  # run app using the socket.io flask extension
