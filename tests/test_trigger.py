
from sqlalchemy_pgevents.base import execute
from sqlalchemy_pgevents.trigger import register_trigger_function


class TestTrigger:
    def test_add_trigger_function(self, connection):
        register_trigger_function(connection)

        trigger_function_registered = False
        try:
            execute(
                connection, "SELECT pg_get_functiondef('public.pgevents'::regproc);")
            trigger_function_registered = True
        except DatabaseError:
            # Ignore error, its only use in this test is cause following
            # assertion to fail
            pass

        assert (trigger_function_registered == True)
