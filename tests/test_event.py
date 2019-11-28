import json
from uuid import UUID

from psycopg2 import ProgrammingError
from pytest import fixture, mark

from psycopg2_pgevents.sql import execute
from psycopg2_pgevents.event import Event, poll, register_event_channel, unregister_event_channel
from psycopg2_pgevents.trigger import install_trigger, install_trigger_function


@fixture
def event_channel_registered(connection):
    register_event_channel(connection)


@fixture
def triggers_installed(connection):
    install_trigger_function(connection, rowid='id')
    install_trigger(connection, 'settings')
    install_trigger(connection, 'orders', schema='pointofsale')


class TestEvent:
    def test_event_fromjson(self):
        json_string = """
        {
            "event_id": "c2d29867-3d0b-d497-9191-18a9d8ee7830",
            "event_type": "insert",
            "schema_name": "public",
            "table_name": "widget",
            "row_id": "1"
        }
        """

        evt = Event.fromjson(json_string)
        assert (evt.id == UUID('c2d29867-3d0b-d497-9191-18a9d8ee7830'))
        assert (evt.type == 'insert')
        assert (evt.schema_name == 'public')
        assert (evt.table_name == 'widget')
        assert (evt.row_id == '1')

    def test_event_tojson(self):
        evt = Event(
            'c2d29867-3d0b-d497-9191-18a9d8ee7830',
            'insert',
            'public',
            'widget',
            '1'
        )

        json_string = evt.tojson()
        json_dict = json.loads(json_string)
        assert (json_dict['event_id'] == str(evt.id))
        assert (json_dict['event_type'] == evt.type)
        assert (json_dict['schema_name'] == evt.schema_name)
        assert (json_dict['table_name'] == evt.table_name)
        assert (json_dict['row_id'] == evt.row_id)

    def test_register_event_channel(self, connection):
        channel_registered = False

        register_event_channel(connection)

        results = execute(connection, 'SELECT pg_listening_channels();')
        if results and 'psycopg2_pgevents_channel' in results[0]:
            channel_registered = True

        assert (channel_registered == True)

    @mark.usefixtures('event_channel_registered')
    def test_unregister_event_channel(self, connection):
        channel_registered = True

        unregister_event_channel(connection)

        results = execute(connection, 'SELECT pg_listening_channels();')
        if not results:
            channel_registered = False

        assert (channel_registered == False)

    @mark.usefixtures('triggers_installed', 'event_channel_registered')
    def test_poll_timeout(self, connection):
        num_events = 0

        for event in poll(connection):
            num_events += 1

        assert (num_events == 0)

    @mark.usefixtures('triggers_installed', 'event_channel_registered')
    def test_poll_public_schema_table_event(self, connection, client):
        execute(client, "INSERT INTO public.settings(key, value) VALUES('foo', 1);")

        events = [event for event in poll(connection)]

        assert (len(events) == 1)

        event = events.pop(0)

        assert (event.type == 'INSERT')
        assert (event.schema_name == 'public')
        assert (event.table_name == 'settings')

    @mark.usefixtures('triggers_installed', 'event_channel_registered')
    def test_poll_custom_schema_table_event(self, connection, client):
        execute(client, "INSERT INTO pointofsale.orders(description) VALUES('bar');")

        events = [event for event in poll(connection)]

        assert (len(events) == 1)

        event = events.pop(0)

        assert (event.type == 'INSERT')
        assert (event.schema_name == 'pointofsale')
        assert (event.table_name == 'orders')

    @mark.usefixtures('triggers_installed', 'event_channel_registered')
    def test_poll_event_event_types(self, connection, client):
        execute(client, "INSERT INTO public.settings(key, value) VALUES('foo', 1);")

        events = [event for event in poll(connection)]

        assert (len(events) == 1)

        event = events.pop(0)

        assert (event.type == 'INSERT')
        assert (event.schema_name == 'public')
        assert (event.table_name == 'settings')

        execute(client, "UPDATE public.settings SET value = 2 WHERE id = {row_id};".format(row_id=event.row_id))
        execute(client, "DELETE FROM public.settings WHERE id = {row_id};".format(row_id=event.row_id))

        events = [event for event in poll(connection)]

        assert (len(events) == 2)

        event = events.pop(0)

        assert (event.type == 'UPDATE')
        assert (event.schema_name == 'public')
        assert (event.table_name == 'settings')

        event = events.pop(0)

        assert (event.type == 'DELETE')
        assert (event.schema_name == 'public')
        assert (event.table_name == 'settings')

    @mark.usefixtures('triggers_installed', 'event_channel_registered')
    def test_poll_multiple_table_events(self, connection, client):
        execute(client, "INSERT INTO public.settings(key, value) VALUES('foo', 1);")
        execute(client, "INSERT INTO pointofsale.orders(description) VALUES('bar');")
        events = [event for event in poll(connection)]

        assert (len(events) == 2)

        event = events.pop(0)
        assert (event.type == 'INSERT')
        assert (event.schema_name == 'public')
        assert (event.table_name == 'settings')

        event = events.pop(0)
        assert (event.type == 'INSERT')
        assert (event.schema_name == 'pointofsale')
        assert (event.table_name == 'orders')
