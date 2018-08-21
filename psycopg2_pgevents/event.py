"""This module provides functionality for managing and polling for events."""
__all__ = ['poll', 'register_event_channel', 'unregister_event_channel']


import json
import select
from typing import Dict, Iterable

from psycopg2_pgevents.db import execute
from psycopg2.extensions import connection


def register_event_channel(connection: connection) -> None:
    """Register pgevents event channel in the database.

    Parameters
    ----------
    connection: psycopg2.extensions.connection
        Active connection to a PostGreSQL database.

    Returns
    -------
    None

    """
    execute(connection, 'LISTEN "pgevents";')


def unregister_event_channel(connection: connection) -> None:
    """Un-register pgevents event channel from the database.

    Parameters
    ----------
    connection: psycopg2.extensions.connection
        Active connection to a PostGreSQL database.

    Returns
    -------
    None

    """
    execute(connection, 'UNLISTEN "pgevents";')


def poll(connection: connection, timeout: float=1.0) -> Iterable[Dict]:
    """Poll the connection for notification events.

    This method operates as an iterable. It will keep returning events until all events have been read.

    Parameters
    ----------
    connection: psycopg2.extensions.connection
        Active connection to a PostGreSQL database.
    timeout: float
        Number of seconds to block for an event before timing out.

    Returns
    -------
    event: dict or None
        If an event is available, a dictionary is returned, following this format:
            {
                'id': '<ID>',
                'event': '<INSERT|UPDATE|DELETE>',
                'schema_name': '<SCHEMA_NAME>',
                'table_name': '<TABLE_NAME>'
            }

        If no event is available, None is returned.

    Examples
    --------
    >>> events = [evt for evt in connection.poll()]

    >>> for evt in connection.poll():
            print(evt)

    """
    if select.select([connection], [], [], timeout) == ([], [], []):
        return
    else:
        connection.poll()
        while connection.notifies:
            notification = connection.notifies.pop()
            yield json.loads(notification.payload)
