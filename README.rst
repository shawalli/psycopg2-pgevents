#################
psycopg2-pgevents
#################

.. image:: https://badge.fury.io/py/psycopg2-pgevents.svg
    :target: https://badge.fury.io/py/psycopg2-pgevents
.. image:: https://coveralls.io/repos/github/shawalli/psycopg2-pgevents/badge.svg?branch=master
    :target: https://coveralls.io/github/shawalli/psycopg2-pgevents?branch=master
.. image:: https://img.shields.io/badge/License-MIT-yellow.svg
    :target: https://opensource.org/licenses/MIT

This package makes it simple to use PostGreSQL's NOTIFY/LISTEN eventing system
from Python in a consistent, pleasing manner.

Note that this project officially supports Python 3.6+. This is primarily due
to static typing.

*******
Example
*******

The following shows an example of the package in action.

Assumptions
-----------

 - PostGreSQL server is running locally.
 - default database (``postgres``) is available.
 - table exists in database in the public schema with the name ``orders``.

.. code-block:: python

    from psycopg2 import connect
    from psycopg2_pgevents.trigger import install_trigger, \
        install_trigger_function, uninstall_trigger, uninstall_trigger_function
    from psycopg2_pgevents.event import poll, register_event_channel, \
        unregister_event_channel

    connection = connect(dsn='postgres:///postgres')
    connection.autocommit = True

    install_trigger_function(connection)
    install_trigger(connection, 'orders')
    register_event_channel(connection)

    try:
        print('Listening for events...')
        while True:
            for evt in poll(connection):
                print('New Event: {}'.format(evt))
    except KeyboardInterrupt:
        print('User exit via Ctrl-C; Shutting down...')
        unregister_event_channel(connection)
        uninstall_trigger(connection, 'orders')
        uninstall_trigger_function(connection)
        print('Shutdown complete.')

***************
Troubleshooting
***************

* The connection's ``autocommit`` property must be enabled for this package to
  operate correctly. This requirement is provided by PostGreSQL's NOTIFY/LISTEN
  mechanism.

* The same connection that is used with ``register_event_channel()`` must be
  used with ``poll()`` in order to receive events. This is due to the nature of
  how PostGreSQL manages "listening" connections.

* If the table that you'd like to listen to is not in the public schema, the
  schema name must be given as a keyword argument in the ``install_trigger()``
  method.

**********************
Authorship and License
**********************

Written by Shawn Wallis and distributed under the MIT license.
