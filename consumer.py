from psycopg2 import connect
from psycopg2_pgevents.trigger import install_trigger, \
	install_trigger_function, uninstall_trigger, uninstall_trigger_function
from psycopg2_pgevents.event import poll, register_event_channel, \
	unregister_event_channel
import json
from collections import namedtuple

DB_PORT=5432
DB_USERNAME="postgres"
DB_PASSWORD="password"
DB_HOST="127.0.0.1"
DB_DATABASE="eventtriggertest"

connection = connect(
	host=DB_HOST,
	database=DB_DATABASE,
	user=DB_USERNAME,
	password=DB_PASSWORD
)



connection.autocommit = True
install_trigger_function(connection, 'customers', True)
install_trigger(connection, 'customers')
install_trigger_function(connection, 'users', True)
install_trigger(connection, 'users')
register_event_channel(connection)

try:
    print('Listening for events...')
    while True:
        for evt in poll(connection):
            print('New Event: {evt}'.format(evt=evt))
            print(f'{json.dumps(evt.row)}')
except KeyboardInterrupt:
    print('User exit via Ctrl-C; Shutting down...')
    unregister_event_channel(connection)
    uninstall_trigger(connection, 'users')
    uninstall_trigger(connection, 'customers')
    uninstall_trigger_function(connection, 'users')
    uninstall_trigger_function(connection, 'customers')
    print('Shutdown complete.') 
