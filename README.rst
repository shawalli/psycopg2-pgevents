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
producer.py
***************
.. code-block:: python


	from sqlalchemy import Column, Integer, String
	from sqlalchemy import create_engine
	from sqlalchemy.ext.declarative import declarative_base
	from sqlalchemy import inspect
	from sqlalchemy.orm import sessionmaker
	from faker import Faker

	faker = Faker()

	DB_PORT=5432
	DB_USERNAME="postgres"
	DB_PASSWORD="password"
	DB_HOST="127.0.0.1"
	DB_DATABASE="eventtriggertest"

	DATABASE_URI_PROD = f"postgresql+psycopg2://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"

	engine = create_engine(DATABASE_URI_PROD, echo = True)
	Session = sessionmaker(bind = engine)
	Base = declarative_base()

	session = Session()

	class Customer(Base):
		__tablename__ = 'customers'
		customer_id = Column(Integer, primary_key=True)
		name = Column(String)
		address = Column(String)
		email = Column(String)

	class User(Base):
		__tablename__ = 'users'
		user_id = Column(Integer, primary_key=True)
		name = Column(String)
		address = Column(String)
		email = Column(String)

	def add_person():

		c = Customer()
		u = User()

		u.name = faker.name()
		u.email = faker.email()
		u.address = faker.address()

		c.name = faker.name()
		c.email = faker.email()
		c.address = faker.address()

		session.add(c)
		session.add(u)
		session.commit()


	def main():
		Base.metadata.create_all(engine)
		insp = inspect(engine)
		print(insp.get_table_names())

	if __name__ == '__main__':
		main()
		add_person()


***************
consumer.py
***************
.. code-block:: python

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
	install_trigger_function(connection, 'customers', True, "customer_id")
	install_trigger(connection, 'customers')
	install_trigger_function(connection, 'users', True, "user_id")
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
