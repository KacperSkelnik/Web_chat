document.addEventListener('DOMContentLoaded', () => {
	var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

	socket.on('connect', () => {
		socket.emit("Iam connected");
	});

	socket.on('message', data => {
		console.log(`Message revived: ${data}`);
	});

});