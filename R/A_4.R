lambda <- slider(0.1, 10, 0.1, 7)
n <- slider(1, 10, 1, 6)

x <- seq(0, qpois(0.999, n*lambda), length.out = 1000)

cdf_X <- function(x) ppois(x, lambda)
cdf_3Xminus2 <- function(x) ppois(pmax(floor((x + 2)/3), 0), lambda)
cdf_X2 <- function(x) ppois(floor(sqrt(x)), lambda)
cdf_SumXi <- function(x) ppois(x, n*lambda)

plot_func(cdf_X, x, "X")
plot_func(cdf_3Xminus2, x, "3X-2")
plot_func(cdf_X2, x, "X²")
plot_func(cdf_SumXi, x, "Sum X_i")