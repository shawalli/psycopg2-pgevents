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
 - DB "eventtriggertest" is available


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

Orignally Written by Shawn Wallis and distributed under the MIT license.

