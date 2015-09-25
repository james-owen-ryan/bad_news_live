from flask import Flask, render_template, request
from bad_news import Game


app = Flask(__name__, static_url_path='/static')


@app.route('/wizard')
def wizard():
    """Render the Wizard interface."""
    return render_template('wizard.html')


@app.route('/actor')
def actor():
    """Render the Actor interface."""
    return render_template('actor.html')


if __name__ == '__main__':
    app.game = Game(single_player=False)
    app.player = app.game.player
    app.deceased_character = app.game.deceased_character
    app.next_of_kin = app.game.next_of_kin
    app.run(debug=False)
else:
    pass