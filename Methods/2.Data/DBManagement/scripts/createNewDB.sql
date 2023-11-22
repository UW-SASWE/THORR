CREATE DATABASE  IF NOT EXISTS `HydroThermalHistory` DEFAULT CHARACTER SET utf8 ;
USE `HydroThermalHistory`;

SET FOREIGN_KEY_CHECKS = 0;

CREATE TABLE IF NOT EXISTS `Basins` (
  `BasinID` int NOT NULL AUTO_INCREMENT,
  `Prefix` varchar(45) NOT NULL DEFAULT 'BAS',
  `Name` varchar(255) NOT NULL,
  `DrainageAreaSqKm` float DEFAULT NULL COMMENT 'Drainage area of the Basin in square-kilometers',
  `MajorRiverID` int DEFAULT NULL,
  `geometry` geometry NOT NULL /*!80003 SRID 4326 */,
  PRIMARY KEY (`BasinID`),
  UNIQUE KEY `BasinID_UNIQUE` (`BasinID`),
  KEY `Fk_MajorRiver` (`MajorRiverID`),
  CONSTRAINT `Fk_MajorRiver` FOREIGN KEY (`MajorRiverID`) REFERENCES `Rivers` (`RiverID`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `Rivers` (
  `RiverID` INT NOT NULL AUTO_INCREMENT,
  `Prefix` varchar(45) NOT NULL DEFAULT 'RIV',
  `Name` varchar(255) DEFAULT NULL,
  `LengthKm` float DEFAULT NULL COMMENT 'Length of the river in kilometers',
  `WidthM` float DEFAULT NULL COMMENT 'Width in meters',
  `BasinID` int DEFAULT NULL COMMENT 'ID for the basin in which this river lies',
  `geometry` geometry NOT NULL /*!80003 SRID 4326 */,
  PRIMARY KEY (`RiverID`),
  UNIQUE KEY `RiverID_UNIQUE` (`RiverID`),
  KEY `Fk_Basin` (`BasinID`),
  CONSTRAINT `Fk_Basin` FOREIGN KEY (`BasinID`) REFERENCES `Basins` (`BasinID`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `Dams` (
  `DamID` int NOT NULL AUTO_INCREMENT,
  `Prefix` varchar(45) NOT NULL DEFAULT 'DAM',
  `Name` varchar(255) NOT NULL,
  `Reservoir` varchar(255) DEFAULT NULL,
  `AltName` varchar(255) DEFAULT NULL,
  `RiverID` int DEFAULT NULL,
  `BasinID` int DEFAULT NULL,
  `AdminUnit` varchar(255) DEFAULT NULL,
  `Country` varchar(255) DEFAULT NULL,
  `Year` year DEFAULT NULL,
  `AreaSqKm` float DEFAULT NULL,
  `CapacityMCM` float DEFAULT NULL,
  `DepthM` float DEFAULT NULL,
  `ElevationMASL` int DEFAULT NULL,
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
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `Reaches` (
  `ReachID` int NOT NULL AUTO_INCREMENT,
  `Prefix` varchar(45) NOT NULL DEFAULT 'REA',
  `Name` varchar(255) DEFAULT NULL,
  `RiverID` int DEFAULT NULL,
  `ClimateClass` int DEFAULT NULL COMMENT 'Legend linking the numeric values in the maps to the Köppen-Geiger classes.\nThe RGB colors used in Beck et al. [2018] are provided between parentheses',
  `WidthMin` float DEFAULT NULL COMMENT 'Minimum width (meters)',
  `WidthMean` float DEFAULT NULL COMMENT 'Mean width (meters)',
  `WidthMax` float DEFAULT NULL COMMENT 'Maximum width (meters)',
  `geometry` geometry NOT NULL /*!80003 SRID 4326 */,
  PRIMARY KEY (`ReachID`),
  UNIQUE KEY `ReachID_UNIQUE` (`ReachID`),
  KEY `Fk_river` (`RiverID`),
  CONSTRAINT `Fk_river` FOREIGN KEY (`RiverID`) REFERENCES `Rivers` (`RiverID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `DamLandsatWaterTemp` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `Date` date NOT NULL,
  `DamID` int DEFAULT NULL,
  `Value` float DEFAULT NULL COMMENT 'Landsat-based water temperature for reservoirs',
  PRIMARY KEY (`ID`),
  UNIQUE KEY `DamLandsatWaterTempID_UNIQUE` (`ID`),
  KEY `Fk_water_temp_dam` (`DamID`),
  CONSTRAINT `Fk_water_temp_dam` FOREIGN KEY (`DamID`) REFERENCES `Dams` (`DamID`) ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `ReachLandsatWaterTemp` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `Date` date NOT NULL,
  `ReachID` int DEFAULT NULL,
  `Value` float DEFAULT NULL COMMENT 'Landsat-based water temperature for reaches',
  PRIMARY KEY (`ID`),
  UNIQUE KEY `ReachLandsatWaterTempID_UNIQUE` (`ID`),
  KEY `Fk_water_temp_reach` (`ReachID`),
  CONSTRAINT `Fk_water_temp_reach` FOREIGN KEY (`ReachID`) REFERENCES `Reaches` (`ReachID`) ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `ReachLandsatLandTemp` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `Date` date NOT NULL,
  `ReachID` int DEFAULT NULL,
  `Value` float DEFAULT NULL COMMENT 'Landsat-based land temperature on the reach corridor',
  PRIMARY KEY (`ID`),
  UNIQUE KEY `ReachLandsatLandTempID_UNIQUE` (`ID`),
  KEY `Fk_land_temp_reach` (`ReachID`),
  CONSTRAINT `Fk_land_temp_reach` FOREIGN KEY (`ReachID`) REFERENCES `Reaches` (`ReachID`) ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `ReachNDVI` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `Date` date NOT NULL,
  `ReachID` int DEFAULT NULL,
  `Value` float DEFAULT NULL COMMENT 'NDVI on the reach buffer or corridor',
  PRIMARY KEY (`ID`),
  UNIQUE KEY `ReachNDVIID_UNIQUE` (`ID`),
  KEY `Fk_NDVI_reach` (`ReachID`),
  CONSTRAINT `Fk_NDVI_reach` FOREIGN KEY (`ReachID`) REFERENCES `Reaches` (`ReachID`) ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `ReachEstimatedWaterTemp` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `Date` date NOT NULL,
  `ReachID` int DEFAULT NULL,
  `Value` float DEFAULT NULL COMMENT 'Estimated water temperature for reach',
  `Tag` VARCHAR(45) NOT NULL COMMENT 'SM - Semi-monthly estimate\nM - Monthly estimate',
  PRIMARY KEY (`ID`),
  UNIQUE KEY `ReachNDVIID_UNIQUE` (`ID`),
  KEY `Fk_est_water_temp_reach` (`ReachID`),
  CONSTRAINT `Fk_est_water_temp_reach` FOREIGN KEY (`ReachID`) REFERENCES `Reaches` (`ReachID`) ON UPDATE CASCADE
) ENGINE=InnoDB;

-- CREATE TABLE `ReachLandsatLTMDaily` (
--   `ID` int NOT NULL AUTO_INCREMENT,
--   `DayOfYear` int NOT NULL,
--   `WaterTemperature` float DEFAULT NULL COMMENT 'Mean water temperature',
--   `WaterTemperature5` float DEFAULT NULL COMMENT '5th percentile',
--   `WaterTemperature95` float DEFAULT NULL COMMENT '95th percentile',
--   `LandTemperature` float DEFAULT NULL COMMENT 'Mean',
--   `LandTemperature5` float DEFAULT NULL COMMENT '5th percentile',
--   `LandTemperature95` float DEFAULT NULL COMMENT '95th percentile land temp',
--   `ReachID` int NOT NULL,
--   PRIMARY KEY (`ID`),
--   UNIQUE KEY `ID_UNIQUE` (`ID`),
--   KEY `Fk_reachdlandsatltmdaily` (`ReachID`),
--   CONSTRAINT `Fk_reachdlandsatltmdaily` FOREIGN KEY (`ReachID`) REFERENCES `Reaches` (`ReachID`) ON DELETE RESTRICT ON UPDATE CASCADE
-- ) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `ReachLandsatLTMSemiMonthly` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `Month` int NOT NULL,
  `DayOfMonth` int NOT NULL,
  `WaterTemperature` float DEFAULT NULL COMMENT 'Mean water temperature',
  `WaterTemperature5` float DEFAULT NULL COMMENT '5th percentile',
  `WaterTemperature95` float DEFAULT NULL COMMENT '95th percentile',
  `LandTemperature` float DEFAULT NULL COMMENT 'Mean',
  `LandTemperature5` float DEFAULT NULL COMMENT '5th percentile',
  `LandTemperature95` float DEFAULT NULL COMMENT '95th percentile land temp',
  `ReachID` int NOT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `ID_UNIQUE` (`ID`),
  KEY `Fk_reachdlandsatltmsemimonthly` (`ReachID`),
  CONSTRAINT `Fk_reachdlandsatltmsemimonthly` FOREIGN KEY (`ReachID`) REFERENCES `Reaches` (`ReachID`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE `ReachLandsatLTMMonthly` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `Month` int NOT NULL,
  `WaterTemperature` float DEFAULT NULL COMMENT 'Mean water temperature',
  `WaterTemperature5` float DEFAULT NULL COMMENT '5th percentile',
  `WaterTemperature95` float DEFAULT NULL COMMENT '95th percentile',
  `LandTemperature` float DEFAULT NULL COMMENT 'Mean',
  `LandTemperature5` float DEFAULT NULL COMMENT '5th percentile',
  `LandTemperature95` float DEFAULT NULL COMMENT '95th percentile land temp',
  `ReachID` int NOT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `ID_UNIQUE` (`ID`),
  KEY `Fk_reachdlandsatltmmonthly` (`ReachID`),
  CONSTRAINT `Fk_reachdlandsatltmmonthly` FOREIGN KEY (`ReachID`) REFERENCES `Reaches` (`ReachID`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

SET FOREIGN_KEY_CHECKS = 1;