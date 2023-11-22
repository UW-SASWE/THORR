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


test_data = rbind(LR1_test_set, LR2_1_test_set, LR2_2_test_set, RFR1_test_set, RFR2_1_test_set, RFR2_2_test_set, ANN1_test_set, ANN2_1_test_set, ANN2_2_test_set)
test_data$deviations = test_data$Estimated - test_data$InsituTemp

# Plot
variations = list(
  "1" = "No Regulation",
  "2" = "Regulation 1",
  "3" = "Regulation 2"
)

variation_labeller = function(variable, value) {
  return(variations[value])
}

# select from test data where rel_dist is not 0
dam_test_data = test_data %>%
  filter(rel_dist != 0)


p1 = ggplot(dam_test_data, aes(x=type, y=deviations, fill=factor(variation))) +
  geom_boxplot() + # add mean points
  stat_summary(fun=mean, geom="point", shape=23, size=2, position=position_dodge(width=0.75), color="white") +
  scale_fill_colorblind(labels=c("No Regulation", "Regulation 1", "Regulation 2")) +
  theme_bw() +
  labs(y = expression("Deviation ("*~degree*C*")"), title = "a) Reaches within 50-km of a dam")+
  # clear x axis label
  theme(axis.title.x=element_blank(),
        # axis.text.x=element_blank(),
        legend.title=element_blank(),
        legend.text=element_text(size=12),
        legend.position="none",
  )

# p1

p2 = ggplot(test_data, aes(x=type, y=deviations, fill=factor(variation))) +
  geom_boxplot() + # add mean points
  stat_summary(fun=mean, geom="point", shape=23, size=2, position=position_dodge(width=0.75), color="white") +
  scale_fill_colorblind(labels=c("No Regulation", "Regulation 1", "Regulation 2")) +
  theme_bw() +
  labs(y = expression("Deviation ("*~degree*C*")"), title="b) all reaches in the test set")+
  # clear x axis label
  theme(axis.title.x=element_blank(),
        # axis.text.x=element_blank(),
        legend.title=element_blank(),
        legend.text=element_text(size=12),
        legend.position="bottom",
  )
# p2


p1 /
  p2 


# plot insitu vs estimated for grouped by type
p3 = ggplot(dam_test_data, aes(x=InsituTemp, y=Estimated, color=factor(variation))) +
  geom_point() +
  geom_abline(intercept = 0, slope = 1, color = "black", linetype = "dashed") +
  scale_color_colorblind(labels=c("No Regulation", "Regulation 1", "Regulation 2")) +
  library(readr)
  labs(x = expression("In-situ Temperature ("*~degree*C*")"),
       y = expression("Estimated Temperature ("*~degree*C*")"))+
  # clear x axis label
  theme(
    # axis.title.x=element_blank(),
        # axis.text.x=element_blank(),
        legend.title=element_blank(),
        legend.text=element_text(size=12),
        legend.position="top",
  )

p3

plot = p1 / p2

ggsave("Results/0.Figures/dam_reaches1.png", plot,
       width = 5,
       height = 7)
