library(rjags)
library(coda)

setwd("C:/Users/mathw/OneDrive/Desktop/College/Classes/Fall 24/STAT 425/stat425project")
regression.data <- read.csv("data/swap_regression_data.csv", header = TRUE)

N <- nrow(regression.data)
y <- round(regression.data$avg_pos_swap)

X <- as.matrix(regression.data[,1:5])

min_max_norm <- function(x) {
  (x - min(x)) / (max(x) - min(x))
}

# X <- cbind(1, apply(X, 2, min_max_norm))
X <- cbind(1, X)

mu <- rep(0, ncol(X))
tau <- diag(0.001, ncol(X))

jagsData <- list(
  y = y,
  X = X,
  N = N,
  mu = mu,
  tau = tau
)

model <- jags.model(file = "code/poisson_glm.txt", data = jagsData, n.chains=3, n.adapt=1e4)
result <- coda.samples(model, variable.names = c("theta"), n.iter = 1e5, n.burnin = 1e5)

summary(result)

for (i in 1:ncol(X)){
  plot(result[,i], main = colnames(X)[i])
}

effectiveSize(result)
gelman.diag(result)
