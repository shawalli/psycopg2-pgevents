from psycopg2 import DatabaseError, ProgrammingError
from pytest import fixture, mark

from sqlalchemy_pgevents.base import execute
from sqlalchemy_pgevents.trigger import register_trigger_function, unregister_trigger_function


@fixture
def trigger_fn_registered(connection):
    register_trigger_function(connection)


class TestTrigger:
    def test_add_trigger_function(self, connection):
        trigger_function_registered = False

        register_trigger_function(connection)
        try:
            execute(connection, "SELECT pg_get_functiondef('public.pgevents'::regproc);")
            trigger_function_registered = True
        except DatabaseError:
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
