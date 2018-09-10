"""This module provides functionality for managing and polling for events."""
__all__ = ['Event', 'poll', 'register_event_channel', 'unregister_event_channel']


import json
import select
from typing import Dict, Iterable
from uuid import UUID

from psycopg2_pgevents.sql import execute
from psycopg2.extensions import connection

from psycopg2_pgevents.debug import log

_LOGGER_NAME = 'pgevents.event'


class Event:
    """Represent a psycopg2-pgevents event.

    Attributes
    ----------
    id: UUID
        Event UUID.
    type: str
        PostGreSQL event type, one of 'INSERT', 'UPDATE', or 'DELETE'.
    schema_name: str
        Schema in which the event occurred.
    table_name: str
        Table in which event occurred.
    row_id: str
        Row ID of event. This attribute is a string so that it can
        represent both regular id's and things like UUID's.
    """
    id: str
    type: str
    schema_name: str
    table_name: str
    row_id: str

    def __init__(self, id_: UUID, type_: str, schema_name: str, table_name: str, row_id: str) -> None:
        """Initialize a new Event.

        Parameters
        ----------
        id_: UUID
            Event UUID.
        type_: str
            PostGreSQL event type, one of 'INSERT', 'UPDATE', or 'DELETE'.
        schema_name: str
            Schema in which the event occurred.
        table_name: str
            Table in which event occurred.
        row_id: str
            Row ID of event. This attribute is a string so that it can
            represent both regular id's and things like UUID's.

        Returns
        -------
        None

        """
        self.id = id_
        self.type = type_
        self.schema_name = schema_name
        self.table_name = table_name
        self.row_id = row_id

    def __repr__(self):
        return '<Event id:{id_} type:{type_} table:{schema}.{table} row-id:{row_id}'.format(
            id_=self.id,
            type_=self.type,
            schema=self.schema_name,
            table=self.table_name,
            row_id=self.row_id
        )

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
            UUID(obj['event_id']),
            obj['event_type'],
            obj['schema_name'],
            obj['table_name'],
            obj['row_id']
        )

    def tojson(self) -> str:
        """Serialize an Event into JSON.

        Returns
        -------
        str
            JSON-serialized Event.

        """
        return json.dumps({
            'event_id': str(self.id),
            'event_type': self.type,
            'schema_name': self.schema_name,
            'table_name': self.table_name,
            'row_id': self.row_id
        })


def register_event_channel(connection: connection) -> None:
    """Register psycopg2-pgevents event channel in the database.

    Parameters
    ----------
    connection: psycopg2.extensions.connection
        Active connection to a PostGreSQL database.

    Returns
    -------
    None

    """
    log('Registering psycopg2-pgevents channel...', logger_name=_LOGGER_NAME)
    execute(connection, 'LISTEN "psycopg2_pgevents_channel";')


def unregister_event_channel(connection: connection) -> None:
    """Un-register psycopg2-pgevents event channel from the database.

    Parameters
    ----------
    connection: psycopg2.extensions.connection
        Active connection to a PostGreSQL database.

    Returns
    -------
    None

    """
    log('Unregistering psycopg2-pgevents channel...', logger_name=_LOGGER_NAME)
    execute(connection, 'UNLISTEN "psycopg2_pgevents_channel";')


def poll(connection: connection, timeout: float=1.0) -> Iterable[Event]:
    """Poll the connection for notification events.

    This method operates as an iterable. It will keep returning events until
    all events have been read.

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

    if timeout > 0.0:
        log('Polling for events (Blocking, {} seconds)...'.format(timeout), logger_name=_LOGGER_NAME)
    else:
        log('Polling for events (Non-Blocking)...', logger_name=_LOGGER_NAME)
    if select.select([connection], [], [], timeout) == ([], [], []):
        log('...No events found', logger_name=_LOGGER_NAME)
        return
    else:
        log('Events', logger_name=_LOGGER_NAME)
        log('------', logger_name=_LOGGER_NAME)
        connection.poll()
        while connection.notifies:
            event = connection.notifies.pop(0)
            log(str(event), logger_name=_LOGGER_NAME)
            yield Event.fromjson(event.payload)
