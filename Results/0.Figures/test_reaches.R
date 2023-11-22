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
  RFR2_1_test_set,
  RFR2_2_test_set,
  # ANN1_test_set,
  # ANN2_1_test_set,
  # ANN2_2_test_set
)
test_data$deviations = test_data$Estimated - test_data$InsituTemp

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
variations = c("1" = "No Regulation",
               "2" = "Regulation 1",
               "3" = "Regulation 2")

variation_labeller = function(variable, value) {
  return(variations[value])
}

# plot time series of estimated and insitu temperatures
p1 = ggplot(test_reach1, aes(x = Date, y = Estimated, color = type)) +
  geom_line() +
  # geom_point() +
  # geom_line(aes(y = InsituTemp), color = "black") +
  geom_point(aes(y = InsituTemp), color = "blue", size = 0.5) +
  facet_wrap( ~ factor(variation, labels = variations),  ncol = 1,) +
  scale_color_colorblind() +
  # scale_color_manual(values = c("#00AFBB", "#E7B800", "#FC4E07")) +
  labs(x = "Date", y = "Temperature (°C)",
       title = "Columbia River below Grand Coulee Dam near Barry, WA ") +
  theme_bw() +
  theme(
    plot.title = element_text(hjust = 0.5),
    # put legend at bottom
    legend.position = "bottom",
    legend.title = element_blank(),
  )



# plot time series of estimated and insitu temperatures
p2 = ggplot(test_reach2 %>% filter(variation != 2),
            aes(x = Date, y = Estimated, color = type)) +
  geom_line() +
  # geom_point() +
  # geom_line(aes(y = InsituTemp), color = "black") +
  geom_point(aes(y = InsituTemp), color = "blue", size = 0.5) +
  facet_wrap( ~ factor(variation, labels = c("1" = "No Regulation",
                                             # "2" = "Regulation 1",
                                             "3" = "Regulation 2")),  ncol = 1,) +
  scale_color_colorblind() +
  # scale_color_manual(values = c("#00AFBB", "#E7B800", "#FC4E07")) +
  labs(x = "Date", y = "Temperature (°C)",
       title = "Kootenai River below Libby Dam near Libby, MT") +
  theme_bw() +
  theme(
    plot.title = element_text(hjust = 0.5),
    # put legend at bottom
    legend.position = "bottom",
    legend.title = element_blank(),
  )

p2

# plot time series of estimated and insitu temperatures
p3 = ggplot(test_reach3, aes(x = Date, y = Estimated, color = type)) +
  geom_line() +
  # geom_point() +
  # geom_line(aes(y = InsituTemp), color = "black") +
  geom_point(aes(y = InsituTemp), color = "blue", size = 0.5) +
  facet_wrap( ~ factor(variation, labels = variations),  ncol = 1,) +
  scale_color_colorblind() +
  # scale_color_manual(values = c("#00AFBB", "#E7B800", "#FC4E07")) +
  labs(x = "Date", y = "Temperature (°C)",
       title = "Kootenai River below Libby Dam near Libby, MT") +
  theme_bw() +
  theme(
    plot.title = element_text(hjust = 0.5),
    # put legend at bottom
    legend.position = "bottom",
    legend.title = element_blank(),
  )

# plot time series of estimated and insitu temperatures
p4 = ggplot(test_reach4, aes(x = Date, y = Estimated, color = type)) +
  geom_line() +
  # geom_point() +
  # geom_line(aes(y = InsituTemp), color = "black") +
  geom_point(aes(y = InsituTemp), color = "blue", size = 0.5) +
  facet_wrap( ~ factor(variation, labels = variations),  ncol = 1,) +
  scale_color_colorblind() +
  # scale_color_manual(values = c("#00AFBB", "#E7B800", "#FC4E07")) +
  labs(x = "Date", y = "Temperature (°C)",
       title = "Okanogan River at Oroville, WA") +
  theme_bw() +
  theme(
    plot.title = element_text(hjust = 0.5),
    # put legend at bottom
    legend.position = "bottom",
    legend.title = element_blank(),
  )

ggsave(
  "Results/0.Figures/test_reach1.png",
  plot = p1,
  width = 6,
  height = 7
)
ggsave(
  "Results/0.Figures/test_reach2.png",
  plot = p2,
  width = 6,
  height = 7
)
ggsave(
  "Results/0.Figures/test_reach3.png",
  plot = p3,
  width = 6,
  height = 7
)
ggsave(
  "Results/0.Figures/test_reach4.png",
  plot = p4,
  width = 6,
  height = 7
)
