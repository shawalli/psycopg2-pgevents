--
-- **** Schema: public ****
--

SET search_path = public, pg_catalog;

--
-- Name: pgnotify; Type: FUNCTION; Schema: public; Owner: -
--

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

--
-- Name: pgnotify; Type: TRIGGER; Schema: public; Owner: settings
--

DROP TRIGGER IF EXISTS pgnotify ON public.settings;

CREATE TRIGGER pgnotify
AFTER INSERT ON public.settings
FOR EACH ROW
EXECUTE PROCEDURE public.pgnotify();

--
-- **** Schema: salesforce ****
--

SET search_path = salesforce, pg_catalog;

--
-- Name: pgnotify; Type: TRIGGER; Schema: salesforce; Owner: order__c
--

DROP TRIGGER IF EXISTS pgnotify ON salesforce.order__c;

CREATE TRIGGER pgnotify
AFTER INSERT ON salesforce.order__c
FOR EACH ROW
EXECUTE PROCEDURE public.pgnotify();

--
-- **** Schema: - ****
--

SET search_path = "$user", public;
