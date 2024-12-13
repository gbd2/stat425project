library(rjags)
library(coda)

setwd("")

no.prcp <- read.csv("data/no_prcp_manufacturer.csv", header = TRUE)
w.prcp <- read.csv("data/with_prcp_manufacturer.csv", header = TRUE)

# Fit on dry conditions data
n.1 <- c(length(no.prcp$Toyota), length(no.prcp$Chevrolet), length(no.prcp$Ford)) * 5
y.1 <- c(sum(no.prcp$Toyota), sum(no.prcp$Chevrolet), sum(no.prcp$Ford))
N <- 3

jagsData <- list("y" = y.1, "n" = n.1, "N" = N, 
             "mua" = 1, "mub" = 1, 
             "logn" = log(2))

model <- jags.model(file = "code/hierarchical_binomial.txt", data = jagsData, n.chains=3)
result.1 <- coda.samples(model, variable.names = "p", n.iter=1e4, n.adapt=1e3)

summary(result.1)
plot(result.1)
effectiveSize(result.1)
gelman.diag(result.1)

# Fit on rainy conditions data
n.2 <- c(length(w.prcp$Toyota), length(w.prcp$Chevrolet), length(w.prcp$Ford)) * 5
y.2 <- c(sum(w.prcp$Toyota), sum(w.prcp$Chevrolet), sum(w.prcp$Ford))
N <- 3

jagsData <- list("y" = y.2, "n" = n.2, "N" = N, 
                 "mua" = 1, "mub" = 1, 
                 "logn" = log(2))

model <- jags.model(file = "code/hierarchical_binomial.txt", data = jagsData, n.chains=3)
result.2 <- coda.samples(model, variable.names = "p", n.iter=1e4, n.adapt=1e3)

summary(result.2)
plot(result.2)
effectiveSize(result.2)
gelman.diag(result.2)

# Evaluate probabilities
mean(c(result.1[,1][[1]]) < c(result.2[,1])[[1]])
mean(c(result.1[,2][[1]]) < c(result.2[,2])[[1]])
mean(c(result.1[,3][[1]]) < c(result.2[,3])[[1]])