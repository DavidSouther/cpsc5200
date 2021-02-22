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

_connection = None
def connect(host=args.bus):
    global _connection
    if _connection is None:
        logging.info('Starting connection')
        params = pika.ConnectionParameters(host=host)
        _connection = pika.BlockingConnection(params)
    logging.info('Have connection')
    return _connection

_channels = {}
def channel(name):
    global _channels
    if not name in _channels:
        logging.info('Starting channel %s', name)
        _channels[name] = connect().channel()
        _channels[name].queue_declare(queue=name, durable=True)
    logging.info('Have channel %s', name)
    return _channels[name]

def publish(queue, message):
    c = channel(queue)
    if c is None:
        logging.info('Failed to publish message, no channel available')
    else:
        c.basic_publish(
            exchange='',
            routing_key=queue,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ))

def listen(queue, callback):
    ch = channel(queue)
    ch.basic_qos(prefetch_count=1)
    ch.basic_consume(queue, on_message_callback=callback)
    ch.start_consuming()
    return ch
