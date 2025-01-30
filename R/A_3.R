lambda <- slider(0.1, 5, 0.1, 0.5)
n <- slider(1, 10, 1, 3)

x <- seq(0, 20, length.out = 1000)

cdf_X <- function(x) pexp(x, lambda)
cdf_2plus5X <- function(x) ifelse(x >= 2, pexp((x - 2)/5, lambda), 0)
cdf_X2 <- function(x) pexp(sqrt(pmax(x, 0)), lambda)
cdf_SumXi <- function(x) pgamma(x, shape = n, rate = lambda)

plot_func(cdf_X, x, "X")
plot_func(cdf_2plus5X, x, "2+5X")
plot_func(cdf_X2, x, "X²")
plot_func(cdf_SumXi, x, "Sum X_i")