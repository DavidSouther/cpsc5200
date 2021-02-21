import argparse
import logging
import pika
from flask import g

parser = argparse.ArgumentParser()
parser.add_argument('--bus', type=str, default='bus')
parser.add_argument('--queue', type=str, default='images')
(args, _) = parser.parse_known_args()

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

def publish(message):
    channel().basic_publish(
        exchange='',
        routing_key=args.queue,
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
        ))
