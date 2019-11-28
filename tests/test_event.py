import json
from uuid import UUID

from pytest import fixture, mark

from psycopg2_pgevents import event
from psycopg2_pgevents.sql import execute
from psycopg2_pgevents.trigger import install_trigger, install_trigger_function


@fixture
def event_channel_registered(connection):
    event.register_event_channel(connection)


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

        evt = event.Event.fromjson(json_string)
        assert evt.id == UUID("c2d29867-3d0b-d497-9191-18a9d8ee7830")
        assert evt.type == "insert"
        assert evt.schema_name == "public"
        assert evt.table_name == "widget"
        assert evt.row_id == "1"

    def test_event_tojson(self):
        evt = event.Event("c2d29867-3d0b-d497-9191-18a9d8ee7830", "insert", "public", "widget", "1")

        json_string = evt.tojson()
        json_dict = json.loads(json_string)
        assert json_dict["event_id"] == str(evt.id)
        assert json_dict["event_type"] == evt.type
        assert json_dict["schema_name"] == evt.schema_name
        assert json_dict["table_name"] == evt.table_name
        assert json_dict["row_id"] == evt.row_id

    def test_register_event_channel(self, connection):
        channel_registered = False

        event.register_event_channel(connection)

        results = execute(connection, "SELECT pg_listening_channels();")
        if results and "psycopg2_pgevents_channel" in results[0]:
            channel_registered = True

        assert channel_registered

    @mark.usefixtures("event_channel_registered")
    def test_unregister_event_channel(self, connection):
        channel_registered = True

        event.unregister_event_channel(connection)

        results = execute(connection, "SELECT pg_listening_channels();")
        if not results:
            channel_registered = False

        assert not channel_registered

    @mark.usefixtures("triggers_installed", "event_channel_registered")
    def test_poll_timeout(self, connection):
        num_evts = 0

        for evt in event.poll(connection):
            num_evts += 1

        assert num_evts == 0

    @mark.usefixtures("triggers_installed", "event_channel_registered")
    def test_poll_public_schema_table_event(self, connection, client):
        execute(client, "INSERT INTO public.settings(key, value) VALUES('foo', 1);")

        evts = [evt for evt in event.poll(connection)]

        assert len(evts) == 1

        evt = evts.pop(0)

        assert evt.type == "INSERT"
        assert evt.schema_name == "public"
        assert evt.table_name == "settings"

    @mark.usefixtures("triggers_installed", "event_channel_registered")
    def test_poll_custom_schema_table_event(self, connection, client):
        execute(client, "INSERT INTO pointofsale.orders(description) VALUES('bar');")

        evts = [evt for evt in event.poll(connection)]

        assert len(evts) == 1

        evt = evts.pop(0)

        assert evt.type == "INSERT"
        assert evt.schema_name == "pointofsale"
        assert evt.table_name == "orders"

    @mark.usefixtures("triggers_installed", "event_channel_registered")
    def test_poll_event_event_types(self, connection, client):
        execute(client, "INSERT INTO public.settings(key, value) VALUES('foo', 1);")

        evts = [evt for evt in event.poll(connection)]

        assert len(evts) == 1

        evt = evts.pop(0)

        assert evt.type == "INSERT"
        assert evt.schema_name == "public"
        assert evt.table_name == "settings"

        execute(client, "UPDATE public.settings SET value = 2 WHERE id = {row_id};".format(row_id=evt.row_id))
        execute(client, "DELETE FROM public.settings WHERE id = {row_id};".format(row_id=evt.row_id))

        evts = [evt for evt in event.poll(connection)]

        assert len(evts) == 2

        evt = evts.pop(0)

        assert evt.type == "UPDATE"
        assert evt.schema_name == "public"
        assert evt.table_name == "settings"

        evt = evts.pop(0)

        assert evt.type == "DELETE"
        assert evt.schema_name == "public"
        assert evt.table_name == "settings"

    @mark.usefixtures("triggers_installed", "event_channel_registered")
    def test_poll_multiple_table_evts(self, connection, client):
        execute(client, "INSERT INTO public.settings(key, value) VALUES('foo', 1);")
        execute(client, "INSERT INTO pointofsale.orders(description) VALUES('bar');")
        evts = [evt for evt in event.poll(connection)]

        assert len(evts) == 2

        evt = evts.pop(0)
        assert evt.type == "INSERT"
        assert evt.schema_name == "public"
        assert evt.table_name == "settings"

        evt = evts.pop(0)
        assert evt.type == "INSERT"
        assert evt.schema_name == "pointofsale"
        assert evt.table_name == "orders"
