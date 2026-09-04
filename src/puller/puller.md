purpose: loop calling once() for a role until a stop file appears
signature: puller(role: str, config_path: str, invoke, options: dict) -> int
inputs: role, config_path, invoke as for pull_once; options dict with 'stop_file' and optional 'once'
outputs: number of passes made
side effects: sleeps between passes; calls once(), which may claim and mutate items
work item id 0003-4-puller-code
