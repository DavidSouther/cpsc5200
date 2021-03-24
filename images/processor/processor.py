from threading import Thread
from datetime import datetime
from time import sleep
import logging
from werkzeug.serving import run_with_reloader

from common import bus, db
from common.wait import wait_for_tcp


_operations = None


def operations():
    global _operations
    if _operations is not None \
            and _operations.ident is not None \
            and not _operations.is_alive():
        _operations = None
    if _operations is None:
        _operations = OperationsThread()
    if not _operations.is_alive():
        _operations.start()
    return _operations


class OperationsThread(Thread):
    def __init__(self, *args, **kwargs):
        Thread.__init__(self, *args, **kwargs)
        self.ops = []
        self.channel = None
        self.session = None

    def run(self):
        wait_for_tcp('db', '5432')
        wait_for_tcp('bus', '5672')
        self.channel = bus.make_channel(bus.make_connection())
        self.session = db.Session()
        while True:
            self.process_ops()
            sleep(1)

    def add_op(self, op):
        # The internet thinks this is thread safe
        logging.info('Adding %s', op)
        self.ops.append(op)

    def process_ops(self):
        ops = self.ops[:]
        self.ops = []
        logging.info('Processing queue length %d', len(ops))
        for op in ops:
            (_, operation_id, previous_id, *_) = op.split(' ')
            operation = self.operation(operation_id)
            prior_operation = self.operation(operation.previous_id)
            if previous_id == 'current' or prior_operation.completed is not None:
                # Previous operation has been completed, so remove this one and
                # schedule it
                command = f'{operation.photo_id} {operation.id} {previous_id} {operation.description}'
                logging.info('Sending task for conversion %s', command)
                bus.basic_publish(self.channel, bus.CONVERT_QUEUE, command)
                try:
                    ops.remove(op)
                except:
                    pass
        logging.info('Queue length after processing %d', len(ops))
        self.ops = ops + self.ops

    def operation(self, id):
        return self.session.query(db.Operation).filter(db.Operation.id == id).first()


def handle_operation(ch, method, props, body):
    global operations_thread
    body = body.decode('utf-8')
    logging.info('Received %s', body)
    ch.basic_ack(delivery_tag=method.delivery_tag)
    operations().add_op(body)
    logging.info('Queued for conversion')


def finished_operation(ch, method, props, body):
    body = body.decode('utf-8')
    logging.info('Received %s', body)
    ch.basic_ack(delivery_tag=method.delivery_tag)
    operation_id = body.split(' ')[1]
    finish(operation_id)
    logging.info('Marked image finished')


def finish(operation_id):
    session = db.Session()
    operation = session.query(db.Operation).filter(
        db.Operation.id == operation_id).first()
    operation.completed = datetime.now().isoformat()
    session.add(operation)
    session.commit()


@run_with_reloader
def main():
    wait_for_tcp('bus', '5672')
    bus.consume(
        (bus.COMMAND_QUEUE, handle_operation),
        (bus.FINISHED_QUEUE, finished_operation),
    )
