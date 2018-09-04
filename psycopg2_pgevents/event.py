"""This module provides functionality for managing and polling for events."""
__all__ = ['Event', 'poll', 'register_event_channel', 'unregister_event_channel']


import json
import select
from typing import Dict, Iterable

from psycopg2_pgevents.db import execute
from psycopg2.extensions import connection


class Event:
    """Represent a psycopg2-pgevents event."""
    event: str
    schema_name: str
    table_name: str
    id: str

    def __init__(self, event: str, schema_name: str, table_name: str, id: str):
        """Initialize a new Event.

        Parameters
        ----------
        event: str
            PostGreSQL event, one of 'INSERT', 'UPDATE', or 'DELETE'.
        schema_name: str
            Schema where the event occurred.
        table_name: str
            Table where event occurred.
        id: str
            Row ID of event. This attribute is a string so that it can
            represent both regular id's and things like UUID's.

        Returns
        -------
        None

        """
        self.event = event
        self.schema_name = schema_name
        self.table_name = table_name
        self.id = id

    @classmethod
    def fromjson(cls, json_string: str) -> 'Event':
        """Create a new Event from a from a psycopg2-pgevent event JSON.

        Parameters
        ----------
        json_string: str
            Valid psycopg2-pgevent event JSON.

        Returns
        -------
        Event
            Event created from JSON deserialization.

        """
        obj = json.loads(json_string)
        return cls(
            obj['event'],
            obj['schema_name'],
            obj['table_name'],
            obj['id']
        )

    def tojson(self) -> str:
        """Serialize an Event into JSON.

        Returns
        -------
        str
            JSON-serialized Event.

        """
        return json.dumps({
            'event': self.event,
            'schema_name': self.schema_name,
            'table_name': self.table_name,
            'id': self.id
        })


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
    event: Event or None
        If an event is available, an Event is returned.
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
            event = connection.notifies.pop()
            yield Event.fromjson(event.payload)
