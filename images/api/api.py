#!/usr/bin/env python3

import argparse
import logging
import pika

from pathlib import Path
from flask import Flask, jsonify, g, request

app = Flask(__name__)

logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.DEBUG, datefmt='%H:%M:%S')
parser = argparse.ArgumentParser()
parser.add_argument('--bus', type=str, default='bus')
parser.add_argument('--queue', type=str, default='images')
parser.add_argument('--nas', type=str, default='/nas')
(args, _) = parser.parse_known_args()

NAS = Path(args.nas)

def channel():
    if 'channel' not in g:
        logging.debug('Opening channel on %s', args.bus)
        params = pika.ConnectionParameters(host=args.bus)
        connection = pika.BlockingConnection(params)
        g.channel = connection.channel()
        g.channel.queue_declare(queue=args.queue, durable=True)
        logging.debug('Opened channel on %s', args.bus)
    logging.debug('Using channel on %s', args.bus)
    return g.channel

ID = 1
def next_id():
    global ID
    id = ID
    ID += 1
    return str(id)

@app.route('/photo', methods=['POST'])
def upload():
    id = next_id()
    folder = NAS / 'photos' / id
    file = folder / 'first.png'
    logging.info('Writing file to %s', folder)
    folder.mkdir(parents=True, exist_ok = True)
    request.files['file'].save(file)
    (folder/'current.png').symlink_to(file)
    return f'/photo/{id}'

@app.route('/photo/<id>:transform', methods=['POST'])
def transform(id):
    message = f'Transforming {id}'
    logging.info(message)
    channel().basic_publish(
        exchange='',
        routing_key=args.queue,
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
        ))
    return jsonify([5])

if __name__ == '__main__':
    app.run()
