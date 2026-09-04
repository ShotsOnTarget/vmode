purpose: write a wiki page dict to `<root>/<id>.md` in the wiki's front-matter format
signature: wiki_write(root: str, page: dict) -> str
inputs: root: directory, created if missing. page: dict with id, title, pattern, evidence, cost, fix, created, last_used, times_used
outputs: path of the written file `<root>/<id>.md`, overwriting if present
side effects: creates root directory if missing; writes/overwrites a file on disk
work item id: 0002-2-wiki_write-code
