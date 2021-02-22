import logging
from flask import g

from common import bus

def channel():
    if 'channel' not in g:
        g.channel = bus.channel(bus.COMMAND_QUEUE)
    return g.channel

def publish(message):
    bus.publish(bus.COMMAND_QUEUE, message)