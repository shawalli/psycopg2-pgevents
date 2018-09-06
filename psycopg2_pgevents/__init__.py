"""This package provides the ability to listen for PostGreSQL table events at the database level."""
from psycopg2_pgevents.__about__ import __author__, __copyright__, __email__, __license__, __summary__, \
    __title__, __uri__, __version__


from psycopg2_pgevents.debug import log, set_debug
from psycopg2_pgevents.event import poll, register_event_channel, unregister_event_channel
from psycopg2_pgevents.sql import execute
from psycopg2_pgevents.trigger import install_trigger, install_trigger_function, trigger_function_installed, \
    trigger_installed, uninstall_trigger, uninstall_trigger_function
