library(ggplot2)
library(ggthemes)
library(dplyr)
library(readr)

library(patchwork)

# Read in test data
LR1_test_set = read_csv("Results/2.WaterTempEst/1.LinearRegression/LR1_test_set.csv")
LR2_1_test_set = read_csv("Results/2.WaterTempEst/1.LinearRegression/LR2_1_test_set.csv")
LR2_2_test_set = read_csv("Results/2.WaterTempEst/1.LinearRegression/LR2_2_test_set.csv")

RFR1_test_set = read_csv("Results/2.WaterTempEst/2.RandomForestRegression/RFR1_test_set.csv")
RFR2_1_test_set = read_csv("Results/2.WaterTempEst/2.RandomForestRegression/RFR2_1_test_set.csv")
RFR2_2_test_set = read_csv("Results/2.WaterTempEst/2.RandomForestRegression/RFR2_2_test_set.csv")


ANN1_test_set = read_csv("Results/2.WaterTempEst/3.ANN/ANN1_test_set.csv")
ANN2_1_test_set = read_csv("Results/2.WaterTempEst/3.ANN/ANN2_1_test_set.csv")
ANN2_2_test_set = read_csv("Results/2.WaterTempEst/3.ANN/ANN2_2_test_set.csv")

# Read in evaluation data
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


test_data = rbind(
  LR1_test_set,
  LR2_1_test_set,
  LR2_2_test_set,
  RFR1_test_set,
  RFR2_1_test_set,
  RFR2_2_test_set,
  ANN1_test_set,
  ANN2_1_test_set,
  ANN2_2_test_set
)
test_data$deviations = test_data$Estimated - test_data$InsituTemp

test_data$width_class = ifelse(test_data$Width < 120, "Width < 120", "Width > 120")
test_data$dist_class = ifelse(test_data$rel_dist == 0, ">50 km of dam", "<50 km of dam")
test_data$Date = as.Date(test_data$Date, format = "%Y-%m-%d")
test_data$deviation = test_data$Estimated - test_data$InsituTemp
test_data$variation = as.factor(test_data$variation)

req_cols = colnames(LR1_eval)

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

eval_data_2 = rbind(RFR1_eval,
                    RFR2_1_eval,
                    RFR2_2_eval)
write_csv(eval_data_2, "Results/2.WaterTempEst/4.Evaluation/eval_data_2.csv")

# write_csv(test_data, "Results/2.WaterTempEst/test_data.csv")

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

# if type is LR, set performance column to good, ANN, set to better, RFR set to best
eval_data$performance = ifelse(
  eval_data$type == "Linear Regression",
  "Good",
  ifelse(eval_data$type == "Random Forest Regression", "Best", "Better")
)

aggregated_mean_deviation = eval_data %>%
  group_by(model, variation, type, performance) %>%
  summarise_at(vars(rmse, nse, r_sqaured, mse), c("mean"=mean, "sd"=sd), na.rm = TRUE)

aggregated_mean_deviation2 = eval_data_2 %>%
  filter
  group_by(model, variation, type) %>%
  summarise_at(vars(rmse_within_50, nse_within_50, r_sqaured_within_50, mse_within_50), c("mean"=mean, "sd"=sd), na.rm = TRUE)



p1 = ggplot(
  test_data %>% filter(type == "Random Forest Regression" &
                         variation == 1),
  aes(
    x = InsituTemp,
    y = Estimated,
    color = dist_class,
    shape = dist_class,
  )
) +
  geom_point(size = 2,) +
  geom_abline(intercept = 0,
              slope = 1,
              show_guide = FALSE) +
  geom_smooth(
    method = lm,
    se = FALSE,
    fullrange = TRUE,
    show.legend = TRUE,
    size = 0.75
  ) +
  scale_color_colorblind(# values = c("Width < 120" = "red", "Width > 120" = "blue"),
    labels = c("<50 km of dam", ">50 km of dam"),
    name = "Distance class:") +
  scale_shape_manual(
    values = c(">50 km of dam" = 17, "<50 km of dam" = 4),
    labels = c("<50 km of dam", ">50 km of dam"),
    name = "Distance class:"
  ) +
  theme_bw() +
  theme(legend.position = c(0.8, 0.2), ) +
  scale_x_continuous(name = "In-situ temperature (°C)",
                     breaks = seq(0, 30, 10),
                     limits = c(0, 30)) +
  scale_y_continuous(name = "Landsat temperature (°C)",
                     breaks = seq(0, 30, 10),
                     limits = c(0, 30)) +
  labs(title = "a)")

p1

p2 = ggplot(
  test_data %>% filter(type == "Random Forest Regression" &
                         variation == 1),
  aes(x = dist_class, y = deviation, fill = dist_class)
) +
  geom_boxplot()  + # add mean points
  stat_summary(
    fun = mean,
    geom = "point",
    shape = 23,
    size = 2,
    position = position_dodge(width = 0.75),
    color = "white"
  ) + # geom_text(data = aggregated_mean_deviation, aes(label = round(deviation, 2) , y = deviation + 1.75), color = "white") +
  scale_fill_colorblind() +
  theme_bw() +
  scale_x_discrete(name = "Width category",) +
  scale_y_continuous(name = "Deviation  (°C)") +
  theme(legend.position = "none") +
  labs(title = "c)")

p2

p3 = ggplot(
  test_data %>% filter(type == "Random Forest Regression" &
                         rel_dist == 0),
  aes(x = variation, y = deviation, fill = variation)
) +
  geom_boxplot()  + # add mean points
  stat_summary(
    fun = mean,
    geom = "point",
    shape = 23,
    size = 2,
    position = position_dodge(width = 0.75),
    color = "white"
  ) + # geom_text(data = aggregated_mean_deviation, aes(label = round(deviation, 2) , y = deviation + 1.75), color = "white") +
  scale_fill_colorblind() +
  theme_bw() +
  scale_x_discrete(name = "Variation",) +
  scale_y_continuous(name = "Deviation  (°C)") +
  theme(legend.position = "none") +
  labs(title = "c)")

p3

# compare the performance of the selected model without without reservoir dynamics
# within 50 km downstream of dams and beyond.
downstream_reach_assessment = read_csv("Results/2.WaterTempEst/donwstream_reach_assessment1.csv")
p4 = ggplot(downstream_reach_assessment,
            aes(
              y = distance_category,
              x = rmse,
              fill = factor(distance_category)
            )) +
  # geom_boxplot() + # add mean points
  geom_col(width = 0.6) +
  # geom_label(aes(label = performance), position = position_dodge(width = 0.9), size=2.75,vjust = +0.5, color="white", show.legend = FALSE) +
  geom_text(
    aes(label = paste0(round(rmse, 2))),
    position = position_dodge(width = 0.9),
    vjust = +0.5,
    hjust = +1.50,
    color = "white",
    size = 3,
    show.legend = FALSE
  ) +
  # expand_limits(x=c(0, 3.5)) +
  # stat_summary(fun=mean, geom="point", shape=23, size=2, position=position_dodge(width=0.75), color="white") +
  scale_fill_colorblind() +
  scale_y_discrete(labels = c(">50 km\nbelow dam", "<50 km\nbelow dam")) +
  theme_bw() +
  labs(x = expression("RMSE (" * degree * C * ")")) +
  # clear x axis label
  theme(
    axis.title.y = element_blank(),
    # axis.text.x=element_blank(),
    legend.title = element_blank(),
    # legend.text=element_text(size=12),
    legend.position = "none",
  )

p4

p5 = ggplot(downstream_reach_assessment,
            aes(
              y = distance_category,
              x = r2,
              fill = factor(distance_category)
            )) +
  # geom_boxplot() + # add mean points
  geom_col(width = 0.6) +
  # geom_label(aes(label = performance), position = position_dodge(width = 0.9), vjust = +0.5, size=2.75,color="white", show.legend = FALSE) +
  # geom_text(aes(label = paste0("(",round(r_sqaured_mean,2),")")), position = position_dodge(width = 0.9), vjust = +1.5, color="white", size=3, show.legend = FALSE) +
  geom_text(
    aes(label = paste0(round(r2, 2))),
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
  scale_y_discrete(labels = c(">50 km\nbelow dam", "<50 km\nbelow dam")) +
  # expand_limits(x=c(0, 1)) +
  theme_bw() +
  labs(x = expression(paste("R" ^ 2, )), y = "Model Type") +
  # clear x axis label
  theme(axis.title.y = element_blank(),
        # axis.text.x=element_blank(),
        # legend.title=element_text(face="bold", size=13),
        # legend.text=element_text(size=12),
        legend.position = "none",)

p5

p6 = ggplot(downstream_reach_assessment,
            aes(
              y = distance_category,
              x = nse,
              fill = factor(distance_category)
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
    aes(label = paste0(round(nse, 2))),
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
  scale_y_discrete(labels = c(">50 km\nbelow dam", "<50 km\nbelow dam")) +
  # expand_limits(x=c(0, 1)) +
  theme_bw() +
  labs(x = expression("NSE"), y = "Model Type") +
  # clear x axis label
  theme(axis.title.y = element_blank(),
        # axis.text.x=element_blank(),
        # legend.title=element_text(face="bold", size=13),
        # legend.text=element_text(size=12),
        legend.position = "none",)
p6

plot2 = p4 / p5 / p6

# plot2 + plot_annotation(caption = "<50 km: Reaches within 50 km downstream of a dam.\n>50 km: Reaches beyond 50 km downstream of a dam.")
# 
# ggsave(
#   "Results/0.Figures/downstream_reach_assessment.png",
#   plot = plot2,
#   width = 3.75,
#   height = 3.75,
#   units = "in"
# )

p7 = ggplot(
  eval_data_2 %>% filter(type == "Random Forest Regression" &
                         variation != 3),
  aes(
    x = as.factor(variation),
    y = rmse_within_50,
    fill = factor(variation)
  )
) +
  geom_boxplot() + # add mean points
  stat_summary(
    fun = mean,
    geom = "point",
    shape = 23,
    size = 2,
    position = position_dodge(width = 0.75),
    color = "white"
  )+
  geom_text(data =aggregated_mean_deviation2%>% filter(type == "Random Forest Regression" &
                                                  variation != 3), mapping=aes(x=, y=rmse_within_50_mean,label = paste0(round(rmse_within_50_mean,2))), position = position_dodge(width = 0.9), vjust = -1.5, hjust=0.5, color="white", size=3, show.legend = FALSE)+
  scale_fill_colorblind() +
  scale_x_discrete()+
  theme_bw() +
  labs(y = expression("RMSE ("*degree*C*")"), x="Variation", title="a)") +
  # clear x axis label
  theme(
    # axis.title.x = element_blank(),
    # axis.text.x = element_blank(),
    # legend.title = element_blank(),
    legend.text = element_text(size = 12),
    legend.position = "None",
  )
p7

p8 = ggplot(
  eval_data_2 %>% filter(type == "Random Forest Regression" &
                           variation != 3),
  aes(
    x = as.factor(variation),
    y = r_sqaured_within_50,
    fill = factor(variation)
  )
) +
  geom_boxplot() + # add mean points
  stat_summary(
    fun = mean,
    geom = "point",
    shape = 23,
    size = 2,
    position = position_dodge(width = 0.75),
    color = "white"
  )+
  geom_text(data =aggregated_mean_deviation2%>% filter(type == "Random Forest Regression" &
                                                         variation != 3), mapping=aes(x=, y=r_sqaured_within_50_mean,label = paste0(round(r_sqaured_within_50_mean,3))), position = position_dodge(width = 0.9), vjust = -1.5, hjust=0.5, color="white", size=3, show.legend = FALSE)+
  scale_fill_colorblind() +
  scale_x_discrete()+
  theme_bw() +
  labs(y = expression(paste("R"^2,)), x="Variation", title="b)") +
  # clear x axis label
  theme(
    # axis.title.x = element_blank(),
    # axis.text.x = element_blank(),
    # legend.title = element_blank(),
    legend.text = element_text(size = 12),
    legend.position = "None",
  )
p8

p9 = ggplot(
  eval_data_2 %>% filter(type == "Random Forest Regression" &
                           variation != 3),
  aes(
    x = as.factor(variation),
    y = nse_within_50,
    fill = factor(variation)
  )
) +
  geom_boxplot() + # add mean points
  stat_summary(
    fun = mean,
    geom = "point",
    shape = 23,
    size = 2,
    position = position_dodge(width = 0.75),
    color = "white"
  )+
  geom_text(data =aggregated_mean_deviation2%>% filter(type == "Random Forest Regression" &
                                                         variation != 3), mapping=aes(x=, y=nse_within_50_mean,label = paste0(round(nse_within_50_mean,3))), position = position_dodge(width = 0.9), vjust = -1.5, hjust=0.5, color="white", size=3, show.legend = FALSE)+
  scale_fill_colorblind() +
  scale_x_discrete()+
  theme_bw() +
  labs(y = "NSE", x="Variation", title="c)") +
  # clear x axis label
  theme(
    # axis.title.x = element_blank(),
    # axis.text.x = element_blank(),
    # legend.title = element_blank(),
    legend.text = element_text(size = 12),
    legend.position = "None",
  )
p9

plot3 = p7 + p8 + p9
plot3

ggsave(
  "Results/0.Figures/downstream_variation_assessment.png",
  plot = plot3,
  width = 5,
  height = 3.3,
  units = "in"
)
