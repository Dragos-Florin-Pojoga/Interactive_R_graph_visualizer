# this needs 1:1 scaling

# https://www.reddit.com/r/teenagers/comments/b92sov/comment/ek2r8bt/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button
# https://www.desmos.com/calculator/7iaudxgfpb

theta <- seq(0, 2 * pi, length.out = 1000)

# 1. Ellipse: 2.5y² + x² = 7.5
x1 <- seq(-sqrt(7.5), sqrt(7.5), length.out = 1000)
y1_upper <- sqrt((7.5 - x1^2) / 2.5)
y1_lower <- -y1_upper
plot_line(x1, y1_upper)
plot_line(x1, y1_lower)

# 2. Line: y = 5x + 1.26 for 0.093 ≤ x ≤ 0.3365
x2 <- seq(0.093, 0.3365, length.out = 100)
plot_line(x2, 5 * x2 + 1.26)

# 3. Line: y = -0.2x + 3 for 0.3365 ≤ x ≤ 2
x3 <- seq(0.3365, 2, length.out = 100)
plot_line(x3, -0.2 * x3 + 3)

# 4. Circle: (y-0.35)² + (x-1)² = 0.2
r <- sqrt(0.2)
plot_line(1 + r * cos(theta), 0.35 + r * sin(theta))

# 5. Circle: (y-0.35)² + (x+1)² = 0.2
plot_line(-1 + r * cos(theta), 0.35 + r * sin(theta))

# 6. Circle: (y-2.5)² + (x-2.45)² = 0.2
plot_line(2.45 + r * cos(theta), 2.5 + r * sin(theta))

# 7. Parabola: y = (x/1.8)² - 1.3 for -1 ≤ x ≤ 1
x7 <- seq(-1, 1, length.out = 100)
plot_line(x7, (x7 / 1.8)^2 - 1.3)

# 8. Upper Half: y = sqrt(10 - 4.5x²) - 2.2 for x ≤ -1.45
x8 <- seq(-sqrt(10/4.5), -1.45, length.out = 100)
plot_line(x8, sqrt(10 - 4.5 * x8^2) - 2.2)

# 9. Lower Half: y = -sqrt(10 - 4.5x²) - 2.2
x9 <- seq(-sqrt(10/4.5), sqrt(10/4.5), length.out = 1000)
plot_line(x9, -sqrt(10 - 4.5 * x9^2) - 2.2)

# 10. Circle Segment: y = sqrt(0.3 - (x+2.5)²) + 0.9 for x < -2.022
x10 <- seq(-2.5 - sqrt(0.3), -2.022, length.out = 100)
plot_line(x10, sqrt(0.3 - (x10 + 2.5)^2) + 0.9)

# 11. Circle Segment: y = -sqrt(0.3 - (x+2.5)²) + 0.9 for x < -2.715
x11 <- seq(-2.5 - sqrt(0.3), -2.715, length.out = 100)
plot_line(x11, -sqrt(0.3 - (x11 + 2.5)^2) + 0.9)

# 12. Circle Segment: y = sqrt(0.3 - (x-2.5)²) + 0.9 for x > 2.022
x12 <- seq(2.022, 2.5 + sqrt(0.3), length.out = 100)
plot_line(x12, sqrt(0.3 - (x12 - 2.5)^2) + 0.9)

# 13. Circle Segment: y = -sqrt(0.3 - (x-2.5)²) + 0.9 for x > 2.715
x13 <- seq(2.715, 2.5 + sqrt(0.3), length.out = 100)
plot_line(x13, -sqrt(0.3 - (x13 - 2.5)^2) + 0.9)

# 14. Upper Half: y = sqrt(10 - 4.5x²) - 2.2 for x ≥ 1.45
x14 <- seq(1.45, sqrt(10/4.5), length.out = 100)
plot_line(x14, sqrt(10 - 4.5 * x14^2) - 2.2)

# 15. Horizontal Line: y = -5.36 for -2.2 ≤ x ≤ 2.2
x15 <- seq(-2.2, 2.2, length.out = 100)
plot_line(x15, rep(-5.36, 100))

# 16. Circle Segment: y = 0.8√(1 - (x-1.2)²) -5.36 for x ≥ 0.982
x16 <- seq(0.982, 2.2, length.out = 100)
plot_line(x16, 0.8 * sqrt(1 - (x16 - 1.2)^2) - 5.36)

# 17. Circle Segment: y = 0.8√(1 - (x+1.2)²) -5.36 for x ≤ -0.982
x17 <- seq(-2.2, -0.982, length.out = 100)
plot_line(x17, 0.8 * sqrt(1 - (x17 + 1.2)^2) - 5.36)

# 18. Circle Segment: y = √(1.4 - (x+1)²) -3 for x ≤ -1.485
x18 <- seq(-1 - sqrt(1.4), -1.485, length.out = 100)
plot_line(x18, sqrt(1.4 - (x18 + 1)^2) - 3)

# 19. Circle Segment: y = -√(1.4 - (x+1)²) -3 for x ≤ -1.166
x19 <- seq(-1 - sqrt(1.4), -1.166, length.out = 100)
plot_line(x19, -sqrt(1.4 - (x19 + 1)^2) - 3)

# 20. Circle Segment: y = √(1.4 - (x-1)²) -3 for x ≥ 1.485
x20 <- seq(1.485, 1 + sqrt(1.4), length.out = 100)
plot_line(x20, sqrt(1.4 - (x20 - 1)^2) - 3)

# 21. Circle Segment: y = -√(1.4 - (x-1)²) -3 for x ≥ 1.166
x21 <- seq(1.166, 1 + sqrt(1.4), length.out = 100)
plot_line(x21, -sqrt(1.4 - (x21 - 1)^2) - 3)

# * translated from desmos to R using AI