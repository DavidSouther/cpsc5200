
import logging

from flask import jsonify, g, request

from app import app
import bus
import db
import photos

@app.before_first_request
def connect():
    db.migrate()

@app.route('/photos', methods=['GET'])
def list():
    photos = db.session().query(db.Photo).all()
    return '\n'.join([f'/photo/{photo.id}' for photo in photos])

@app.route('/photos', methods=['POST'])
def upload():
    device = request.form['device']
    logging.info('Uploading file from %s', device)
    id = photos.next_id(device)
    photos.write(id, request.files['file'])
    return f'/photos/{id}'

@app.route('/photos/<int:id>:transform', methods=['POST'])
def transform(id):
    message = f'Transforming {id}'
    logging.info(message)
    bus.publish(message)
    return jsonify([5])

if __name__ == '__main__':
    connect()
    app.run(debug=True, host='0.0.0.0')
