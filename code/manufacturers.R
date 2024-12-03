library(rjags)
library(coda)

setwd("C:/Users/mathw/OneDrive/Desktop/College/Classes/Fall 24/STAT 425/stat425project")

no.prcp <- read.csv("data/no_prcp_manufacturer.csv", header = TRUE)
w.prcp <- read.csv("data/with_prcp_manufacturer.csv", header = TRUE)


n.1 <- c(length(no.prcp$Toyota), length(no.prcp$Chevrolet), length(no.prcp$Ford)) * 5
y.1 <- c(sum(no.prcp$Toyota), sum(no.prcp$Chevrolet), sum(no.prcp$Ford))
N <- 3

jagsData <- list("y" = y.1, "n" = n.1, "N" = N, 
             "mua" = 1, "mub" = 1, 
             "logn" = log(2))

model <- jags.model(file = "code/hierarchical_binomial.txt", data = jagsData, n.chains=1)
result <- coda.samples(model, variable.names = "p", n.iter=1e4, n.adapt=1e3)

summary(result)
plot(result)


n.2 <- c(length(w.prcp$Toyota), length(w.prcp$Chevrolet), length(w.prcp$Ford)) * 5
y.2 <- c(sum(w.prcp$Toyota), sum(w.prcp$Chevrolet), sum(w.prcp$Ford))
N <- 3

jagsData <- list("y" = y.2, "n" = n.2, "N" = N, 
                 "mua" = 1, "mub" = 1, 
                 "logn" = log(2))

model <- jags.model(file = "code/hierarchical_binomial.txt", data = jagsData, n.chains=1)
result <- coda.samples(model, variable.names = "p", n.iter=1e4, n.adapt=1e3)

summary(result)
plot(result)