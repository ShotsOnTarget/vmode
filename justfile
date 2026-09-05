set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]

# The record client every recipe uses; a stale bd elsewhere on PATH cannot read the Dolt record.
export VMODE_BD := "C:/Users/steve/code/bin/bd.exe"

# Start the board HTTP server on 127.0.0.1 (blocking). Needs the Dolt record server on port 3306.
board port="8080":
    $env:PYTHONPATH = "src"; python -c "import signal, os; signal.signal(signal.SIGINT, lambda *a: os._exit(0)); from board_serve.board_serve import board_serve; board_serve({{port}})"
