import subprocess

r_process = subprocess.Popen(
    ["R", "--slave"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1,
)

def run_r_script(script):
    wrapped_script = f"""
    tryCatch({{
        {script}
        cat("END_OF_OUTPUT\\n")
    }}, error = function(e) {{
        cat("ERROR:", e$message, "\\n")
        cat("END_OF_OUTPUT\\n")
    }})
    """
    
    r_process.stdin.write(wrapped_script + "\n")
    r_process.stdin.flush()
    
    output = []
    while True:
        line = r_process.stdout.readline()
        if not line:
            break  # Process died?
        line = line.strip()
        if line == "END_OF_OUTPUT":
            break
        output.append(line)
    
    for line in output:
        if line.startswith("ERROR:"):
            print(f"R Error: {line}")
            return None
    
    try:
        xs = [float(v) for v in output[0].split(',')]
        ys = [float(v) for v in output[1].split(',')]
    except (IndexError, ValueError) as e:
        print(f"Parse error: {e}")
        return None
    
    return xs, ys

if __name__ == "__main__":
    sample_script = '''
    xs <- seq(1, 10, 0.5)
    ys <- sin(xs)
    cat(paste(xs, collapse=','), '\\n')
    cat(paste(ys, collapse=','), '\\n')
    '''
    
    result = run_r_script(sample_script)
    if result:
        xs, ys = result
        print(f"Got {len(xs)} X values and {len(ys)} Y values")

    result = run_r_script(sample_script)
    if result:
        xs, ys = result
        print(f"Got {len(xs)} X values and {len(ys)} Y values")

    result = run_r_script(sample_script)
    if result:
        xs, ys = result
        print(f"Got {len(xs)} X values and {len(ys)} Y values")