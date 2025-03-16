xs <- seq(-5, 5, length.out = 200)

mean_result <- tryCatch({
    integrate(function(x) x * (1/(pi*(1+x^2))), -Inf, Inf)$value
}, error = function(e) "divergentă")

var_result <- tryCatch({
    ex2 <- integrate(function(x) x^2 * (1/(pi*(1+x^2))), -Inf, Inf)$value
    ex2 - if(is.numeric(mean_result)) mean_result^2 else NA
}, error = function(e) "divergentă")

f <- function(x) 1/(pi*(1+x^2))

plot_func(f, xs, "g)")

cat("Media:", if(is.numeric(mean_result)) mean_result else "nedefinită (integrală divergentă)",
    "\nVarianța:", if(is.numeric(var_result)) var_result else "nedefinită (integrală divergentă)")
