import json
import select

from sqlalchemy_pgevents.base import execute


def register_event_channel(connection):
    execute(connection, 'LISTEN "pgevents";')


def unregister_event_channel(connection):
    execute(connection, 'UNLISTEN "pgevents";')


def poll(connection, timeout=1.0):
    if select.select([connection], [], [], timeout) == ([], [], []):
        return
    else:
        connection.poll()
        while connection.notifies:
            notification = connection.notifies.pop()
            yield json.loads(notification.payload)
