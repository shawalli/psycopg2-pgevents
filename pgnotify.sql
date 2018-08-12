SET search_path = public, pg_catalog;

CREATE OR REPLACE FUNCTION pgnotify()
RETURNS TRIGGER AS $function$
  BEGIN
    RAISE WARNING 'triggered';
    PERFORM pg_notify(
        'pgnotify',
        json_build_object(
          'schema_name', TG_TABLE_SCHEMA,
          'table_name', TG_TABLE_NAME,
          'id', NEW.id
      )::text
    );
    RETURN NEW;
  END;
$function$
LANGUAGE plpgsql;

SET search_path = salesforce, pg_catalog;

DROP TRIGGER IF EXISTS pgnotify ON salesforce.order__c;

CREATE TRIGGER pgnotify
AFTER INSERT ON salesforce.order__c
FOR EACH ROW
EXECUTE PROCEDURE public.pgnotify();
