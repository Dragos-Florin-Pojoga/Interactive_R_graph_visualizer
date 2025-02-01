r <- slider(1, 10, 1, 9)
p <- slider(0.1, 1, 0.1, 0.4)
n <- slider(1, 10, 1, 4)

x <- seq(0, (n * r), length.out = 1000)

cdf_X <- function(x) pbinom(x, r, p)
cdf_5Xminus4 <- function(x) pbinom(pmax(floor((x + 4)/5), 0), r, p)
cdf_X3 <- function(x) pbinom(floor(x^(1/3)), r, p)
cdf_SumXi <- function(x) pbinom(x, n*r, p)

plot_func(cdf_X, x, "X")
plot_func(cdf_5Xminus4, x, "5X-4")
plot_func(cdf_X3, x, "X³")
plot_func(cdf_SumXi, x, "Sum X_i")