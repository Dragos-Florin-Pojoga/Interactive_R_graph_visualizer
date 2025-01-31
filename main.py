import sys
import signal

import r_runner, app


if __name__ == "__main__":
    # needed for CTRL+C to work with pyqt6
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    r_runner.spawn_R_PROCESS()
    
    app.init(sys.argv)
    exit_code = app.run()
    
    sys.exit(exit_code)
