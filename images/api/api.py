
import logging

from flask import request

from app import app
from common import db
import bus
import photos

logging.basicConfig(level=logging.INFO)

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
    logging.info('Transforming %s', id)
    photo = db.session().query(db.Photo).filter(db.Photo.id == id).first()
    ops = request.stream.readlines()
    results = []
    last_op = 'current'
    for op in ops:
        op = op.decode('utf-8').strip()
        logging.info('Sending operation on %s: %s', photo.id, op)
        operation = photos.next_operation(photo, last_op, op)
        message = f'{photo.id} {operation.id} {last_op} {op}'
        last_op = operation.id
        logging.info('Publishing %s', message)
        bus.publish(message)
        results.append(f'/photos/{photo.id}/steps/{operation.id}')
    return '\n'.join(results)

if __name__ == '__main__':
    connect()
    app.run(debug=True, host='0.0.0.0')
