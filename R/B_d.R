x <- 1:9
r_x <- log(x) / (x + 1)
Z <- sum(r_x)
k <- 1 / Z
# Mean and Variance
mean <- sum(x * k * r_x)
ex2 <- sum(x^2 * k * r_x)
var <- ex2 - mean^2

plot_line(x, k * r_x, "d)")
cat("Media:", mean, "Varianța:", var)