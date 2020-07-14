from os import environ
from pathlib import Path

from psycopg2 import connect
from pytest import fixture
from testfixtures import LogCapture

from psycopg2_pgevents.debug import set_debug

DATABASE_BASE_URL = environ.get("TEST_DATABASE_BASE_URL", "postgres://")
CI_DATABASE = environ.get("TEST_DATABASE_CI", "postgres")

CI_DATABASE_DSN = "/".join([DATABASE_BASE_URL, CI_DATABASE])
TEST_DATABASE_DSN = "/".join([DATABASE_BASE_URL, "test"])

DATABASE_SHAPE_SQL_FILE = Path(Path(__file__).parent, "resources", "database_shape.sql")


@fixture
def log_capture():
    set_debug(True)

    with LogCapture() as capture:
        yield capture


@fixture
def connection():
    # Create fresh test database
    _conn = connect(dsn=CI_DATABASE_DSN, password="postgres")
    _conn.autocommit = True

    _curs = _conn.cursor()
    _curs.execute("DROP DATABASE IF EXISTS test")
    _curs.execute("CREATE DATABASE test")
    _conn.close()

    # Create test database connection
    conn = connect(dsn=TEST_DATABASE_DSN, password="postgres")
    conn.autocommit = True
    curs = conn.cursor()

    # Define test database shape
    with open(DATABASE_SHAPE_SQL_FILE, "r") as sql_file:
        sql_contents = sql_file.read()

        curs.execute(sql_contents)

    yield conn

    conn.close()


@fixture
def client():
    conn = connect(dsn=TEST_DATABASE_DSN)
    conn.autocommit = True

    yield conn

    conn.close()
