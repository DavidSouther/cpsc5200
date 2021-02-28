import argparse
import logging
from pathlib import Path
from common import db

parser = argparse.ArgumentParser()
parser.add_argument('--nas', type=str, default='/nas')
(args, _) = parser.parse_known_args()

NAS = Path(args.nas)


def next_id(device):
    photo = db.Photo(device=device)
    db.session().add(photo)
    db.session().commit()
    return str(photo.id)


def next_operation(photo, last_operation, op):
    previous_id = None
    if last_operation != 'current':
        previous_id = int(last_operation)
    operation = db.Operation(
        photo=photo, previous_id=previous_id, description=op)
    db.session().add(operation)
    db.session().commit()
    return operation


def write(id, upload):
    folder = NAS / 'photos' / id
    filepath = folder / 'first.png'
    logging.info('Writing file to %s', folder)
    folder.mkdir(parents=True, exist_ok=True)
    upload.save(filepath)
    (folder/'current.png').symlink_to(filepath)
