library(ggplot2)
library(ggthemes)
library(dplyr)
library(readr)

library(patchwork)

# Read in data
LR1_test_set = read_csv("Results/2.WaterTempEst/1.LinearRegression/LR1_test_set.csv")
LR2_1_test_set = read_csv("Results/2.WaterTempEst/1.LinearRegression/LR2_1_test_set.csv")
LR2_2_test_set = read_csv("Results/2.WaterTempEst/1.LinearRegression/LR2_2_test_set.csv")

RFR1_test_set = read_csv("Results/2.WaterTempEst/2.RandomForestRegression/RFR1_test_set.csv")
RFR2_1_test_set = read_csv("Results/2.WaterTempEst/2.RandomForestRegression/RFR2_1_test_set.csv")
RFR2_2_test_set = read_csv("Results/2.WaterTempEst/2.RandomForestRegression/RFR2_2_test_set.csv")


ANN1_test_set = read_csv("Results/2.WaterTempEst/3.ANN/ANN1_test_set.csv")
ANN2_1_test_set = read_csv("Results/2.WaterTempEst/3.ANN/ANN2_1_test_set.csv")
ANN2_2_test_set = read_csv("Results/2.WaterTempEst/3.ANN/ANN2_2_test_set.csv")

# Combine data
LR1_test_set$variation = 1
LR1_test_set$type = "Linear Regression"
LR2_1_test_set$variation = 2
LR2_1_test_set$type = "Linear Regression"
LR2_2_test_set$variation = 3
LR2_2_test_set$type = "Linear Regression"

RFR1_test_set$variation = 1
RFR1_test_set$type = "Random Forest Regression"
RFR2_1_test_set$variation = 2
RFR2_1_test_set$type = "Random Forest Regression"
RFR2_2_test_set$variation = 3
RFR2_2_test_set$type = "Random Forest Regression"

ANN1_test_set$variation = 1
ANN1_test_set$type = "Artificial Neural Network"
ANN2_1_test_set$variation = 2
ANN2_1_test_set$type = "Artificial Neural Network"
ANN2_2_test_set$variation = 3
ANN2_2_test_set$type = "Artificial Neural Network"


colnames(LR1_test_set)[27] = "Estimated"
colnames(LR2_1_test_set)[27] = "Estimated"
colnames(LR2_2_test_set)[27] = "Estimated"

colnames(RFR1_test_set)[27] = "Estimated"
colnames(RFR2_1_test_set)[27] = "Estimated"
colnames(RFR2_2_test_set)[27] = "Estimated"

colnames(ANN1_test_set)[27] = "Estimated"
colnames(ANN2_1_test_set)[27] = "Estimated"
colnames(ANN2_2_test_set)[27] = "Estimated"


test_data = rbind(
  # LR1_test_set,
  # LR2_1_test_set,
  # LR2_2_test_set,
  RFR1_test_set,
  RFR2_1_test_set
  # RFR2_2_test_set,
  # ANN1_test_set,
  # ANN2_1_test_set,
  # ANN2_2_test_set
)
test_data$deviations = test_data$Estimated - test_data$InsituTemp
# filter test data for dates greater than 2020-01-01
# test_data = test_data %>% filter(Date > "2020-01-01")

test_reaches = c(
  "Columbia_River_59",
  "Willamette_River_15",
  "Kootenay_River_47",
  "Okanogan_River_29"
)

test_reach1 = test_data %>% filter(ReachName == test_reaches[1]) %>% arrange(type, Date)
test_reach2 = test_data %>% filter(ReachName == test_reaches[2]) %>% arrange(type, Date)
test_reach3 = test_data %>% filter(ReachName == test_reaches[3]) %>% arrange(type, Date)
test_reach4 = test_data %>% filter(ReachName == test_reaches[4]) %>% arrange(type, Date)

# Plot
variations_labels = c("1" = "Variation 1",
               "2" = "Variation 2")

variation_labeller = function(variable, value) {
  return(variations[value])
}

# plot for test reach 1
timeseries1 = ggplot(test_reach1 %>% filter(Date > "2020-01-01"), aes(x = Date, y = Estimated, color = as.factor(variation))) +
  geom_line() +
  # geom_point() +
  # geom_line(aes(y = InsituTemp), color = "black") +
  geom_point(aes(y = InsituTemp), color = "blue", size = 0.5) +
  scale_color_colorblind(labels=variations_labels) +
  # scale_color_manual(values = c("#00AFBB", "#E7B800", "#FC4E07")) +
  labs(x = "Date", y = "Temperature (°C)",
       title = "a) Test Reach 1 - Below Grand Coulee Dam, WA") +
  theme_bw() +
  theme(
    # plot.title = element_text(hjust = 0.5),
    # plot.title = element_blank(),
    # put legend at bottom
    legend.position = "bottom",
    legend.title = element_blank(),
  )

timeseries1

# 1-1 plot for test reach 1 variation 1
scatter1_1 = ggplot(test_reach1 %>% filter(variation==1), aes(x = InsituTemp, y = Estimated, color = as.factor(variation))) +
  # geom_line() +
  geom_point() +
  geom_abline(intercept = 0, slope = 1, color = "black") +
  scale_color_colorblind(labels=variations_labels) +
  # scale_color_manual(values = c("#00AFBB", "#E7B800", "#FC4E07")) +
  labs(x = "Insitu Tempearture (°C)", y = "Estimated\nTemperature (°C)",
       title = "Variation 1") +
  theme_bw() +
  theme(
    # plot.title = element_text(hjust = 0.5),
    plot.title = element_blank(),
    # put legend at bottom
    legend.position = "none",
    legend.title = element_blank(),
  )

scatter1_1

# 1-1 plot for test reach 1 variation 2
scatter1_2 = ggplot(test_reach1 %>% filter(variation==2), aes(x = InsituTemp, y = Estimated, color = as.factor(variation))) +
  # geom_line() +
  geom_point() +
  geom_abline(intercept = 0, slope = 1, color = "black") +
  scale_color_colorblind(labels=variations_labels) +
  # scale_color_manual(values = c("#00AFBB", "#E7B800", "#FC4E07")) +
  labs(x = "Insitu Tempearture (°C)", y = "Estimated\nTemperature (°C)",
       title = "Variation 1") +
  theme_bw() +
  theme(
    # plot.title = element_text(hjust = 0.5),
    plot.title = element_blank(),
    # put legend at bottom
    legend.position = "none",
    legend.title = element_blank(),
  )

scatter1_2

# plot for test reach 2
timeseries2 = ggplot(test_reach2 %>% filter(Date > "2020-01-01"), aes(x = Date, y = Estimated, color = as.factor(variation))) +
  geom_line() +
  # geom_point() +
  # geom_line(aes(y = InsituTemp), color = "black") +
  geom_point(aes(y = InsituTemp), color = "blue", size = 0.5) +
  scale_color_colorblind(labels=variations_labels) +
  # scale_color_manual(values = c("#00AFBB", "#E7B800", "#FC4E07")) +
  labs(x = "Date", y = "Temperature (°C)",
       title = "d) Test Reach 4 - At Albany, OR") +
  theme_bw() +
  theme(
    # plot.title = element_text(hjust = 0.5),
    # plot.title = element_blank(),
    # put legend at bottom
    axis.title.y=element_blank(),
    legend.position = "none",
    legend.title = element_blank(),
  )

timeseries2

# 1-1 plot for test reach 2 variation 1
scatter2_1 = ggplot(test_reach1 %>% filter(variation==1), aes(x = InsituTemp, y = Estimated, color = as.factor(variation))) +
  # geom_line() +
  geom_point() +
  geom_abline(intercept = 0, slope = 1, color = "black") +
  scale_color_colorblind(labels=variations_labels) +
  # scale_color_manual(values = c("#00AFBB", "#E7B800", "#FC4E07")) +
  labs(x = "Insitu Tempearture (°C)", y = "Estimated\nTemperature (°C)",
       title = "Variation 1") +
  theme_bw() +
  theme(
    # plot.title = element_text(hjust = 0.5),
    plot.title = element_blank(),
    # put legend at bottom
    legend.position = "none",
    legend.title = element_blank(),
  )

scatter2_1

# plot for test reach 3
timeseries3 = ggplot(test_reach3 %>% filter(Date > "2020-01-01"), aes(x = Date, y = Estimated, color = as.factor(variation))) +
  geom_line() +
  # geom_point() +
  # geom_line(aes(y = InsituTemp), color = "black") +
  geom_point(aes(y = InsituTemp), color = "blue", size = 0.5) +
  scale_color_colorblind(labels=variations_labels) +
  # scale_color_manual(values = c("#00AFBB", "#E7B800", "#FC4E07")) +
  labs(x = "Date", y = "Temperature (°C)",
       title = "b) Test Reach 2 - Below Libby Dam, MT") +
  theme_bw() +
  theme(
    # plot.title = element_text(hjust = 0.5),
    # plot.title = element_blank(),
    # put legend at bottom
    axis.title.y=element_blank(),
    legend.position = "none",
    legend.title = element_blank(),
  )

timeseries3

# 1-1 plot for test reach 3 variation 1
scatter3_1 = ggplot(test_reach3 %>% filter(variation==1), aes(x = InsituTemp, y = Estimated, color = as.factor(variation))) +
  # geom_line() +
  geom_point() +
  geom_abline(intercept = 0, slope = 1, color = "black") +
  scale_color_colorblind(labels=variations_labels) +
  # scale_color_manual(values = c("#00AFBB", "#E7B800", "#FC4E07")) +
  labs(x = "Insitu Tempearture (°C)", y = "Estimated\nTemperature (°C)",
       title = "Variation 1") +
  theme_bw() +
  theme(
    # plot.title = element_text(hjust = 0.5),
    plot.title = element_blank(),
    # put legend at bottom
    legend.position = "none",
    legend.title = element_blank(),
  )

scatter3_1

# 1-1 plot for test reach 3 variation 2
scatter3_2 = ggplot(test_reach3 %>% filter(variation==2), aes(x = InsituTemp, y = Estimated, color = as.factor(variation))) +
  # geom_line() +
  geom_point() +
  geom_abline(intercept = 0, slope = 1, color = "black") +
  scale_color_colorblind(labels=variations_labels) +
  # scale_color_manual(values = c("#00AFBB", "#E7B800", "#FC4E07")) +
  labs(x = "Insitu Tempearture (°C)", y = "Estimated\nTemperature (°C)",
       title = "Variation 1") +
  theme_bw() +
  theme(
    # plot.title = element_text(hjust = 0.5),
    plot.title = element_blank(),
    # put legend at bottom
    legend.position = "none",
    legend.title = element_blank(),
  )

scatter3_2

# plot for test reach 3
timeseries4 = ggplot(test_reach4 %>% filter(Date > "2020-01-01"), aes(x = Date, y = Estimated, color = as.factor(variation))) +
  geom_line() +
  # geom_point() +
  # geom_line(aes(y = InsituTemp), color = "black") +
  geom_point(aes(y = InsituTemp), color = "blue", size = 0.5) +
  scale_color_colorblind(labels=variations_labels) +
  # scale_color_manual(values = c("#00AFBB", "#E7B800", "#FC4E07")) +
  labs(x = "Date", y = "Temperature (°C)",
       title = "c) Test Reach 3 - Below Osoyos Lake, WA") +
  theme_bw() +
  theme(
    # plot.title = element_text(hjust = 0.5),
    # plot.title = element_blank(),
    # put legend at bottom
    # axis.title.y=element_blank(),
    legend.position = "bottom",
    legend.title = element_blank(),
  )

timeseries4

# 1-1 plot for test reach 3 variation 1
scatter4_1 = ggplot(test_reach4 %>% filter(variation==1), aes(x = InsituTemp, y = Estimated, color = as.factor(variation))) +
  # geom_line() +
  geom_point() +
  geom_abline(intercept = 0, slope = 1, color = "black") +
  scale_color_colorblind(labels = c()) +
  # scale_color_manual(values = c("#00AFBB", "#E7B800", "#FC4E07")) +
  labs(x = "Insitu Tempearture (°C)", y = "Estimated\nTemperature (°C)",
       title = "Variation 1") +
  theme_bw() +
  theme(
    # plot.title = element_text(hjust = 0.5),
    plot.title = element_blank(),
    # put legend at bottom
    legend.position = "none",
    legend.title = element_blank(),
  )

scatter4_1

# 1-1 plot for test reach 3 variation 2
scatter4_2 = ggplot(test_reach4 %>% filter(variation==2), aes(x = InsituTemp, y = Estimated, color = as.factor(variation))) +
  # geom_line() +
  geom_point() +
  geom_smooth(method = "lm", se = FALSE) +
  geom_abline(intercept = 0, slope = 1, color = "black") +
  scale_color_colorblind(labels=variations_labels) +
  # scale_color_manual(values = c("#00AFBB", "#E7B800", "#FC4E07")) +
  labs(x = "Insitu Tempearture (°C)", y = "Estimated\nTemperature (°C)",
       title = "Variation 2") +
  theme_bw() +
  theme(
    # plot.title = element_text(hjust = 0.5),
    plot.title = element_blank(),
    # put legend at bottom
    legend.position = "bottom",
    legend.title = element_blank(),
  )

scatter4_2

plots = timeseries1 + scatter1_1 + scatter1_2 + timeseries2 + scatter2_1 + plot_spacer() + timeseries3 + scatter3_1 + scatter3_2 + timeseries4 + scatter4_1 + scatter4_2 +
  plot_layout(widths=c(2,1,1))
timeseries_plots = (timeseries1 + timeseries3 )/( timeseries4 + timeseries2)/guide_area() +
  plot_layout(guides = "collect", heights = c(1, 1, 0.1))
  # plot_layout(widths=c(2,1,1))
timeseries_plots

ggsave("Results/0.Figures/test_reaches_timeseries.png", plot=timeseries_plots, width=10, height=5, units="in", dpi=300)

