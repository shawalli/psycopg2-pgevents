from psycopg2 import DatabaseError, ProgrammingError


def execute(connection, statement):
    cursor = connection.cursor()
    autocommit_setting = connection.autocommit

    result = list()
    try:
        connection.autocommit = True

        cursor.execute(statement)

        try:
            response = cursor.fetchall()
            if not response:
                # Empty response list
                return None
        except ProgrammingError as e:
            if e.args and e.args[0] == 'no results to fetch':
                # No response available (i.e. no response given)
                return None
            else:
                # Some other PG error; re-raise
                raise e

        first_line = response[0]
        if first_line[0].startswith('ERROR'):
            # Error returned in response
            msg = '\n'.join([' '.join(line) for line in response])

            raise DatabaseError(msg)

        return result
    finally:
        connection.autocommit = autocommit_setting
