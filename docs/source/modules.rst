Modules
=======

Command Line Interface
----------------------
THORR has a command line interface (CLI) that allows you to interact with the the package from the terminal. The CLI provides a number of commands that can be used to create new projects, manage existing projects and run other THORR services. The CLI is accessible by running the `python -m thorr` command from the terminal. For example, to create a new project with the :ref:`new-project <new-project>` command, run the following command from the terminal:

.. code-block:: bash

    python -m thorr new-project NAME [DIR]

The following commands are available:

.. _new-project:
``thorr new-project``
~~~~~~~~~~~~~~~~~~~~~~~~
Create a new project with the specified name and directory. The project directory will be created in the current working directory if no directory is specified.

    .. program-output:: python -m thorr new-project --help

.. _get-thorr-data:
``thorr get-thorr-data``
~~~~~~~~~~~~~~~~~~~~~~~
Download data from the specified source and save it to the specified directory. THORR's data includes trained machine learning models and GIS data for the various regions.

    .. program-output:: python -m thorr get-thorr-data --help

.. _database-setup:
``thorr database-setup``
~~~~~~~~~~~~~~~~~~~~~~~~
Create the database tables required by THORR to store project data. The database system must be running and accessible to the THORR project.

    .. program-output:: python -m thorr database-setup --help

.. _retrieve-data:
``thorr retrieve-data``
~~~~~~~~~~~~~~~~~~~~~~~
Retrieve satellite data from Google Earth Engine (GEE) and save it to a specified database. 

    .. program-output:: python -m thorr retrieve-data --help

.. _estimate-temperature:
``thorr estimate-temperature``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Estimate water temperature using a trained machine learning model.

    .. program-output:: python -m thorr estimate-temperature --help


.. Satellite Data Retrieval
.. ------------------------

.. Machine Learning
.. ----------------

.. Database Management
.. -------------------

.. Data Preprocessing
.. ------------------

