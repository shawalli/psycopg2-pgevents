from psycopg2 import InternalError, ProgrammingError
from pytest import fixture, mark

from psycopg2_pgevents.sql import execute
from psycopg2_pgevents.trigger import install_trigger, install_trigger_function, trigger_function_installed, \
    trigger_installed, uninstall_trigger, uninstall_trigger_function


@fixture
def trigger_fn_installed(connection):
    install_trigger_function(connection)


@fixture
def public_schema_trigger_installed(connection):
    install_trigger(connection, 'settings')


@fixture
def custom_schema_trigger_installed(connection):
    install_trigger(connection, 'orders', schema='pointofsale')


class TestTrigger:
    # TODO: add tests for install_trigger_function where:
    #       - overwrite=False, prior_install=True
    #       - overwrite=True, prior_install=True
    # TODO: add tests for install_trigger where:
    #       - overwrite=False, prior_install=True
    #       - overwrite=True, prior_install=True

    def test_trigger_function_not_installed(self, connection):
        installed = trigger_function_installed(connection)

        assert (installed == False)

    @mark.usefixtures('trigger_fn_installed')
    def test_trigger_function_installed(self, connection):
        installed = trigger_function_installed(connection)

        assert (installed == True)

    def test_add_trigger_function(self, connection):
        trigger_function_installed = False

        install_trigger_function(connection)
        try:
            execute(connection, "SELECT pg_get_functiondef('public.psycopg2_pgevents_create_event'::regproc);")
            trigger_function_installed = True
        except:
            # Ignore error, its only use in this test is cause following
            # assertion to fail
            pass

        assert (trigger_function_installed == True)

    @mark.usefixtures('trigger_fn_installed')
    def test_remove_trigger_function(self, connection):
        trigger_function_installed = True

        uninstall_trigger_function(connection)
        try:
            execute(connection, "SELECT pg_get_functiondef('public.psycopg2_pgevents_create_event'::regproc);")
        except ProgrammingError:
            trigger_function_installed = False

        assert (trigger_function_installed == False)

    @mark.usefixtures('trigger_fn_installed')
    def test_add_public_schema_trigger(self, connection):
        trigger_installed = False

        install_trigger(connection, 'settings')

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
                trigger_installed = True
        except:
            # Ignore error, its only use in this test is cause following
            # assertion to fail
            pass

        assert (trigger_installed == True)

    @mark.usefixtures('trigger_fn_installed')
    def test_add_custom_schema_trigger(self, connection):
        trigger_installed = False

        install_trigger(connection, 'orders', schema='pointofsale')

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
                trigger_installed = True
        except:
            # Ignore error, its only use in this test is cause following
            # assertion to fail
            pass

        assert (trigger_installed == True)

    def test_trigger_not_installed(self, connection):
        installed = trigger_installed(connection, 'settings')

        assert (installed == False)

    @mark.usefixtures('trigger_fn_installed', 'public_schema_trigger_installed')
    def test_trigger_installed(self, connection):
        installed = trigger_installed(connection, 'settings')

        assert (installed == True)

    @mark.usefixtures('trigger_fn_installed', 'public_schema_trigger_installed')
    def test_remove_trigger_function_with_dependent_triggers(self, connection):
        trigger_function_removal_failed = False
        trigger_function_still_installed = False

        try:
            uninstall_trigger_function(connection)
        except InternalError:
            trigger_function_removal_failed = True

        try:
            execute(connection, "SELECT pg_get_functiondef('public.psycopg2_pgevents_create_event'::regproc);")
            trigger_function_still_installed = True
        except:
            # Ignore error, its only use in this test is cause following
            # assertion to fail
            pass

        assert (trigger_function_removal_failed == True)
        assert (trigger_function_still_installed == True)

    @mark.usefixtures('trigger_fn_installed', 'public_schema_trigger_installed')
    def test_force_remove_trigger_function_with_dependent_triggers(self, connection):
        trigger_function_still_installed = True
        trigger_installed = False

        uninstall_trigger_function(connection, force=True)

        try:
            execute(connection, "SELECT pg_get_functiondef('public.psycopg2_pgevents_create_event'::regproc);")
        except ProgrammingError:
            trigger_function_still_installed = False

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
            trigger_installed = False

        assert (trigger_function_still_installed == False)
        assert (trigger_installed == False)

    @mark.usefixtures('trigger_fn_installed', 'public_schema_trigger_installed')
    def test_remove_public_schema_trigger(self, connection):
        trigger_installed = True

        uninstall_trigger(connection, 'settings')
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
            trigger_installed = False

        assert (trigger_installed == False)

    @mark.usefixtures('trigger_fn_installed', 'custom_schema_trigger_installed')
    def test_remove_custom_schema_trigger(self, connection):
        trigger_installed = True

        uninstall_trigger(connection, 'orders', schema='pointofsale')
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
            trigger_installed = False

        assert (trigger_installed == False)
