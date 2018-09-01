"""This module provides functionality for interacting directly with the database."""
__all__ = ['execute']


from typing import List, Optional, Tuple

from psycopg2 import ProgrammingError
from psycopg2.extensions import connection


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

    cursor = connection.cursor()
    cursor.execute(statement)

    # Get response
    try:
        response = cursor.fetchall()
        if not response:
            # Empty response list
            return None
    except ProgrammingError as e:
        if e.args and e.args[0] == 'no results to fetch':
            # No response available (i.e. no response given)
            return None

        # Some other programming error; re-raise
        raise e
    finally:
        cursor.close()

    return response
