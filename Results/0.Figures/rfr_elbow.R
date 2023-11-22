library(ggplot2)
library(dplyr)
library(patchwork)
library(readr)

rfr1_cv = read_csv("Results/2.WaterTempEst/2.RandomForestRegression/RFR1_cv_results.csv")
rfr2_cv = read_csv("Results/2.WaterTempEst/2.RandomForestRegression/RFR2_1_cv_results.csv")

p1 = ggplot(data=rfr1_cv, aes(x=param_n_estimators,y=mean_test_score)) +
  geom_line() +
  geom_point() +
  geom_vline(xintercept = 150, linetype="dashed") +
  labs(x="Number of Estimators (n)", y="Mean Test Score (MSE)", title="a)") +
  theme_bw()
  # theme(plot.title = element_text(hjust = 0.5))

p1

p2 = ggplot(data=rfr2_cv, aes(x=param_n_estimators,y=mean_test_score)) +
  geom_line() +
  geom_point() +
  geom_vline(xintercept = 250, linetype="dashed") +
  labs(x="Number of Estimators (n)", y="Mean Test Score (MSE)", title="b)") +
  theme_bw()
  # theme(plot.title = element_text(hjust = 0.5))

p2

plot = p1 + p2

ggsave("Results/0.Figures/rfr_elbow.png", plot,
       width = 6.5,
       height = 3,
       units = "in",
       dpi = 300)
