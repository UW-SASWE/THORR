library(RMariaDB)
library(ggplot2)
library(dplyr)
library(patchwork)

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
# dbListTables(hydrothermal_db)

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
ORDER BY RAND();
"
hydrothermal_data = dbGetQuery(hydrothermal_db, query)
hydrothermal_data$width_class = ifelse(hydrothermal_data$Width < 120, "Width < 120", "Width > 120")
hydrothermal_data$shape = ifelse(hydrothermal_data$Width < 120, 10, 25)

hydrothermal_data$width_class = factor(hydrothermal_data$width_class,
                                       levels = c("Width < 120", "Width > 120"))
hydrothermal_data$deviation = hydrothermal_data$WaterTemp - hydrothermal_data$InsituTemp

p1 = ggplot(
  hydrothermal_data,
  aes(
    x = InsituTemp,
    y = WaterTemp,
    color = width_class,
    shape = width_class,
  )
) +
  geom_point(size = 2, ) +
  geom_abline(intercept = 0,
              slope = 1,
              linetype = "dashed",
              show.legend = FALSE) +
  geom_smooth(
    method = lm,
    se = FALSE,
    fullrange = TRUE,
    show.legend = TRUE,
    size = 0.75
  ) +
  scale_color_colorblind(# values = c("Width < 120" = "red", "Width > 120" = "blue"),
    labels = c("< 120 m", "> 120 m"),
    name = "Reach width:") +
  scale_shape_manual(
    values = c("Width < 120" = 17, "Width > 120" = 4),
    labels = c("< 120 m", "> 120 m"),
    name = "Reach width:"
  ) +
  theme_bw() +
  theme(legend.position = c(0.8, 0.2),) +
  scale_x_continuous(name = "In-situ temperature (°C)",
                     breaks = seq(0, 55, 10),
                     limits = c(0, 55)) +
  scale_y_continuous(name = "Landsat temperature (°C)",
                     breaks = seq(0, 55, 10),
                     limits = c(0, 55)) +
  labs(title = "a)")

# p1
deviation_trend =  hydrothermal_data %>%
  mutate(points_bin = cut(Width, breaks = c(seq(0, 3000, 120)))) %>%
  group_by(points_bin) %>%
  summarise_at(vars(deviation), mean, na.rm = TRUE)

deviation_trend$midpoints = c(seq(0 + 120 / 2, 3000 - 120 / 2, 120))[1:length(deviation_trend$points_bin)]
deviation_trend$width_class = ifelse(deviation_trend$midpoints < 120, "Width < 120", "Width > 120")

# plot the means of the deviations
p2 = ggplot(
  deviation_trend,
  aes(
    x = midpoints,
    y = deviation,
    color = width_class,
    shape = width_class,
    size = width_class,
    # size=2
  )
) +
  geom_point() +
  geom_smooth(
    method = lm,
    se = FALSE,
    fullrange = TRUE,
    show.legend = TRUE,
    size = 0.75
  ) +
  theme_bw() +
  theme(legend.position = c(0.8, 0.8),) +
  scale_color_colorblind(# values = c("Width < 120" = "red", "Width > 120" = "blue"),
    labels = c("< 120 m", "> 120 m"),
    name = "Reach width") +
  scale_shape_manual(
    values = c("Width < 120" = 17, "Width > 120" = 4),
    labels = c("< 120 m", "> 120 m"),
    name = "Reach width"
  ) +
  scale_size_manual(
    values = c(2, 2),
    labels = c("< 120 m", "> 120 m"),
    name = "Reach width"
  ) +
  scale_x_continuous(
    name = "Reach width (m)",
    breaks = seq(0, 1920, 240),
    limits = c(0, 1920)
  ) +
  scale_y_continuous(name = "Mean deviation (°C)") +
  labs(title = "b)")


# density plot of deviations
p3 = ggplot(hydrothermal_data,
            aes(x = deviation,
                color = width_class,)) +
  # geom_density() +
  stat_density(geom = "line", position = "identity") +
  theme_bw() +
  theme(legend.position = c(0.8, 0.8),) +
  scale_color_colorblind(# values = c("Width < 120" = "red", "Width > 120" = "blue"),
    labels = c("< 120 m", "> 120 m"),
    name = "Reach width") +
  scale_x_continuous(name = "Landsat deviation from In-situ (°C)", ) +
  scale_y_continuous(name = "Density") +
  labs(title = "c)")

aggregated_mean_deviation = hydrothermal_data %>%
  group_by(width_class) %>%
  summarise_at(vars(deviation), mean, na.rm = TRUE)

p4 = ggplot(hydrothermal_data,
            aes(x = width_class, y = deviation, fill = width_class)) +
  geom_boxplot()  + # add mean points
  stat_summary(
    fun = mean,
    geom = "point",
    shape = 23,
    size = 2,
    position = position_dodge(width = 0.75),
    color = "white"
  ) + geom_text(data = aggregated_mean_deviation, aes(label = round(deviation, 2) , y = deviation + 1.75), color = "white") +
  scale_fill_colorblind() +
  theme_bw() +
  scale_x_discrete(name = "Width category", ) +
  scale_y_continuous(name = "Deviation  (°C)") +
  theme(legend.position = "none") +
  labs(title = "c)")

p4



p1 + p2 + p4
# p1 /
# (p2 + p3)

# (p1 | (p2/p3))

# + plot_annotation(title = "Comparison of Landsat and in-situ water temperatures",
#                   caption = "Figure 1. Comparison of Landsat and in-situ water temperatures. a) Scatterplot of Landsat and in-situ water temperatures. The black line is the 1:1 line. b) Mean deviation of Landsat and in-situ water temperatures by reach width. c) Density plot of deviations of Landsat and in-situ water temperatures by reach width.") +
#   theme(plot.title = element_text(hjust = 0.5),
#         plot.caption = element_text(hjust = 0.2))

ggsave("Results/0.Figures/landsat_v_insitu.png",
       width = 12,
       height = 4.5)

