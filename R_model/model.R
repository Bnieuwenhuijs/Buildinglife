# File: model.R
# Author: Ioannis-Pavlos Panteliadis <i.p.panteliadis@students.uu.nl>
# Last Updated: 05/14/2019
# 
# Brief:  Generate correlation plot for the given data.

# Custom sampling function
sample.df <- function(df, n) df[sample(nrow(df), n), , drop = FALSE]

RMSE <- function(model, observed){
    sqrt(mean((m - o)^2))
}


#####################
# The "real" dataset
#####################
df <- read.csv(file = "Buildinglife_dataset.csv")
train <- sample.df(df, 1000)
test <- sample.df(df, 405)

linearMod <- lm(concrete_base ~ brick_wall_total + glass_window_area + steel, data = train)
summary(linearMod)
AIC(linearMod)
BIC(linearMod)

actual <- test$concrete_base
predicted <- predict(linearMod, test)

# Root mean squared error
rmse <- sqrt(mean(residuals(linearMod)  ^2))
rmse

# Residual sum of squares
rss <- sum(residuals(linearMod)^2)
rss










