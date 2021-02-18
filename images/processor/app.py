#!/usr/bin/env python3

import argparse
import logging
import pika

from time import sleep

logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.INFO, datefmt='%H:%M:%S')
parser = argparse.ArgumentParser()
parser.add_argument('--bus', type=str, default='bus')
parser.add_argument('--queue', type=str, default='images')

class Processor:
    def __init__(self, args):
        self.host = args.bus
        self.queue = args.queue
        self.channel = None

    def listen(self):
        callback = lambda ch, method, props, body: self.process(ch, method, props, body)
        started = False
        while not started:
            try:
                params = pika.ConnectionParameters(self.host)
                connection = pika.BlockingConnection(params)
                self.channel = connection.channel()
                self.channel.queue_declare(queue=self.queue, durable=True)
                self.channel.basic_qos(prefetch_count=1)
                self.channel.basic_consume(queue=self.queue, on_message_callback=callback)
                self.channel.start_consuming()
                started = True
            except pika.exceptions.AMQPConnectionError:
                sleep(1)
        logging.info('Listening for messages on %s. Exit with Ctrl+C', self.channel)

    def process(self, ch, method, props, body):
        logging.info('On channel %s received %r', ch, body.decode())
        self.op()
        self.channel.basic_ack(delivery_tag=method.delivery_tag)
        logging.info('Done with image')
    
    def op(self):
        pass

if __name__ == '__main__':
    logging.info('Waiting for RabbitMQ')
    Processor(parser.parse_args()).listen()