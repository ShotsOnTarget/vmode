purpose: read a wiki page written by wiki_write and return it as a dict.
signature: wiki_read(root: str, page_id: str) -> dict
inputs: root directory containing wiki pages; page_id identifying the page.
outputs: the page dict {'id', 'title', 'pattern', 'evidence', 'cost', 'fix', 'created', 'last_used', 'times_used'}.
side effects: reads a file from disk; none written.
work item id: 0002-2-wiki_read-code
