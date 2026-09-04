purpose: list every record item of a given kind, including closed ones
signature: record_list_kind(kind: str) -> list[dict]
inputs: kind: one of the six kinds
outputs: list of {'id','kind','title','owner','state'} for every item with that kind label
side effects: spawns a subprocess running the `bd` executable, via record_run
work item id: 0001-1-record_list_kind-code
