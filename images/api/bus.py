import argparse
import logging
import pika
from flask import g

parser = argparse.ArgumentParser()
parser.add_argument('--bus', type=str, default='bus')
parser.add_argument('--queue', type=str, default='images')
(args, _) = parser.parse_known_args()

def make_channel():
    try:
        logging.debug('Opening channel on %s', args.bus)
        params = pika.ConnectionParameters(host=args.bus)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.queue_declare(queue=args.queue, durable=True)
        logging.debug('Opened channel on %s', args.bus)
        return channel
    except:
        return None

def channel():
    if 'channel' not in g:
        g.channel = make_channel()
    logging.debug('Using channel on %s', args.bus)
    return g.channel

def publish(message):
    c = channel()
    if c is None:
        logging.info('Failed to publish message, no channel available')
    else:
        c.basic_publish(
            exchange='',
            routing_key=args.queue,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ))
