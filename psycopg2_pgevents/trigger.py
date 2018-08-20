"""This module provides functionality for managing triggers."""
from psycopg2_pgevents.db import execute
from psycopg2.extensions import connection

__all__ = ['install_trigger', 'install_trigger_function', 'uninstall_trigger', 'uninstall_trigger_function']

INSTALL_TRIGGER_FUNCTION_STATEMENT = """
SET search_path = public, pg_catalog;

CREATE OR REPLACE FUNCTION pgevents()
RETURNS TRIGGER AS $function$
  DECLARE
    row_id integer;
  BEGIN
    IF (TG_OP = 'DELETE') THEN
      row_id = OLD.id;
    ELSE
      row_id = NEW.id;
    END IF;
    PERFORM pg_notify(
     'pgevents',
      json_build_object(
        'event', TG_OP,
        'schema_name', TG_TABLE_SCHEMA,
        'table_name', TG_TABLE_NAME,
        'id', row_id
      )::text
    );
    RETURN NULL;
  END;
$function$
LANGUAGE plpgsql;

SET search_path = "$user", public;
"""

UNINSTALL_TRIGGER_FUNCTION_STATEMENT = """
DROP FUNCTION IF EXISTS public.pgevents() {modifier};
"""

INSTALL_TRIGGER_STATEMENT_TEMPLATE = """
SET search_path = {schema}, pg_catalog;

DROP TRIGGER IF EXISTS pgevents ON {schema}.{table};

CREATE TRIGGER pgevents
AFTER INSERT OR UPDATE OR DELETE ON {schema}.{table}
FOR EACH ROW
EXECUTE PROCEDURE public.pgevents();

SET search_path = "$user", public;
"""

UNINSTALL_TRIGGER_STATEMENT_TEMPLATE = """
DROP TRIGGER IF EXISTS pgevents ON {schema}.{table};
"""


def install_trigger_function(connection: connection) -> None:
    """Install the pgevents trigger function against the database.

    Parameters
    ----------
    connection: psycopg2.extensions.connection
        Active connection to a PostGreSQL database.

    Returns
    -------
    None

    """
    execute(connection, INSTALL_TRIGGER_FUNCTION_STATEMENT)


def uninstall_trigger_function(connection: connection, force: bool=False) -> None:
    """Uninstall the pgevents trigger function from the database.

    Parameters
    ----------
    connection: psycopg2.extensions.connection
        Active connection to a PostGreSQL database.
    force: bool
        If True, force the un-registration even if dependent triggers are still installed.
        If False, if there are any dependent triggers for the trigger function, the un-registration will fail

    Returns
    -------
    None

    """
    modifier = ''
    if force:
        modifier = 'CASCADE'
    statement = UNINSTALL_TRIGGER_FUNCTION_STATEMENT.format(modifier=modifier)
    execute(connection, statement)


def install_trigger(connection: connection, table: str, schema: str='public') -> None:
    """Install a pgevents trigger against a table.

    Parameters
    ----------
    connection: psycopg2.extensions.connection
        Active connection to a PostGreSQL database.
    table: str
        Table for which the trigger should be installed.
    schema: str
        Schema to which the table belongs.

    Returns
    -------
    None

    """
    statement = INSTALL_TRIGGER_STATEMENT_TEMPLATE.format(
        schema=schema,
        table=table
    )
    execute(connection, statement)


def uninstall_trigger(connection: connection, table: str, schema: str='public') -> None:
    """Uninstall a pgevents trigger from a table.

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
    statement = UNINSTALL_TRIGGER_STATEMENT_TEMPLATE.format(
        schema=schema,
        table=table
    )
    execute(connection, statement)
