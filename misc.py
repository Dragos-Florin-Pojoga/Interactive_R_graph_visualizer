def clamp(min, max, val):
    if val < min:
        return min
    if val > max:
        return max
    return val

def snap(min, max, step, val):
    if val < min:
        return min
    if val > max:
        return max
    
    steps = round((val - min) / step)
    stepped = min + steps * step

    return clamp(min, max, stepped)

def scaled_to_value(min, step, scaled):
    return min + scaled * step

def value_to_scaled(min, step, value):
    return round((value - min) / step)

