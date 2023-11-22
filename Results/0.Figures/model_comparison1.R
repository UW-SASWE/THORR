library(ggplot2)
library(ggthemes)
library(dplyr)
library(readr)

library(patchwork)

# Read in data
LR1_eval = read_csv("Results/2.WaterTempEst/1.LinearRegression/LR1_eval.csv")
LR2_1_eval = read_csv("Results/2.WaterTempEst/1.LinearRegression/LR2_1_eval.csv")
LR2_2_eval = read_csv("Results/2.WaterTempEst/1.LinearRegression/LR2_2_eval.csv")

RFR1_eval = read_csv("Results/2.WaterTempEst/2.RandomForestRegression/RFR1_eval.csv")
RFR2_1_eval = read_csv("Results/2.WaterTempEst/2.RandomForestRegression/RFR2_1_eval.csv")
RFR2_2_eval = read_csv("Results/2.WaterTempEst/2.RandomForestRegression/RFR2_2_eval.csv")

ANN1_eval = read_csv("Results/2.WaterTempEst/3.ANN/ANN1_eval.csv")
ANN2_1_eval = read_csv("Results/2.WaterTempEst/3.ANN/ANN2_1_eval.csv")
ANN2_2_eval = read_csv("Results/2.WaterTempEst/3.ANN/ANN2_2_eval.csv")

# Combine data
LR1_eval$variation = 1
LR1_eval$type = "Linear Regression"
LR2_1_eval$variation = 2
LR2_1_eval$type = "Linear Regression"
LR2_2_eval$variation = 3
LR2_2_eval$type = "Linear Regression"

RFR1_eval$variation = 1
RFR1_eval$type = "Random Forest Regression"
RFR2_1_eval$variation = 2
RFR2_1_eval$type = "Random Forest Regression"
RFR2_2_eval$variation = 3
RFR2_2_eval$type = "Random Forest Regression"

ANN1_eval$variation = 1
ANN1_eval$type = "Artificial Neural Network"
ANN2_1_eval$variation = 2
ANN2_1_eval$type = "Artificial Neural Network"
ANN2_2_eval$variation = 3
ANN2_2_eval$type = "Artificial Neural Network"

req_cols = colnames(LR1_eval)

req_cols
rfr1 = data.frame(
  model = RFR1_eval$model,
  fold = RFR1_eval$fold,
  rmse = RFR1_eval$rmse_within_50,
  nse = RFR1_eval$nse,
  r_sqaured = RFR1_eval$r_sqaured_within_50,
  mse = RFR1_eval$mse,
  variation = RFR1_eval$variation,
  type = "Random Forest Regression"
)

eval_data = rbind(
  # LR1_eval,
  # LR2_1_eval,
  # LR2_2_eval,
  # RFR1_eval[req_cols],
  RFR2_1_eval[req_cols],
  # RFR2_2_eval[req_cols],
  # ANN1_eval,
  # ANN2_1_eval,
  # ANN2_2_eval
)
# Plot
variations = list("1" = "No Regulation",
                  "2" = "Regulation 1",
                  "3" = "Regulation 2")

variation_labeller = function(variable, value) {
  return(variations[value])
}

p1 = ggplot(eval_data, aes(
  x = as.factor(variation),
  y = rmse,
  fill = factor(variation)
)) +
  geom_boxplot() + # add mean points
  stat_summary(
    fun = mean,
    geom = "point",
    shape = 23,
    size = 2,
    position = position_dodge(width = 0.75),
    color = "white"
  ) +
  scale_fill_colorblind() +
  scale_x_discrete()+
  theme_bw() +
  labs(y = expression("RMSE (" *  ~ degree * C * ")")) +
  # clear x axis label
  theme(
    axis.title.x = element_blank(),
    # axis.text.x = element_blank(),
    legend.title = element_blank(),
    legend.text = element_text(size = 12),
    legend.position = "None",
  )
p1

p2 = ggplot(eval_data, aes(
  x = as.factor(variation),
  y = nse,
  fill = factor(variation)
)) +
  geom_boxplot() + # add mean points
  stat_summary(
    fun = mean,
    geom = "point",
    shape = 23,
    size = 2,
    position = position_dodge(width = 0.75),
    color = "white"
  ) +
  scale_fill_colorblind() +
  scale_x_discrete()+
  theme_bw() +
  labs(y = "NSE") +
  # clear x axis label
  theme(
    axis.title.x = element_blank(),
    # axis.text.x = element_blank(),
    legend.title = element_blank(),
    legend.text = element_text(size = 12),
    legend.position = "None",
  )

p2
p3 = ggplot(eval_data, aes(
  x = type,
  y = r_sqaured,
  fill = factor(variation)
)) +
  geom_boxplot() + # add mean points
  stat_summary(
    fun = mean,
    geom = "point",
    shape = 23,
    size = 2,
    position = position_dodge(width = 0.75),
    color = "white"
  ) +
  scale_fill_colorblind() +
  scale_x_discrete()+
  theme_bw() +
  labs(y = "NSE") +
  # clear x axis label
  theme(
    axis.title.x = element_blank(),
    # axis.text.x = element_blank(),
    legend.title = element_blank(),
    legend.text = element_text(size = 12),
    legend.position = "None",
  )

p1 +
  p2 +
  p3


ggsave("Results/0.Figures/model_comparison1.png",
       width = 5,
       height = 7)
