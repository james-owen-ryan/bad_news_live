from flask import Flask, render_template, request
from flask.ext.socketio import SocketIO, emit
from bad_news import Game


app = Flask(__name__, static_url_path='/static')
app.game = Game(single_player=False)
app.communicator = app.game.communicator
app.player = app.game.player
app.deceased_character = app.game.deceased_character
app.next_of_kin = app.game.next_of_kin
socketio = SocketIO(app)


@app.route('/wizard')
def wizard():
    """Render the Wizard interface."""
    return render_template('wizard.html')


@app.route('/actor')
def actor():
    """Render the Actor interface."""
    return render_template('actor.html', communicator=app.game.communicator)


@app.route('/player')
def player():
    """Render the Player interface."""
    return render_template('player.html', player_exposition=app.game.communicator.player_exposition)


@socketio.on('my event', namespace='/test')
def render_player_exposition():
    """Render exposition text for the player interface."""
    exposition = app.communicator.player_exposition
    emit('my response', {'data': exposition, 'count': 99})


@socketio.on('connect', namespace='/test')
def establish_connection_to_player_interface():
    """Establish a connection with the player interface and render initial exposition text."""
    exposition = app.communicator.player_exposition
    emit('my response', {'data': exposition, 'count': 0})


if __name__ == '__main__':
    # app.run(debug=False)
    socketio.run(app)
else:
    pass