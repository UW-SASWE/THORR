import mysql.connector
import psycopg
import pandas as pd
import geopandas as gpd
from pathlib import Path
import numpy as np

from thorr.utils import read_config


class Connect:
    def __init__(
        self,
        config_file,
        # section=None,
        logger=None,
        return_conn=False,
        db_type="postgresql",
    ):
        self.config_file = config_file
        # if not section:
        #     self.section = db_type
        # else:
        #     self.section = section
        self.logger = logger
        self.db_type = db_type

        if self.db_type == "mysql":
            self.connect = mysql.connector.connect
            self.Error = mysql.connector.Error
        elif self.db_type == "postgresql":
            self.connect = psycopg.connect
            self.Error = psycopg.Error

        self.createConnection()
        self.return_conn = return_conn
        # self.createEngine()s

    def createConnection(self):
        """Connect to database"""

        db_config = read_config(self.config_file)
        self.connection = None

        try:
            if self.logger is not None:
                self.logger.info("Connecting to database...")
            else:
                # print("Connecting to database...")
                pass

            if self.db_type == "mysql":
                self.database = db_config["database"]["database"]
                self.connection = self.connect(
                    user=db_config["database"]["user"],
                    # database=db_config["database"]["database"],
                    password=db_config["database"]["password"],
                    host=db_config["database"]["host"],
                    port=db_config["database"]["port"],
                )

                database=db_config["database"]["database"]
                cursor = self.connection.cursor()

                # Create database if it doesn't exist
                cursor.execute(
                    f"CREATE SCHEMA IF NOT EXISTS `{database}` DEFAULT CHARACTER SET utf8mb3"
                )
                cursor.execute(f"USE `{database}`")

                if self.connection.is_connected():
                    if self.logger is not None:
                        self.logger.info("Database connection established.")
                    else:
                        # print("Database connection established.")
                        pass
                else:
                    if self.logger is not None:
                        self.logger.info("Database connection failed.")
                    else:
                        print("Database connection failed.")
            elif self.db_type == "postgresql":
                self.user = db_config["database"]["user"]
                self.schema = db_config["database"]["schema"]
                self.connection = self.connect(
                    user=db_config["database"]["user"],
                    dbname=db_config["database"]["database"],
                    password=db_config["database"]["password"],
                    host=db_config["database"]["host"],
                    port=db_config["database"]["port"],
                )

                if not self.connection.closed:
                    if self.logger is not None:
                        self.logger.info("Database connection established.")
                    else:
                        # print("Database connection established.")
                        pass
                else:
                    if self.logger is not None:
                        self.logger.info("Database connection failed.")
                    else:
                        print("Database connection failed.")

            # if self.connection.is_connected():
            #     if self.logger is not None:
            #         self.logger.info("Database connection established.")
            #     else:
            #         print("Database connection established.")
            # else:
            #     if self.logger is not None:
            #         self.logger.info("Database connection failed.")
            #     else:
            #         print("Database connection failed.")

        except self.Error as error:
            if self.logger is not None:
                self.logger.error(error)
            else:
                print(error)

    def query_with_fetchmany(self, query, chunksize=100):
        try:
            # dbconfig = read_db_config()
            # conn = MySQLConnection(**dbconfig)
            cursor = self.connection.cursor()

            cursor.execute(query)

            chunks = []

            while True:
                chunk = cursor.fetchmany(chunksize)
                if not chunk:
                    break
                chunks.append(pd.DataFrame(chunk))

            df = pd.concat(chunks, ignore_index=True)
            df.columns = [i[0] for i in cursor.description]

            return df

        except self.Error as error:
            if self.logger is not None:
                self.logger.error(error)
            else:
                print(error)

    def close(self):
        """Close MySQL database connection"""
        try:
            self.connection.close()
            if self.logger is not None:
                self.logger.info("Connection closed.")
            else:
                print("Connection closed.")
        except self.Error as error:
            if self.logger is not None:
                self.logger.error(error)
            else:
                print(error)


# function to set up mysql database
def mysql_setup(config_file):
    db = Connect(config_file, db_type="mysql")
    database = db.database
    connection = db.connection
    cursor = connection.cursor()

    # turn off foreign key checks
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

    # # Create the Basins table
    # basins_query = """
    # CREATE TABLE IF NOT EXISTS `Basins` (
    #     `BasinID` SMALLINT NOT NULL AUTO_INCREMENT,
    #     `Name` varchar(255) NOT NULL,
    #     `DrainageAreaSqKm` float DEFAULT NULL COMMENT 'Drainage area of the Basin in square-kilometers',
    #     `MajorRiverID` MEDIUMINT DEFAULT NULL,
    #     `geometry` geometry NOT NULL /*!80003 SRID 4326 */,
    #     PRIMARY KEY (`BasinID`),
    #     UNIQUE KEY `BasinID_UNIQUE` (`BasinID`),
    #     KEY `Fk_MajorRiver` (`MajorRiverID`),
    #     CONSTRAINT `Fk_MajorRiver` FOREIGN KEY (`MajorRiverID`) REFERENCES `Rivers` (`RiverID`) ON DELETE SET NULL ON UPDATE CASCADE
    # ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3
    # """
    # cursor.execute(basins_query)

    # Create regions table
    regions_query = """
    CREATE TABLE IF NOT EXISTS `Regions` (
        `RegionID` SMALLINT NOT NULL AUTO_INCREMENT,
        `Name` varchar(255) NOT NULL,
        `geometry` geometry NOT NULL /*!80003 SRID 4326 */,
        PRIMARY KEY (`RegionID`),
        UNIQUE KEY `RegionID_UNIQUE` (`RegionID`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3
    """
    cursor.execute(regions_query)


    # Create the Rivers table
    rivers_query = """
    CREATE TABLE IF NOT EXISTS `Rivers` (
        `RiverID` MEDIUMINT NOT NULL AUTO_INCREMENT,
        `Name` varchar(255) DEFAULT NULL,
        `LengthKm` float DEFAULT NULL COMMENT 'Length of the river in kilometers',
        `WidthM` float DEFAULT NULL COMMENT 'Width in meters',
        `RegionID` SMALLINT DEFAULT NULL COMMENT 'ID for the region in which this river lies',
        `geometry` geometry NOT NULL /*!80003 SRID 4326 */,
        PRIMARY KEY (`RiverID`),
        UNIQUE KEY `RiverID_UNIQUE` (`RiverID`),
        KEY `Fk_Region` (`RegionID`),
        CONSTRAINT `Fk_Region` FOREIGN KEY (`RegionID`) REFERENCES `Regions` (`RegionID`) ON DELETE SET NULL ON UPDATE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3
    """
    cursor.execute(rivers_query)

    # Create the Dams table
    dams_query = """
    CREATE TABLE IF NOT EXISTS `Dams` (
        `DamID` int NOT NULL AUTO_INCREMENT,
        `Name` varchar(255) NOT NULL,
        `Reservoir` varchar(255) DEFAULT NULL,
        `AltName` varchar(255) DEFAULT NULL,
        `RiverID` MEDIUMINT DEFAULT NULL,
        `RegionID` SMALLINT DEFAULT NULL,
        `Country` varchar(255) DEFAULT NULL,
        `Year` year DEFAULT NULL,
        `AreaSqKm` float DEFAULT NULL,
        `CapacityMCM` float DEFAULT NULL,
        `DepthM` float DEFAULT NULL,
        `ElevationMASL` int DEFAULT NULL,
        `MainUse` varchar(255) DEFAULT NULL,
        `LONG_DD` float DEFAULT NULL,
        `LAT_DD` float DEFAULT NULL,
        `DamGeometry` point /*!80003 SRID 4326 */ DEFAULT NULL COMMENT 'Point geometry for the dam',
        `ReservoirGeometry` polygon /*!80003 SRID 4326 */ DEFAULT NULL COMMENT 'Polygon geometry for the reservoir',
        PRIMARY KEY (`DamID`),
        UNIQUE KEY `DamID_UNIQUE` (`DamID`),
        KEY `Fk_regions_dams` (`RegionID`),
        KEY `Fk_river_dams` (`RiverID`),
        CONSTRAINT `Fk_regions_dams` FOREIGN KEY (`RegionID`) REFERENCES `Regions` (`RegionID`) ON DELETE SET NULL ON UPDATE CASCADE,
        CONSTRAINT `Fk_river_dams` FOREIGN KEY (`RiverID`) REFERENCES `Rivers` (`RiverID`) ON DELETE SET NULL ON UPDATE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3
    """
    cursor.execute(dams_query)

    # create the Reaches table
    reaches_query = """
    CREATE TABLE IF NOT EXISTS `Reaches` (
        `ReachID` int NOT NULL AUTO_INCREMENT,
        `Name` varchar(255) DEFAULT NULL,
        `RiverID` MEDIUMINT DEFAULT NULL,
        `ClimateClass` int DEFAULT NULL COMMENT 'Legend linking the numeric values in the maps to the Köppen-Geiger classes.\nThe RGB colors used in Beck et al. [2018] are provided between parentheses',
        `WidthMin` float DEFAULT NULL COMMENT 'Minimum width (meters)',
        `WidthMean` float DEFAULT NULL COMMENT 'Mean width (meters)',
        `WidthMax` float DEFAULT NULL COMMENT 'Maximum width (meters)',
        `RKm` float DEFAULT NULL COMMENT 'Distance from the mouth of the river (km)',
        `geometry` geometry NOT NULL /*!80003 SRID 4326 */,
        `buffered_geometry` geometry /*!80003 SRID 4326 */ DEFAULT NULL,
        PRIMARY KEY (`ReachID`),
        UNIQUE KEY `ReachID_UNIQUE` (`ReachID`),
        KEY `Fk_river` (`RiverID`),
        CONSTRAINT `Fk_river` FOREIGN KEY (`RiverID`) REFERENCES `Rivers` (`RiverID`) ON DELETE CASCADE ON UPDATE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3
    """
    cursor.execute(reaches_query)

    # Create the DamData table
    dam_data_query = """
    CREATE TABLE IF NOT EXISTS `DamData` (
        `ID` int NOT NULL AUTO_INCREMENT,
        `Date` date NOT NULL,
        `DamID` int NOT NULL,
        `WaterTempC` float NOT NULL COMMENT 'Landsat-based water temperature for reservoirs',
        `Mission` varchar(4) DEFAULT NULL COMMENT 'The Landsat satellite mission',
        PRIMARY KEY (`ID`),
        UNIQUE KEY `DamDataID_UNIQUE` (`ID`),
        KEY `Fk_water_temp_dam` (`DamID`),
        CONSTRAINT `Fk_water_temp_dam` FOREIGN KEY (`DamID`) REFERENCES `Dams` (`DamID`) ON DELETE CASCADE ON UPDATE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3
    """
    cursor.execute(dam_data_query)

    # Create the ReachData table
    query = """
    CREATE TABLE IF NOT EXISTS `ReachData` (
        `ID` int NOT NULL AUTO_INCREMENT,
        `Date` date NOT NULL,
        `ReachID` int NOT NULL,
        `LandTempC` float DEFAULT NULL COMMENT 'Landsat-based land temperature on the reach corridor. Unit: degrees Celsius',
        `WaterTempC` float DEFAULT NULL COMMENT 'Landsat-based water temperature along the reach. Unit: degrees Celsius',
        `NDVI` float DEFAULT NULL COMMENT 'Landsat-based land temperature on the reach corridor',
        `Mission` VARCHAR(4) NULL COMMENT 'The Landsat satellite mission',
        `EstTempC` float DEFAULT NULL COMMENT 'Estimated water temperature based on the thorr algorithm',
        PRIMARY KEY (`ID`),
        UNIQUE KEY `ReachLandsatDataID_UNIQUE` (`ID`),
        KEY `Fk_landsat_data_reach` (`ReachID`),
        CONSTRAINT `Fk_landsat_data_reach` FOREIGN KEY (`ReachID`) REFERENCES `Reaches` (`ReachID`) ON DELETE CASCADE ON UPDATE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3
    """
    cursor.execute(query)

    # turn on foreign key checks
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    pass


# function to set up postgresql database
def postgresql_setup(config_file):
    db = Connect(config_file, db_type="postgresql")
    user = db.user
    schema = db.schema
    connection = db.connection
    cursor = connection.cursor()

    # enable postgis extension
    cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    # Create database if it doesn't exist
    cursor.execute(
        f"""CREATE SCHEMA IF NOT EXISTS {schema}
    AUTHORIZATION {user};"""
    )

    # disable all triggers
    cursor.execute("SET session_replication_role = 'replica'")

    # # Create the Basins table
    # basins_query = f"""
    # CREATE TABLE IF NOT EXISTS "{schema}"."Basins"
    # (
    #     "BasinID" smallint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 32767 CACHE 1 ),
    #     "Name" character varying(255) COLLATE pg_catalog."default" NOT NULL,
    #     "DrainageAreaSqKm" double precision,
    #     "MajorRiverID" smallint,
    #     "geometry" geometry NOT NULL,
    #     CONSTRAINT "Basins_pkey" PRIMARY KEY ("BasinID"),
    #     CONSTRAINT "BasinID_UNIQUE" UNIQUE ("BasinID")
    # )

    # TABLESPACE pg_default;

    # ALTER TABLE IF EXISTS "{schema}"."Basins"
    #     OWNER to {user};

    # COMMENT ON COLUMN "{schema}"."Basins"."DrainageAreaSqKm"
    #     IS 'Drainage area of the Basin in square-kilometers';
    # """
    # cursor.execute(basins_query)

    # create a regions table
    regions_query = f"""
    CREATE TABLE IF NOT EXISTS "{schema}"."Regions"
    (
        "RegionID" smallint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 32767 CACHE 1 ),
        "Name" character varying(255) COLLATE pg_catalog."default" NOT NULL,
        "geometry" geometry NOT NULL,
        CONSTRAINT "Regions_pkey" PRIMARY KEY ("RegionID"),
        CONSTRAINT "RegionID_UNIQUE" UNIQUE ("RegionID")
    )

    TABLESPACE pg_default;

    ALTER TABLE IF EXISTS "{schema}"."Regions"
        OWNER to {user};
    """
    cursor.execute(regions_query)

    # Create the Rivers table
    rivers_query = f"""
    CREATE TABLE IF NOT EXISTS "{schema}"."Rivers"
    (
        "RiverID" smallint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 32767 CACHE 1 ),
        "Name" character varying(255) COLLATE pg_catalog."default" NOT NULL,
        "LengthKm" double precision,
        "WidthM" double precision,
        "RegionID" smallint,
        "geometry" geometry NOT NULL,
        CONSTRAINT "Rivers_pkey" PRIMARY KEY ("RiverID"),
        CONSTRAINT "RiverID_UNIQUE" UNIQUE ("RiverID"),
        CONSTRAINT "Fk_Region" FOREIGN KEY ("RegionID")
            REFERENCES "{schema}"."Regions" ("RegionID") MATCH SIMPLE
            ON UPDATE CASCADE
            ON DELETE SET NULL
            NOT VALID
    )

    TABLESPACE pg_default;

    ALTER TABLE IF EXISTS "{schema}"."Rivers"
        OWNER to {user};

    COMMENT ON COLUMN "{schema}"."Rivers"."LengthKm"
        IS 'Length of the river in kilometers';

    COMMENT ON COLUMN "{schema}"."Rivers"."WidthM"
        IS 'Width in meters';

    COMMENT ON COLUMN "{schema}"."Rivers"."RegionID"
        IS 'ID for the Region in which this river lies';
    """
    cursor.execute(rivers_query)

    # # add foreign key constraint to basin
    # print(
    #     f"""
    #     IF NOT EXISTS (SELECT *
    #         FROM INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS
    #         WHERE "constraint_name" = 'Fk_MajorRiver' AND "constraint_schema" = '{schema}')
    #     ALTER TABLE "{schema}"."Basins"
    #         ADD CONSTRAINT "Fk_MajorRiver" FOREIGN KEY ("MajorRiverID")
    #         REFERENCES "{schema}"."Rivers" ("RiverID") MATCH SIMPLE
    #         ON UPDATE CASCADE
    #         ON DELETE SET NULL
    #         NOT VALID
    # """
    # )

    # cursor.execute(
    #     f"""
    #     ALTER TABLE "{schema}"."Basins"
    #         DROP CONSTRAINT IF EXISTS "Fk_MajorRiver";

    #     ALTER TABLE "{schema}"."Basins"
    #         ADD CONSTRAINT "Fk_MajorRiver" FOREIGN KEY ("MajorRiverID")
    #         REFERENCES "{schema}"."Rivers" ("RiverID") MATCH SIMPLE
    #         ON UPDATE CASCADE
    #         ON DELETE SET NULL
    #         NOT VALID;
    # """
    # )

    # Create the Dams table
    dams_query = f"""
    CREATE TABLE IF NOT EXISTS "{schema}"."Dams"
    (
        "DamID" integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
        "Name" character varying(255) COLLATE pg_catalog."default" NOT NULL,
        "Reservoir" character varying(255) COLLATE pg_catalog."default",
        "AltName" character varying(255) COLLATE pg_catalog."default",
        "RiverID" smallint,
        "RegionID" smallint,
        "Country" character varying(255) COLLATE pg_catalog."default" DEFAULT NULL::character varying,
        "Year" integer,
        "AreaSqKm" double precision,
        "CapacityMCM" double precision,
        "DepthM" double precision,
        "ElevationMASL" integer,
        "MainUse" character varying(255) COLLATE pg_catalog."default" DEFAULT NULL::character varying,
        "LONG_DD" double precision,
        "LAT_DD" double precision,
        "DamGeometry" geometry NOT NULL,
        "ReservoirGeometry" geometry,
        CONSTRAINT "Dams_pkey" PRIMARY KEY ("DamID"),
        CONSTRAINT "DamID_UNIQUE" UNIQUE ("DamID"),
        CONSTRAINT "Fk_region_dams" FOREIGN KEY ("RegionID")
            REFERENCES "{schema}"."Regions" ("RegionID") MATCH SIMPLE
            ON UPDATE CASCADE
            ON DELETE SET NULL
            NOT VALID,
        CONSTRAINT "Fk_river_dams" FOREIGN KEY ("RiverID")
            REFERENCES "{schema}"."Rivers" ("RiverID") MATCH SIMPLE
            ON UPDATE NO ACTION
            ON DELETE NO ACTION
            NOT VALID
    )

    TABLESPACE pg_default;

    ALTER TABLE IF EXISTS "{schema}"."Dams"
        OWNER to {user};

    COMMENT ON COLUMN "{schema}"."Dams"."DamGeometry"
        IS 'Point geometry for the dam';

    COMMENT ON COLUMN "{schema}"."Dams"."ReservoirGeometry"
        IS 'Polygon geometry for the reservoir';
    """
    cursor.execute(dams_query)

    # create the Reaches table
    reaches_query = f"""
    CREATE TABLE IF NOT EXISTS "{schema}"."Reaches"
    (
        "ReachID" integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
        "Name" character varying(255) COLLATE pg_catalog."default" NOT NULL,
        "RiverID" smallint,
        "ClimateClass" smallint,
        "WidthMin" double precision,
        "WidthMean" double precision,
        "WidthMax" double precision,
        "RKm" double precision,
        "geometry" geometry NOT NULL,
        "buffered_geometry" geometry,
        CONSTRAINT "Reaches_pkey" PRIMARY KEY ("ReachID"),
        CONSTRAINT "ReachID_UNIQUE" UNIQUE ("ReachID"),
        CONSTRAINT "Fk_river" FOREIGN KEY ("RiverID")
            REFERENCES "{schema}"."Rivers" ("RiverID") MATCH SIMPLE
            ON UPDATE CASCADE
            ON DELETE CASCADE
            NOT VALID
    )

    TABLESPACE pg_default;

    ALTER TABLE IF EXISTS "{schema}"."Reaches"
        OWNER to {user};
    """
    cursor.execute(reaches_query)

    # create the Nodes table
    nodes_query = f"""
    CREATE TABLE IF NOT EXISTS "{schema}"."Nodes"
    (
        "NodeID" integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
        "Name" character varying(255) COLLATE pg_catalog."default" NOT NULL,
        "ReachID" integer,
        "ClimateClass" smallint,
        "WidthMin" double precision,
        "WidthMean" double precision,
        "WidthMax" double precision,
        "RKm" double precision,
        "geometry" geometry NOT NULL,
        "buffered_geometry" geometry,
        CONSTRAINT "Reaches_pkey" PRIMARY KEY ("ReachID"),
        CONSTRAINT "ReachID_UNIQUE" UNIQUE ("ReachID"),
        CONSTRAINT "Fk_river" FOREIGN KEY ("RiverID")
            REFERENCES "{schema}"."Rivers" ("RiverID") MATCH SIMPLE
            ON UPDATE CASCADE
            ON DELETE CASCADE
            NOT VALID
    )

    TABLESPACE pg_default;

    ALTER TABLE IF EXISTS "{schema}"."Reaches"
        OWNER to {user};
    """
    cursor.execute(reaches_query)

    # Create the DamData table
    dam_data_query = f"""
    CREATE TABLE IF NOT EXISTS "{schema}"."DamData"
    (
        "ID" integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
        "Date" date NOT NULL,
        "DamID" smallint NOT NULL,
        "WaterTempC" double precision NOT NULL,
        "Mission" character varying(4) COLLATE pg_catalog."default" DEFAULT NULL::character varying,
        CONSTRAINT "DamData_pkey" PRIMARY KEY ("ID"),
        CONSTRAINT "DamDataID_UNIQUE" UNIQUE ("ID"),
        CONSTRAINT "Fk_water_temp_dam" FOREIGN KEY ("DamID")
            REFERENCES "{schema}"."Dams" ("DamID") MATCH SIMPLE
            ON UPDATE CASCADE
            ON DELETE CASCADE
            NOT VALID
    )

    TABLESPACE pg_default;

    ALTER TABLE IF EXISTS "{schema}"."DamData"
        OWNER to {user};
    """
    cursor.execute(dam_data_query)

    # Create the ReachData table
    query = f"""
    CREATE TABLE IF NOT EXISTS "{schema}"."ReachData"
    (
        "ID" integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
        "Date" date NOT NULL,
        "ReachID" smallint NOT NULL,
        "LandTempC" double precision,
        "WaterTempC" double precision,
        "NDVI" double precision,
        "Mission" character varying(4) COLLATE pg_catalog."default",
        "EstTempC" double precision,
        CONSTRAINT "ReachData_pkey" PRIMARY KEY ("ID"),
        CONSTRAINT "ReachDataID_UNIQUE" UNIQUE ("ID"),
        CONSTRAINT "Fk_data_reach" FOREIGN KEY ("ReachID")
            REFERENCES "{schema}"."Reaches" ("ReachID") MATCH SIMPLE
            ON UPDATE CASCADE
            ON DELETE CASCADE
            NOT VALID
    )

    TABLESPACE pg_default;

    ALTER TABLE IF EXISTS "{schema}"."ReachData"
        OWNER to {user};
    """
    cursor.execute(query)

    # enable all triggers
    cursor.execute("SET session_replication_role = 'origin'")

    connection.commit()

    pass


# function to set up postgresql database
def postgresql_setup_new(config_file):
    db = Connect(config_file, db_type="postgresql")
    user = db.user
    schema = db.schema
    connection = db.connection
    cursor = connection.cursor()

    # enable postgis extension
    cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    # Create database if it doesn't exist
    cursor.execute(
        f"""CREATE SCHEMA IF NOT EXISTS {schema}
    AUTHORIZATION {user};"""
    )

    # disable all triggers
    cursor.execute("SET session_replication_role = 'replica'")

    # # Create the Basins table
    # basins_query = f"""
    # CREATE TABLE IF NOT EXISTS "{schema}"."Basins"
    # (
    #     "BasinID" smallint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 32767 CACHE 1 ),
    #     "Name" character varying(255) COLLATE pg_catalog."default" NOT NULL,
    #     "DrainageAreaSqKm" double precision,
    #     "MajorRiverID" smallint,
    #     "geometry" geometry NOT NULL,
    #     CONSTRAINT "Basins_pkey" PRIMARY KEY ("BasinID"),
    #     CONSTRAINT "BasinID_UNIQUE" UNIQUE ("BasinID")
    # )

    # TABLESPACE pg_default;

    # ALTER TABLE IF EXISTS "{schema}"."Basins"
    #     OWNER to {user};

    # COMMENT ON COLUMN "{schema}"."Basins"."DrainageAreaSqKm"
    #     IS 'Drainage area of the Basin in square-kilometers';
    # """
    # cursor.execute(basins_query)

    # create a regions table
    regions_query = f"""
    CREATE TABLE IF NOT EXISTS "{schema}"."Regions"
    (
        region_id smallint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 32767 CACHE 1 ),
        name character varying(255) COLLATE pg_catalog."default" NOT NULL,
        geometry geometry NOT NULL,
        CONSTRAINT regions_pkey PRIMARY KEY (region_id)
    )

    TABLESPACE pg_default;

    ALTER TABLE IF EXISTS "{schema}"."Regions"
        OWNER to {user};
    """
    cursor.execute(regions_query)

    # Create the Rivers table
    rivers_query = f"""
    CREATE TABLE IF NOT EXISTS {schema}.rivers
    (
        river_id smallint NOT NULL,
        name character varying(255) COLLATE pg_catalog."default",
        length_km double precision,
        region_id smallint,
        geometry geometry NOT NULL,
        CONSTRAINT rivers_pkey PRIMARY KEY (river_id),
        CONSTRAINT fkey_region FOREIGN KEY (region_id)
            REFERENCES {schema}.regions (region_id) MATCH SIMPLE
            ON UPDATE NO ACTION
            ON DELETE NO ACTION
    )

    TABLESPACE pg_default;

    ALTER TABLE IF EXISTS {schema}.rivers
        OWNER to {user};

    COMMENT ON COLUMN {schema}.rivers.length_km
        IS 'estimated length of the river in kilometers';

    COMMENT ON COLUMN {schema}.rivers.region_id
        IS 'id for the Region in which this river lies';
    """
    cursor.execute(rivers_query)

    # # add foreign key constraint to basin
    # print(
    #     f"""
    #     IF NOT EXISTS (SELECT *
    #         FROM INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS
    #         WHERE "constraint_name" = 'Fk_MajorRiver' AND "constraint_schema" = '{schema}')
    #     ALTER TABLE "{schema}"."Basins"
    #         ADD CONSTRAINT "Fk_MajorRiver" FOREIGN KEY ("MajorRiverID")
    #         REFERENCES "{schema}"."Rivers" ("RiverID") MATCH SIMPLE
    #         ON UPDATE CASCADE
    #         ON DELETE SET NULL
    #         NOT VALID
    # """
    # )

    # cursor.execute(
    #     f"""
    #     ALTER TABLE "{schema}"."Basins"
    #         DROP CONSTRAINT IF EXISTS "Fk_MajorRiver";

    #     ALTER TABLE "{schema}"."Basins"
    #         ADD CONSTRAINT "Fk_MajorRiver" FOREIGN KEY ("MajorRiverID")
    #         REFERENCES "{schema}"."Rivers" ("RiverID") MATCH SIMPLE
    #         ON UPDATE CASCADE
    #         ON DELETE SET NULL
    #         NOT VALID;
    # """
    # )

    # # Create the Dams table
    # dams_query = f"""
    # CREATE TABLE IF NOT EXISTS "{schema}"."Dams"
    # (
    #     "DamID" integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    #     "Name" character varying(255) COLLATE pg_catalog."default" NOT NULL,
    #     "Reservoir" character varying(255) COLLATE pg_catalog."default",
    #     "AltName" character varying(255) COLLATE pg_catalog."default",
    #     "RiverID" smallint,
    #     "RegionID" smallint,
    #     "Country" character varying(255) COLLATE pg_catalog."default" DEFAULT NULL::character varying,
    #     "Year" integer,
    #     "AreaSqKm" double precision,
    #     "CapacityMCM" double precision,
    #     "DepthM" double precision,
    #     "ElevationMASL" integer,
    #     "MainUse" character varying(255) COLLATE pg_catalog."default" DEFAULT NULL::character varying,
    #     "LONG_DD" double precision,
    #     "LAT_DD" double precision,
    #     "DamGeometry" geometry NOT NULL,
    #     "ReservoirGeometry" geometry,
    #     CONSTRAINT "Dams_pkey" PRIMARY KEY ("DamID"),
    #     CONSTRAINT "DamID_UNIQUE" UNIQUE ("DamID"),
    #     CONSTRAINT "Fk_region_dams" FOREIGN KEY ("RegionID")
    #         REFERENCES "{schema}"."Regions" ("RegionID") MATCH SIMPLE
    #         ON UPDATE CASCADE
    #         ON DELETE SET NULL
    #         NOT VALID,
    #     CONSTRAINT "Fk_river_dams" FOREIGN KEY ("RiverID")
    #         REFERENCES "{schema}"."Rivers" ("RiverID") MATCH SIMPLE
    #         ON UPDATE NO ACTION
    #         ON DELETE NO ACTION
    #         NOT VALID
    # )

    # TABLESPACE pg_default;

    # ALTER TABLE IF EXISTS "{schema}"."Dams"
    #     OWNER to {user};

    # COMMENT ON COLUMN "{schema}"."Dams"."DamGeometry"
    #     IS 'Point geometry for the dam';

    # COMMENT ON COLUMN "{schema}"."Dams"."ReservoirGeometry"
    #     IS 'Polygon geometry for the reservoir';
    # """
    # cursor.execute(dams_query)

    # create the Reaches table
    reaches_query = f"""
    CREATE TABLE IF NOT EXISTS "{schema}"."Reaches"
    (
        "ReachID" integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
        "Name" character varying(255) COLLATE pg_catalog."default" NOT NULL,
        "RiverID" smallint,
        "ClimateClass" smallint,
        "WidthMin" double precision,
        "WidthMean" double precision,
        "WidthMax" double precision,
        "RKm" double precision,
        "geometry" geometry NOT NULL,
        "buffered_geometry" geometry,
        CONSTRAINT "Reaches_pkey" PRIMARY KEY ("ReachID"),
        CONSTRAINT "ReachID_UNIQUE" UNIQUE ("ReachID"),
        CONSTRAINT "Fk_river" FOREIGN KEY ("RiverID")
            REFERENCES "{schema}"."Rivers" ("RiverID") MATCH SIMPLE
            ON UPDATE CASCADE
            ON DELETE CASCADE
            NOT VALID
    )

    TABLESPACE pg_default;

    ALTER TABLE IF EXISTS "{schema}"."Reaches"
        OWNER to {user};
    """
    cursor.execute(reaches_query)

    # create the Nodes table
    nodes_query = f"""
    CREATE TABLE IF NOT EXISTS "{schema}"."Nodes"
    (
        "NodeID" integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
        "Name" character varying(255) COLLATE pg_catalog."default" NOT NULL,
        "ReachID" integer,
        "ClimateClass" smallint,
        "WidthMin" double precision,
        "WidthMean" double precision,
        "WidthMax" double precision,
        "RKm" double precision,
        "geometry" geometry NOT NULL,
        "buffered_geometry" geometry,
        CONSTRAINT "Reaches_pkey" PRIMARY KEY ("ReachID"),
        CONSTRAINT "ReachID_UNIQUE" UNIQUE ("ReachID"),
        CONSTRAINT "Fk_river" FOREIGN KEY ("RiverID")
            REFERENCES "{schema}"."Rivers" ("RiverID") MATCH SIMPLE
            ON UPDATE CASCADE
            ON DELETE CASCADE
            NOT VALID
    )

    TABLESPACE pg_default;

    ALTER TABLE IF EXISTS "{schema}"."Reaches"
        OWNER to {user};
    """
    cursor.execute(reaches_query)

    # Create the DamData table
    dam_data_query = f"""
    CREATE TABLE IF NOT EXISTS "{schema}"."DamData"
    (
        "ID" integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
        "Date" date NOT NULL,
        "DamID" smallint NOT NULL,
        "WaterTempC" double precision NOT NULL,
        "Mission" character varying(4) COLLATE pg_catalog."default" DEFAULT NULL::character varying,
        CONSTRAINT "DamData_pkey" PRIMARY KEY ("ID"),
        CONSTRAINT "DamDataID_UNIQUE" UNIQUE ("ID"),
        CONSTRAINT "Fk_water_temp_dam" FOREIGN KEY ("DamID")
            REFERENCES "{schema}"."Dams" ("DamID") MATCH SIMPLE
            ON UPDATE CASCADE
            ON DELETE CASCADE
            NOT VALID
    )

    TABLESPACE pg_default;

    ALTER TABLE IF EXISTS "{schema}"."DamData"
        OWNER to {user};
    """
    cursor.execute(dam_data_query)

    # Create the ReachData table
    query = f"""
    CREATE TABLE IF NOT EXISTS "{schema}"."ReachData"
    (
        "ID" integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
        "Date" date NOT NULL,
        "ReachID" smallint NOT NULL,
        "LandTempC" double precision,
        "WaterTempC" double precision,
        "NDVI" double precision,
        "Mission" character varying(4) COLLATE pg_catalog."default",
        "EstTempC" double precision,
        CONSTRAINT "ReachData_pkey" PRIMARY KEY ("ID"),
        CONSTRAINT "ReachDataID_UNIQUE" UNIQUE ("ID"),
        CONSTRAINT "Fk_data_reach" FOREIGN KEY ("ReachID")
            REFERENCES "{schema}"."Reaches" ("ReachID") MATCH SIMPLE
            ON UPDATE CASCADE
            ON DELETE CASCADE
            NOT VALID
    )

    TABLESPACE pg_default;

    ALTER TABLE IF EXISTS "{schema}"."ReachData"
        OWNER to {user};
    """
    cursor.execute(query)

    # enable all triggers
    cursor.execute("SET session_replication_role = 'origin'")

    connection.commit()

    pass




# function to set up a fresh database
def db_setup(config_file, upload_gis_=False):
    db_config = read_config(config_file)
    db_type = db_config["database"]["type"].lower()
    if db_type == "mysql":
        mysql_setup(config_file)
    elif db_type == "postgresql":
        postgresql_setup(config_file)

    if upload_gis_:
        proj_dir = Path(db_config["project"]["project_dir"])

        gpkg = proj_dir / db_config["data"]["gis_geopackage"]
        gpkg_layers = db_config["data.geopackage_layers"]

        upload_gis(config_file, gpkg, gpkg_layers, db_type)


def null_or_value(value):
    if str(value) == "nan":
        return "NULL"
    else:
        return value


def mysql_upload_gis(config_file, gpkg, gpkg_layers):
    db = Connect(config_file, db_type="mysql")
    database = db.database
    connection = db.connection
    cursor = connection.cursor()

    if "basins" in gpkg_layers:

        # print( gpkg, gpkg_layers)
        basins_gdf = gpd.read_file(gpkg, layer=gpkg_layers["basins"])
        # print(basins_gdf)
        srid = basins_gdf.crs.to_epsg()

        for i, basin in basins_gdf.iterrows():
            query = f"""
                INSERT INTO `{database}`.`Basins` (Name, DrainageAreaSqKm, geometry)
                SELECT '{basin['Name']}', {basin['AreaSqKm']}, ST_GeomFromText('{basin['geometry'].wkt}', {srid}, 'axis-order=long-lat')
                WHERE NOT EXISTS (SELECT * FROM `{database}`.`Basins` WHERE Name = '{basin['Name']}');
                """

            cursor.execute(query)
            connection.commit()

    if "regions" in gpkg_layers:

        # print( gpkg, gpkg_layers)
        regions_gdf = gpd.read_file(gpkg, layer=gpkg_layers["regions"])
        # print(basins_gdf)
        srid = regions_gdf.crs.to_epsg()

        for i, region in regions_gdf.iterrows():
            query = f"""
                INSERT INTO `{database}`.`Regions` (Name, geometry)
                SELECT '{region['Name']}', ST_GeomFromText('{region['geometry'].wkt}', {srid}, 'axis-order=long-lat')
                WHERE NOT EXISTS (SELECT * FROM `{database}`.`Regions` WHERE Name = '{region['Name']}');
                """

            cursor.execute(query)
            connection.commit()

    if "rivers" in gpkg_layers:
        rivers_gdf = gpd.read_file(gpkg, layer=gpkg_layers["rivers"])
        srid = rivers_gdf.crs.to_epsg()

        for i, river in rivers_gdf.iterrows():

            # query = f"""
            #     INSERT INTO  `{database}`.`Rivers` (Name, LengthKm, geometry)
            #     SELECT '{river['GNIS_Name']}', {river['LengthKM']}, ST_GeomFromText('{river['geometry'].wkt}', {srid}, 'axis-order=long-lat')
            #     WHERE NOT EXISTS (SELECT * FROM  `{database}`.`Rivers` WHERE Name = '{river['GNIS_Name']}');
            #     """

            query = f"""
                INSERT INTO  `{database}`.`Rivers` (Name, geometry)
                SELECT '{river['Name']}', ST_GeomFromText('{river['geometry'].wkt}', {srid}, 'axis-order=long-lat')
                WHERE NOT EXISTS (SELECT * FROM  `{database}`.`Rivers` WHERE Name = '{river['Name']}');
                """

            cursor.execute(query)
            connection.commit()

            query2 = f"""
                UPDATE `{database}`.`Rivers`
                SET RegionID = (SELECT RegionID FROM Regions WHERE Name = '{river['Region']}')
                WHERE Name = "{river['Name']}";
                """

            cursor.execute(query2)
            connection.commit()

        # # Update the MajorRiverID column if the river exists in the Rivers table
        # if "basins" in gpkg_layers:
        #     basins_gdf = gpd.read_file(gpkg, layer=gpkg_layers["basins"])

        #     for i, basin in basins_gdf.iterrows():
        #         query = f"""
        #             UPDATE `{database}`.`Basins`
        #             SET MajorRiverID = (SELECT RiverID FROM Rivers WHERE Name = '{basin['MajorRiver']}')
        #             WHERE Name = '{basin['Name']}';
        #             """

        #     cursor.execute(query)
        #     connection.commit()

    if "dams" in gpkg_layers:
        dams_gdf = gpd.read_file(gpkg, layer=gpkg_layers["dams"])
        srid = dams_gdf.crs.to_epsg()

        # TODO: use the cast feature like the one in the reaches query
        fill_values = {
            "RES_NAME": "",
            "DAM_NAME": "",
            "ALT_NAME": "",
            "RIVER": "",
            "ALT_RIVER": "",
            "MAIN_BASIN": "",
            "SUB_BASIN": "",
            "NEAR_CITY": "",
            "ALT_CITY": np.nan,
            "ADMIN_UNIT": "",
            "SEC_ADMIN": np.nan,
            "COUNTRY": "",
            "SEC_CNTRY": np.nan,
            "YEAR": np.nan,
            "ALT_YEAR": np.nan,
            "REM_YEAR": np.nan,
            "DAM_HGT_M": np.nan,
            "ALT_HGT_M": np.nan,
            "DAM_LEN_M": np.nan,
            "ALT_LEN_M": np.nan,
            "AREA_SKM": np.nan,
            "AREA_POLY": np.nan,
            "AREA_REP": np.nan,
            "AREA_MAX": np.nan,
            "AREA_MIN": np.nan,
            "CAP_MCM": np.nan,
            "CAP_MAX": np.nan,
            "CAP_REP": np.nan,
            "CAP_MIN": np.nan,
            "DEPTH_M": np.nan,
            "DIS_AVG_LS": np.nan,
            "DOR_PC": np.nan,
            "ELEV_MASL": np.nan,
            "CATCH_SKM": np.nan,
            "CATCH_REP": np.nan,
            "DATA_INFO": np.nan,
            "USE_IRRI": "",
            "USE_ELEC": "",
            "USE_SUPP": "",
            "USE_FCON": "",
            "USE_RECR": "",
            "USE_NAVI": "",
            "USE_FISH": "",
            "USE_PCON": np.nan,
            "USE_LIVE": np.nan,
            "USE_OTHR": "",
            "MAIN_USE": "",
            "LAKE_CTRL": "",
            "MULTI_DAMS": "",
            "TIMELINE": np.nan,
            "COMMENTS": "",
            "URL": "",
            "QUALITY": "",
            "EDITOR": "",
            "LONG_DD": np.nan,
            "LAT_DD": np.nan,
            "POLY_SRC": "",
        }
        dams_gdf.fillna(fill_values, inplace=True)

        for i, dam in dams_gdf.iterrows():
            query = f"""
                INSERT INTO `{database}`.`Dams` (Name, Reservoir, AltName, Country, Year, AreaSqKm, CapacityMCM, DepthM, ElevationMASL, MainUse, LONG_DD, LAT_DD, DamGeometry)
                SELECT '{str(dam['DAM_NAME']).replace("'", "''")}', NULLIF('{str(dam['RES_NAME']).replace("'", "''")}', ''), NULLIF('{str(dam['ALT_NAME'])}',''), '{dam['COUNTRY']}', NULLIF({null_or_value(dam['YEAR'])}, NULL), NULLIF({null_or_value(dam['AREA_SKM'])}, NULL), NULLIF({null_or_value(dam['CAP_MCM'])}, NULL), NULLIF({null_or_value(dam['DEPTH_M'])}, NULL), NULLIF({null_or_value(dam['ELEV_MASL'])}, NULL),  '{dam['MAIN_USE']}', {dam['LONG_DD']}, {dam['LAT_DD']}, ST_PointFromText('{dam['geometry'].wkt}', {srid}, 'axis-order=long-lat')
                WHERE NOT EXISTS (SELECT * FROM `{database}`.`Dams` WHERE Name = '{str(dam['DAM_NAME']).replace("'", "''")}');
                """

            cursor.execute(query)
            connection.commit()

            # Update the RiverID column if the river exists in the Rivers table
            query2 = f"""
            UPDATE `{database}`.`Dams`
            SET RiverID = (SELECT RiverID FROM `{database}`.`Rivers` WHERE Name = '{dam['RIVER']}')
            WHERE Name = '{str(dam['DAM_NAME']).replace("'", "''")}';
            """

            cursor.execute(query2)
            connection.commit()

            # Update the RegionID column if the basin exists in the Basins table
            query3 = f"""
            UPDATE `{database}`.`Dams`
            SET RegionID = (SELECT RegionID FROM `{database}`.`Regions` WHERE Name = 'Columbia River Basin')
            WHERE Name = '{str(dam['DAM_NAME']).replace("'", "''")}';
            """

            cursor.execute(query3)
            connection.commit()

    if "reservoirs" in gpkg_layers:
        reservoirs_gdf = gpd.read_file(gpkg, layer=gpkg_layers["reservoirs"])
        srid = reservoirs_gdf.crs.to_epsg()
        # dams_gdf.fillna("", inplace=True)

        for i, reservoir in reservoirs_gdf.iterrows():
            query = f"""
                UPDATE `{database}`.`Dams`
                SET ReservoirGeometry = ST_GeomFromText('{reservoir['geometry'].wkt}', 4326, 'axis-order=long-lat')
                WHERE Name = '{str(reservoir['DAM_NAME']).replace("'", "''")}';
                """

            cursor.execute(query)
            connection.commit()

    if "reaches" in gpkg_layers:
        reaches_gdf = gpd.read_file(gpkg, layer=gpkg_layers["reaches"])
        srid = reaches_gdf.crs.to_epsg()

        # for i, reach in reaches_gdf.iterrows():
        #     # Iinsert reach data into the table if the entry doesn't already exist
        for i, reach in reaches_gdf.iterrows():

            query = f"""
                INSERT INTO `{database}`.`Reaches` (Name, RiverID, ClimateClass, WidthMin, WidthMean, WidthMax, RKm, geometry)
                SELECT "{reach['Name']}",(SELECT RiverID FROM Rivers WHERE Name = '{reach['river_name']}'), {reach['koppen']}, NULLIF("{str(reach['WidthMin'])}",'nan'), NULLIF("{str(reach['WidthMean'])}",'nan'), NULLIF("{str(reach['WidthMax'])}",'nan'), NULLIF("{str(reach['RKm'])}",'nan'), ST_GeomFromText('{reach['geometry'].wkt}', {srid}, 'axis-order=long-lat')
                WHERE NOT EXISTS (SELECT * FROM `{database}`.`Reaches` WHERE Name = "{reach['Name']}");
                """

            cursor.execute(query)
            connection.commit()

        if "buffered_reaches" in gpkg_layers:
            buffered_reaches_gdf = gpd.read_file(
                gpkg, layer=gpkg_layers["buffered_reaches"]
            )
            srid = buffered_reaches_gdf.crs.to_epsg()

            for i, buffered_reach in buffered_reaches_gdf.iterrows():
                query = f"""
                    UPDATE `{database}`.`Reaches`
                    SET buffered_geometry = ST_GeomFromText('{buffered_reach['geometry'].wkt}', {srid}, 'axis-order=long-lat')
                    WHERE Name = '{buffered_reach['Name']}';
                    """

                cursor.execute(query)
                connection.commit()
            



def postgresql_upload_gis(config_file, gpkg, gpkg_layers):
    db = Connect(config_file, db_type="postgresql")
    schema = db.schema
    connection = db.connection
    cursor = connection.cursor()

    # print( gpkg, gpkg_layers)
    # gpkg_layers = data_paths["data.geopackage_layers"]

    if "basins" in gpkg_layers:

        # print( gpkg, gpkg_layers)
        basins_gdf = gpd.read_file(gpkg, layer=gpkg_layers["basins"])
        # print(basins_gdf)
        srid = basins_gdf.crs.to_epsg()

        for i, basin in basins_gdf.iterrows():
            query = f"""
                INSERT INTO "{schema}"."Basins" ("Name", "DrainageAreaSqKm", "geometry")
                SELECT '{basin['Name']}', {basin['AreaSqKm']}, 'SRID={srid};{basin['geometry'].wkt}'
                WHERE NOT EXISTS (SELECT * FROM "{schema}"."Basins" WHERE "Name" = '{basin['Name']}')
                """

            cursor.execute(query)
            connection.commit()

    

    if "regions" in gpkg_layers:

        # print( gpkg, gpkg_layers)
        regions_gdf = gpd.read_file(gpkg, layer=gpkg_layers["regions"])
        # print(basins_gdf)
        srid = regions_gdf.crs.to_epsg()

        for i, region in regions_gdf.iterrows():
            query = f"""
                INSERT INTO "{schema}"."Regions" ("Name", "geometry")
                SELECT '{region['Name']}', 'SRID={srid};{region['geometry'].wkt}'
                WHERE NOT EXISTS (SELECT * FROM "{schema}"."Regions" WHERE "Name" = '{region['Name']}')
                """

            cursor.execute(query)
            connection.commit()

    if "rivers" in gpkg_layers:
        rivers_gdf = gpd.read_file(gpkg, layer=gpkg_layers["rivers"])
        srid = rivers_gdf.crs.to_epsg()

        for i, river in rivers_gdf.iterrows():
            # query = f"""
            #     INSERT INTO "{schema}"."Rivers" ("Name", "LengthKm", "geometry")
            #     SELECT '{river['GNIS_Name']}', {river['LengthKM']}, 'SRID={srid};{river['geometry'].wkt}'
            #     WHERE NOT EXISTS (SELECT * FROM "{schema}"."Rivers" WHERE "Name" = '{river['GNIS_Name']}')
            #     """
            
            query = f"""
                INSERT INTO "{schema}"."Rivers" ("Name", "geometry")
                SELECT '{river['Name']}', 'SRID={srid};{river['geometry'].wkt}'
                WHERE NOT EXISTS (SELECT * FROM "{schema}"."Rivers" WHERE "Name" = '{river['Name']}')
                """

            cursor.execute(query)
            connection.commit()

            query2 = f"""
            UPDATE "{schema}"."Rivers"
            SET "RegionID" = (SELECT "RegionID" FROM "{schema}"."Regions" WHERE "Name" = '{river['Region']}')
            WHERE "Name" = '{river['Name']}'
            """

            cursor.execute(query2)
            connection.commit()

        # # Update the MajorRiverID column if the river exists in the Rivers table
        # if "basins" in gpkg_layers:
        #     basins_gdf = gpd.read_file(gpkg, layer=gpkg_layers["basins"])

        #     for i, basin in basins_gdf.iterrows():
        #         query = f"""
        #         UPDATE "{schema}"."Basins"
        #         SET "MajorRiverID" = (SELECT "RiverID" FROM "{schema}"."Rivers" WHERE "Name" = '{basin['MajorRiver']}')
        #         WHERE "Name" = '{basin['Name']}'
        #         """

        #     cursor.execute(query)
        #     connection.commit()

    if "dams" in gpkg_layers:
        dams_gdf = gpd.read_file(gpkg, layer=gpkg_layers["dams"])
        srid = dams_gdf.crs.to_epsg()

        # TODO: use the cast feature like the one in the reaches query
        fill_values = {
            "RES_NAME": "",
            "DAM_NAME": "",
            "ALT_NAME": "",
            "RIVER": "",
            "ALT_RIVER": "",
            "MAIN_BASIN": "",
            "SUB_BASIN": "",
            "NEAR_CITY": "",
            "ALT_CITY": np.nan,
            "ADMIN_UNIT": "",
            "SEC_ADMIN": np.nan,
            "COUNTRY": "",
            "SEC_CNTRY": np.nan,
            "YEAR": np.nan,
            "ALT_YEAR": np.nan,
            "REM_YEAR": np.nan,
            "DAM_HGT_M": np.nan,
            "ALT_HGT_M": np.nan,
            "DAM_LEN_M": np.nan,
            "ALT_LEN_M": np.nan,
            "AREA_SKM": np.nan,
            "AREA_POLY": np.nan,
            "AREA_REP": np.nan,
            "AREA_MAX": np.nan,
            "AREA_MIN": np.nan,
            "CAP_MCM": np.nan,
            "CAP_MAX": np.nan,
            "CAP_REP": np.nan,
            "CAP_MIN": np.nan,
            "DEPTH_M": np.nan,
            "DIS_AVG_LS": np.nan,
            "DOR_PC": np.nan,
            "ELEV_MASL": np.nan,
            "CATCH_SKM": np.nan,
            "CATCH_REP": np.nan,
            "DATA_INFO": np.nan,
            "USE_IRRI": "",
            "USE_ELEC": "",
            "USE_SUPP": "",
            "USE_FCON": "",
            "USE_RECR": "",
            "USE_NAVI": "",
            "USE_FISH": "",
            "USE_PCON": np.nan,
            "USE_LIVE": np.nan,
            "USE_OTHR": "",
            "MAIN_USE": "",
            "LAKE_CTRL": "",
            "MULTI_DAMS": "",
            "TIMELINE": np.nan,
            "COMMENTS": "",
            "URL": "",
            "QUALITY": "",
            "EDITOR": "",
            "LONG_DD": np.nan,
            "LAT_DD": np.nan,
            "POLY_SRC": "",
        }
        dams_gdf.fillna(fill_values, inplace=True)

        for i, dam in dams_gdf.iterrows():
            query = f"""
                INSERT INTO "{schema}"."Dams" ("Name", "Reservoir", "AltName", "Country", "Year", "AreaSqKm", "CapacityMCM", "DepthM", "ElevationMASL", "MainUse", "LONG_DD", "LAT_DD", "DamGeometry")
                SELECT '{str(dam['DAM_NAME']).replace("'", "''")}', NULLIF('{str(dam['RES_NAME']).replace("'", "''")}', ''), NULLIF('{str(dam['ALT_NAME'])}',''), '{dam['COUNTRY']}', NULLIF({null_or_value(dam['YEAR'])}, NULL), NULLIF({null_or_value(dam['AREA_SKM'])}, NULL), NULLIF({null_or_value(dam['CAP_MCM'])}, NULL), NULLIF({null_or_value(dam['DEPTH_M'])}, NULL), NULLIF({null_or_value(dam['ELEV_MASL'])}, NULL),  '{dam['MAIN_USE']}', {dam['LONG_DD']}, {dam['LAT_DD']}, 'SRID={srid};{dam['geometry'].wkt}'
                WHERE NOT EXISTS (SELECT * FROM "{schema}"."Dams" WHERE "Name" = '{str(dam['DAM_NAME']).replace("'", "''")}');
                """

            cursor.execute(query)
            connection.commit()

            # Update the RiverID column if the river exists in the Rivers table
            query2 = f"""
            UPDATE "{schema}"."Dams"
            SET "RiverID" = (SELECT "RiverID" FROM "{schema}"."Rivers" WHERE "Name" = '{dam['RIVER']}')
            WHERE "Name" = '{str(dam['DAM_NAME']).replace("'", "''")}'
            """

            cursor.execute(query2)
            connection.commit()

            # Update the BasinID column if the basin exists in the Basins table
            query3 = f"""
            UPDATE "{schema}"."Dams"
            SET "RegionID" = (SELECT "RegionID" FROM "{schema}"."Regions" WHERE "Name" = 'Columbia River Basin')
            WHERE "Name" = '{str(dam['DAM_NAME']).replace("'", "''")}'
            """

            cursor.execute(query3)
            connection.commit()

    if "reservoirs" in gpkg_layers:
        reservoirs_gdf = gpd.read_file(gpkg, layer=gpkg_layers["reservoirs"])
        srid = reservoirs_gdf.crs.to_epsg()
        # dams_gdf.fillna("", inplace=True)

        for i, reservoir in reservoirs_gdf.iterrows():
            query = f"""
                UPDATE "{schema}"."Dams"
                SET "ReservoirGeometry" = 'SRID={srid};{reservoir['geometry'].wkt}'
                WHERE "Name" = '{str(reservoir['DAM_NAME']).replace("'", "''")}'
                """

            cursor.execute(query)
            connection.commit()

    if "reaches" in gpkg_layers:
        reaches_gdf = gpd.read_file(gpkg, layer=gpkg_layers["reaches"])
        srid = reaches_gdf.crs.to_epsg()

        # for i, reach in reaches_gdf.iterrows():
        #     # Iinsert reach data into the table if the entry doesn't already exist
        for i, reach in reaches_gdf.iterrows():

            query = f"""
                INSERT INTO "{schema}"."Reaches" ("Name", "RiverID", "ClimateClass", "WidthMin", "WidthMean", "WidthMax", "RKm", "geometry")
                SELECT '{reach['Name']}', (SELECT "RiverID" FROM {schema}."Rivers" WHERE "Name" = '{reach['river_name']}'), {reach['koppen']}, CAST(NULLIF('{str(reach['WidthMin'])}','NaN') AS double precision), CAST(NULLIF('{str(reach['WidthMean'])}','NaN') AS double precision), CAST(NULLIF('{str(reach['WidthMax'])}','NaN') AS double precision), CAST(NULLIF('{str(reach['RKm'])}','NaN') AS double precision), 'SRID={srid};{reach['geometry'].wkt}'
                WHERE NOT EXISTS (SELECT * FROM {schema}."Reaches" WHERE "Name" = '{reach['Name']}')
                """

            cursor.execute(query)
            connection.commit()

        if "buffered_reaches" in gpkg_layers:
            buffered_reaches_gdf = gpd.read_file(
                gpkg, layer=gpkg_layers["buffered_reaches"]
            )
            srid = buffered_reaches_gdf.crs.to_epsg()

            for i, buffered_reach in buffered_reaches_gdf.iterrows():
                query = f"""
                    UPDATE "{schema}"."Reaches"
                    SET "buffered_geometry" = 'SRID={srid};{buffered_reach['geometry'].wkt}'
                    WHERE "Name" = '{buffered_reach['Name']}'
                    """

                cursor.execute(query)
                connection.commit()


def upload_gis(config_file, gpkg, gpkg_layers, db_type="mysql"):
    print("Uploading GIS data to database...")
    if db_type == "mysql":
        mysql_upload_gis(
            config_file,
            gpkg,
            gpkg_layers,
        )
    elif db_type == "postgresql":
        postgresql_upload_gis(
            config_file,
            gpkg,
            gpkg_layers,
        )
    print("GIS data uploaded successfully!")