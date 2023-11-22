library(ggplot2)
library(ggthemes)
library(readr)
library(dplyr)

ml1_blk1_cv = read_csv("Results/ML1/blk1_crossval.csv")

ggplot(data = ml1_blk1_cv, aes(x = epoch, y = loss, color = class)) +
  geom_point(size=0.05) +
  geom_smooth(method = "loess", se = FALSE, span = 0.1) +
  theme_bw() +
  theme(legend.position = c(0.8, 0.8), )
# scale_color_manual(values=c("red", "blue", "green", "orange", "purple")) +
# theme_economist() +
# labs(title="ML1 Block 1 Cross Validation Loss", x="Epoch", y="Loss") +
# theme(plot.title = element_text(hjust = 0.5))


cv_trends =  ml1_blk1_cv %>%
  group_by(class, epoch) %>%
  summarise_at(vars(loss), mean, na.rm = TRUE)

ggplot() +
  geom_smooth(
    data = ml1_blk1_cv,
    aes(x = epoch, y = loss, color = class),
    method = "loess",
    se = FALSE,
    span = 0.2
  ) +
  # geom_line(data = cv_trends, aes(x = epoch, y = loss, color = class)) +
  theme_bw()
