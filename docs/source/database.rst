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
THORR uses a predefined database tables to store project data. Tables in the THORR database include :ref:`basins-table`, :ref:`rivers-table`, :ref:`reaches-table`, :ref:`dams-table`, :ref:`reachdata-table`, and :ref:`damdata-table`. Below are the descriptions of the tables and their columns:

.. _basins-table:
Basins
~~~~~~
The basins table stores information about the drainage basins in the project region.

+------------------+------------------------------------------------------------------+-----------+
|      Column      |                           Description                            | Data Type |
+==================+==================================================================+===========+
| BasinID          | Unique ID for the drainage  basin                                | Integer   |
+------------------+------------------------------------------------------------------+-----------+
| Name             | Name of the drainage  basin                                      | Text      |
+------------------+------------------------------------------------------------------+-----------+
| DrainageAreaSqKm | Total area of the drainage basin (km\ :sup:`2`\  )               | Float     |
+------------------+------------------------------------------------------------------+-----------+
| MajorRiverID     | Unique ID corresponding to the major river in the drainage basin | Integer   |
+------------------+------------------------------------------------------------------+-----------+
| geometry         | Polygon geometry for the drainage basin                          | Polygon   |
+------------------+------------------------------------------------------------------+-----------+

.. _rivers-table:
Rivers
~~~~~~
The rivers table stores information about the rivers in the project region.

+----------+------------------------------------------------------+-----------+
|  Column  |                     Description                      | Data Type |
+==========+======================================================+===========+
| RiverID  | Unique ID for the river                              | Integer   |
+----------+------------------------------------------------------+-----------+
| Name     | Name of the river                                    | Text      |
+----------+------------------------------------------------------+-----------+
| LengthKm | Length of the river (km)                             | Float     |
+----------+------------------------------------------------------+-----------+
| WidthM   | Average width of the river (m)                       | Float     |
+----------+------------------------------------------------------+-----------+
| BasinID  | Unique ID corresponding to the parent drainage basin | Integer   |
+----------+------------------------------------------------------+-----------+
| geometry | Line geometry for the river                          | Line      |
+----------+------------------------------------------------------+-----------+

.. _reaches-table:
Reaches
~~~~~~~
Rivers are divided into reaches. The reaches table stores information about the river reaches in the project region.

+-------------------+----------------------------------------------------------------------+-----------+
|      Column       |                             Description                              | Data Type |
+===================+======================================================================+===========+
| ReachID           | Unique ID for the reach                                              | Integer   |
+-------------------+----------------------------------------------------------------------+-----------+
| Name              | Name of the reach (river name + numerical sequence)                  | Text      |
+-------------------+----------------------------------------------------------------------+-----------+
| RiverID           | Unique ID corresponding to the parent river                          | Integer   |
+-------------------+----------------------------------------------------------------------+-----------+
| ClimateClass      | Köppen-Geiger climate class [#koppen]_                               | Integer   |
+-------------------+----------------------------------------------------------------------+-----------+
| WidthMin          | Minimum width of the reach (m)                                       | Float     |
+-------------------+----------------------------------------------------------------------+-----------+
| WidthMean         | Mean width of the reach (m)                                          | Float     |
+-------------------+----------------------------------------------------------------------+-----------+
| WidthMax          | Maximum width of the reach (m)                                       | Float     |
+-------------------+----------------------------------------------------------------------+-----------+
| RKm               | Distance from the river mount to the center of the reach (km)        | Integer   |
+-------------------+----------------------------------------------------------------------+-----------+
| geometry          | Line geometry of the reach                                           | Line      |
+-------------------+----------------------------------------------------------------------+-----------+
| buffered_geometry | Polygon geometry around the banks of the reach                       | Polygon   |
+-------------------+----------------------------------------------------------------------+-----------+

.. _dams-table:
Dams
~~~~
The dams table stores information about the dams in the project region. The dams information were obtained from the `Global Reservoir and Dam (GRanD) database <https://www.globaldamwatch.org/grand>`_ [#grand]_.

+-------------------+------------------------------------------------------+-----------+
|      Column       |                     Description                      | Data Type |
+===================+======================================================+===========+
| DamID             | Unique ID for the dam                                | Integer   |
+-------------------+------------------------------------------------------+-----------+
| Name              | Name of the dam                                      | Text      |
+-------------------+------------------------------------------------------+-----------+
| Reservoir         | Name of the reservoir                                | Text      |
+-------------------+------------------------------------------------------+-----------+
| AltName           | Alternate name of the reservoir                      | Text      |
+-------------------+------------------------------------------------------+-----------+
| RiverID           | Unique ID corresponding to the parent river          | Integer   |
+-------------------+------------------------------------------------------+-----------+
| BasinID           | Unique ID corresponding to the parent drainage basin | Integer   |
+-------------------+------------------------------------------------------+-----------+
| Country           | Country in which the dam is located                  | Text      |
+-------------------+------------------------------------------------------+-----------+
| Year              | Year on which the dam was built                      | Integer   |
+-------------------+------------------------------------------------------+-----------+
| AreaSqKm          | Area covered by the reservoir (km\ :sup:`2`\ )       | Float     |
+-------------------+------------------------------------------------------+-----------+
| CapacityMCM       | Storage capacity of the reservoir (m\ :sup:`3`\  )   | Float     |
+-------------------+------------------------------------------------------+-----------+
| DepthM            | Depth of the reservoir (m)                           | Float     |
+-------------------+------------------------------------------------------+-----------+
| ElevationMASL     | Elevation of the dam above sea level (m)             | Integer   |
+-------------------+------------------------------------------------------+-----------+
| MainUse           | Main use of the dam                                  | Text      |
+-------------------+------------------------------------------------------+-----------+
| LONG_DD           | Longituide of the dam (decimal degrees)              | Float     |
+-------------------+------------------------------------------------------+-----------+
| LAT_DD            | Laituide of the dam (decimal degrees)                | Float     |
+-------------------+------------------------------------------------------+-----------+
| DamGeometry       | Point geometry signifying the location of the dam    | Point     |
+-------------------+------------------------------------------------------+-----------+
| ReservoirGeometry | Polygon geometry for the reservoir                   | Polygon   |
+-------------------+------------------------------------------------------+-----------+

.. _reachdata-table:
ReachData
~~~~~~~~~
The reachdata tables stores the water temperature estimates and other retrieved satellite data for a given reach.

+------------+----------------------------------------------------------+---------+
|     ID     |               Unique ID for the data entry               | Integer |
+============+==========================================================+=========+
| Date       | Date corresponding to the water temperature              | Date    |
+------------+----------------------------------------------------------+---------+
| ReachID    | Corresponding reach ID for the water temperature         | Integer |
+------------+----------------------------------------------------------+---------+
| LandTempC  | Satellite-based land temperature around the reach (℃)    | Float   |
+------------+----------------------------------------------------------+---------+
| WaterTempC | Satellite-based water temperature of the reach (℃)       | Float   |
+------------+----------------------------------------------------------+---------+
| NDVI       | Estimated Normalized Difference Vegetation Index         | Float   |
+------------+----------------------------------------------------------+---------+
| Mission    | Satellite mission corresponding to the data entry        | Text    |
+------------+----------------------------------------------------------+---------+
| EstTempC   | Estimated water temperature based on the THORR model (℃) | Float   |
+------------+----------------------------------------------------------+---------+



.. _damdata-table:
DamData
~~~~~~~
The damdata tables stores reservoir water temperature obtained directly from satellites.

+------------+--------------------------------------------------------+-----------+
|   Column   |                      Description                       | Data Type |
+============+========================================================+===========+
| ID         | Unique ID for the data entry                           | Integer   |
+------------+--------------------------------------------------------+-----------+
| Date       | Date corresponding to the water temperature            | Date      |
+------------+--------------------------------------------------------+-----------+
| DamID      | Corresponding dam ID for the water temperature         | Integer   |
+------------+--------------------------------------------------------+-----------+
| WaterTempC | Satellite-based water temperature of the reservoir (℃) | Float     |
+------------+--------------------------------------------------------+-----------+



.. rubric:: References

.. [#koppen] Beck, H. E., Zimmermann, N. E., McVicar, T. R., Vergopolan, N., Berg, A., & Wood, E. F. (2018). Present and future Köppen-Geiger climate classification maps at 1-km resolution. Scientific Data, 5(1), 180214. https://doi.org/10.1038/sdata.2018.214
.. [#grand] Lehner, B., C. Reidy Liermann, C. Revenga, C. Vörösmarty, B. Fekete, P. Crouzet, P. Döll, M. Endejan, K. Frenken, J. Magome, C. Nilsson, J.C. Robertson, R. Rodel, N. Sindorf, and D. Wisser. 2011. High-resolution mapping of the world's reservoirs and dams for sustainable river-flow management. Frontiers in Ecology and the Environment 9 (9): 494-502.