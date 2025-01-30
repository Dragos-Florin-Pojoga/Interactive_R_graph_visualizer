import subprocess
import re

def frange(start, stop, step):
    while start <= stop:
        yield start
        start += step

def parse_and_replace(line):
    match = re.match(r"(\w+)\s*<-\s*param\(([^)]+)\)", line)
    if not match:
        raise ValueError(f"Line does not match expected format: {line}")

    variable_name = match.group(1)
    args = match.group(2).split(",")
    start, end, step = map(float, args)

    sequence = [round(x, 10) for x in frange(start, end, step)]

    r_sequence = "c(" + ", ".join(map(str, sequence)) + ")"
    new_line = f"{variable_name} <- {r_sequence}"
    return new_line

def preprocess_r_script(r_script, **params):
    lines = r_script.split("\n")
    updated_lines = []
    for line in lines:
        if "param(" in line:
            updated_lines.append(parse_and_replace(line))
        else:
            updated_lines.append(line)
    return "\n".join(updated_lines)

if __name__ == "__main__":
    r_script = """
x <- param(1, 10, 0.1)
y <- param(1, 10, 0.2)
results <- sin(x * y)
cat(results, sep="\n")
"""

    updated_script = preprocess_r_script(r_script)
    print(updated_script)

    process = subprocess.run(
        ["Rscript", "-e", updated_script],
        capture_output=True,
        text=True,
    )

    if process.returncode != 0:
        raise RuntimeError(f"R script failed: {process.stderr}")

    results = [float(r) for r in process.stdout.strip().split('\n')]
    print(results)