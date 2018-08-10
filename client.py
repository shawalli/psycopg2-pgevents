import select
import datetime

import psycopg2

conn = psycopg2.connect(
    database="pgnotify",
    user="swallis"
)
conn.autocommit = True

curs = conn.cursor()
curs.execute('LISTEN "salesforce.pgnotify";')

try:
    seconds_passed = 0
    print("Waiting for notifications on channel 'pgnotify'")
    while 1:
        if select.select([conn],[],[],5) == ([],[],[]):
            seconds_passed += 5
            print("{} seconds passed without a notification...".format(seconds_passed))
        else:
            seconds_passed = 0
            conn.poll()
            while conn.notifies:
                notify = conn.notifies.pop()
                print("Got NOTIFY:", datetime.datetime.now(), notify.pid, notify.channel, notify.payload)
except KeyboardInterrupt:
    curs.execute("UNLISTEN pgnotify;")
    conn.close()