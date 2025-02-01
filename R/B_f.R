x_min <- slider(-5, 5, 0.01, -2)
x_max <- slider(-5, 5, 0.01, 4)

f <- function(x) {
    ifelse(x < 0, (1/3)*exp(x), ifelse(x < 1, 1/3, (1/3)*exp(-(x - 1))))
}

xs <- seq(x_min, x_max, length.out = 1000)

plot_func(f, xs, name = "f(x)")

mu <- integrate(function(x) x * f(x), -Inf, Inf)$value
ex2 <- integrate(function(x) x^2 * f(x), -Inf, Inf)$value
varianta <- ex2 - mu^2

cat("Media:", mu, "\n")
cat("Varianța:", varianta, "\n")