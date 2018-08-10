CREATE OR REPLACE FUNCTION pgnotify()
RETURNS TRIGGER AS $function$
  BEGIN
    RAISE WARNING 'triggered';
    NOTIFY pgnotify, 'halp1';
    NOTIFY PGNOTIFY, 'halp2';
    NOTIFY "pgnotify", 'halp3';
    RETURN NEW;
  END;
$function$
LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS pgnotify ON order__c;

CREATE TRIGGER pgnotify
AFTER INSERT ON order__c
FOR EACH ROW
EXECUTE PROCEDURE pgnotify();
