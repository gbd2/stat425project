library(rjags)
library(coda)

setwd("C:/Users/mathw/OneDrive/Desktop/College/Classes/Fall 24/STAT 425/stat425project")
regression.data <- read.csv("data/manufacturer_regression_data.csv", header = TRUE)

N <- nrow(regression.data)
M <- 3
y <- regression.data$top5_count
groups <- as.integer(factor(regression.data$manufacturer))
X <- as.matrix(regression.data[,1:5])

min_max_norm <- function(x) {
  (x - min(x)) / (max(x) - min(x))
}

X <- cbind(1, apply(X, 2, min_max_norm))


mu <- rep(0, ncol(X))
tau <- diag(0.001, ncol(X))

jagsData <- list(
  y = y,
  X = X,
  N = N,
  M = M,
  groups = groups,
  mu.theta = mu,
  mu.gamma = mu,
  tau.theta = tau,
  tau.gamma = tau
)

model <- jags.model(file = "code/binomial_glmm.txt", data = jagsData, n.chains=1)
result <- coda.samples(model, variable.names = c("theta", "gamma"), n.iter=1e4, n.burnin=1e3, n.thin=10)
summary(result)

for (i in 1:ncol(X)){
  plot(result[,i], main = colnames(X)[i])
}