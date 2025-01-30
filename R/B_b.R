a <- slider(-10, 10, 1, 0)
b <- slider(-10, 10, 1, 0)
# Normalization
Z <- integrate(function(x) a*x + b*x^2, 0, 1)$value
k <- 1 / Z
# Mean and Variance
mean <- integrate(function(x) x * k * (a*x + b*x^2), 0, 1)$value
ex2 <- integrate(function(x) x^2 * k * (a*x + b*x^2), 0, 1)$value
var <- ex2 - mean^2

xs <- seq(0, 1, length.out = 100)
plot_func(function(x) k * (a*x + b*x^2), xs, "b)")
cat("Media:", mean, "Varianța:", var)