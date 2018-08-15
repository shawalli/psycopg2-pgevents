import select
import datetime

import psycopg2

conn = psycopg2.connect(
    database="pgevents",
    user="swallis"
)
conn.autocommit = True

curs = conn.cursor()
curs.execute('LISTEN "pgevents";')

try:
    seconds_passed = 0
    print("Waiting for notifications on channel 'pgevents'")
    while 1:
        if select.select([conn], [], [], 5) == ([], [], []):
            seconds_passed += 5
            print('{seconds} seconds passed without a notification...'.format(seconds=seconds_passed))
        else:
            seconds_passed = 0
            conn.poll()
            while conn.notifies:
                notify = conn.notifies.pop()
                print(
                    'NOTIFY:{timestamp}:{pid}:{channel}: {message}'.format(
                        timestamp=datetime.datetime.now(),
                        pid=notify.pid
                        channel=notify.channel,
                        message=notify.payload
                    )
                )
except KeyboardInterrupt:
    print("Unlistening for events")
    curs.execute("UNLISTEN pgevents;")
    conn.close()
