purpose: run the `bd` CLI with given arguments and return its parsed JSON output
signature: record_run(args: list[str]) -> dict | list
inputs: args: the bd arguments after the program name, e.g. ['show', 'vm-1']; '--json' is appended internally
outputs: the parsed JSON that bd printed on stdout
side effects: spawns a subprocess running the `bd` executable
work item id: 0001-1-record_run-code
