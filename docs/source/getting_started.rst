Getting Started
===============

Installation
------------
Install from PyPI
~~~~~~~~~~~~~~~~~
.. TODO: Update the link to the final PyPI package
THORR is available on `PyPI <https://test.pypi.org/project/thorr/>`_ and can be installed using pip:

.. TODO: Update the link to the final PyPI package
.. code-block:: bash
    :linenos:

    pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ thorr

Initial Setup
-------------
Use THORR's command-line interface to create a new project. The ``new-project`` command creates a new THORR project with the specified name and directory using the following syntax:

.. code-block:: bash
    :linenos:

    python -m thorr new-project [OPTIONS] NAME [DIR]

Replace ``NAME`` with the name of your project and ``DIR`` with the directory where you want to create the project. If ``DIR`` is not provided, the project will be created in the current directory. When creating a new project, you can also download THORR's data files. See :ref:`new-project` for more information on the available options.

To create a new THORR project called *my_project* in the current directory and download the data files, run the following command:

.. code-block:: bash
    :linenos:

    python -m thorr new-project --get-data my_project 

This command will create a new directory with the project name and the following structure:

.. code-block:: text

    my_project/
    ├── .env/
    └── data/

The ``.env`` directory contains the configuration files for the project, and the ``data`` directory contains the data files. By default, a template configuration file is created in the ``.env`` directory. You can customize the configuration file to suit your project's needs. See :ref:`configuration` for more information on configuring your project.

To create a new THORR project without downloading the data files or creating a template configuration file, run the following command:

.. code-block:: bash
    :linenos:

    python -m thorr new-project my_project

.. _configuration:
Configuration
-------------
THORR uses a configuration file to manage project settings and parameters. The configuration file is an INI (``.ini``) file located in the ``.env`` directory of the project.

Here is an example of a THORR configuration file:

.. code-block:: ini

    [project]
    title = my_project
    project_dir = my_project
    region = global
    description = 
    start_date = 
    end_date = 

    [database]
    type = postgresql
    user = my_username
    password = my_password
    host = localhost
    port = 1234
    database = name_of_database
    schema = name_of_schema

    [data]
    gis_geopackage = data/gis/thorr_gis.gpkg
    ml_model = data/ml/global_ml.joblib

    [data.geopackage_layers]
    basins = Basins
    rivers = Rivers
    dams = Dams
    reservoirs = Reservoirs
    reaches = Reaches
    buffered_reaches = BufferedReaches

    [ee]
    private_key_path = /path/to/earth/engine/private/key.json
    service_account = service_account_email

The configuration file contains the following sections: :ref:`config-project`, :ref:`config-database`, :ref:`config-database`, and :ref:`config-gee`. Each section contains key-value pairs that define the settings and parameters for the project.

.. _config-project:
``[project]``
~~~~~~~~~~~~~~
The ``[project]`` section contains the project settings, such as the project name, description, and version. The following keys are available in the ``[project]`` section:

+-------------+--------------------------------------------------+
|     Key     |                      Value                       |
+=============+==================================================+
| name        | The name or title of the project                 |
+-------------+--------------------------------------------------+
| project_dir | Path to the project directory                    |
+-------------+--------------------------------------------------+
| region      | Region for the project                           |
+-------------+--------------------------------------------------+
| description | Brief description of the project                 |
+-------------+--------------------------------------------------+
| start_date  | Start date for THORR water temperature estimates |
+-------------+--------------------------------------------------+
| end_date    | End date for THORR water temperature estimates   |
+-------------+--------------------------------------------------+

.. _config-database:
``[database]``
~~~~~~~~~~~~~~~
The ``[database]`` section contains the database connection settings. The following keys are available in the ``[database]`` section:

+----------+-------------------------------------------------+
|   Key    |                      Value                      |
+==========+=================================================+
| type     | Type of database: postgresql or mysql           |
+----------+-------------------------------------------------+
| user     | Username                                        |
+----------+-------------------------------------------------+
| password | Password                                        |
+----------+-------------------------------------------------+
| host     | Host address                                    |
+----------+-------------------------------------------------+
| port     | Port number                                     |
+----------+-------------------------------------------------+
| database | Name of the database where the schema is stored |
+----------+-------------------------------------------------+
| schema   | Name of the schema                              |
+----------+-------------------------------------------------+

See :doc:`database` for more information on setting up the database.

.. _data:
``[data]``
~~~~~~~~~~
The ``[data]`` section contains the paths to the GIS and machine learning data files. An additional :ref:`data.geopackage_layers` sub-section is dedicated to the GIS geopackage layers. The following keys are available in the ``[data]`` section:

+----------------+----------------------------------------------------------------------------------------+
|      Key       |                                         Value                                          |
+================+========================================================================================+
| gis_geopackage | File path to the GIS geopackage file that contains all the vector files used by THORR. |
+----------------+----------------------------------------------------------------------------------------+
| ml_model       | Path to the machine learning model used to generate water temperature                  |
+----------------+----------------------------------------------------------------------------------------+

.. _data.geopackage_layers:
``[data.geopackage_layers]``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The ``[data.geopackage_layers]`` sub-section contains the names of the layers in the GIS geopackage file. The following keys are available in the ``[data.geopackage_layers]`` sub-section:

+------------+---------------------------+
|    Key     |           Value           |
+============+===========================+
| basins     | Layer name for basins     |
+------------+---------------------------+
| rivers     | Layer name for rivers     |
+------------+---------------------------+
| dams       | Layer name for dams       |
+------------+---------------------------+
| reservoirs | Layer name for reservoirs |
+------------+---------------------------+
| reaches    | Layer name for reaches    |
+------------+---------------------------+

See :doc:`gis` for more information on how THORR's GIS data is structured.

.. _config-gee:
``[ee]``
~~~~~~~~
The ``[ee]`` section contains the configuration settings for Google Earth Engine (GEE). THORR obtains satellite information from the GEE platform. Therefore, a GEE service account and private key are required. The following keys are available in the ``[ee]`` section:

+------------------+----------------------------------------+
|       Key        |                 Value                  |
+==================+========================================+
| private_key_path | /path/to/earth/engine/private/key.json |
+------------------+----------------------------------------+
| service_account  | service_account_email                  |
+------------------+----------------------------------------+

Workflow and Cronjob
--------------------
Once the project is set up and configured, you can start using THORR to generate water temperature estimates. THORR's workflow consists of 4 main steps:

1. Read and process GIS information from database
2. Retrieve and process satellite data from Google Earth Engine
3. Generate water temeprature estimates using machine learning models
4. Save the results to the database

This workflow can be automated to run at regular intervals using a cronjob.
.. TODO: Add instructions on setting up a cronjob to run the THORR workflow at regular intervals.