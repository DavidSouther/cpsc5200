import argparse
import logging
import pika

logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser()
parser.add_argument('--bus', type=str, default='bus')
(args, _) = parser.parse_known_args()

COMMAND_QUEUE = 'commands'
CONVERT_QUEUE = 'convert'
FINISHED_QUEUE = 'finished'


def make_connection(host=args.bus):
    params = pika.ConnectionParameters(host=host)
    return pika.BlockingConnection(params)


_connection = None
_channels = {}


def connect(host=args.bus):
    global _connection
    if _connection is None:
        logging.info('Starting connection')
        _connection = make_connection(host)
    logging.info('Have connection')
    return _connection


def make_channel(conn):
    ch = conn.channel()
    ch.basic_qos(prefetch_count=1)
    return ch


def channel(name):
    global _channels
    if not name in _channels:
        logging.info('Starting channel %s', name)
        _channels[name] = make_channel(connect())
        _channels[name].queue_declare(queue=name, durable=False)
    logging.info('Have channel %s', name)
    return _channels[name]


def basic_publish(ch, queue, message):
    ch.basic_publish(
        exchange='',
        routing_key=queue,
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
        ))


def publish(queue, message):
    c = channel(queue)
    if c is None:
        logging.info('Failed to publish message, no channel available')
    else:
        basic_publish(c, queue, message)


def consume(*queues):
    ch = make_channel(connect())
    for (queue, callback) in queues:
        ch.queue_declare(queue=queue, durable=False)
        ch.basic_consume(queue, on_message_callback=callback)
    ch.start_consuming()
    return ch


def listen(queue, callback):
    ch = channel(queue)
    ch.basic_consume(queue, on_message_callback=callback)
    ch.start_consuming()
    return ch
