"""This module provides functionality for managing triggers."""
__all__ = [
    "install_trigger",
    "install_trigger_function",
    "trigger_function_installed",
    "trigger_installed",
    "uninstall_trigger",
    "uninstall_trigger_function",
]


from psycopg2 import ProgrammingError
from psycopg2.extensions import connection

from psycopg2_pgevents.debug import log
from psycopg2_pgevents.sql import execute

_LOGGER_NAME = "pgevents.trigger"


INSTALL_TRIGGER_FUNCTION_STATEMENT = """
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

SET search_path = public, pg_catalog;

CREATE OR REPLACE FUNCTION {trigger_function}()
RETURNS TRIGGER AS $function$
  BEGIN
    IF (TG_OP = 'DELETE') THEN
      PERFORM pg_notify(
        'psycopg2_pgevents_channel',
        json_build_object(
            'event_id', uuid_generate_v4(),
            'event_type', TG_OP,
            'schema_name', TG_TABLE_SCHEMA,
            'table_name', TG_TABLE_NAME,
            'row', OLD
        )::text
      );
    ELSE
      PERFORM pg_notify(
        'psycopg2_pgevents_channel',
        json_build_object(
            'event_id', uuid_generate_v4(),
            'event_type', TG_OP,
            'schema_name', TG_TABLE_SCHEMA,
            'table_name', TG_TABLE_NAME,
            'row', NEW
        )::text
      );
    END IF;
    RETURN NULL;

    EXCEPTION
	WHEN data_exception THEN
	    RAISE WARNING '[AUDIT.IF_MODIFIED_FUNC] - UDF ERROR [DATA EXCEPTION] - SQLSTATE: %, SQLERRM: %',SQLSTATE,SQLERRM;
	    RETURN NULL;
	WHEN unique_violation THEN
	    RAISE WARNING '[AUDIT.IF_MODIFIED_FUNC] - UDF ERROR [UNIQUE] - SQLSTATE: %, SQLERRM: %',SQLSTATE,SQLERRM;
	    RETURN NULL;
	WHEN others THEN
	    RAISE WARNING '[AUDIT.IF_MODIFIED_FUNC] - UDF ERROR [OTHER] - SQLSTATE: %, SQLERRM: %',SQLSTATE,SQLERRM;
	    RETURN NULL;
  END;
$function$
LANGUAGE plpgsql;

SET search_path = "$user", public;
"""

UNINSTALL_TRIGGER_FUNCTION_STATEMENT = """
DROP FUNCTION IF EXISTS public.{trigger_function}() {modifier};
"""

INSTALL_TRIGGER_STATEMENT = """
SET search_path = {schema}, pg_catalog;

DROP TRIGGER IF EXISTS {trigger_name} ON {schema}.{table};

CREATE TRIGGER {trigger_name}
AFTER INSERT OR UPDATE OR DELETE ON {schema}.{table}
FOR EACH ROW
EXECUTE PROCEDURE public.{trigger_function}();

SET search_path = "$user", public;
"""

UNINSTALL_TRIGGER_STATEMENT = """
DROP TRIGGER IF EXISTS {trigger_name} ON {schema}.{table};
"""

SELECT_TRIGGER_STATEMENT = """
SELECT
    *
FROM
    information_schema.triggers
WHERE
    event_object_schema = '{schema}' AND
    event_object_table = '{table}' AND
    trigger_name = '{trigger_name}';
"""


def trigger_function_installed(connection: connection, trigger_function: str):
    """Test whether or not the psycopg2-pgevents trigger function is installed.

    Parameters
    ----------
    connection: psycopg2.extensions.connection
        Active connection to a PostGreSQL database.

    Returns
    -------
    bool
        True if the trigger function is installed, otherwise False.

    """
    installed = False

    log("Checking if trigger function installed...", logger_name=_LOGGER_NAME)

    try:
        execute(connection, f"SELECT pg_get_functiondef('public.{trigger_function}'::regproc);")
        installed = True
    except ProgrammingError as e:
        if e.args:
            error_stdout = e.args[0].splitlines()
            error = error_stdout.pop(0)
            if error.endswith("does not exist"):
                # Trigger function not installed
                pass
            else:
                # Some other exception; re-raise
                raise e
        else:
            # Some other exception; re-raise
            raise e

    log("...{}installed".format("" if installed else "NOT "), logger_name=_LOGGER_NAME)

    return installed


def trigger_installed(connection: connection, table: str, schema: str = "public"):
    """Test whether or not a psycopg2-pgevents trigger is installed for a table.

    Parameters
    ----------
    connection: psycopg2.extensions.connection
        Active connection to a PostGreSQL database.
    table: str
        Table whose trigger-existence will be checked.
    schema: str
        Schema to which the table belongs.

    Returns
    -------
    bool
        True if the trigger is installed, otherwise False.

    """
    installed = False

    log("Checking if {}.{} trigger installed...".format(schema, table), logger_name=_LOGGER_NAME)

    statement = SELECT_TRIGGER_STATEMENT.format(table=table, schema=schema, trigger_name=f"{table}_trigger")

    result = execute(connection, statement)
    if result:
        installed = True

    log("...{}installed".format("" if installed else "NOT "), logger_name=_LOGGER_NAME)

    return installed


def install_trigger_function(connection: connection,
                             table_name: str,
                             overwrite: bool = False) -> None:
    """Install the psycopg2-pgevents trigger function against the database.

    Parameters
    ----------
    connection: psycopg2.extensions.connection
        Active connection to a PostGreSQL database.
    overwrite: bool
        Whether or not to overwrite existing installation of psycopg2-pgevents
        trigger function, if existing installation is found.

    Returns
    -------
    None

    """
    prior_install = False

    if not overwrite:
        prior_install = trigger_function_installed(connection,
                                                   f"{table_name}_function")

    if not prior_install:
        log("Installing trigger function...", logger_name=_LOGGER_NAME)

        execute(connection,
                INSTALL_TRIGGER_FUNCTION_STATEMENT.format(
                    trigger_function=f"{table_name}_function"))
    else:
        log("Trigger function already installed; skipping...", logger_name=_LOGGER_NAME)


def uninstall_trigger_function(connection: connection,
                              table_name: str,
                              force: bool = False) -> None:
    """Uninstall the psycopg2-pgevents trigger function from the database.

    Parameters
    ----------
    connection: psycopg2.extensions.connection
        Active connection to a PostGreSQL database.
    force: bool
        If True, force the un-registration even if dependent triggers are still
        installed. If False, if there are any dependent triggers for the trigger
        function, the un-registration will fail.

    Returns
    -------
    None

    """
    modifier = ""
    if force:
        modifier = "CASCADE"

    log("Uninstalling trigger function (cascade={})...".format(force), logger_name=_LOGGER_NAME)

    statement = UNINSTALL_TRIGGER_FUNCTION_STATEMENT.format(modifier=modifier,
                trigger_function=f"{table_name}_function")
    execute(connection, statement)


def install_trigger(connection: connection, table: str, schema: str = "public", overwrite: bool = False) -> None:
    """Install a psycopg2-pgevents trigger against a table.

    Parameters
    ----------
    connection: psycopg2.extensions.connection
        Active connection to a PostGreSQL database.
    table: str
        Table for which the trigger should be installed.
    schema: str
        Schema to which the table belongs.
    overwrite: bool
        Whether or not to overwrite existing installation of trigger for the
        given table, if existing installation is found.

    Returns
    -------
    None

    """
    prior_install = False

    if not overwrite:
        prior_install = trigger_installed(connection, table, schema)

    if not prior_install:
        log("Installing {}.{} trigger...".format(schema, table), logger_name=_LOGGER_NAME)

        statement = INSTALL_TRIGGER_STATEMENT.format(schema=schema,
                                                     table=table,
                                                     trigger_name=f"{table}_trigger",
                                                     trigger_function=f"{table}_function")
        execute(connection, statement)
    else:
        log("{}.{} trigger already installed; skipping...".format(schema, table), logger_name=_LOGGER_NAME)


def uninstall_trigger(connection: connection, table: str, schema: str = "public") -> None:
    """Uninstall a psycopg2-pgevents trigger from a table.

    Parameters
    ----------
    connection: psycopg2.extensions.connection
        Active connection to a PostGreSQL database.
    table: str
        Table for which the trigger should be uninstalled.
    schema: str
        Schema to which the table belongs.

    Returns
    -------
    None

    """
    log("Uninstalling {}.{} trigger...".format(schema, table), logger_name=_LOGGER_NAME)

    statement = UNINSTALL_TRIGGER_STATEMENT.format(schema=schema, table=table, trigger_name=f"{table}_trigger")
    execute(connection, statement)
