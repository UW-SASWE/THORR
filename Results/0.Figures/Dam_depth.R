library(ggplot2)
library(ggthemes)
library(dplyr)
library(readr)

library(patchwork)


# compare the performance of the selected model without without reservoir dynamics
# within 50 km downstream of dams and beyond.
dam_depth_assessment = read_csv("Results/2.WaterTempEst/4.Evaluation/dam_depth_v_performance.csv")
p4 = ggplot(dam_depth_assessment,
            aes(
              y = class,
              x = RMSE,
              fill = factor(class)
            )) +
  # geom_boxplot() + # add mean points
  geom_col(width = 0.6) +
  # geom_label(aes(label = performance), position = position_dodge(width = 0.9), size=2.75,vjust = +0.5, color="white", show.legend = FALSE) +
  geom_text(
    aes(label = paste0(round(RMSE, 2))),
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
  scale_y_discrete(labels = c("Deep (> 10m)", "Shallow (<10 m)")) +
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

p5 = ggplot(dam_depth_assessment,
            aes(
              y = class,
              x = R2,
              fill = factor(class)
            )) +
  # geom_boxplot() + # add mean points
  geom_col(width = 0.6) +
  # geom_label(aes(label = performance), position = position_dodge(width = 0.9), vjust = +0.5, size=2.75,color="white", show.legend = FALSE) +
  # geom_text(aes(label = paste0("(",round(r_sqaured_mean,2),")")), position = position_dodge(width = 0.9), vjust = +1.5, color="white", size=3, show.legend = FALSE) +
  geom_text(
    aes(label = paste0(round(R2, 2))),
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
  scale_y_discrete(labels = c("Deep (> 10m)", "Shallow (<10 m)")) +
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

p6 = ggplot(dam_depth_assessment,
            aes(
              y = class,
              x = NSE,
              fill = factor(class)
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
    aes(label = paste0(round(NSE, 2))),
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
  scale_y_discrete(labels = c("Deep (> 10m)", "Shallow (<10 m)")) +
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
plot2
ggsave("Results/0.Figures/performance_by_reservoir_depth.png", plot=plot2, width=3.75, height=3.75, units="in")

# plot2 + plot_annotation(caption = "<50 km: Reaches within 50 km downstream of a dam.\n>50 km: Reaches beyond 50 km downstream of a dam.")
# 
# ggsave(
#   "Results/0.Figures/dam_depth_assessment.png",
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
    y = RMSE_within_50,
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
                                                         variation != 3), mapping=aes(x=, y=RMSE_within_50_mean,label = paste0(round(RMSE_within_50_mean,2))), position = position_dodge(width = 0.9), vjust = -1.5, hjust=0.5, color="white", size=3, show.legend = FALSE)+
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
    y = NSE_within_50,
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
                                                         variation != 3), mapping=aes(x=, y=NSE_within_50_mean,label = paste0(round(NSE_within_50_mean,3))), position = position_dodge(width = 0.9), vjust = -1.5, hjust=0.5, color="white", size=3, show.legend = FALSE)+
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
