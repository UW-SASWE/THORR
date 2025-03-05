Database Setup
==============
THORR uses a relational database system to store and manage project data. The database system is specified in the project configuration file. THORR supports `PostgreSQL <https://www.postgresql.org/>`_ (recommended) and `MySQL <https://www.mysql.com/>`_. The database system must be running and accessible to the THORR project.

.. note::
    PostgreSQL users should install the `PostGIS <https://postgis.net/>`_ extension to support spatial data.

To set up a database for THORR, you first have to create a new database in the database system. Create the database directly on your installed database's interface.

.. tab:: PostgreSQL
    
    .. code-block:: sql

        CREATE DATABASE thorr;

.. tab:: MySQL

    .. code-block:: sql

        CREATE DATABASE thorr;

Replace ``thorr`` with the name of your database.

Next, specify the database name and connection parameters (including the name of the schema) in the project configuration file under the :ref:`config-database` section.

Complete the database setup by running the :ref:`database-setup` command from the terminal:

.. code-block:: bash

    python -m thorr database-setup path/to/config.ini

Specify the path to the project configuration file in the command above. The database tables will be created in the specified database using the connection parameters provided in the project configuration file.

Database Tables
---------------
THORR uses a predefined database tables to store project data. 

    The schema will be created in the specified database using the connection parameters provided in the project configuration file.