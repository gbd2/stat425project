library(rjags)
library(coda)

setwd("")
regression.data <- read.csv("data/manufacturer_regression_data.csv", header = TRUE)

N <- nrow(regression.data)
M <- 3

y <- regression.data$top5_count
groups <- as.integer(factor(regression.data$manufacturer))

X <- as.matrix(regression.data[,1:12])

min_max_norm <- function(x) {
  (x - min(x)) / (max(x) - min(x))
}

X <- cbind(1, apply(X, 2, min_max_norm))

mu <- rep(0, ncol(X))
tau <- diag(0.1, ncol(X))

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

model <- jags.model(file = "code/binomial_glmm.txt", data = jagsData, n.chains=3)
result <- coda.samples(model, variable.names = c("theta", "gamma"), n.iter = 20000, n.burnin = 5000, n.thin = 5)

summary(result)
plot(result)
gelman.diag(result)
