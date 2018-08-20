"""This module provides functionality for managing triggers."""
from typing import TYPE_CHECKING

from psycopg2_pgevents.db import execute

if TYPE_CHECKING:
    from psycopg2.extensions import connection

__all__ = ['register_trigger', 'register_trigger_function', 'unregister_trigger', 'unregister_trigger_function']

REGISTER_TRIGGER_FUNCTION_STATEMENT = """
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

UNREGISTER_TRIGGER_FUNCTION_STATEMENT = """
DROP FUNCTION IF EXISTS public.pgevents() {modifier};
"""

REGISTER_TRIGGER_STATEMENT_TEMPLATE = """
SET search_path = {schema}, pg_catalog;

DROP TRIGGER IF EXISTS pgevents ON {schema}.{table};

CREATE TRIGGER pgevents
AFTER INSERT OR UPDATE OR DELETE ON {schema}.{table}
FOR EACH ROW
EXECUTE PROCEDURE public.pgevents();

SET search_path = "$user", public;
"""

UNREGISTER_TRIGGER_STATEMENT_TEMPLATE = """
DROP TRIGGER IF EXISTS pgevents ON {schema}.{table};
"""


def register_trigger_function(connection: connection) -> None:
    """Register the pgevents trigger function against the database.

    Parameters
    ----------
    connection: psycopg2.extensions.connection
        Active connection to a PostGreSQL database.

    Returns
    -------
    None

    """
    execute(connection, REGISTER_TRIGGER_FUNCTION_STATEMENT)


def unregister_trigger_function(connection: connection, force: bool=False) -> None:
    """Register the pgevents trigger function against the database.

    Parameters
    ----------
    connection: psycopg2.extensions.connection
        Active connection to a PostGreSQL database.
    force: bool
        If True, force the un-registration even if dependent triggers are still registered.
        If False, if there are any dependent triggers for the trigger function, the un-registration will fail

    Returns
    -------
    None

    """
    modifier = ''
    if force:
        modifier = 'CASCADE'
    statement = UNREGISTER_TRIGGER_FUNCTION_STATEMENT.format(modifier=modifier)
    execute(connection, statement)


def register_trigger(connection: connection, table: str, schema: str='public') -> None:
    """Register a pgevents trigger against a table.

    Parameters
    ----------
    connection: psycopg2.extensions.connection
        Active connection to a PostGreSQL database.
    table: str
        Table for which the trigger should be registered.
    schema: str
        Schema to which the table belongs.

    Returns
    -------
    None

    """
    statement = REGISTER_TRIGGER_STATEMENT_TEMPLATE.format(
        schema=schema,
        table=table
    )
    execute(connection, statement)


def unregister_trigger(connection: connection, table: str, schema: str='public') -> None:
    """Un-register a pgevents trigger from a table.

    Parameters
    ----------
    connection: psycopg2.extensions.connection
        Active connection to a PostGreSQL database.
    table: str
        Table for which the trigger should be un-registered.
    schema: str
        Schema to which the table belongs.

    Returns
    -------
    None

    """
    statement = UNREGISTER_TRIGGER_STATEMENT_TEMPLATE.format(
        schema=schema,
        table=table
    )
    execute(connection, statement)
