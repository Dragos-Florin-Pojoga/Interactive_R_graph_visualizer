mu <- slider(-5, 5, 1, -2)
sigma <- slider(0.1, 5, 0.1, 1.4)
n <- slider(1, 10, 1, 3)

x <- seq(-10, 20, length.out = 1000)

cdf_X <- function(x) pnorm(x, mu, sigma)
cdf_3minus2X <- function(x) pnorm(x, 3 - 2*mu, 2*sigma)
cdf_X2 <- function(x) pchisq(pmax(x, 0)/sigma^2, df = 1, ncp = (mu/sigma)^2)
cdf_SumXi <- function(x) pnorm(x, n*mu, sqrt(n)*sigma)
cdf_SumXi2 <- function(x) pchisq(pmax(x, 0)/sigma^2, df = n, ncp = n*(mu/sigma)^2)

plot_func(cdf_X, x, "X")
plot_func(cdf_3minus2X, x, "3-2X")
plot_func(cdf_X2, x, "X²")
plot_func(cdf_SumXi, x, "Sum X_i")
plot_func(cdf_SumXi2, x, "Sum X_i²")