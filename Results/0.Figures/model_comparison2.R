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

eval_data = rbind(
  LR1_eval,
  LR2_1_eval,
  LR2_2_eval,
  RFR1_eval[req_cols],
  RFR2_1_eval[req_cols],
  RFR2_2_eval[req_cols],
  ANN1_eval,
  ANN2_1_eval,
  ANN2_2_eval
)

# if type is LR, set performance column to good, ANN, set to better, RFR set to best
eval_data$performance = ifelse(
  eval_data$type == "Linear Regression",
  "Good",
  ifelse(eval_data$type == "Random Forest Regression", "Best", "Better")
)

aggregated_mean_deviation = eval_data %>%
  group_by(model, variation, type, performance) %>%
  filter(variation == 2) %>%
  summarise_at(vars(rmse, nse, r_sqaured, mse), c("mean"=mean, "sd"=sd), na.rm = TRUE)


p1 = ggplot(aggregated_mean_deviation,
            aes(y = type, x = rmse_mean, fill = factor(type))) +
  # geom_boxplot() + # add mean points
  geom_col(width = 0.6) +
  # geom_label(aes(label = performance), position = position_dodge(width = 0.9), size=2.75,vjust = +0.5, color="white", show.legend = FALSE) +
  geom_text(aes(label = paste0(round(rmse_mean,2))), position = position_dodge(width = 0.9), vjust = +0.5, hjust=+1.50, color="white", size=3, show.legend = FALSE) +
  # expand_limits(x=c(0, 3.5)) +
  # stat_summary(fun=mean, geom="point", shape=23, size=2, position=position_dodge(width=0.75), color="white") +
  scale_fill_colorblind() +
  theme_bw() +
  labs(x = expression("RMSE ("*degree*C*")"))+
  # clear x axis label
  theme(
    axis.title.y=element_blank(),
    # axis.text.x=element_blank(),
    legend.title=element_blank(),
    # legend.text=element_text(size=12),
    legend.position="none",
  )

p1

p2 = ggplot(aggregated_mean_deviation, aes(y=type, x=r_sqaured_mean, fill=factor(type) 
                                           # fill=factor(type)
)) +
  # geom_boxplot() + # add mean points
  geom_col(width = 0.6) +
  # geom_label(aes(label = performance), position = position_dodge(width = 0.9), vjust = +0.5, size=2.75,color="white", show.legend = FALSE) +
  # geom_text(aes(label = paste0("(",round(r_sqaured_mean,2),")")), position = position_dodge(width = 0.9), vjust = +1.5, color="white", size=3, show.legend = FALSE) +
  geom_text(aes(label = paste0(round(r_sqaured_mean,2))), position = position_dodge(width = 0.9), vjust = +0.5, hjust=+1.5, color="white", size=3, show.legend = FALSE) +
  # geom_errorbar(aes(ymin=r_sqaured_mean-r_sqaured_sd, ymax=r_sqaured_mean+r_sqaured_sd), width=.2, position=position_dodge(.9)) +
  # stat_summary(fun=mean, geom="point", shape=23, size=2, position=position_dodge(width=0.75), color="white") +
  scale_fill_colorblind('Model Type') +
  # expand_limits(x=c(0, 1)) +
  theme_bw() +
  labs(x = expression(paste("R"^2,)), y="Model Type")+
  # clear x axis label
  theme(
    axis.title.y=element_blank(),
    # axis.text.x=element_blank(),
    # legend.title=element_text(face="bold", size=13),
    # legend.text=element_text(size=12),
    legend.position="none",
  )

p2

p3 = ggplot(aggregated_mean_deviation, aes(y=type, x=nse_mean, fill=factor(type) 
                                           # fill=factor(type)
)) +
  geom_col(width = 0.6) +
  # geom_label(
  #   aes(label = performance),
  #   position = position_dodge(width = 0.9),
  #   vjust = +0.5,
  #   size = 2.75,
  #   color = "white",
  #   show.legend = FALSE
  # ) +
  geom_text(
    aes(label = paste0(round(nse_mean, 2))),
    position = position_dodge(width = 0.9),
    vjust = +0.5,
    hjust = +1.5,
    color = "white",
    size = 3,
    show.legend = FALSE
  ) +
  # geom_errorbar(aes(ymin=r_sqaured_mean-r_sqaured_sd, ymax=r_sqaured_mean+r_sqaured_sd), width=.2, position=position_dodge(.9)) +
  # stat_summary(fun=mean, geom="point", shape=23, size=2, position=position_dodge(width=0.75), color="white") +
  scale_fill_colorblind('Model Type') +
  # expand_limits(x=c(0, 1)) +
  theme_bw() +
  labs(x = expression("NSE"), y="Model Type")+
  # clear x axis label
  theme(
    axis.title.y=element_blank(),
    # axis.text.x=element_blank(),
    # legend.title=element_text(face="bold", size=13),
    # legend.text=element_text(size=12),
    legend.position="none",
  )
p3

plot = p1 / p2 / p3

plot
ggsave("Results/0.Figures/model_comparison2.png", plot=plot, width=5, height=4, units="in")

