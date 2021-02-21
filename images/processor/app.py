#!/usr/bin/env python3

import argparse
import logging
from pathlib import Path
import pika

from time import sleep

logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.INFO, datefmt='%H:%M:%S')
parser = argparse.ArgumentParser()
parser.add_argument('--bus', type=str, default='bus')
parser.add_argument('--queue', type=str, default='images')
parser.add_argument('--nas', type=str, default='/nas')
(args, _) = parser.parse_known_args()

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
        self.op(body)
        self.channel.basic_ack(delivery_tag=method.delivery_tag)
        logging.info('Done with image')
    
    def op(self, body):
        body = body.decode('utf-8')
        (photo_id, operation_id, prior_operation, operation, *arguments) = body.split(' ')
        try:
            arguments = self.convert_arguments(operation, arguments)
        except:
            logging.info('Failed to build arguments for %s', body)
            return
        photo_path = Path(args.nas) / 'photos' / photo_id
        source = photo_path / f'{prior_operation}.png'
        target = photo_path / f'{operation_id}.png'
        command = ['convert'] + arguments + [source, target]
        logging.info("Executing %s", command)

    def convert_arguments(self, operation, args):
        """
        flip horizontal -> -flop
        flip vertical -> -flip
        rotate -> -rotate {d}
        crop l:t:w:h -> -crop {w}x{h}+{l}+{t}
        resize x?:y? -> -resize {x}x{y}
        grayscale -> -grayscale
        """
        args = maybe(args)
        if operation == 'flip':
            if args == 'horizontal':
                return ['-flip']
            if args == 'vertical':
                return ['-flop']
        if operation == 'rotate':
            return ['-rotate', str(int(args))]
        if operation == 'crop':
            (l, t, w, h) = args.split(':')
            return ['-crop', f'{w}x{h}+{l}+{t}']
        if operation == 'resize':
            (x, y) = args.split(':')
            if x == None:
                x = y
            if y == None:
                y = x
            return ['-resize', f'{x}x{y}']
        if operation == 'grayscale':
            return ['-grayscale']

def maybe(n):
    if len(n) > 0:
        return n[0]
    else:
        return None

if __name__ == '__main__':
    logging.info('Waiting for RabbitMQ')
    Processor(parser.parse_args()).listen()