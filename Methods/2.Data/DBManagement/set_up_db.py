# TODO: Add docstring

import argparse
import sys
import geemap
import ee
from pathlib import Path
import pandas as pd
import os
from pathlib import Path
import time
from random import randint
import json
import datetime
import geopandas as gpd

# TODO: use the utils package to read the configuration file
from configparser import ConfigParser


def read_config(config_path, required_sections=[]):
    """
    Read configuration file

    Parameters:
    -----------
    config_path: str
        path to configuration file
    required_sections: list
        list of required sections in the configuration file

    Returns:
    --------
    dict
        dictionary of configuration parameters
    """

    config = ConfigParser()
    config.read(config_path)

    if required_sections:
        for section in required_sections:
            if section not in config.sections():
                raise Exception(
                    f"Section {section} not found in the {config_path} file"
                )
        # create a dictionary of parameters
        config_dict = {
            section: dict(config.items(section)) for section in required_sections
        }
    else:
        config_dict = {
            section: dict(config.items(section)) for section in config.sections()
        }

    return config_dict


# import connect
# TODO: convert this to a function in the utils package
def get_db_connection(package_dir, db_config_path, logger=None, return_conn=False):
    utils = str(package_dir / "utils")
    sys.path.insert(0, utils)
    from sql import connect  # utility functions for connecting to MySQL

    conn = connect.Connect(Path(db_config_path), logger=logger)
    connection = conn.conn

    if return_conn:
        return conn
    else:
        return connection


def get_logger(
    package_dir,
    project_title,
    log_dir,
    logger_format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
):
    utils = str(package_dir / "utils")
    sys.path.insert(0, utils)
    import logger

    logger = logger.Logger(
        project_title=project_title, log_dir=log_dir, logger_format=logger_format
    ).get_logger()

    return logger


def set_up_db(
    connection,
    basins_shp=None,
    rivers_shp=None,
    dams_shp=None,
    reservoirs_shp=None,
    reaches_shp=None,
    logger=None,
):
    cursor = connection.cursor()

    # CREATE SCHEMA IF NOT EXISTS `THORR` DEFAULT CHARACTER SET utf8
    cursor.execute("CREATE SCHEMA IF NOT EXISTS `thorr` DEFAULT CHARACTER SET utf8;")

    # # Create tables for the database
    # query = """
    # SET
    # FOREIGN_KEY_CHECKS = 0;

    # CREATE TABLE IF NOT EXISTS
    # `Basins` (
    #     `BasinID` INT(11) NOT NULL AUTO_INCREMENT,
    #     `Prefix` VARCHAR(45) NOT NULL DEFAULT 'BAS',
    #     `Name` VARCHAR(255) NOT NULL,
    #     `DrainageAreaSqKm` FLOAT DEFAULT NULL COMMENT 'Drainage area of the Basin in square-kilometers',
    #     `MajorRiverID` INT(11) DEFAULT NULL,
    #     `geometry` GEOMETRY NOT NULL,
    #     PRIMARY KEY (`BasinID`),
    #     UNIQUE KEY `BasinID_UNIQUE` (`BasinID`),
    #     KEY `Fk_MajorRiver` (`MajorRiverID`),
    #     CONSTRAINT `Fk_MajorRiver` FOREIGN KEY (`MajorRiverID`) REFERENCES `Rivers` (`RiverID`) ON DELETE SET NULL ON UPDATE CASCADE
    # ) ENGINE = INNODB;

    # CREATE TABLE IF NOT EXISTS
    # `DamLandsatWaterTemp` (
    #     `ID` INT(11) NOT NULL AUTO_INCREMENT,
    #     `Date` DATE NOT NULL,
    #     `DamID` INT(11) DEFAULT NULL,
    #     `Value` FLOAT DEFAULT NULL COMMENT 'Landsat-based water temperature for reservoirs',
    #     PRIMARY KEY (`ID`),
    #     UNIQUE KEY `DamLandsatWaterTempID_UNIQUE` (`ID`),
    #     KEY `Fk_water_temp_dam` (`DamID`),
    #     CONSTRAINT `Fk_water_temp_dam` FOREIGN KEY (`DamID`) REFERENCES `Dams` (`DamID`) ON DELETE CASCADE ON UPDATE CASCADE
    # ) ENGINE = INNODB;

    # CREATE TABLE IF NOT EXISTS
    # `Dams` (
    #     `DamID` INT(11) NOT NULL AUTO_INCREMENT,
    #     `Prefix` VARCHAR(45) NOT NULL DEFAULT 'DAM',
    #     `Name` VARCHAR(255) NOT NULL,
    #     `Reservoir` VARCHAR(255) DEFAULT NULL,
    #     `AltName` VARCHAR(255) DEFAULT NULL,
    #     `RiverID` INT(11) DEFAULT NULL,
    #     `BasinID` INT(11) DEFAULT NULL,
    #     `AdminUnit` VARCHAR(255) DEFAULT NULL,
    #     `Country` VARCHAR(255) DEFAULT NULL,
    #     `Year` YEAR(4) DEFAULT NULL,
    #     `AreaSqKm` FLOAT DEFAULT NULL,
    #     `CapacityMCM` FLOAT DEFAULT NULL,
    #     `DepthM` FLOAT DEFAULT NULL,
    #     `ElevationMASL` INT(11) DEFAULT NULL,
    #     `MainUse` VARCHAR(255) DEFAULT NULL,
    #     `LONG_DD` FLOAT DEFAULT NULL,
    #     `LAT_DD` FLOAT DEFAULT NULL,
    #     `DamGeometry` POINT DEFAULT NULL COMMENT 'Point geometry for the dam',
    #     `ReservoirGeometry` POLYGON DEFAULT NULL COMMENT 'Polygon geometry for the reservoir',
    #     PRIMARY KEY (`DamID`),
    #     UNIQUE KEY `DamID_UNIQUE` (`DamID`),
    #     KEY `Fk_river_dams` (`RiverID`),
    #     KEY `Fk_basin_dams` (`BasinID`),
    #     CONSTRAINT `Fk_basin_dams` FOREIGN KEY (`BasinID`) REFERENCES `Basins` (`BasinID`) ON DELETE SET NULL ON UPDATE CASCADE,
    #     CONSTRAINT `Fk_river_dams` FOREIGN KEY (`RiverID`) REFERENCES `Rivers` (`RiverID`) ON DELETE SET NULL ON UPDATE CASCADE
    # ) ENGINE = INNODB;

    # CREATE TABLE IF NOT EXISTS
    # `Reaches` (
    #     `ReachID` INT(11) NOT NULL AUTO_INCREMENT,
    #     `Prefix` VARCHAR(45) NOT NULL DEFAULT 'REA',
    #     `Name` VARCHAR(255) DEFAULT NULL,
    #     `RiverID` INT(11) DEFAULT NULL,
    #     `ClimateClass` INT(11) DEFAULT NULL COMMENT 'Legend linking the numeric values in the maps to the Köppen-Geiger classes.
    #     The RGB colors used in Beck et al. [2018] are provided between parentheses',
    #     WidthMin FLOAT DEFAULT NULL COMMENT 'Minimum width (meters)',
    #     WidthMean FLOAT DEFAULT NULL COMMENT 'Mean width (meters)',
    #     WidthMax FLOAT DEFAULT NULL COMMENT 'Maximum width (meters)',
    #     geometry GEOMETRY NOT NULL,
    #     PRIMARY KEY (ReachID),
    #     UNIQUE KEY ReachID_UNIQUE (ReachID),
    #     KEY Fk_river (RiverID),
    #     CONSTRAINT Fk_river FOREIGN KEY (RiverID) REFERENCES Rivers (RiverID) ON DELETE CASCADE ON UPDATE CASCADE
    # ) ENGINE = INNODB;

    # CREATE TABLE IF NOT EXISTS
    # `ReachEstimatedWaterTemp` (
    #     `ID` INT(11) NOT NULL AUTO_INCREMENT,
    #     `Date` DATE NOT NULL,
    #     `ReachID` INT(11) DEFAULT NULL,
    #     `Value` FLOAT DEFAULT NULL COMMENT 'Estimated water temperature for reach',
    #     `Tag` VARCHAR(45) NOT NULL COMMENT 'SM - Semi-monthly estimate
    #     M - Monthly estimate',
    #     PRIMARY KEY (`ID`),
    #     UNIQUE KEY `ReachNDVIID_UNIQUE` (`ID`),
    #     KEY `Fk_est_water_temp_reach` (`ReachID`),
    #     CONSTRAINT `Fk_est_water_temp_reach` FOREIGN KEY (`ReachID`) REFERENCES `Reaches` (`ReachID`) ON DELETE CASCADE ON UPDATE CASCADE
    # ) ENGINE = INNODB;

    # CREATE TABLE IF NOT EXISTS
    # `ReachInsituWaterTemp` (
    #     `ID` INT(11) NOT NULL AUTO_INCREMENT,
    #     `Date` DATE NOT NULL,
    #     `ReachID` INT(11) DEFAULT NULL,
    #     `Value` FLOAT DEFAULT NULL COMMENT 'Insitu water temperature for reach',
    #     PRIMARY KEY (`ID`),
    #     UNIQUE KEY `ReachInsituWaterTempID_UNIQUE` (`ID`),
    #     KEY `Fk_insitu_water_temp_reach` (`ReachID`),
    #     CONSTRAINT `Fk_insitu_water_temp_reach` FOREIGN KEY (`ReachID`) REFERENCES `Reaches` (`ReachID`) ON DELETE CASCADE ON UPDATE CASCADE
    # ) ENGINE = INNODB;

    # CREATE TABLE IF NOT EXISTS
    # `ReachLandsatLandTemp` (
    #     `ID` INT(11) NOT NULL AUTO_INCREMENT,
    #     `Date` DATE NOT NULL,
    #     `ReachID` INT(11) DEFAULT NULL,
    #     `Value` FLOAT DEFAULT NULL COMMENT 'Landsat-based land temperature on the reach corridor',
    #     PRIMARY KEY (`ID`),
    #     UNIQUE KEY `ReachLandsatLandTempID_UNIQUE` (`ID`),
    #     KEY `Fk_land_temp_reach` (`ReachID`),
    #     CONSTRAINT `Fk_land_temp_reach` FOREIGN KEY (`ReachID`) REFERENCES `Reaches` (`ReachID`) ON DELETE CASCADE ON UPDATE CASCADE
    # ) ENGINE = INNODB;

    # CREATE TABLE IF NOT EXISTS
    # `ReachLandsatWaterTemp` (
    #     `ID` INT(11) NOT NULL AUTO_INCREMENT,
    #     `Date` DATE NOT NULL,
    #     `ReachID` INT(11) DEFAULT NULL,
    #     `Value` FLOAT DEFAULT NULL COMMENT 'Landsat-based water temperature for reaches',
    #     PRIMARY KEY (`ID`),
    #     UNIQUE KEY `ReachLandsatWaterTempID_UNIQUE` (`ID`),
    #     KEY `Fk_water_temp_reach` (`ReachID`),
    #     CONSTRAINT `Fk_water_temp_reach` FOREIGN KEY (`ReachID`) REFERENCES `Reaches` (`ReachID`) ON DELETE CASCADE ON UPDATE CASCADE
    # ) ENGINE = INNODB;

    # CREATE TABLE IF NOT EXISTS
    # `ReachNDVI` (
    #     `ID` INT(11) NOT NULL AUTO_INCREMENT,
    #     `Date` DATE NOT NULL,
    #     `ReachID` INT(11) DEFAULT NULL,
    #     `Value` FLOAT DEFAULT NULL COMMENT 'NDVI on the reach buffer or corridor',
    #     PRIMARY KEY (`ID`),
    #     UNIQUE KEY `ReachNDVIID_UNIQUE` (`ID`),
    #     KEY `Fk_NDVI_reach` (`ReachID`),
    #     CONSTRAINT `Fk_NDVI_reach` FOREIGN KEY (`ReachID`) REFERENCES `Reaches` (`ReachID`) ON DELETE CASCADE ON UPDATE CASCADE
    # ) ENGINE = INNODB;

    # CREATE TABLE IF NOT EXISTS
    # `Rivers` (
    #     `RiverID` INT(11) NOT NULL AUTO_INCREMENT,
    #     `Prefix` VARCHAR(45) NOT NULL DEFAULT 'RIV',
    #     `Name` VARCHAR(255) DEFAULT NULL,
    #     `LengthKm` FLOAT DEFAULT NULL COMMENT 'Length of the river in kilometers',
    #     `WidthM` FLOAT DEFAULT NULL COMMENT 'Width in meters',
    #     `BasinID` INT(11) DEFAULT NULL COMMENT 'ID for the basin in which this river lies',
    #     `geometry` GEOMETRY NOT NULL,
    #     PRIMARY KEY (`RiverID`),
    #     UNIQUE KEY `RiverID_UNIQUE` (`RiverID`),
    #     KEY `Fk_Basin` (`BasinID`),
    #     CONSTRAINT `Fk_Basin` FOREIGN KEY (`BasinID`) REFERENCES `Basins` (`BasinID`) ON DELETE SET NULL ON UPDATE CASCADE
    # ) ENGINE = INNODB;

    # SET
    # FOREIGN_KEY_CHECKS = 1;
    # """

    # cursor.execute(query)
    # # connection.commit()

    # upload basins shapefile to database
    if basins_shp:
        # Load basin shapefile
        basins_gdf = gpd.read_file(basins_shp)
        basins_gdf = basins_gdf.to_crs(
            epsg=4326
        )  # convert to WGS84. This is the CRS used by the database

        # Insert basin data into the table if the entry doesn't already exist
        for i, row in basins_gdf.iterrows():
            query = f"""
            INSERT INTO Basins (Name, DrainageAreaSqKm, geometry)
            SELECT '{row['Name']}', {row['AreaSqKm']}, ST_GeomFromText('{row['geometry'].wkt}', 4326, 'axis-order=long-lat')
            WHERE NOT EXISTS (SELECT * FROM Basins WHERE Name = '{row['Name']}')
            """

            cursor.execute(query)
            connection.commit()


    if rivers_shp:
        rivers_gdf = gpd.read_file(rivers_shp)
        rivers_gdf = rivers_gdf.to_crs(
            epsg=4326
        )  # convert to WGS84. This is the CRS used by the database

        # Insert river data into the table if the entry doesn't already exist
        for i, row in rivers_gdf.iterrows():
            query = f"""
            INSERT INTO Rivers (Name, LengthKm, geometry)
            SELECT '{row['GNIS_Name']}', {row['LengthKM']}, ST_GeomFromText('{row['geometry'].wkt}', 4326, 'axis-order=long-lat')
            WHERE NOT EXISTS (SELECT * FROM Rivers WHERE Name = '{row['GNIS_Name']}')
            """

            cursor.execute(query)
            connection.commit()

            # # Update the BasinID column if the basin exists in the Basins table
            # query2 = f"""
            # UPDATE Rivers
            # SET BasinID = (SELECT BasinID FROM Basins WHERE Name = '{row['Basin']}')
            # WHERE Name = '{row['GNIS_Name']}'
            # """
            query2 = f"""
            UPDATE Rivers
            SET BasinID = (SELECT BasinID FROM Basins WHERE Name = '{row['Basin']}'), LengthKm = {row['LengthKM']}
            WHERE Name = "{row['GNIS_Name']}"
            """

            cursor.execute(query2)
            connection.commit()

            # Update the MajorRiverID column if the river exists in the Rivers table
            for i, row in basins_gdf.iterrows():
                query = f"""
                UPDATE Basins
                SET MajorRiverID = (SELECT RiverID FROM Rivers WHERE Name = '{row['MajorRiver']}')
                WHERE Name = '{row['Name']}'
                """

                cursor.execute(query)
                connection.commit()

    if dams_shp and reservoirs_shp:
        dams_gdf = gpd.read_file(dams_shp)
        dams_gdf = dams_gdf.to_crs(
            epsg=4326
        )  # convert to WGS84. This is the CRS used by the database
        reservoirs_gdf = gpd.read_file(reservoirs_shp)
        reservoirs_gdf = reservoirs_gdf.to_crs(
            epsg=4326
        )  # convert to WGS84. This is the CRS used by the database

        dams_gdf.fillna("", inplace=True)
        reservoirs_gdf.fillna("", inplace=True)

        # Insert river data into the table if the entry doesn't already exist
        for i, row in dams_gdf.iterrows():
            # print(row['DAM_NAME'])
            query = f"""
            INSERT INTO Dams (Name, Reservoir, AltName, AdminUnit, Country, Year, AreaSqKm, CapacityMCM, DepthM, ElevationMASL, MainUse, LONG_DD, LAT_DD, DamGeometry)
            SELECT "{row['DAM_NAME']}", NULLIF("{row['RES_NAME']}", ''), NULLIF("{str(row['ALT_NAME'])}",''), '{row['ADMIN_UNIT']}', '{row['COUNTRY']}', {row['YEAR']}, {row['AREA_SKM']}, {row['CAP_MCM']}, {row['DEPTH_M']}, {row['ELEV_MASL']}, '{row['MAIN_USE']}', {row['LONG_DD']}, {row['LAT_DD']}, ST_PointFromText('{row['geometry'].wkt}', 4326, 'axis-order=long-lat')
            WHERE NOT EXISTS (SELECT * FROM Dams WHERE Name = "{row['DAM_NAME']}")
            """

            cursor.execute(query)
            connection.commit()

            # Update the RiverID column if the river exists in the Rivers table
            query2 = f"""
            UPDATE Dams
            SET RiverID = (SELECT RiverID FROM Rivers WHERE Name = "{row['RIVER']}")
            WHERE Name = "{row['DAM_NAME']}"
            """

            cursor.execute(query2)
            connection.commit()

            # Update the BasinID column if the basin exists in the Basins table
            query3 = f"""
            UPDATE Dams
            SET BasinID = (SELECT BasinID FROM Basins WHERE Name = 'Columbia River Basin')
            WHERE Name = "{row['DAM_NAME']}"
            """

            cursor.execute(query3)
            connection.commit()

        # Insert reservoir data into the table if the entry doesn't already exist
        for i, row in reservoirs_gdf.iterrows():
            query = f"""
            UPDATE Dams
            SET ReservoirGeometry = ST_GeomFromText('{row['geometry'].wkt}', 4326, 'axis-order=long-lat')
            WHERE Name = "{row['DAM_NAME']}"
            """

            cursor.execute(query)
            connection.commit()

    if reaches_shp:
        reaches_gdf = gpd.read_file(reaches_shp)
        reaches_gdf = reaches_gdf.to_crs(
            epsg=4326
        )  # convert to WGS84. This is the CRS used by the database

        # Insert reach data into the table if the entry doesn't already exist
        for i, row in reaches_gdf.iterrows():
            # query = f"""
            # INSERT INTO Reaches (Name, RiverID, ClimateClass, Width, Width5, Width95, Depth, Depth5, Depth95, geometry)
            # SELECT "{row['reach_id']}",(SELECT RiverID FROM Rivers WHERE Name = '{row['GNIS_Name']}'), {row['koppen']}, {row["WIDTH"]}, {row["WIDTH5"]}, {row["WIDTH95"]}, {row["DEPTH"]}, {row["DEPTH5"]}, {row["DEPTH95"]}, ST_GeomFromText('{row['geometry'].wkt}', 4326, 'axis-order=long-lat')
            # WHERE NOT EXISTS (SELECT * FROM Reaches WHERE Name = "{row['reach_id']}")
            # """

            query = f"""
            INSERT INTO Reaches (Name, RiverID, ClimateClass, WidthMin, WidthMean, WidthMax, geometry)
            SELECT "{row['reach_id']}",(SELECT RiverID FROM Rivers WHERE Name = '{row['GNIS_Name']}'), {row['koppen']}, NULLIF("{str(row['WidthMin'])}",'nan'), NULLIF("{str(row['WidthMean'])}",'nan'), NULLIF("{str(row['WidthMax'])}",'nan'), ST_GeomFromText('{row['geometry'].wkt}', 4326, 'axis-order=long-lat')
            WHERE NOT EXISTS (SELECT * FROM Reaches WHERE Name = "{row['reach_id']}")
            """

            try:
                cursor.execute(query)
                connection.commit()
            except Exception as e:
                if logger is not None:
                    logger.error(f"Error: {e}")
                else:
                    print(f"Error: {e}")

    connection.close()

    if logger is not None:
        logger.info(f"Database set up complete.")
    else:
        print("Database set up complete")


def main(args):
    config_path = Path(args.config)
    config_dict = read_config(
        config_path,
        # required_sections=["project", "mysql", "data"]
    )

    project_dir = Path(config_dict["project"]["project_dir"])
    db_config_path = project_dir / config_dict["mysql"]["db_config_path"]

    logger = get_logger(
        package_dir=Path(
            config_dict["project"]["package_dir"]
        ),  # base directory for the package
        project_title=config_dict["project"]["title"],
        log_dir=Path(project_dir, "logs"),
        logger_format="%(asctime)s - %(name)s - reservoirs - %(levelname)s - %(message)s",
    )

    # get database connection
    connection = get_db_connection(
        package_dir=Path(
            config_dict["project"]["package_dir"]
        ),  # base directory for the package
        db_config_path=db_config_path,  # db_config_path
        logger=logger,
    )
    
    basins_shp = Path(project_dir, config_dict["data"]["basins_shp"])
    rivers_shp = Path(project_dir, config_dict["data"]["rivers_shp"])
    dams_shp = Path(project_dir, config_dict["data"]["dams_shp"])
    reservoirs_shp = Path(project_dir, config_dict["data"]["reservoirs_shp2"]) #TODO: change this to reservoirs_shp. Check to see if the reservoirs_shp2 is still needed
    reaches_shp = Path(project_dir, config_dict["data"]["reaches_shp"])

    set_up_db(
        connection,
        basins_shp=basins_shp,
        rivers_shp=rivers_shp,
        dams_shp=dams_shp,
        reservoirs_shp=reservoirs_shp,
        reaches_shp=reaches_shp,
        logger=logger,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config", type=str, help="path to config file", required=True
    )

    main(args=parser.parse_args())
