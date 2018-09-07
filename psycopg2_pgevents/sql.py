"""This module provides functionality for interacting directly with the database."""
__all__ = ['execute']


from typing import Dict, List, Optional, Tuple, Union

from psycopg2 import ProgrammingError
from psycopg2.extensions import connection, cursor

from psycopg2_pgevents.debug import log

_LOGGER_NAME = 'pgevents.sql'


class Psycopg2Cursor(cursor):
    def execute(self, query: str, args: Union[Dict, List, None]=None):
        log('Query', logger_name=_LOGGER_NAME)
        log('-----', logger_name=_LOGGER_NAME)
        log(self.mogrify(query, args), logger_name=_LOGGER_NAME)

        try:
            super().execute(query, args)
        except Exception as e:
            log('Exception', category='error', logger_name=_LOGGER_NAME)
            log('---------', category='error', logger_name=_LOGGER_NAME)
            log(
                '{name}: {msg}'.format(
                    name=e.__class__.__name__,
                    msg=str(e)
                ),
                category='error',
                logger_name=_LOGGER_NAME
            )
            raise


def execute(connection: connection, statement: str) -> Optional[List[Tuple[str, ...]]]:
    """Execute PGSQL statement and fetches the statement response.

    Parameters
    ----------
    connection: psycopg2.extensions.connection
        Active connection to a PostGreSQL database.
    statement: str
        PGSQL statement to run against the database.

    Returns
    -------
    response: list or None
        List of tuples, where each tuple represents a formatted line of response from the database engine, where
        each tuple item roughly corresponds to a column. For instance, while a raw SELECT response might include
        the table headers, psycopg2 returns only the rows that matched. If no response was given, None is returned.
    """
    response = list()  # type: List

    # See the following link for reasoning behind both with statements:
    #   http://initd.org/psycopg/docs/usage.html#with-statement
    #
    # Additionally, the with statement makes this library safer to use with
    # higher-level libraries (e.g. SQLAlchemy) that don't inherently respect
    # PostGreSQL's autocommit isolation-level, since the transaction is
    # properly completed for each statement.
    with connection:
        with connection.cursor(cursor_factory=Psycopg2Cursor) as cursor:
            cursor.execute(statement)
            connection.commit()

            # Get response
            try:
                response = cursor.fetchall()
                if not response:
                    # Empty response list
                    log('<No Response>', logger_name=_LOGGER_NAME)
                    return None
            except ProgrammingError as e:
                if e.args and e.args[0] == 'no results to fetch':
                    # No response available (i.e. no response given)
                    log('<No Response>', logger_name=_LOGGER_NAME)
                    return None

                # Some other programming error; re-raise
                raise e

            log('Response', logger_name=_LOGGER_NAME)
            log('--------', logger_name=_LOGGER_NAME)
            for line in response:
                log(str(line), logger_name=_LOGGER_NAME)

    return response
