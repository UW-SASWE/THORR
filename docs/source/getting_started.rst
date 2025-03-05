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

Replace ``NAME`` with the name of your project and ``DIR`` with the directory where you want to create the project. If ``DIR`` is not provided, the project will be created in the current directory. When creating a new project, you can specify to create a template configuration file and download the data files. See :ref:`new-project` for more information on the available options.

To create a new THORR project in the current directory, run the following command:

.. code-block:: bash
    :linenos:

    python -m thorr new-project my_project

This command will create a new directory with the project name and the following structure:

.. code-block:: text

    my_project/
    ├── .env/
    └── data/

The ``.env`` directory contains the configuration files for the project, and the ``data`` directory contains the data files.


Configuration
-------------


Cronjob
-------