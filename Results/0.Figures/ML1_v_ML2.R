library(ggplot2)
library(ggthemes)
library(dplyr)
library(readr)

# Read in data
ml1_vml2 = read_csv("Results/ML2/cv_ml1_v_ml2.csv")

# Plot boxplots of ML1 and ML2
ggplot(ml1_vml2, aes(x = Model, y = RMSE, color=Model)) +
  geom_boxplot() +
  theme_few() +
  labs(x = "Model", y = "RMSE", title = "Comparison of Cross-validated RMSE for ML1 and ML2 (50 km downstream of dams)")
