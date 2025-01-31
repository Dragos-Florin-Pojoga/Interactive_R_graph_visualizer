import subprocess

from constants import CUSTOM_R_CODE

# persistent R interactive process
R_PROCESS = 'NOT_YET_INITIALIZED'

def spawn_R_PROCESS():
    global R_PROCESS
    R_PROCESS = subprocess.Popen(
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
    {CUSTOM_R_CODE}
    {script}
    cat("\\nEND_OF_OUTPUT\\n")
}}, error = function(e) {{
    cat("\\nERROR:", e$message, "\\n")
    cat("\\nEND_OF_OUTPUT\\n")
}})
"""
    for i in range(1,3):
        try:
            R_PROCESS.stdin.write(wrapped_script + "\n")
            R_PROCESS.stdin.flush()
        except:
            print("!!! R PROCESS DIED")
            spawn_R_PROCESS()
            # this here, is an extremely lazy thing
            # if we send unfinished code to the R process, it may simply give up and exit
            # instead of trying to detect valid R code, we just respawn and kill as many processes as needed
            # this is why writing code directly in the editor is quite slow.
            # it may be spawning a process for every letter typed in an unfinished code that will cause the interpreter to exit :/
            continue
        break
    else:
        print("!!! UNABLE TO RESPAWN R PROCESS")
        exit()
    
    output = []
    while True:
        line = R_PROCESS.stdout.readline()
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
    
    return output

