purpose: the one check shared by Builders and the Supervisor's gates
signature: check_folder(folder: str, options: dict) -> list[str]
inputs: folder under src; options changed, cases, kind
outputs: failed rule names as the gates name them, [] when clean
side effects: runs ruff and pytest as subprocesses
work item id: 0006-1-check_folder-code
