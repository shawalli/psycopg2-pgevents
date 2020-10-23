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

CREATE OR REPLACE FUNCTION psycopg2_pgevents_create_event{triggerid}()
RETURNS TRIGGER AS $function$
  DECLARE
    row_id {rowidtype};
  BEGIN
    IF (TG_OP = 'DELETE') THEN
      row_id = OLD.{rowid};
    ELSE
      row_id = NEW.{rowid};
    END IF;
    PERFORM pg_notify(
     'psycopg2_pgevents_channel',
      json_build_object(
        'event_id', uuid_generate_v4(),
        'event_type', TG_OP,
        'schema_name', TG_TABLE_SCHEMA,
        'table_name', TG_TABLE_NAME,
        'row_id', row_id
      )::text
    );
    RETURN NULL;
  END;
$function$
LANGUAGE plpgsql;

SET search_path = "$user", public;
"""

UNINSTALL_TRIGGER_FUNCTION_STATEMENT = """
DROP FUNCTION IF EXISTS public.psycopg2_pgevents_create_event{triggerid}() {modifier};
"""

INSTALL_TRIGGER_STATEMENT = """
SET search_path = {schema}, pg_catalog;

DROP TRIGGER IF EXISTS psycopg2_pgevents_trigger{triggerid} ON {schema}.{table};

CREATE TRIGGER psycopg2_pgevents_trigger{triggerid}
AFTER INSERT{orupdate}{ordelete} ON {schema}.{table}
FOR EACH ROW
EXECUTE PROCEDURE public.psycopg2_pgevents_create_event{triggerid}();

SET search_path = "$user", public;
"""

UNINSTALL_TRIGGER_STATEMENT = """
DROP TRIGGER IF EXISTS psycopg2_pgevents_trigger{triggerid} ON {schema}.{table};
"""

SELECT_TRIGGER_STATEMENT = """
SELECT
    *
FROM
    information_schema.triggers
WHERE
    event_object_schema = '{schema}' AND
    event_object_table = '{table}' AND
    trigger_name = 'psycopg2_pgevents_trigger{triggerid}';
"""


def trigger_function_installed(connection: connection, triggerid: str = ""):
    """Test whether or not the psycopg2-pgevents trigger function is installed.

    Parameters
    ----------
    connection: psycopg2.extensions.connection
        Active connection to a PostGreSQL database.
    triggerid: str
        If there's more than 1 trigger in this database, we need to uniquely identify the trigger with an extra id

    Returns
    -------
    bool
        True if the trigger function is installed, otherwise False.

    """
    installed = False

    log("Checking if trigger function installed...", logger_name=_LOGGER_NAME)

    if triggerid:
        triggerid = "_{triggerid}".format(triggerid=triggerid)

    try:
        execute(
            connection,
            "SELECT pg_get_functiondef('public.psycopg2_pgevents_create_event{triggerid}'::regproc);".format(
                triggerid=triggerid
            ),
        )
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


def trigger_installed(connection: connection, table: str, schema: str = "public", triggerid: str = ""):
    """Test whether or not a psycopg2-pgevents trigger is installed for a table.

    Parameters
    ----------
    connection: psycopg2.extensions.connection
        Active connection to a PostGreSQL database.
    table: str
        Table whose trigger-existence will be checked.
    schema: str
        Schema to which the table belongs.
    triggerid: str
        If there's more than 1 trigger in this database, we need to uniquely identify the trigger with an extra id

    Returns
    -------
    bool
        True if the trigger is installed, otherwise False.

    """
    installed = False

    log("Checking if {}.{} trigger installed...".format(schema, table), logger_name=_LOGGER_NAME)

    # FIXME: add some validation to ensure valid characters for triggerid
    if triggerid:
        triggerid = "_{triggerid}".format(triggerid=triggerid)

    statement = SELECT_TRIGGER_STATEMENT.format(table=table, schema=schema, triggerid=triggerid)

    result = execute(connection, statement)
    if result:
        installed = True

    log("...{}installed".format("" if installed else "NOT "), logger_name=_LOGGER_NAME)

    return installed


def install_trigger_function(
    connection: connection, rowid, rowidtype: str, overwrite: bool = False, triggerid: str = ""
) -> None:
    """Install the psycopg2-pgevents trigger function against the database.

    Parameters
    ----------
    connection: psycopg2.extensions.connection
        Active connection to a PostGreSQL database.
    overwrite: bool
        Whether or not to overwrite existing installation of psycopg2-pgevents
        trigger function, if existing installation is found.
    rowid: string
        The id to return for the row, e.g. id, ordercode, etc
    triggerid: str
        If there's more than 1 trigger in this database, we need to uniquely identify the trigger with an extra id

    Returns
    -------
    None

    """
    prior_install = False

    if not overwrite:
        prior_install = trigger_function_installed(connection, triggerid)

    if triggerid:
        triggerid = "_{triggerid}".format(triggerid=triggerid)

    if not prior_install:
        log("Installing trigger function...", logger_name=_LOGGER_NAME)

        execute(
            connection, INSTALL_TRIGGER_FUNCTION_STATEMENT.format(rowid=rowid, rowidtype=rowidtype, triggerid=triggerid)
        )
    else:
        log("Trigger function already installed; skipping...", logger_name=_LOGGER_NAME)


def uninstall_trigger_function(connection: connection, force: bool = False, triggerid: str = "") -> None:
    """Uninstall the psycopg2-pgevents trigger function from the database.

    Parameters
    ----------
    connection: psycopg2.extensions.connection
        Active connection to a PostGreSQL database.
    force: bool
        If True, force the un-registration even if dependent triggers are still
        installed. If False, if there are any dependent triggers for the trigger
        function, the un-registration will fail.
    triggerid: str
        If there's more than 1 trigger in this database, we need to uniquely identify the trigger with an extra id

    Returns
    -------
    None

    """
    modifier = ""
    if force:
        modifier = "CASCADE"

    if triggerid:
        triggerid = "_{triggerid}".format(triggerid=triggerid)

    log("Uninstalling trigger function (cascade={})...".format(force), logger_name=_LOGGER_NAME)

    statement = UNINSTALL_TRIGGER_FUNCTION_STATEMENT.format(modifier=modifier, triggerid=triggerid)
    execute(connection, statement)


def install_trigger(
    connection: connection,
    table: str,
    schema: str = "public",
    overwrite: bool = False,
    trigger_on_update: bool = True,
    trigger_on_delete: bool = True,
    triggerid: str = "",
) -> None:
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
    trigger_on_update: bool
        Whether or not to add a "OR UPDATE" clause to the trigger; by default "ON INSERT OR UPDATE OR DELETE" is used
    trigger_on_delete: bool
        Whether or not to add a "OR DELETE" clause to the trigger; by default "ON INSERT OR UPDATE OR DELETE" is used
    triggerid: str
        If there's more than 1 trigger in this database, we need to uniquely identify the trigger with an extra id

    Returns
    -------
    None

    """
    prior_install = False
    orupdate = " OR UPDATE"
    ordelete = " OR DELETE"

    if not overwrite:
        prior_install = trigger_installed(connection, table, schema)

    if not trigger_on_update:
        orupdate = ""

    if not trigger_on_delete:
        ordelete = ""

    if triggerid:
        triggerid = "_{triggerid}".format(triggerid=triggerid)

    if not prior_install:
        log("Installing {}.{} trigger...".format(schema, table), logger_name=_LOGGER_NAME)

        statement = INSTALL_TRIGGER_STATEMENT.format(
            schema=schema, table=table, orupdate=orupdate, ordelete=ordelete, triggerid=triggerid
        )
        execute(connection, statement)
    else:
        log("{}.{} trigger already installed; skipping...".format(schema, table), logger_name=_LOGGER_NAME)


def uninstall_trigger(connection: connection, table: str, schema: str = "public", triggerid: str = "") -> None:
    """Uninstall a psycopg2-pgevents trigger from a table.

    Parameters
    ----------
    connection: psycopg2.extensions.connection
        Active connection to a PostGreSQL database.
    table: str
        Table for which the trigger should be uninstalled.
    schema: str
        Schema to which the table belongs.
    triggerid: str
        If there's more than 1 trigger in this database, we need to uniquely identify the trigger with an extra id

    Returns
    -------
    None

    """
    log("Uninstalling {}.{} trigger...".format(schema, table), logger_name=_LOGGER_NAME)

    if triggerid:
        triggerid = "_{triggerid}".format(triggerid=triggerid)
    statement = UNINSTALL_TRIGGER_STATEMENT.format(schema=schema, table=table, triggerid=triggerid)
    execute(connection, statement)
