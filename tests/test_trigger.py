from psycopg2 import InternalError, ProgrammingError
from pytest import fixture, mark

from psycopg2_pgevents.db import execute
from psycopg2_pgevents.trigger import register_trigger, register_trigger_function, unregister_trigger, \
    unregister_trigger_function


@fixture
def trigger_fn_registered(connection):
    register_trigger_function(connection)


@fixture
def public_schema_trigger_registered(connection):
    register_trigger(connection, 'settings')


@fixture
def custom_schema_trigger_registered(connection):
    register_trigger(connection, 'orders', schema='pointofsale')


class TestTrigger:
    def test_add_trigger_function(self, connection):
        trigger_function_registered = False

        register_trigger_function(connection)
        try:
            execute(connection, "SELECT pg_get_functiondef('public.pgevents'::regproc);")
            trigger_function_registered = True
        except:
            # Ignore error, its only use in this test is cause following
            # assertion to fail
            pass

        assert (trigger_function_registered == True)

    @mark.usefixtures('trigger_fn_registered')
    def test_remove_trigger_function(self, connection):
        trigger_function_registered = True

        unregister_trigger_function(connection)
        try:
            execute(connection, "SELECT pg_get_functiondef('public.pgevents'::regproc);")
        except ProgrammingError:
            trigger_function_registered = False

        assert (trigger_function_registered == False)

    @mark.usefixtures('trigger_fn_registered')
    def test_add_public_schema_trigger(self, connection):
        trigger_registered = False

        register_trigger(connection, 'settings')

        try:
            statement = """
            SELECT
                *
            FROM
                information_schema.triggers
            WHERE
                event_object_schema = 'public' AND
                event_object_table = 'settings';
            """
            result = execute(connection, statement)
            if result:
                trigger_registered = True
        except:
            # Ignore error, its only use in this test is cause following
            # assertion to fail
            pass

        assert (trigger_registered == True)

    @mark.usefixtures('trigger_fn_registered')
    def test_add_custom_schema_trigger(self, connection):
        trigger_registered = False

        register_trigger(connection, 'orders', schema='pointofsale')

        try:
            statement = """
            SELECT
                *
            FROM
                information_schema.triggers
            WHERE
                event_object_schema = 'pointofsale' AND
                event_object_table = 'orders';
            """
            result = execute(connection, statement)
            if result:
                trigger_registered = True
        except:
            # Ignore error, its only use in this test is cause following
            # assertion to fail
            pass

        assert (trigger_registered == True)

    @mark.usefixtures('trigger_fn_registered', 'public_schema_trigger_registered')
    def test_remove_trigger_function_with_dependent_triggers(self, connection):
        trigger_function_removal_failed = False
        trigger_function_still_registered = False

        try:
            unregister_trigger_function(connection)
        except InternalError:
            trigger_function_removal_failed = True

        try:
            execute(connection, "SELECT pg_get_functiondef('public.pgevents'::regproc);")
            trigger_function_still_registered = True
        except:
            # Ignore error, its only use in this test is cause following
            # assertion to fail
            pass

        assert (trigger_function_removal_failed == True)
        assert (trigger_function_still_registered == True)

    @mark.usefixtures('trigger_fn_registered', 'public_schema_trigger_registered')
    def test_force_remove_trigger_function_with_dependent_triggers(self, connection):
        trigger_function_still_registered = True
        trigger_registered = False

        unregister_trigger_function(connection, force=True)

        try:
            execute(connection, "SELECT pg_get_functiondef('public.pgevents'::regproc);")
        except ProgrammingError:
            trigger_function_still_registered = False

        statement = """
        SELECT
            *
        FROM
            information_schema.triggers
        WHERE
            event_object_schema = 'settings' AND
            event_object_table = 'public';
        """
        result = execute(connection, statement)
        if not result:
            trigger_registered = False

        assert (trigger_function_still_registered == False)
        assert (trigger_registered == False)

    @mark.usefixtures('trigger_fn_registered', 'public_schema_trigger_registered')
    def test_remove_public_schema_trigger(self, connection):
        trigger_registered = True

        unregister_trigger(connection, 'settings')
        statement = """
        SELECT
            *
        FROM
            information_schema.triggers
        WHERE
            event_object_schema = 'settings' AND
            event_object_table = 'public';
        """
        result = execute(connection, statement)
        if not result:
            trigger_registered = False

        assert (trigger_registered == False)

    @mark.usefixtures('trigger_fn_registered', 'custom_schema_trigger_registered')
    def test_remove_custom_schema_trigger(self, connection):
        trigger_registered = True

        unregister_trigger(connection, 'orders', schema='pointofsale')
        statement = """
        SELECT
            *
        FROM
            information_schema.triggers
        WHERE
            event_object_schema = 'orders' AND
            event_object_table = 'pointofsale';
        """
        result = execute(connection, statement)
        if not result:
            trigger_registered = False

        assert (trigger_registered == False)
