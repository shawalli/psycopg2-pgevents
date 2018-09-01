from psycopg2 import ProgrammingError
from pytest import fixture, mark

from psycopg2_pgevents.db import execute
from psycopg2_pgevents.event import poll, register_event_channel, unregister_event_channel
from psycopg2_pgevents.trigger import install_trigger, install_trigger_function


@fixture
def event_channel_registered(connection):
    register_event_channel(connection)


@fixture
def triggers_installed(connection):
    install_trigger_function(connection)
    install_trigger(connection, 'settings')
    install_trigger(connection, 'orders', schema='pointofsale')


class TestEvent:
    def test_register_event_channel(self, connection):
        channel_registered = False

        register_event_channel(connection)

        results = execute(connection, 'SELECT pg_listening_channels();')
        if results and 'pgevents' in results[0]:
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
        num_notifications = 0

        for notification in poll(connection):
            num_notifications += 1

        assert (num_notifications == 0)

    @mark.usefixtures('triggers_installed', 'event_channel_registered')
    def test_poll_public_schema_table_notification(self, connection, client):
        execute(client, "INSERT INTO public.settings(key, value) VALUES('foo', 1);")

        notifications = [notification for notification in poll(connection)]

        assert (len(notifications) == 1)

        notification = notifications.pop()

        assert (notification['event'] == 'INSERT')
        assert (notification['schema_name'] == 'public')
        assert (notification['table_name'] == 'settings')

        bad_notification_keys = set(notification.keys()).difference(set(('id', 'event', 'schema_name', 'table_name')))
        assert (len(bad_notification_keys) == 0)

    @mark.usefixtures('triggers_installed', 'event_channel_registered')
    def test_poll_custom_schema_table_notification(self, connection, client):
        execute(client, "INSERT INTO pointofsale.orders(description) VALUES('bar');")

        notifications = [notification for notification in poll(connection)]

        assert (len(notifications) == 1)

        notification = notifications.pop()

        assert (notification['event'] == 'INSERT')
        assert (notification['schema_name'] == 'pointofsale')
        assert (notification['table_name'] == 'orders')

        bad_notification_keys = set(notification.keys()).difference(set(('id', 'event', 'schema_name', 'table_name')))
        assert (len(bad_notification_keys) == 0)

    @mark.usefixtures('triggers_installed', 'event_channel_registered')
    def test_poll_notification_event_types(self, connection, client):
        execute(client, "INSERT INTO public.settings(key, value) VALUES('foo', 1);")

        notifications = [notification for notification in poll(connection)]

        assert (len(notifications) == 1)

        notification = notifications.pop()

        assert (notification['event'] == 'INSERT')
        assert (notification['schema_name'] == 'public')
        assert (notification['table_name'] == 'settings')

        bad_notification_keys = set(notification.keys()).difference(set(('id', 'event', 'schema_name', 'table_name')))
        assert (len(bad_notification_keys) == 0)

        execute(client, "UPDATE public.settings SET value = 2 WHERE id = {row_id};".format(row_id=notification['id']))
        execute(client, "DELETE FROM public.settings WHERE id = {row_id};".format(row_id=notification['id']))

        notifications = [notification for notification in poll(connection)]

        assert (len(notifications) == 2)

        notification = notifications.pop()

        assert (notification['event'] == 'UPDATE')
        assert (notification['schema_name'] == 'public')
        assert (notification['table_name'] == 'settings')

        notification = notifications.pop()

        assert (notification['event'] == 'DELETE')
        assert (notification['schema_name'] == 'public')
        assert (notification['table_name'] == 'settings')

    @mark.usefixtures('triggers_installed', 'event_channel_registered')
    def test_poll_multiple_table_notifications(self, connection, client):
        execute(client, "INSERT INTO public.settings(key, value) VALUES('foo', 1);")
        execute(client, "INSERT INTO pointofsale.orders(description) VALUES('bar');")
        notifications = [notification for notification in poll(connection)]

        assert (len(notifications) == 2)

        notification = notifications.pop()
        assert (notification['event'] == 'INSERT')
        assert (notification['schema_name'] == 'public')
        assert (notification['table_name'] == 'settings')

        notification = notifications.pop()
        assert (notification['event'] == 'INSERT')
        assert (notification['schema_name'] == 'pointofsale')
        assert (notification['table_name'] == 'orders')
