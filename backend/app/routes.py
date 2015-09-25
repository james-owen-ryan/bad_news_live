from flask import Flask, render_template, request


app = Flask(__name__, static_url_path='/gameglobs/static')


@app.route('/wizard')
def wizard():
    """Render the Wizard interface."""
    return render_template('wizard.html')


@app.route('/actor')
def actor():
    """Render the Actor interface."""
    return render_template('actor.html')


if __name__ == '__main__':
    app.run(debug=True)
else:
    pass
