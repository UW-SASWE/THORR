SET
  FOREIGN_KEY_CHECKS = 0;

CREATE TABLE IF NOT EXISTS
  `Basins` (
    `BasinID` int(11) NOT NULL AUTO_INCREMENT,
    `Prefix` varchar(45) NOT NULL DEFAULT 'BAS',
    `Name` varchar(255) NOT NULL,
    `DrainageAreaSqKm` float DEFAULT NULL COMMENT 'Drainage area of the Basin in square-kilometers',
    `MajorRiverID` int(11) DEFAULT NULL,
    `geometry` geometry NOT NULL,
    PRIMARY KEY (`BasinID`),
    UNIQUE KEY `BasinID_UNIQUE` (`BasinID`),
    KEY `Fk_MajorRiver` (`MajorRiverID`),
    CONSTRAINT `Fk_MajorRiver` FOREIGN KEY (`MajorRiverID`) REFERENCES `Rivers` (`RiverID`) ON DELETE SET NULL ON UPDATE CASCADE
  ) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS
  `DamLandsatWaterTemp` (
    `ID` int(11) NOT NULL AUTO_INCREMENT,
    `Date` date NOT NULL,
    `DamID` int(11) DEFAULT NULL,
    `Value` float DEFAULT NULL COMMENT 'Landsat-based water temperature for reservoirs',
    PRIMARY KEY (`ID`),
    UNIQUE KEY `DamLandsatWaterTempID_UNIQUE` (`ID`),
    KEY `Fk_water_temp_dam` (`DamID`),
    CONSTRAINT `Fk_water_temp_dam` FOREIGN KEY (`DamID`) REFERENCES `Dams` (`DamID`) ON DELETE CASCADE ON UPDATE CASCADE
  ) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS
  `Dams` (
    `DamID` int(11) NOT NULL AUTO_INCREMENT,
    `Prefix` varchar(45) NOT NULL DEFAULT 'DAM',
    `Name` varchar(255) NOT NULL,
    `Reservoir` varchar(255) DEFAULT NULL,
    `AltName` varchar(255) DEFAULT NULL,
    `RiverID` int(11) DEFAULT NULL,
    `BasinID` int(11) DEFAULT NULL,
    `AdminUnit` varchar(255) DEFAULT NULL,
    `Country` varchar(255) DEFAULT NULL,
    `Year` year(4) DEFAULT NULL,
    `AreaSqKm` float DEFAULT NULL,
    `CapacityMCM` float DEFAULT NULL,
    `DepthM` float DEFAULT NULL,
    `ElevationMASL` int(11) DEFAULT NULL,
    `MainUse` varchar(255) DEFAULT NULL,
    `LONG_DD` float DEFAULT NULL,
    `LAT_DD` float DEFAULT NULL,
    `DamGeometry` point DEFAULT NULL COMMENT 'Point geometry for the dam',
    `ReservoirGeometry` polygon DEFAULT NULL COMMENT 'Polygon geometry for the reservoir',
    PRIMARY KEY (`DamID`),
    UNIQUE KEY `DamID_UNIQUE` (`DamID`),
    KEY `Fk_river_dams` (`RiverID`),
    KEY `Fk_basin_dams` (`BasinID`),
    CONSTRAINT `Fk_basin_dams` FOREIGN KEY (`BasinID`) REFERENCES `Basins` (`BasinID`) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT `Fk_river_dams` FOREIGN KEY (`RiverID`) REFERENCES `Rivers` (`RiverID`) ON DELETE SET NULL ON UPDATE CASCADE
  ) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS
  `Reaches` (
    `ReachID` int(11) NOT NULL AUTO_INCREMENT,
    `Prefix` varchar(45) NOT NULL DEFAULT 'REA',
    `Name` varchar(255) DEFAULT NULL,
    `RiverID` int(11) DEFAULT NULL,
    `ClimateClass` int(11) DEFAULT NULL COMMENT 'Legend linking the numeric values in the maps to the Köppen-Geiger classes.\nThe RGB colors used in Beck et al. [2018] are provided between parentheses',
    `WidthMin` float DEFAULT NULL COMMENT 'Minimum width (meters)',
    `WidthMean` float DEFAULT NULL COMMENT 'Mean width (meters)',
    `WidthMax` float DEFAULT NULL COMMENT 'Maximum width (meters)',
    `geometry` geometry NOT NULL,
    PRIMARY KEY (`ReachID`),
    UNIQUE KEY `ReachID_UNIQUE` (`ReachID`),
    KEY `Fk_river` (`RiverID`),
    CONSTRAINT `Fk_river` FOREIGN KEY (`RiverID`) REFERENCES `Rivers` (`RiverID`) ON DELETE CASCADE ON UPDATE CASCADE
  ) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS
  `ReachEstimatedWaterTemp` (
    `ID` int(11) NOT NULL AUTO_INCREMENT,
    `Date` date NOT NULL,
    `ReachID` int(11) DEFAULT NULL,
    `Value` float DEFAULT NULL COMMENT 'Estimated water temperature for reach',
    `Tag` varchar(45) NOT NULL COMMENT 'SM - Semi-monthly estimate\nM - Monthly estimate',
    PRIMARY KEY (`ID`),
    UNIQUE KEY `ReachNDVIID_UNIQUE` (`ID`),
    KEY `Fk_est_water_temp_reach` (`ReachID`),
    CONSTRAINT `Fk_est_water_temp_reach` FOREIGN KEY (`ReachID`) REFERENCES `Reaches` (`ReachID`) ON DELETE CASCADE ON UPDATE CASCADE
  ) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS
  `ReachInsituWaterTemp` (
    `ID` int(11) NOT NULL AUTO_INCREMENT,
    `Date` date NOT NULL,
    `ReachID` int(11) DEFAULT NULL,
    `Value` float DEFAULT NULL COMMENT 'Insitu water temperature for reach',
    PRIMARY KEY (`ID`),
    UNIQUE KEY `ReachInsituWaterTempID_UNIQUE` (`ID`),
    KEY `Fk_insitu_water_temp_reach` (`ReachID`),
    CONSTRAINT `Fk_insitu_water_temp_reach` FOREIGN KEY (`ReachID`) REFERENCES `Reaches` (`ReachID`) ON DELETE CASCADE ON UPDATE CASCADE
  ) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS
  `ReachLandsatLandTemp` (
    `ID` int(11) NOT NULL AUTO_INCREMENT,
    `Date` date NOT NULL,
    `ReachID` int(11) DEFAULT NULL,
    `Value` float DEFAULT NULL COMMENT 'Landsat-based land temperature on the reach corridor',
    PRIMARY KEY (`ID`),
    UNIQUE KEY `ReachLandsatLandTempID_UNIQUE` (`ID`),
    KEY `Fk_land_temp_reach` (`ReachID`),
    CONSTRAINT `Fk_land_temp_reach` FOREIGN KEY (`ReachID`) REFERENCES `Reaches` (`ReachID`) ON DELETE CASCADE ON UPDATE CASCADE
  ) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS
  `ReachLandsatWaterTemp` (
    `ID` int(11) NOT NULL AUTO_INCREMENT,
    `Date` date NOT NULL,
    `ReachID` int(11) DEFAULT NULL,
    `Value` float DEFAULT NULL COMMENT 'Landsat-based water temperature for reaches',
    PRIMARY KEY (`ID`),
    UNIQUE KEY `ReachLandsatWaterTempID_UNIQUE` (`ID`),
    KEY `Fk_water_temp_reach` (`ReachID`),
    CONSTRAINT `Fk_water_temp_reach` FOREIGN KEY (`ReachID`) REFERENCES `Reaches` (`ReachID`) ON DELETE CASCADE ON UPDATE CASCADE
  ) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS
  `ReachNDVI` (
    `ID` int(11) NOT NULL AUTO_INCREMENT,
    `Date` date NOT NULL,
    `ReachID` int(11) DEFAULT NULL,
    `Value` float DEFAULT NULL COMMENT 'NDVI on the reach buffer or corridor',
    PRIMARY KEY (`ID`),
    UNIQUE KEY `ReachNDVIID_UNIQUE` (`ID`),
    KEY `Fk_NDVI_reach` (`ReachID`),
    CONSTRAINT `Fk_NDVI_reach` FOREIGN KEY (`ReachID`) REFERENCES `Reaches` (`ReachID`) ON DELETE CASCADE ON UPDATE CASCADE
  ) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS
  `Rivers` (
    `RiverID` int(11) NOT NULL AUTO_INCREMENT,
    `Prefix` varchar(45) NOT NULL DEFAULT 'RIV',
    `Name` varchar(255) DEFAULT NULL,
    `LengthKm` float DEFAULT NULL COMMENT 'Length of the river in kilometers',
    `WidthM` float DEFAULT NULL COMMENT 'Width in meters',
    `BasinID` int(11) DEFAULT NULL COMMENT 'ID for the basin in which this river lies',
    `geometry` geometry NOT NULL,
    PRIMARY KEY (`RiverID`),
    UNIQUE KEY `RiverID_UNIQUE` (`RiverID`),
    KEY `Fk_Basin` (`BasinID`),
    CONSTRAINT `Fk_Basin` FOREIGN KEY (`BasinID`) REFERENCES `Basins` (`BasinID`) ON DELETE SET NULL ON UPDATE CASCADE
  ) ENGINE = InnoDB;

SET
  FOREIGN_KEY_CHECKS = 1;