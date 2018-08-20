"""This package provides the ability to listen for PostGreSQL table events at the database level."""
from psycopg2_pgevents.__about__ import __author__, __copyright__, __email__, __license__, __summary__, \
    __title__, __uri__, __version__


from psycopg2_pgevents.db import execute
from psycopg2_pgevents.event import poll, register_event_channel, unregister_event_channel
from psycopg2_pgevents.trigger import register_trigger, register_trigger_function, unregister_trigger, \
    unregister_trigger_function
