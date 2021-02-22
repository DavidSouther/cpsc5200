#!/usr/bin/env python3

import argparse
import logging
from time import sleep
from random import random

from pathlib import Path

from werkzeug.serving import run_with_reloader

from common import bus
from common.wait import wait_for_tcp

logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.INFO, datefmt='%H:%M:%S')
parser = argparse.ArgumentParser()
parser.add_argument('--nas', type=str, default='/nas')
(args, _) = parser.parse_known_args()

def listen():
    callback = lambda ch, method, props, body: process(ch, method, props, body)
    bus.listen(bus.CONVERT_QUEUE, callback)

def process(ch, method, props, body):
    body = body.decode('utf-8')
    ch.basic_ack(delivery_tag=method.delivery_tag)
    logging.info('Received command %s', body)
    (photo_id, operation_id, prior_operation, operation, *arguments) = body.split(' ')
    logging.info('')
    try:
        op(photo_id, operation_id, prior_operation, operation, *arguments)
        bus.publish(bus.FINISHED_QUEUE, f'DONE {photo_id} {operation_id}')
    except Exception as e:
        logging.error(e)
    logging.info('Done with image')

def op(photo_id, operation_id, prior_operation, operation, *arguments):
    arguments = convert_arguments(operation, arguments)
    logging.info('Performing %s on %s/%s with args %s', operation, photo_id, prior_operation, ' '.join(arguments or []))
    photo_path = Path(args.nas) / 'photos' / photo_id
    source = photo_path / f'{prior_operation}.png'
    target = photo_path / f'{operation_id}.png'
    command = ['convert'] + arguments + [source, target]
    logging.info("Executing %s", command)

    sleep(random() * 2)

def convert_arguments(operation, args):
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
    return None

def maybe(n):
    if len(n) > 0:
        return n[0]
    else:
        return None

@run_with_reloader
def main():
    logging.info('Waiting for RabbitMQ')
    wait_for_tcp('bus', '5672')
    listen()

if __name__ == '__main__':
    main()