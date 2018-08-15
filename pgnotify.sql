--
-- **** Schema: public ****
--

SET search_path = public, pg_catalog;

--
-- Name: pgevents; Type: FUNCTION; Schema: public; Owner: -
--

CREATE OR REPLACE FUNCTION pgevents()
RETURNS TRIGGER AS $function$
  BEGIN
    RAISE WARNING 'triggered';
    PERFORM pg_notify(
        'pgevents',
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
-- Name: pgevents; Type: TRIGGER; Schema: public; Owner: settings
--

DROP TRIGGER IF EXISTS pgevents ON public.settings;

CREATE TRIGGER pgevents
AFTER INSERT ON public.settings
FOR EACH ROW
EXECUTE PROCEDURE public.pgevents();

--
-- **** Schema: pointofsale ****
--

SET search_path = pointofsale, pg_catalog;

--
-- Name: pgevents; Type: TRIGGER; Schema: pointofsale; Owner: orders
--

DROP TRIGGER IF EXISTS pgevents ON pointofsale.orders;

CREATE TRIGGER pgevents
AFTER INSERT ON pointofsale.orders
FOR EACH ROW
EXECUTE PROCEDURE public.pgevents();

--
-- **** Schema: - ****
--

SET search_path = "$user", public;
