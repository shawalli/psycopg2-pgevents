
from pathlib import Path

from psycopg2 import connect
from pytest import fixture

DEFAULT_DATABASE = 'postgres'
TEST_DATABASE = 'test'

DATABASE_SHAPE_SQL_FILE = Path(Path(__file__).parent, 'resources', 'database_shape.sql')


@fixture
def connection():
    # Create fresh test database
    _conn = connect(database=DEFAULT_DATABASE)
    _conn.autocommit = True

    _curs = _conn.cursor()
    _curs.execute('DROP DATABASE IF EXISTS {db}'.format(db=TEST_DATABASE))
    _curs.execute('CREATE DATABASE {db}'.format(db=TEST_DATABASE))
    _conn.close()

    # Create test database connection
    conn = connect(database=TEST_DATABASE)
    conn.autocommit = True
    curs = conn.cursor()

    # Define test database shape
    with open(DATABASE_SHAPE_SQL_FILE, 'r') as sql_file:
        sql_contents = sql_file.read()

        curs.execute(sql_contents)

    yield conn

    conn.close()


@fixture
def client():
    conn = connect(database=TEST_DATABASE)
    conn.autocommit = True
    curs = conn.cursor()

    yield conn

    conn.close()
