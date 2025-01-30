a <- slider(0,8,0.01,2.42)
b <- slider(0,8,0.1,0.5)
c <- slider(1,30,1,10)
fn <- function(x) sin(x+a)+b
xs <- seq(-c,c,0.1)
plot_func(fn, xs)

print("example logging")

cat("a:", a , "\nb:", b, "\nc:", c, "\n")