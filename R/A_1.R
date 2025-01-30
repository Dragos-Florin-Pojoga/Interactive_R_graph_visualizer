n <- slider(1, 10, 1, 6)

x <- seq(-5, 10, length.out = 1000)

cdf_X <- function(x) pnorm(x)
cdf_3minus2X <- function(x) 1 - pnorm((3 - x)/2)
cdf_X2 <- function(x) pchisq(pmax(x, 0), df = 1)
cdf_SumXi <- function(x) pnorm(x, 0, sqrt(n))
cdf_SumXi2 <- function(x) pchisq(pmax(x, 0), df = n)

plot_func(cdf_X, x, "X")
plot_func(cdf_3minus2X, x, "3-2X")
plot_func(cdf_X2, x, "X²")
plot_func(cdf_SumXi, x, "Sum X_i")
plot_func(cdf_SumXi2, x, "Sum X_i²")