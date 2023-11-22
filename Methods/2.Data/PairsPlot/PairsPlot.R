library(RMariaDB)
library(ggplot2)
library(dplyr)
library(patchwork)
library(GGally)


rmariadb.settingsfile = "Methods/database_management/mysql_config.ini"
rmariadb.db = "hydrothermal_history"
# ~/Library/CloudStorage/OneDrive-UW/01-Research/01-Hydrothermal History/Methods/database_management/mysql_config.ini

# hydrothermal_db = dbConnect(
#   RMariaDB::MariaDB(),
#   groups = "rs-dbi",
#   default.file = "~/Library/CloudStorage/OneDrive-UW/01-Research/01-Hydrothermal History/.env/.my.cnf"
# )

# Fix this
hydrothermal_db = dbConnect(
  RMariaDB::MariaDB(),
  user = 'root',
  password = "Sunshine@1993",
  dbname = 'hydrothermal_history',
  host = 'localhost'
)


query = "
SELECT
    STR_TO_DATE(CONCAT(Year,
                    '-',
                    LPAD(Month, 2, '00'),
                    '-',
                    LPAD(DayOfMonth, 2, '00')),
            '%Y-%m-%d') AS Date,
    Month,
    DayOfMonth,
    ROUND(WaterTemp, 2) as WaterTemp,
    ROUND(LandTemp, 2) as LandTemp,
    ROUND(NDVI, 2) as NDVI,
    ClimateClass,
    --     ROUND(((watertemp - WaterTemperature) / WaterTemperature),
    --             2) AS PercentDeviation,
    --     ROUND((watertemp - WaterTemperature), 2) AS Deviation,
    Width,
    ReachID,
    ROUND(InsituTemp, 2) AS InsituTemp
FROM
    (SELECT
        1 AS DayOfMonth,
            MONTH(ReachLandsatWaterTemp.date) AS Month,
            YEAR(ReachLandsatWaterTemp.date) AS Year,
            AVG(ReachLandsatWaterTemp.Value) AS WaterTemp,
            AVG(ReachLandsatLandTemp.Value) AS LandTemp,
            AVG(ReachNDVI.Value) AS NDVI,
            IFNULL(Reaches.WidthMean, 30) AS Width,
            Reaches.ClimateClass AS ClimateClass,
            ReachLandsatWaterTemp.ReachID AS ReachID
    FROM
        ReachLandsatWaterTemp
    INNER JOIN ReachLandsatLandTemp USING (date , ReachID)
    INNER JOIN ReachNDVI USING (date , ReachID)
    INNER JOIN Reaches USING (ReachID)
    WHERE
        ReachLandsatWaterTemp.Value > 0
    --    Reaches.Name NOT IN {tuple(reaches_of_interest)}
    --        AND ReachLandsatWaterTemp.Value > 0
    GROUP BY DayOfMonth , Month , Year , ClimateClass , ReachID , Width) AS T
    --         INNER JOIN
    --     ReachLandsatLTMSemiMonthly USING (DayOfMonth , Month , ReachID)
        LEFT JOIN
    (SELECT
        1 AS DayOfMonth,
            MONTH(ReachInsituWaterTemp.date) AS Month,
            YEAR(ReachInsituWaterTemp.date) AS Year,
            AVG(ReachInsituWaterTemp.Value) AS InsituTemp,
            ReachInsituWaterTemp.ReachID AS ReachID
    FROM
        ReachInsituWaterTemp
    INNER JOIN Reaches USING (ReachID)
    WHERE
        ReachInsituWaterTemp.Value > 0
    GROUP BY DayOfMonth , Month , Year , ReachID) AS I USING (DayOfMonth , Month , Year , ReachID)
"
hydrothermal_data = dbGetQuery(hydrothermal_db, query)
hydrothermal_data$width_class = ifelse(hydrothermal_data$Width < 120, "Width < 120", "Width > 120")
hydrothermal_data$shape = ifelse(hydrothermal_data$Width < 120, 10, 25)

hydrothermal_data$width_class = factor(hydrothermal_data$width_class,
                                       levels = c("Width < 120", "Width > 120"))
hydrothermal_data$deviation = hydrothermal_data$WaterTemp - hydrothermal_data$InsituTemp


ggpairs(hydrothermal_data, columns = c(4,5,6,7,10,11)) +
  theme_bw()
  # theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
  # labs(title = "Hydrothermal Data Pairs Plot",
  #      subtitle = "Water Temperature, Land Temperature, NDVI, and Width",
  #      caption = "Data from 2013-2019",
  #      x = "Water Temperature (C)",
  #      y = "Land Temperature (C)",
  #      color = "Width Class",
  #      shape = "Width Class",
  #      fill = "Width Class")
