set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]

# The record client every recipe uses; a stale bd elsewhere on PATH cannot read the Dolt record.
export VMODE_BD := "C:/Users/steve/code/bin/bd.exe"

# Start the board HTTP server on 127.0.0.1 (blocking). Needs the Dolt record server on port 3306.
board port="8080":
    $env:PYTHONPATH = "src"; python -c "import signal, os; signal.signal(signal.SIGINT, lambda *a: os._exit(0)); from board_serve.board_serve import board_serve; board_serve({{port}})"

# Start the Supervisor (from its worktree at HEAD), one Engineer and one Analyst puller, each in its own window that outlives this shell.
loop:
    git -C ../vmode-supervisor checkout -q --detach (git rev-parse HEAD)
    if (Test-Path work/stop) { Remove-Item work/stop }
    Start-Process python -ArgumentList "../vmode-supervisor/tools/run_puller.py supervisor -" -WorkingDirectory (Get-Location)
    Start-Process python -ArgumentList "tools/run_puller.py engineer roles/pullers/by_column.py" -WorkingDirectory (Get-Location)
    Start-Process python -ArgumentList "tools/run_puller.py analyst roles/pullers/by_column.py" -WorkingDirectory (Get-Location)

# Start N Builder pullers in their own windows (default 2).
builders n="2":
    if (Test-Path work/stop) { Remove-Item work/stop }
    1..{{n}} | ForEach-Object { Start-Process python -ArgumentList "tools/run_puller.py builder roles/pullers/by_column.py" -WorkingDirectory (Get-Location); Start-Sleep -Seconds 15 }

# Ask every puller to stop at its next poll.
stop:
    New-Item -ItemType File -Force work/stop | Out-Null
