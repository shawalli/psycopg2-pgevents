from psycopg2 import ProgrammingError

from psycopg2_pgevents.sql import execute


class TestSql:
    def test_execute(self, connection):
        results = execute(connection, 'SELECT * FROM pg_settings;')

        assert (results is not None)

    def test_execute_programming_error(self, connection):
        programming_exception_raised = False
        try:
            # Raise exception by referencing a non-existent table
            execute(connection, 'SELECT * FROM information_schema.triggerss;')
        except ProgrammingError:
            programming_exception_raised = True

        assert (programming_exception_raised == True)

    def test_execute_no_response(self, connection):
        results = execute(connection, 'SELECT * FROM information_schema.triggers;')

        assert (results is None)
