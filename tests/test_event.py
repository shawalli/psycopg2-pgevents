from psycopg2 import ProgrammingError
from pytest import fixture, mark

from sqlalchemy_pgevents.base import execute
from sqlalchemy_pgevents.event import poll, register_event_channel, unregister_event_channel
from sqlalchemy_pgevents.trigger import register_trigger, register_trigger_function


@fixture
def event_channel_registered(connection):
    register_event_channel(connection)


@fixture
def triggers_registered(connection):
    register_trigger_function(connection)
    register_trigger(connection, 'settings')
    register_trigger(connection, 'orders', schema='pointofsale')


def dump(connection, statement):
    print(execute(connection, statement))


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

    @mark.usefixtures('triggers_registered', 'event_channel_registered')
    def test_poll_timout(self, connection):
        num_notifications = 0

        for notification in poll(connection):
            num_notifications += 1

        assert (num_notifications == 0)

    @mark.usefixtures('triggers_registered', 'event_channel_registered')
    def test_poll_public_schema_table_notification(self, connection, client):
        execute(client, "INSERT INTO public.settings(key, value) VALUES('foo', 1);")

        notifications = [notification for notification in poll(connection)]

        assert (len(notifications) == 1)

        notification = notifications.pop()

        assert (notification['schema_name'] == 'public')
        assert (notification['table_name'] == 'settings')

        bad_notification_keys = set(notification.keys()).difference(set(('id', 'schema_name', 'table_name')))
        assert (len(bad_notification_keys) == 0)

    @mark.usefixtures('triggers_registered', 'event_channel_registered')
    def test_poll_custom_schema_table_notification(self, connection, client):
        execute(client, "INSERT INTO pointofsale.orders(description) VALUES('bar');")

        notifications = [notification for notification in poll(connection)]

        assert (len(notifications) == 1)

        notification = notifications.pop()

        assert (notification['schema_name'] == 'pointofsale')
        assert (notification['table_name'] == 'orders')

        bad_notification_keys = set(notification.keys()).difference(set(('id', 'schema_name', 'table_name')))
        assert (len(bad_notification_keys) == 0)

    @mark.usefixtures('triggers_registered', 'event_channel_registered')
    def test_poll_multiple_notifications(self, connection, client):
        execute(client, "INSERT INTO public.settings(key, value) VALUES('foo', 1);")
        execute(client, "INSERT INTO public.settings(key, value) VALUES('bar', 2);")
        execute(client, "INSERT INTO public.settings(key, value) VALUES('baz', 3);")

        notifications = [notification for notification in poll(connection)]

        assert (len(notifications) == 3)

    @mark.usefixtures('triggers_registered', 'event_channel_registered')
    def test_poll_iterative_notifications(self, connection, client):
        execute(client, "INSERT INTO public.settings(key, value) VALUES('foo', 1);")

        notifications = [notification for notification in poll(connection)]
        assert (len(notifications) == 1)

        execute(client, "INSERT INTO public.settings(key, value) VALUES('bar', 2);")
        execute(client, "INSERT INTO public.settings(key, value) VALUES('baz', 3);")

        notifications = [notification for notification in poll(connection)]
        assert (len(notifications) == 2)

    @mark.usefixtures('triggers_registered', 'event_channel_registered')
    def test_poll_multiple_table_notifications(self, connection, client):
        execute(client, "INSERT INTO public.settings(key, value) VALUES('foo', 1);")
        execute(client, "INSERT INTO pointofsale.orders(description) VALUES('bar');")
        notifications = [notification for notification in poll(connection)]

        assert (len(notifications) == 2)

        notification = notifications.pop()
        assert (notification['schema_name'] == 'public')
        assert (notification['table_name'] == 'settings')

        notification = notifications.pop()
        assert (notification['schema_name'] == 'pointofsale')
        assert (notification['table_name'] == 'orders')
