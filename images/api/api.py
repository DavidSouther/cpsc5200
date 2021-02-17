from flask import Flask
app = Flask(__name__)


@app.route('/')
@app.route('/<planet>')
def hello_world(planet="world"):
    return f'Hello, {planet}!'


if __name__ == '__main__':
    app.run()