theta <- slider(0.1, 10, 0.1, 1)
integrand <- function(x) (theta^2 / (1 + theta)) * (1 + x) * exp(-theta * x)
Z <- integrate(integrand, 0, Inf)$value
k <- 1 / Z

mean <- integrate(function(x) x * k * integrand(x), 0, Inf)$value
ex2 <- integrate(function(x) x^2 * k * integrand(x), 0, Inf)$value
var <- ex2 - mean^2

f <- function(x) k * integrand(x)

xs <- seq(0, 10, length.out = 100)
plot_func(f, xs, "e)")
cat("Media:", mean, "\n")
cat("Varianța:", var, "\n")