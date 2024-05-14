SET
  FOREIGN_KEY_CHECKS = 0;

CREATE TABLE IF NOT EXISTS
  `Basins` (
    `BasinID` INT(11) NOT NULL AUTO_INCREMENT,
    `Prefix` VARCHAR(45) NOT NULL DEFAULT 'BAS',
    `Name` VARCHAR(255) NOT NULL,
    `DrainageAreaSqKm` FLOAT DEFAULT NULL COMMENT 'Drainage area of the Basin in square-kilometers',
    `MajorRiverID` INT(11) DEFAULT NULL,
    `geometry` GEOMETRY NOT NULL,
    PRIMARY KEY (`BasinID`),
    UNIQUE KEY `BasinID_UNIQUE` (`BasinID`),
    KEY `Fk_MajorRiver` (`MajorRiverID`),
    CONSTRAINT `Fk_MajorRiver` FOREIGN KEY (`MajorRiverID`) REFERENCES `Rivers` (`RiverID`) ON DELETE SET NULL ON UPDATE CASCADE
  ) ENGINE = INNODB;

CREATE TABLE IF NOT EXISTS
  `DamLandsatWaterTemp` (
    `ID` INT(11) NOT NULL AUTO_INCREMENT,
    `Date` DATE NOT NULL,
    `DamID` INT(11) DEFAULT NULL,
    `Value` FLOAT DEFAULT NULL COMMENT 'Landsat-based water temperature for reservoirs',
    PRIMARY KEY (`ID`),
    UNIQUE KEY `DamLandsatWaterTempID_UNIQUE` (`ID`),
    KEY `Fk_water_temp_dam` (`DamID`),
    CONSTRAINT `Fk_water_temp_dam` FOREIGN KEY (`DamID`) REFERENCES `Dams` (`DamID`) ON DELETE CASCADE ON UPDATE CASCADE
  ) ENGINE = INNODB;

CREATE TABLE IF NOT EXISTS
  `Dams` (
    `DamID` INT(11) NOT NULL AUTO_INCREMENT,
    `Prefix` VARCHAR(45) NOT NULL DEFAULT 'DAM',
    `Name` VARCHAR(255) NOT NULL,
    `Reservoir` VARCHAR(255) DEFAULT NULL,
    `AltName` VARCHAR(255) DEFAULT NULL,
    `RiverID` INT(11) DEFAULT NULL,
    `BasinID` INT(11) DEFAULT NULL,
    `AdminUnit` VARCHAR(255) DEFAULT NULL,
    `Country` VARCHAR(255) DEFAULT NULL,
    `Year` YEAR(4) DEFAULT NULL,
    `AreaSqKm` FLOAT DEFAULT NULL,
    `CapacityMCM` FLOAT DEFAULT NULL,
    `DepthM` FLOAT DEFAULT NULL,
    `ElevationMASL` INT(11) DEFAULT NULL,
    `MainUse` VARCHAR(255) DEFAULT NULL,
    `LONG_DD` FLOAT DEFAULT NULL,
    `LAT_DD` FLOAT DEFAULT NULL,
    `DamGeometry` POINT DEFAULT NULL COMMENT 'Point geometry for the dam',
    `ReservoirGeometry` POLYGON DEFAULT NULL COMMENT 'Polygon geometry for the reservoir',
    PRIMARY KEY (`DamID`),
    UNIQUE KEY `DamID_UNIQUE` (`DamID`),
    KEY `Fk_river_dams` (`RiverID`),
    KEY `Fk_basin_dams` (`BasinID`),
    CONSTRAINT `Fk_basin_dams` FOREIGN KEY (`BasinID`) REFERENCES `Basins` (`BasinID`) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT `Fk_river_dams` FOREIGN KEY (`RiverID`) REFERENCES `Rivers` (`RiverID`) ON DELETE SET NULL ON UPDATE CASCADE
  ) ENGINE = INNODB;

CREATE TABLE IF NOT EXISTS
  `Reaches` (
    `ReachID` INT(11) NOT NULL AUTO_INCREMENT,
    `Prefix` VARCHAR(45) NOT NULL DEFAULT 'REA',
    `Name` VARCHAR(255) DEFAULT NULL,
    `RiverID` INT(11) DEFAULT NULL,
    `ClimateClass` INT(11) DEFAULT NULL COMMENT 'Legend linking the numeric values in the maps to the Köppen-Geiger classes.
    The RGB colors used in Beck et al. [2018] are provided between parentheses',
    WidthMin FLOAT DEFAULT NULL COMMENT 'Minimum width (meters)',
    WidthMean FLOAT DEFAULT NULL COMMENT 'Mean width (meters)',
    WidthMax FLOAT DEFAULT NULL COMMENT 'Maximum width (meters)',
    geometry GEOMETRY NOT NULL,
    PRIMARY KEY (ReachID),
    UNIQUE KEY ReachID_UNIQUE (ReachID),
    KEY Fk_river (RiverID),
    CONSTRAINT Fk_river FOREIGN KEY (RiverID) REFERENCES Rivers (RiverID) ON DELETE CASCADE ON UPDATE CASCADE
  ) ENGINE = INNODB;

CREATE TABLE IF NOT EXISTS
  `ReachEstimatedWaterTemp` (
    `ID` INT(11) NOT NULL AUTO_INCREMENT,
    `Date` DATE NOT NULL,
    `ReachID` INT(11) DEFAULT NULL,
    `Value` FLOAT DEFAULT NULL COMMENT 'Estimated water temperature for reach',
    `Tag` VARCHAR(45) NOT NULL COMMENT 'SM - Semi-monthly estimate
    M - Monthly estimate',
    PRIMARY KEY (`ID`),
    UNIQUE KEY `ReachNDVIID_UNIQUE` (`ID`),
    KEY `Fk_est_water_temp_reach` (`ReachID`),
    CONSTRAINT `Fk_est_water_temp_reach` FOREIGN KEY (`ReachID`) REFERENCES `Reaches` (`ReachID`) ON DELETE CASCADE ON UPDATE CASCADE
  ) ENGINE = INNODB;

CREATE TABLE IF NOT EXISTS
  `ReachInsituWaterTemp` (
    `ID` INT(11) NOT NULL AUTO_INCREMENT,
    `Date` DATE NOT NULL,
    `ReachID` INT(11) DEFAULT NULL,
    `Value` FLOAT DEFAULT NULL COMMENT 'Insitu water temperature for reach',
    PRIMARY KEY (`ID`),
    UNIQUE KEY `ReachInsituWaterTempID_UNIQUE` (`ID`),
    KEY `Fk_insitu_water_temp_reach` (`ReachID`),
    CONSTRAINT `Fk_insitu_water_temp_reach` FOREIGN KEY (`ReachID`) REFERENCES `Reaches` (`ReachID`) ON DELETE CASCADE ON UPDATE CASCADE
  ) ENGINE = INNODB;

CREATE TABLE IF NOT EXISTS
  `ReachLandsatLandTemp` (
    `ID` INT(11) NOT NULL AUTO_INCREMENT,
    `Date` DATE NOT NULL,
    `ReachID` INT(11) DEFAULT NULL,
    `Value` FLOAT DEFAULT NULL COMMENT 'Landsat-based land temperature on the reach corridor',
    PRIMARY KEY (`ID`),
    UNIQUE KEY `ReachLandsatLandTempID_UNIQUE` (`ID`),
    KEY `Fk_land_temp_reach` (`ReachID`),
    CONSTRAINT `Fk_land_temp_reach` FOREIGN KEY (`ReachID`) REFERENCES `Reaches` (`ReachID`) ON DELETE CASCADE ON UPDATE CASCADE
  ) ENGINE = INNODB;

CREATE TABLE IF NOT EXISTS
  `ReachLandsatWaterTemp` (
    `ID` INT(11) NOT NULL AUTO_INCREMENT,
    `Date` DATE NOT NULL,
    `ReachID` INT(11) DEFAULT NULL,
    `Value` FLOAT DEFAULT NULL COMMENT 'Landsat-based water temperature for reaches',
    PRIMARY KEY (`ID`),
    UNIQUE KEY `ReachLandsatWaterTempID_UNIQUE` (`ID`),
    KEY `Fk_water_temp_reach` (`ReachID`),
    CONSTRAINT `Fk_water_temp_reach` FOREIGN KEY (`ReachID`) REFERENCES `Reaches` (`ReachID`) ON DELETE CASCADE ON UPDATE CASCADE
  ) ENGINE = INNODB;

CREATE TABLE IF NOT EXISTS
  `ReachNDVI` (
    `ID` INT(11) NOT NULL AUTO_INCREMENT,
    `Date` DATE NOT NULL,
    `ReachID` INT(11) DEFAULT NULL,
    `Value` FLOAT DEFAULT NULL COMMENT 'NDVI on the reach buffer or corridor',
    PRIMARY KEY (`ID`),
    UNIQUE KEY `ReachNDVIID_UNIQUE` (`ID`),
    KEY `Fk_NDVI_reach` (`ReachID`),
    CONSTRAINT `Fk_NDVI_reach` FOREIGN KEY (`ReachID`) REFERENCES `Reaches` (`ReachID`) ON DELETE CASCADE ON UPDATE CASCADE
  ) ENGINE = INNODB;

CREATE TABLE IF NOT EXISTS
  `Rivers` (
    `RiverID` INT(11) NOT NULL AUTO_INCREMENT,
    `Prefix` VARCHAR(45) NOT NULL DEFAULT 'RIV',
    `Name` VARCHAR(255) DEFAULT NULL,
    `LengthKm` FLOAT DEFAULT NULL COMMENT 'Length of the river in kilometers',
    `WidthM` FLOAT DEFAULT NULL COMMENT 'Width in meters',
    `BasinID` INT(11) DEFAULT NULL COMMENT 'ID for the basin in which this river lies',
    `geometry` GEOMETRY NOT NULL,
    PRIMARY KEY (`RiverID`),
    UNIQUE KEY `RiverID_UNIQUE` (`RiverID`),
    KEY `Fk_Basin` (`BasinID`),
    CONSTRAINT `Fk_Basin` FOREIGN KEY (`BasinID`) REFERENCES `Basins` (`BasinID`) ON DELETE SET NULL ON UPDATE CASCADE
  ) ENGINE = INNODB;

SET
  FOREIGN_KEY_CHECKS = 1;