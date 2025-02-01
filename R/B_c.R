x <- 1:1000  # aproximare
r_x <- 4 / (x * (x + 1) * (x + 2))
Z <- sum(r_x)
k <- 1 / Z

mean <- sum(x * k * r_x)
ex2 <- sum(x^2 * k * r_x)
var <- ex2 - mean^2

plot_line(x[1:20], k * r_x[1:20], "c)")
cat("Media:", mean, "\n")
cat("Varianța:", var, "\n")