a <- slider(0.1, 10, 0.1, 4)
# normalizare
Z <- integrate(function(x) x^a, 0, 2)$value
k <- 1 / Z

mean <- integrate(function(x) x * k * x^a, 0, 2)$value
ex2 <- integrate(function(x) x^2 * k * x^a, 0, 2)$value
var <- ex2 - mean^2

xs <- seq(0, 2, length.out = 100)
plot_func(function(x) k * x^a, xs, "a)")
cat("Media:", mean, "\n")
cat("Varianța:", var, "\n")