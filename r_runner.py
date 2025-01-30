import subprocess

def param(start, end, step):
    return [round(x, 10) for x in frange(start, end, step)]

def frange(start, stop, step):
    while start <= stop:
        yield start
        start += step

def execute_r_script(r_snippet, **params):
    for key, value in params.items():
        r_array = "c(" + ", ".join(map(str, value)) + ")"
        r_snippet = r_snippet.replace(f"{key} <- param", f"{key} <- {r_array}")

    print(r_snippet)

    process = subprocess.run(
        ["Rscript", "-e", r_snippet],
        capture_output=True,
        text=True,
    )

    if process.returncode != 0:
        raise RuntimeError(f"R script failed: {process.stderr}")

    return process.stdout.strip()

if __name__ == "__main__":
    r_code = """
    x <- param
    y <- param
    results <- sin(x * y)
    cat(results)
    """

    x_values = param(1, 10, 0.1)
    y_values = param(1, 10, 0.2)

    result = execute_r_script(r_code, x=x_values, y=y_values)
    print(result)